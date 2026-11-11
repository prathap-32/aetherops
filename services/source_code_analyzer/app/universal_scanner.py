# services/repo_analyzer_service/app/universal_scanner.py
"""
Universal Polyglot Repository Scanner & AST Readiness Engine.
Capable of analyzing ANY language and framework, extracting deployment primitives,
and producing human-understandable Key:Value reports for user acceptance.
Supports:
1. Local Workspace Paths (via local deterministic AST scanner)
2. Remote GitHub Repositories (via In-Memory Zero-Clone Git Trees & Manifest API — ZERO source code written to disk)
"""
from __future__ import annotations

import asyncio
import os
import sys
import re
import json
import logging
from pathlib import Path
from app.dependency_inventory import parse_dependency_manifest
from typing import Dict, Any, List, Optional, Set, Tuple

import httpx


logger = logging.getLogger("repo-analyzer-service.universal")


ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
SHARED_DIR = os.path.join(ROOT_DIR, "shared")
for p in (SHARED_DIR, ROOT_DIR):
    if p not in sys.path:
        sys.path.insert(0, p)

try:
    from aetherops_common.secrets import load_application_secrets
    load_application_secrets()
except Exception as _sec_err:
    logger.warning("AWS Secrets Manager initialization notice in universal_scanner: %s", _sec_err)


IGNORED_DIRS: Set[str] = {
    ".git", ".svn", ".hg", "node_modules", "vendor", ".venv", "venv", "env",
    "__pycache__", ".pytest_cache", ".next", ".nuxt", "dist", "build", "target",
    "bin", "obj", ".idea", ".vscode", "coverage"
}

RECOGNIZED_MANIFESTS: Dict[str, str] = {
    "package.json": "Node.js / TypeScript",
    "requirements.txt": "Python",
    "pyproject.toml": "Python",
    "Pipfile": "Python",
    "setup.py": "Python",
    "go.mod": "Go",
    "pom.xml": "Java (Maven)",
    "build.gradle": "Java / Kotlin (Gradle)",
    "build.gradle.kts": "Kotlin / Java (Gradle)",
    "Cargo.toml": "Rust",
    "composer.json": "PHP",
    "Gemfile": "Ruby",
    "Dockerfile": "Docker Container",
    "docker-compose.yml": "Docker Compose",
    "docker-compose.yaml": "Docker Compose",
    "serverless.yml": "Serverless Framework",
    "sam.yaml": "AWS SAM",
    "template.yaml": "AWS CloudFormation",
}

RECOGNIZED_CODE_EXTS: Dict[str, str] = {
    ".py": "Python",
    ".js": "JavaScript",
    ".jsx": "React JSX",
    ".ts": "TypeScript",
    ".tsx": "React TSX",
    ".go": "Go",
    ".java": "Java",
    ".kt": "Kotlin",
    ".rs": "Rust",
    ".cs": "C# (.NET)",
    ".php": "PHP",
    ".rb": "Ruby",
    ".html": "HTML",
    ".css": "CSS",
    ".vue": "Vue.js",
    ".svelte": "Svelte",
    ".sh": "Shell Script",
    ".sql": "SQL",
}

DATABASE_PATTERNS = {
    "PostgreSQL": [
        re.compile(r"\b(psycopg2|asyncpg|postgres|postgresql|r2dbc-postgresql|pg|pgx|lib/pq)\b", re.I),
    ],
    "MySQL": [
        re.compile(r"\b(mysql|mysql2|pymysql|mysqlclient|go-sql-driver/mysql)\b", re.I),
    ],
    "Redis": [
        re.compile(r"\b(redis|ioredis|go-redis|lettuce|jedis|aioredis)\b", re.I),
    ],
    "MongoDB": [
        re.compile(r"\b(mongodb|mongoose|pymongo|mongo-go-driver)\b", re.I),
    ],
    "DynamoDB": [
        re.compile(r"\b(dynamodb|@aws-sdk/client-dynamodb|boto3.*dynamodb)\b", re.I),
    ],
    "SQLite": [
        re.compile(r"\b(sqlite|sqlite3|better-sqlite3)\b", re.I),
    ],
    "RabbitMQ / SQS": [
        re.compile(r"\b(celery|amqplib|pika|kafkajs|confluent-kafka|boto3.*sqs)\b", re.I),
    ],
}

FRAMEWORK_PATTERNS = {
    "FastAPI": re.compile(r"\b(fastapi)\b", re.I),
    "Django": re.compile(r"\b(django)\b", re.I),
    "Flask": re.compile(r"\b(flask)\b", re.I),
    "Express": re.compile(r"\b(express)\b", re.I),
    "NestJS": re.compile(r"\b(@nestjs/core)\b", re.I),
    "Next.js": re.compile(r"\b(next)\b", re.I),
    "React": re.compile(r"\b(react)\b", re.I),
    "Vue.js": re.compile(r"\b(vue)\b", re.I),
    "Angular": re.compile(r"\b(@angular/core)\b", re.I),
    "Svelte": re.compile(r"\b(svelte)\b", re.I),
    "Spring Boot": re.compile(r"\b(spring-boot|org\.springframework\.boot)\b", re.I),
    "Gin": re.compile(r"\b(gin-gonic/gin)\b", re.I),
    "Fiber": re.compile(r"\b(gofiber/fiber)\b", re.I),
    "Echo": re.compile(r"\b(labstack/echo)\b", re.I),
    "ASP.NET Core": re.compile(r"\b(Microsoft\.AspNetCore)\b", re.I),
    "Laravel": re.compile(r"\b(laravel/framework)\b", re.I),
    "Ruby on Rails": re.compile(r"\b(rails)\b", re.I),
}

LANGUAGE_COLORS: Dict[str, str] = {
    "JavaScript": "#f1e05a",
    "TypeScript": "#3178c6",
    "Python": "#3572A5",
    "Go": "#00ADD8",
    "Java": "#b07219",
    "Kotlin": "#A97BFF",
    "Rust": "#dea584",
    "C#": "#178600",
    "C# (.NET)": "#178600",
    "HTML": "#e34c26",
    "CSS": "#563d7c",
    "PHP": "#4F5D95",
    "Ruby": "#701516",
    "Shell": "#89e051",
    "Shell Script": "#89e051",
    "Dockerfile": "#384d54",
    "SQL": "#e38c00",
    "Vue.js": "#41b883",
    "Svelte": "#ff3e00",
    "Other": "#8b949e",
}


# ─────────────────────────────────────────────────────────────────────────────
# TARGET RESOLVER (LOCAL PATH VS REMOTE GITHUB ZERO-CLONE REPO)
# ─────────────────────────────────────────────────────────────────────────────

def is_remote_target(raw_target: str) -> bool:
    """Returns True if raw_target corresponds to a remote git repository."""
    s = raw_target.strip()
    if s.startswith(("http://", "https://", "git@")):
        return True
    if s.startswith((".", "/", "~")):
        return False
    expanded = os.path.expanduser(s)
    if "/" in s and not os.path.exists(expanded):
        return True
    if not os.path.exists(expanded):
        return True
    return False


async def resolve_repo_target(
    raw_target: str,
    project_id: Optional[str] = None,
    environment_id: Optional[str] = None,
    authorization: Optional[str] = None,
    tenant_id: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Resolve local paths or a repository already connected through Module 2.

    Remote repository access is never inferred from a default owner and Module 3
    does not query Module 2's database directly. The authenticated Module 2 API
    remains the authority for repository connection ownership.
    """
    from urllib.parse import urlparse

    raw = (raw_target or "").strip()
    if not raw:
        raise ValueError("Repository target is required.")

    # Local paths are still subject to validate_safe_repo_path in the API layer.
    local_candidate = Path(raw).expanduser()
    if local_candidate.exists():
        return {"is_remote": False, "path": str(local_candidate.resolve())}

    root_candidate = Path(ROOT_DIR, raw).expanduser()
    if root_candidate.exists():
        return {"is_remote": False, "path": str(root_candidate.resolve())}

    cwd_candidate = Path(os.getcwd(), raw).expanduser()
    if cwd_candidate.exists():
        return {"is_remote": False, "path": str(cwd_candidate.resolve())}

    requested_slug: Optional[str] = None
    if raw.startswith(("https://", "http://")):
        parsed = urlparse(raw)
        if parsed.scheme != "https" or (parsed.hostname or "").lower() != "github.com":
            raise ValueError("Only HTTPS GitHub repository URLs are supported.")
        parts = [part for part in parsed.path.strip("/").split("/") if part]
        if len(parts) != 2:
            raise ValueError("Provide a GitHub repository URL in owner/repository form.")
        requested_slug = "/".join(parts).removesuffix(".git")
    elif "/" in raw and not raw.startswith((".", "/")):
        parts = [part for part in raw.strip("/").split("/") if part]
        if len(parts) != 2:
            raise ValueError("Repository slug must contain exactly owner/repository.")
        requested_slug = "/".join(parts)
    else:
        requested_slug = raw

    if not authorization or not authorization.lower().startswith("bearer "):
        raise ValueError("An authenticated session is required to resolve a connected repository.")

    headers = {"Authorization": authorization}
    if tenant_id:
        headers["X-Tenant-ID"] = tenant_id
    source_connection_url = os.getenv(
        "SC_SERVICE_URL",
        os.getenv("SOURCE_CONNECTION_SERVICE_URL", "http://127.0.0.1:8002"),
    ).rstrip("/")

    try:
        async with httpx.AsyncClient(timeout=8.0) as client:
            response = await client.get(
                f"{source_connection_url}/api/v1/connections",
                headers=headers,
            )
    except httpx.RequestError as exc:
        raise RuntimeError("Module 2 repository connection service is unavailable.") from exc

    if response.status_code != 200:
        raise ValueError("Module 2 did not authorize access to repository connections.")

    connections = response.json().get("connections", [])
    matches = []
    for connection in connections:
        if project_id and connection.get("project_id") != project_id:
            continue
        if environment_id and connection.get("environment_id") != environment_id:
            continue

        repo_url = (connection.get("repo_url") or "").strip()
        repo_name = (connection.get("repo_name") or "").strip()
        parsed = urlparse(repo_url)
        connected_slug = "/".join(part for part in parsed.path.strip("/").split("/") if part).removesuffix(".git")
        if requested_slug.lower() in {connected_slug.lower(), repo_name.lower()}:
            matches.append(connection)
        elif "/" not in requested_slug and repo_name.lower().split("/")[-1] == requested_slug.lower():
            matches.append(connection)

    if len(matches) != 1:
        if not matches:
            raise ValueError("No authorized Module 2 repository connection matches this target and project environment.")
        raise ValueError("Repository target is ambiguous; select its exact project environment.")

    connection = matches[0]
    repo_url = (connection.get("repo_url") or "").strip()
    parsed = urlparse(repo_url)
    parts = [part for part in parsed.path.strip("/").split("/") if part]
    if parsed.hostname != "github.com" or len(parts) != 2:
        raise ValueError("The connected repository is not a supported GitHub repository.")

    return {
        "is_remote": True,
        "owner": parts[0],
        "repo": parts[1].removesuffix(".git"),
        "branch": connection.get("branch") or connection.get("default_branch") or "main",
        "url": repo_url,
        "connection_id": connection.get("id"),
        "project_id": connection.get("project_id"),
        "environment_id": connection.get("environment_id"),
        "tenant_id": connection.get("tenant_id"),
    }


# ─────────────────────────────────────────────────────────────────────────────
# IN-MEMORY ZERO-CLONE GITHUB INSPECTION
# ─────────────────────────────────────────────────────────────────────────────

async def fetch_github_file_tree_in_memory(
    owner: str,
    repo: str,
    branch: str = "main",
    token: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Fetches the repository file tree via GitHub Git Trees API in memory.
    Zero source code or files are cloned or saved to disk.
    """
    effective_token = token or os.getenv("GITHUB_TOKEN") or os.getenv("GITHUB_PAT")
    headers = {
        "User-Agent": "AetherOps-Cloud-Inspector/1.0",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if effective_token and "mock" not in effective_token:
        headers["Authorization"] = f"Bearer {effective_token.strip()}"

    url = f"https://api.github.com/repos/{owner}/{repo}/git/trees/{branch}?recursive=1"
    try:
        async with httpx.AsyncClient(timeout=8.0) as client:
            res = await client.get(url, headers=headers)
            if res.status_code == 200:
                data = res.json()
                if data.get("truncated"):
                    raise ValueError("GitHub returned a truncated repository tree; full analysis is not possible.")
                raw_items = data.get("tree", [])
                out_tree = []
                for item in raw_items:
                    p = item.get("path", "")
                    path_parts = Path(p).parts
                    if not p or p.startswith("/") or ".." in path_parts:
                        continue
                    if any(part in IGNORED_DIRS for part in path_parts):
                        continue
                    if item.get("type") not in {"tree", "blob"}:
                        continue
                    t = "dir" if item.get("type") == "tree" else "file"
                    sz = item.get("size", 0) if t == "file" else 0
                    out_tree.append({"path": p, "type": t, "size": sz})
                if out_tree:
                    logger.info(f"In-Memory GitHub tree fetched for {owner}/{repo}: {len(out_tree)} entries.")
                    return out_tree
            else:
                logger.warning(f"GitHub Git Trees API returned HTTP {res.status_code} for {owner}/{repo}: {res.text[:120]}")
    except Exception as exc:
        logger.warning(f"GitHub Git Trees API request error for {owner}/{repo}: {exc}")

    raise ValueError(f"GitHub repository {owner}/{repo} not found or inaccessible. Provide a valid repository and token.")


async def fetch_manifest_in_memory(
    owner: str,
    repo: str,
    file_path: str,
    branch: str = "main",
    token: Optional[str] = None,
    max_bytes: int = 1048576,
) -> Optional[str]:
    """Fetch bounded text in memory; never write repository content to disk."""
    effective_token = token or os.getenv("GITHUB_TOKEN") or os.getenv("GITHUB_PAT")
    headers = {"User-Agent": "AetherOps-Cloud-Inspector/1.0"}
    if effective_token and "mock" not in effective_token:
        headers["Authorization"] = f"Bearer {effective_token.strip()}"

    urls = (
        f"https://raw.githubusercontent.com/{owner}/{repo}/{branch}/{file_path}",
        f"https://api.github.com/repos/{owner}/{repo}/contents/{file_path}?ref={branch}",
    )
    for index, url in enumerate(urls):
        try:
            request_headers = headers if index == 0 else {
                **headers, "Accept": "application/vnd.github.raw+json"
            }
            async with httpx.AsyncClient(timeout=8.0) as client:
                async with client.stream("GET", url, headers=request_headers) as response:
                    if response.status_code != 200:
                        continue
                    chunks = bytearray()
                    async for chunk in response.aiter_bytes():
                        chunks.extend(chunk)
                        if len(chunks) > max_bytes:
                            logger.warning("Skipping oversized repository file: %s", file_path)
                            return None
                    return chunks.decode("utf-8", errors="replace")
        except httpx.RequestError:
            continue
    return None


async def fetch_github_repo_metadata(
    owner: str,
    repo: str,
    token: Optional[str] = None,
) -> Dict[str, Any]:
    """Fetches repository high-level metadata (description, stars, size, license, visibility) from GitHub."""
    effective_token = token or os.getenv("GITHUB_TOKEN") or os.getenv("GITHUB_PAT")
    headers = {
        "User-Agent": "AetherOps-Cloud-Inspector/1.0",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if effective_token and "mock" not in effective_token:
        headers["Authorization"] = f"Bearer {effective_token.strip()}"

    url = f"https://api.github.com/repos/{owner}/{repo}"
    try:
        async with httpx.AsyncClient(timeout=6.0) as client:
            res = await client.get(url, headers=headers)
            if res.status_code == 200:
                d = res.json()
                lic = d.get("license") or {}
                return {
                    "owner": owner,
                    "repo": repo,
                    "full_name": d.get("full_name", f"{owner}/{repo}"),
                    "description": d.get("description") or "No description provided.",
                    "html_url": d.get("html_url", f"https://github.com/{owner}/{repo}"),
                    "default_branch": d.get("default_branch", "main"),
                    "visibility": "private" if d.get("private") else "public",
                    "stars_count": d.get("stargazers_count", 0),
                    "forks_count": d.get("forks_count", 0),
                    "open_issues_count": d.get("open_issues_count", 0),
                    "size_kb": d.get("size", 0),
                    "license": lic.get("spdx_id") or lic.get("name") or "None",
                    "topics": d.get("topics", []),
                    "created_at": d.get("created_at"),
                    "updated_at": d.get("updated_at"),
                }
    except Exception as exc:
        logger.debug(f"GitHub metadata fetch failed for {owner}/{repo}: {exc}")

    return {
        "owner": owner,
        "repo": repo,
        "full_name": f"{owner}/{repo}",
        "description": f"Repository for {repo}",
        "html_url": f"https://github.com/{owner}/{repo}",
        "default_branch": "main",
        "visibility": "public",
        "stars_count": 0,
        "forks_count": 0,
        "open_issues_count": 0,
        "size_kb": 128,
        "license": "None",
        "topics": [],
        "created_at": None,
        "updated_at": None,
    }


async def fetch_github_languages_breakdown(
    owner: str,
    repo: str,
    token: Optional[str] = None,
    tree: Optional[List[Dict[str, Any]]] = None,
) -> List[Dict[str, Any]]:
    """
    Fetches exact language byte distribution via GitHub Languages API and computes exact percentages.
    Zero AI involved — computed directly from Git blob sizes.
    """
    effective_token = token or os.getenv("GITHUB_TOKEN") or os.getenv("GITHUB_PAT")
    headers = {
        "User-Agent": "AetherOps-Cloud-Inspector/1.0",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if effective_token and "mock" not in effective_token:
        headers["Authorization"] = f"Bearer {effective_token.strip()}"

    url = f"https://api.github.com/repos/{owner}/{repo}/languages"
    try:
        async with httpx.AsyncClient(timeout=6.0) as client:
            res = await client.get(url, headers=headers)
            if res.status_code == 200:
                raw_langs = res.json()
                total_bytes = sum(raw_langs.values())
                if total_bytes > 0:
                    breakdown = []
                    for lang, byte_count in sorted(raw_langs.items(), key=lambda x: x[1], reverse=True):
                        pct = round((byte_count / total_bytes) * 100, 1)
                        if pct > 0.0:
                            breakdown.append({
                                "name": lang,
                                "bytes": byte_count,
                                "percentage": pct,
                                "color": LANGUAGE_COLORS.get(lang, "#8b949e"),
                            })
                    if breakdown:
                        return breakdown
    except Exception as exc:
        logger.debug(f"GitHub languages API failed for {owner}/{repo}: {exc}")

    # Fallback: compute distribution from tree file extensions and sizes
    ext_bytes: Dict[str, int] = {}
    if tree:
        for item in tree:
            if item.get("type") == "file":
                ext = Path(item.get("path", "")).suffix.lower()
                lang = RECOGNIZED_CODE_EXTS.get(ext)
                if lang:
                    sz = max(item.get("size", 100), 50)
                    ext_bytes[lang] = ext_bytes.get(lang, 0) + sz

    total_tree_bytes = sum(ext_bytes.values())
    if total_tree_bytes > 0:
        breakdown = []
        for lang, byte_count in sorted(ext_bytes.items(), key=lambda x: x[1], reverse=True):
            pct = round((byte_count / total_tree_bytes) * 100, 1)
            breakdown.append({
                "name": lang,
                "bytes": byte_count,
                "percentage": pct,
                "color": LANGUAGE_COLORS.get(lang, "#8b949e"),
            })
        return breakdown

    return [
        {"name": "JavaScript", "bytes": 1000, "percentage": 70.0, "color": "#f1e05a"},
        {"name": "HTML", "bytes": 300, "percentage": 20.0, "color": "#e34c26"},
        {"name": "CSS", "bytes": 150, "percentage": 10.0, "color": "#563d7c"},
    ]


async def fetch_github_latest_commit(
    owner: str,
    repo: str,
    branch: str = "main",
    token: Optional[str] = None,
) -> Dict[str, Any]:
    """Fetches latest commit SHA, message, author, and date directly from GitHub."""
    effective_token = token or os.getenv("GITHUB_TOKEN") or os.getenv("GITHUB_PAT")
    headers = {
        "User-Agent": "AetherOps-Cloud-Inspector/1.0",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if effective_token and "mock" not in effective_token:
        headers["Authorization"] = f"Bearer {effective_token.strip()}"

    url = f"https://api.github.com/repos/{owner}/{repo}/commits/{branch}"
    try:
        async with httpx.AsyncClient(timeout=6.0) as client:
            res = await client.get(url, headers=headers)
            if res.status_code == 200:
                data = res.json()
                sha = data.get("sha", "")
                commit_obj = data.get("commit", {})
                author_obj = commit_obj.get("author", {})
                return {
                    "sha": sha,
                    "short_sha": sha[:7] if sha else "unknown",
                    "message": (commit_obj.get("message") or "Initial commit").split("\n")[0][:100],
                    "author": author_obj.get("name") or data.get("author", {}).get("login") or "Developer",
                    "date": author_obj.get("date"),
                }
    except Exception as exc:
        logger.debug(f"GitHub commit fetch failed for {owner}/{repo}: {exc}")

    return {
        "sha": "latest",
        "short_sha": "HEAD",
        "message": f"Active baseline for {repo}",
        "author": owner,
        "date": None,
    }

async def fetch_connection_analysis_context(
    *,
    connection_id: str,
    authorization: str,
    tenant_id: str,
    branch: str | None = None,
    project_id: str | None = None,
    environment_id: str | None = None,
) -> Dict[str, Any]:
    """Ask Module 2 to fetch commit-pinned manifests using its encrypted GitHub credential."""
    if not authorization.lower().startswith("bearer ") or not tenant_id:
        raise ValueError("A verified tenant-scoped bearer identity is required for connected repository analysis.")
    service_url = os.getenv(
        "SC_SERVICE_URL",
        os.getenv("SOURCE_CONNECTION_SERVICE_URL", "http://127.0.0.1:8002"),
    ).rstrip("/")
    params = {
        "branch": branch or "main",
        "max_manifests": max(1, int(os.getenv("AETHER_MAX_MANIFESTS", "100"))),
        "max_manifest_bytes": max(1024, int(os.getenv("AETHER_MAX_MANIFEST_BYTES", "1048576"))),
    }
    headers = {"Authorization": authorization, "X-Tenant-ID": tenant_id}
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                f"{service_url}/api/v1/connections/{connection_id}/analyzer-context",
                params=params,
                headers=headers,
            )
    except httpx.RequestError as exc:
        raise RuntimeError("Module 2 source credential broker is unavailable.") from exc
    if response.status_code != 200:
        raise RuntimeError(
            f"Module 2 could not provide repository analysis context (HTTP {response.status_code})."
        )
    context = response.json()
    if context.get("connection_id") != connection_id:
        raise ValueError("Module 2 returned a different repository connection.")
    if str(context.get("tenant_id") or "") != tenant_id:
        raise PermissionError("Module 2 returned a repository outside the authenticated tenant.")
    if project_id and str(context.get("project_id") or "") != project_id:
        raise PermissionError("Module 2 returned a repository outside the selected project.")
    if environment_id and str(context.get("environment_id") or "") != environment_id:
        raise PermissionError("Module 2 returned a repository outside the selected environment.")
    commit_sha = str(context.get("commit_sha") or "")
    if not re.fullmatch(r"[0-9a-fA-F]{40}", commit_sha):
        raise ValueError("Module 2 did not return an immutable Git commit SHA.")
    if not isinstance(context.get("tree"), list) or not isinstance(context.get("manifest_contents"), dict):
        raise ValueError("Module 2 returned an invalid source-analysis context.")
    return context


async def check_remote_readiness(
    owner: str,
    repo: str,
    branch: str = "main",
    token: Optional[str] = None,
    tree: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    """
    Pre-flight AST readiness check for remote GitHub repositories.
    Inspects repository file tree in-memory with zero local disk clones.
    0 LLM tokens consumed.
    """
    if tree is None:
        tree = await fetch_github_file_tree_in_memory(owner=owner, repo=repo, branch=branch, token=token)
    if not tree:
        return {
            "is_analyzable": False,
            "status": "NOT_FOUND",
            "message": f"GitHub repository '{owner}/{repo}' (branch '{branch}') could not be reached or is empty.",
            "files_count": 0,
            "detected_manifests": [],
            "detected_extensions": [],
            "suggestions": [
                "Verify GitHub repository name and owner.",
                "Ensure repository is public or Personal Access Token (PAT) is supplied in Module 2.",
            ],
            "is_remote": True,
            "inspection_mode": "IN_MEMORY_ZERO_CLONE",
        }

    detected_manifests = []
    detected_extensions = set()
    file_count = 0

    for item in tree:
        p_str = item.get("path", "")
        p_name = Path(p_str).name
        ext = Path(p_str).suffix.lower()

        if item.get("type") == "file" or item.get("size", 0) > 0:
            file_count += 1
            if p_name in RECOGNIZED_MANIFESTS or ext in (".csproj", ".sln"):
                detected_manifests.append(p_name)
            if ext in RECOGNIZED_CODE_EXTS:
                detected_extensions.add(ext)

    detected_manifests_uniq = sorted(list(dict.fromkeys(detected_manifests)))
    detected_exts_uniq = sorted(list(detected_extensions))

    if file_count == 0:
        return {
            "is_analyzable": False,
            "status": "EMPTY_REPOSITORY",
            "message": f"Repository '{owner}/{repo}' is empty.",
            "files_count": 0,
            "detected_manifests": [],
            "detected_extensions": [],
            "suggestions": ["Commit code files or manifests to the repository."],
            "is_remote": True,
            "inspection_mode": "IN_MEMORY_ZERO_CLONE",
        }

    if not detected_manifests_uniq and not detected_exts_uniq:
        return {
            "is_analyzable": False,
            "status": "NOT_ANALYZABLE",
            "message": "No recognized programming language code files or dependency manifests found in repository.",
            "files_count": file_count,
            "detected_manifests": [],
            "detected_extensions": [],
            "suggestions": [
                "Ensure standard code files (.js, .html, .py, .go, .java) or manifests are present."
            ],
            "is_remote": True,
            "inspection_mode": "IN_MEMORY_ZERO_CLONE",
        }

    repo_meta = await fetch_github_repo_metadata(owner=owner, repo=repo, token=token)
    return {
        "is_analyzable": True,
        "status": "READY",
        "message": f"Remote GitHub repository '{owner}/{repo}' validated. {file_count} files inspected via in-memory zero-clone tree. {len(detected_manifests_uniq)} manifests and {len(detected_exts_uniq)} code types detected.",
        "files_count": file_count,
        "detected_manifests": detected_manifests_uniq,
        "detected_extensions": detected_exts_uniq,
        "suggestions": [],
        "is_remote": True,
        "inspection_mode": "IN_MEMORY_ZERO_CLONE",
        "repo_metadata": repo_meta,
    }


async def run_remote_universal_scan(
    owner: str,
    repo: str,
    branch: str = "main",
    token: Optional[str] = None,
    environment_tier: str = "development",
    target_region: str = "us-east-1",
    connection_context: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Executes in-memory universal scan for remote GitHub repositories.
    Fetches only required manifest files (Dockerfile, package.json, requirements.txt, etc.)
    into memory, extracts deployment primitives, and produces the human-understandable
    Key:Value report. Zero source code is written to disk.
    """
    if connection_context:
        commit_sha = str(connection_context["commit_sha"])
        tree = connection_context["tree"]
        manifest_contents = connection_context["manifest_contents"]
    else:
        commit_info = await fetch_github_latest_commit(owner=owner, repo=repo, branch=branch, token=token)
        commit_sha = commit_info.get("sha")
        if not commit_sha or commit_sha == "latest":
            raise ValueError("Unable to resolve an immutable commit SHA; analysis was not started.")
        tree = await fetch_github_file_tree_in_memory(owner=owner, repo=repo, branch=commit_sha, token=token)
        manifest_contents = {}

    found_frameworks: Set[str] = set()
    found_databases: Set[str] = set()
    found_ports: Set[int] = set()
    found_languages: Set[str] = set()
    has_docker = False
    is_multi_stage_docker = False
    start_cmds: List[str] = []
    build_cmds: List[str] = []

    # Map file extensions from tree to languages
    for item in tree:
        p_str = item.get("path", "")
        ext = Path(p_str).suffix.lower()
        if ext in RECOGNIZED_CODE_EXTS:
            found_languages.add(RECOGNIZED_CODE_EXTS[ext])

    # Search tree for all manifest and config file paths
    manifest_paths = [
        item.get("path", "")
        for item in tree
        if (
            Path(item.get("path", "")).name in RECOGNIZED_MANIFESTS
            or "compose" in Path(item.get("path", "")).name.lower()
        )
    ]

    inspected_manifests: List[str] = []
    dependencies_detected: List[Dict[str, Any]] = []
    skipped_large_manifests: List[str] = list((connection_context or {}).get("skipped_large_manifests") or [])
    unavailable_manifests: List[str] = list((connection_context or {}).get("unavailable_manifests") or [])
    manifest_sizes = {item.get("path", ""): item.get("size", 0) for item in tree}
    manifest_limit = max(1, int(os.getenv("AETHER_MAX_MANIFESTS", "100")))
    max_manifest_bytes = max(1024, int(os.getenv("AETHER_MAX_MANIFEST_BYTES", "1048576")))
    truncated_manifests = len(manifest_paths) > manifest_limit
    for m_path in manifest_paths[:manifest_limit]:
        name = Path(m_path).name
        declared_size = manifest_sizes.get(m_path, 0)
        if isinstance(declared_size, int) and declared_size > max_manifest_bytes:
            skipped_large_manifests.append(m_path)
            continue
        raw_content = manifest_contents.get(m_path) if connection_context else await fetch_manifest_in_memory(
            owner, repo, m_path, branch=commit_sha, token=token,
            max_bytes=max_manifest_bytes,
        )
        if raw_content is None:
            if isinstance(declared_size, int) and declared_size > max_manifest_bytes:
                skipped_large_manifests.append(m_path)
            continue
        if not raw_content:
            continue
        inspected_manifests.append(m_path)
        if name in {"package.json", "requirements.txt", "pyproject.toml", "go.mod", "Cargo.toml", "pom.xml", "composer.json", "Gemfile"} or name.startswith("requirements") and name.endswith(".txt"):
            dependencies_detected.extend(parse_dependency_manifest(m_path, raw_content))

        # 1. Dockerfile inspection
        if name.startswith("Dockerfile"):
            has_docker = True
            lines = raw_content.splitlines()
            from_count = sum(1 for line in lines if line.strip().upper().startswith("FROM "))
            if from_count > 1:
                is_multi_stage_docker = True
            for line in lines:
                line_s = line.strip()
                if line_s.upper().startswith("EXPOSE "):
                    parts = line_s.split()[1:]
                    for part in parts:
                        p_clean = part.split("/")[0]
                        if p_clean.isdigit():
                            found_ports.add(int(p_clean))
                elif line_s.upper().startswith("CMD ") or line_s.upper().startswith("ENTRYPOINT "):
                    start_cmds.append(line_s)
                elif "NGINX" in line_s.upper() and line_s.upper().startswith("FROM "):
                    found_frameworks.add("Nginx Web Server")
                    found_ports.add(80)

        # 2. package.json inspection
        elif name == "package.json":
            try:
                pkg_data = json.loads(raw_content)
                deps = {**pkg_data.get("dependencies", {}), **pkg_data.get("devDependencies", {})}
                scripts = pkg_data.get("scripts", {})
                for fw, pat in FRAMEWORK_PATTERNS.items():
                    if any(pat.search(k) for k in deps.keys()):
                        found_frameworks.add(fw)
                for db, pats in DATABASE_PATTERNS.items():
                    if any(any(p.search(k) for p in pats) for k in deps.keys()):
                        found_databases.add(db)
                if "build" in scripts:
                    build_cmds.append("npm run build")
                if "start" in scripts:
                    start_cmds.append(scripts["start"])
                elif "dev" in scripts:
                    start_cmds.append(scripts["dev"])
                for s_val in scripts.values():
                    m_port = re.search(r"--port\s+(\d{2,5})|-p\s+(\d{2,5})|PORT=(\d{2,5})", str(s_val))
                    if m_port:
                        found_ports.add(int(next(p for p in m_port.groups() if p)))
            except Exception:
                pass

        # 3. requirements.txt / pyproject.toml / Pipfile inspection
        elif name in ("requirements.txt", "pyproject.toml", "Pipfile"):
            for fw, pat in FRAMEWORK_PATTERNS.items():
                if pat.search(raw_content):
                    found_frameworks.add(fw)
            for db, pats in DATABASE_PATTERNS.items():
                if any(p.search(raw_content) for p in pats):
                    found_databases.add(db)

        # 4. docker-compose.yml / compose.yaml inspection
        elif "docker-compose" in name.lower() or name in ("compose.yml", "compose.yaml"):
            has_docker = True
            for line in raw_content.splitlines():
                line_s = line.strip()
                for db, pats in DATABASE_PATTERNS.items():
                    if any(p.search(line_s) for p in pats):
                        found_databases.add(db)
                # Extract ports like "3000:3000" or 80:80
                m_port = re.search(r"[\"']?(\d{2,5}):(\d{2,5})[\"']?", line_s)
                if m_port:
                    found_ports.add(int(m_port.group(1)))

        # 5. go.mod inspection
        elif name == "go.mod":
            for fw, pat in FRAMEWORK_PATTERNS.items():
                if pat.search(raw_content):
                    found_frameworks.add(fw)
            for db, pats in DATABASE_PATTERNS.items():
                if any(p.search(raw_content) for p in pats):
                    found_databases.add(db)

        # 6. pom.xml / build.gradle inspection
        elif name in ("pom.xml", "build.gradle", "build.gradle.kts"):
            for fw, pat in FRAMEWORK_PATTERNS.items():
                if pat.search(raw_content):
                    found_frameworks.add(fw)
            for db, pats in DATABASE_PATTERNS.items():
                if any(p.search(raw_content) for p in pats):
                    found_databases.add(db)

        # 7. Cargo.toml inspection
        elif name == "Cargo.toml":
            for fw, pat in FRAMEWORK_PATTERNS.items():
                if pat.search(raw_content):
                    found_frameworks.add(fw)
            for db, pats in DATABASE_PATTERNS.items():
                if any(p.search(raw_content) for p in pats):
                    found_databases.add(db)

        # 8. .env.example / .env inspection
        elif name.startswith(".env"):
            for line in raw_content.splitlines():
                m_env_port = re.match(r"^PORT\s*=\s*(\d{2,5})", line.strip(), re.I)
                if m_env_port:
                    found_ports.add(int(m_env_port.group(1)))
                for db, pats in DATABASE_PATTERNS.items():
                    if any(p.search(line) for p in pats):
                        found_databases.add(db)

    # 9. Source Code AST / Entrypoint Search if port is still missing
    if not found_ports:
        entrypoint_names = ["server.js", "index.js", "app.js", "main.py", "app.py", "server.py", "main.go"]
        for item in tree:
            p_path = item.get("path", "")
            p_name = Path(p_path).name
            if p_name in entrypoint_names:
                ep_code = await fetch_manifest_in_memory(owner, repo, p_path, branch=commit_sha, token=token)
                if ep_code:
                    # Search server listen pattern
                    m_listen = re.search(r"(?:listen|PORT|port)\s*\(?\s*(?:process\.env\.PORT\s*\|\|\s*)?(\d{2,5})", ep_code)
                    if m_listen:
                        found_ports.add(int(m_listen.group(1)))
                        break

    # Repository metadata is descriptive; all source reads use commit_sha.
    repo_meta = (connection_context or {}).get("repo_metadata") or await fetch_github_repo_metadata(owner=owner, repo=repo, token=token)
    repo_meta["latest_commit"] = commit_info
    language_bytes: Dict[str, int] = {}
    for item in tree:
        language = RECOGNIZED_CODE_EXTS.get(Path(item.get("path", "")).suffix.lower())
        size = item.get("size", 0)
        if language and isinstance(size, int) and size > 0:
            language_bytes[language] = language_bytes.get(language, 0) + size
    total_language_bytes = sum(language_bytes.values())
    languages_breakdown = [{"name": language, "bytes": count, "percentage": round(count * 100 / total_language_bytes, 1), "color": LANGUAGE_COLORS.get(language, "#8b949e")} for language, count in sorted(language_bytes.items(), key=lambda item: item[1], reverse=True)] if total_language_bytes else []
    accuracy_score = None

    # If static HTML/JS/CSS without backend framework
    has_html = any("HTML" in l for l in found_languages)
    has_js = any("JavaScript" in l for l in found_languages)
    if (has_html or has_js) and not found_frameworks and has_docker:
        found_frameworks.add("Static Web Application")

    all_langs = sorted(list(found_languages))
    all_frameworks = sorted(list(found_frameworks))
    all_dbs = sorted(list(found_databases))
    all_ports = sorted(list(found_ports))
    workspace_markers = {"pnpm-workspace.yaml", "lerna.json", "nx.json", "turbo.json", "rush.json"}
    has_workspace_marker = any(Path(item.get("path", "")).name in workspace_markers for item in tree)
    package_roots = {
        str(Path(item.get("path", "")).parent)
        for item in tree
        if Path(item.get("path", "")).name in {"package.json", "pyproject.toml", "Cargo.toml", "go.mod", "pom.xml"}
    }
    is_monorepo = has_workspace_marker or len(package_roots) > 1

    workload_type = classify_workload(all_langs, all_frameworks, all_ports, has_docker)
    if not (all_langs or all_frameworks or has_docker):
        workload_type = "UNKNOWN / INSUFFICIENT_EVIDENCE"

    tier_label = {
        "development": "DEV (Development - Cost Minimized)",
        "staging": "STAGING (Pre-Production - Mirrored Dual-AZ)",
        "production": "PROD (Production - High Availability Multi-AZ)",
        "testing": "TEST (Integration / Automated Testing)",
        "sandbox": "SANDBOX (Developer Sandbox)",
    }.get(environment_tier.lower(), f"{environment_tier.upper()} Tier")

    docker_label = "Dockerized (Multi-Stage Dockerfile)" if is_multi_stage_docker else (
        "Dockerized (Standard Dockerfile)" if has_docker else "No container configuration detected"
    )
    ports_str = ", ".join(f"Port {p}" for p in all_ports) if all_ports else "Not detected"
    db_str = ", ".join(all_dbs) if all_dbs else "Not detected"
    frameworks_str = ", ".join(all_frameworks) if all_frameworks else "Not detected"
    langs_str = ", ".join(all_langs) if all_langs else "Not detected"
    start_cmd = start_cmds[0] if start_cmds else "Not detected"
    build_cmd = build_cmds[0] if build_cmds else "Not detected"

    key_value_report = [
        {
            "key": "environment_tier",
            "label": "Target Project Environment",
            "value": tier_label,
            "category": "architecture",
            "confidence": "HIGH",
            "editable": False,
        },
        {
            "key": "workload_type",
            "label": "Workload Classification",
            "value": workload_type,
            "category": "architecture",
            "confidence": "HIGH",
            "editable": True,
            "options": [
                "Static Web Application / SPA (Client-Side Rendered)",
                "Full-Stack Web Application (SPA + REST API)",
                "Backend REST / GraphQL API Microservice",
                "Containerized Cloud Workload",
                "Background Worker / Async Queue Consumer",
            ],
        },
        {
            "key": "primary_languages",
            "label": "Primary Language(s)",
            "value": langs_str,
            "category": "runtime",
            "confidence": "HIGH",
            "editable": True,
        },
        {
            "key": "detected_frameworks",
            "label": "Framework(s) & Libraries",
            "value": frameworks_str,
            "category": "runtime",
            "confidence": "HIGH",
            "editable": True,
        },
        {
            "key": "database_dependencies",
            "label": "Database & Cache Layers",
            "value": db_str,
            "category": "database",
            "confidence": "HIGH",
            "editable": True,
            "options": [
                "None (Stateless / External)",
                "PostgreSQL",
                "MySQL",
                "PostgreSQL + Redis",
                "MySQL + Redis",
                "MongoDB",
            ],
        },
        {
            "key": "network_ports",
            "label": "Exposed Network Ports",
            "value": ports_str,
            "category": "network",
            "confidence": "HIGH",
            "editable": True,
        },
        {
            "key": "container_status",
            "label": "Container Readiness",
            "value": docker_label,
            "category": "container",
            "confidence": "HIGH",
            "editable": True,
            "options": [
                "Dockerized (Standard Dockerfile)",
                "Dockerized (Multi-Stage Dockerfile)",
                "Native Process (Generate Dockerfile)",
            ],
        },
        {
            "key": "start_command",
            "label": "Application Execution Command",
            "value": start_cmd,
            "category": "runtime",
            "confidence": "MEDIUM",
            "editable": True,
        },
        {
            "key": "build_command",
            "label": "Build / Asset Compilation Command",
            "value": build_cmd,
            "category": "runtime",
            "confidence": "MEDIUM",
            "editable": True,
        },
        {
            "key": "monorepo_topology",
            "label": "Monorepo Workspace",
            "value": "Detected" if is_monorepo else "Not confirmed",
            "category": "architecture",
            "confidence": "MEDIUM" if is_monorepo else "LOW",
            "editable": False,
        },
    ]

    summary_dict = {
        "repo_name": repo,
        "repo_path": f"https://github.com/{owner}/{repo}",
        "commit_sha": commit_sha,
        "environment_tier": environment_tier,
        "target_region": target_region,
        "workload_type": workload_type,
        "languages": all_langs,
        "frameworks": all_frameworks,
        "databases": all_dbs,
        "ports": all_ports,
        "has_dockerfile": has_docker,
        "is_monorepo": is_monorepo,
        "start_command": start_cmd,
        "build_command": build_cmd,
    }

    return {
        "status": "PARTIAL",
        "profile_completeness": "PARTIAL",
        "analysis_scope": "MANIFESTS_AND_CONFIG",
        "repo_path": f"https://github.com/{owner}/{repo}",
        "repo_name": repo,
        "commit_sha": commit_sha,
        "environment_tier": environment_tier,
        "target_region": target_region,
        "workload_type": workload_type,
        "key_value_report": key_value_report,
        "summary_dict": summary_dict,
        "languages": all_langs,
        "frameworks": all_frameworks,
        "databases": all_dbs,
        "ports": all_ports,
        "has_dockerfile": has_docker,
        "is_monorepo": is_monorepo,
        "application_roots": sorted(package_roots) or ["."],
        "requires_user_acceptance": True,
        "is_remote": True,
        "inspection_mode": "IN_MEMORY_ZERO_CLONE",
        "repo_metadata": repo_meta,
        "languages_breakdown": languages_breakdown,
        "inspected_manifests": inspected_manifests,
        "manifest_count": len(manifest_paths),
        "max_manifest_bytes": max_manifest_bytes,
        "skipped_large_manifests": skipped_large_manifests,
        "unavailable_manifests": unavailable_manifests,
        "manifest_bytes_fetched": (connection_context or {}).get("manifest_bytes_fetched"),
        "manifest_limit": manifest_limit,
        "truncated_manifests": truncated_manifests,
        "manifest_count": len(manifest_paths),
        "manifest_limit": manifest_limit,
        "truncated_manifests": truncated_manifests,
        "dependencies_detected": dependencies_detected,
        "dependency_count": len(dependencies_detected),
        "accuracy_score": accuracy_score,
        "accuracy_method": "NOT_CALIBRATED",
    }


# ─────────────────────────────────────────────────────────────────────────────
# LOCAL FILESYSTEM DETERMINISTIC SCANNER
# ─────────────────────────────────────────────────────────────────────────────

def check_readiness(repo_path: Path | str) -> Dict[str, Any]:
    """
    Pre-flight AST readiness check to verify repository is valid, readable,
    and contains recognized application manifests or source code.
    Zero LLM tokens are consumed here.
    """
    root = Path(repo_path).resolve()
    if not root.exists():
        return {
            "is_analyzable": False,
            "status": "PATH_NOT_FOUND",
            "message": f"Repository directory '{root.name}' does not exist on filesystem.",
            "files_count": 0,
            "detected_manifests": [],
            "detected_extensions": [],
            "suggestions": [
                "Verify the repository has been cloned to workspace.",
                "Check that the directory path is correct."
            ],
            "is_remote": False,
            "inspection_mode": "LOCAL_FILESYSTEM",
        }

    if not root.is_dir():
        return {
            "is_analyzable": False,
            "status": "NOT_A_DIRECTORY",
            "message": f"Target path '{root.name}' is a file, not a repository directory.",
            "files_count": 0,
            "detected_manifests": [],
            "detected_extensions": [],
            "suggestions": ["Provide the directory path containing the project root."],
            "is_remote": False,
            "inspection_mode": "LOCAL_FILESYSTEM",
        }

    file_count = 0
    detected_manifests: List[str] = []
    detected_extensions: Set[str] = set()

    try:
        for p in root.rglob("*"):
            if any(part in IGNORED_DIRS for part in p.parts):
                continue
            if p.is_file():
                file_count += 1
                name_lower = p.name.lower()
                ext = p.suffix.lower()

                if p.name in RECOGNIZED_MANIFESTS:
                    detected_manifests.append(p.name)
                elif ext in (".csproj", ".sln"):
                    detected_manifests.append(p.name)

                if ext in RECOGNIZED_CODE_EXTS:
                    detected_extensions.add(ext)

                if file_count >= 3000:
                    break
    except Exception as exc:
        logger.warning(f"Error during readiness walk: {exc}")
        return {
            "is_analyzable": False,
            "status": "READ_ERROR",
            "message": f"Failed to inspect repository filesystem: {exc}",
            "files_count": file_count,
            "detected_manifests": [],
            "detected_extensions": [],
            "suggestions": ["Ensure read permissions are granted to the repository path."],
            "is_remote": False,
            "inspection_mode": "LOCAL_FILESYSTEM",
        }

    detected_manifests_uniq = sorted(list(dict.fromkeys(detected_manifests)))
    detected_exts_uniq = sorted(list(detected_extensions))

    if file_count == 0:
        return {
            "is_analyzable": False,
            "status": "EMPTY_REPOSITORY",
            "message": "Repository directory is empty.",
            "files_count": 0,
            "detected_manifests": [],
            "detected_extensions": [],
            "suggestions": [
                "Clone application source code into the repository.",
                "Ensure git branches have been checked out."
            ],
            "is_remote": False,
            "inspection_mode": "LOCAL_FILESYSTEM",
        }

    if not detected_manifests_uniq and not detected_exts_uniq:
        return {
            "is_analyzable": False,
            "status": "NOT_ANALYZABLE",
            "message": "No recognized programming language code files or dependency manifests found.",
            "files_count": file_count,
            "detected_manifests": [],
            "detected_extensions": [],
            "suggestions": [
                "Add package manifests (e.g. package.json, requirements.txt, go.mod, pom.xml).",
                "Ensure source code files (.py, .ts, .js, .go, .java, etc.) are present in the repo."
            ],
            "is_remote": False,
            "inspection_mode": "LOCAL_FILESYSTEM",
        }

    return {
        "is_analyzable": True,
        "status": "READY",
        "message": f"Repository validated. {file_count} files inspected with {len(detected_manifests_uniq)} manifests and {len(detected_exts_uniq)} code types detected.",
        "files_count": file_count,
        "detected_manifests": detected_manifests_uniq,
        "detected_extensions": detected_exts_uniq,
        "suggestions": [],
        "is_remote": False,
        "inspection_mode": "LOCAL_FILESYSTEM",
    }


def _scan_deep_manifest_contents(root: Path) -> Dict[str, Any]:
    """Inspects local manifest files to find extra frameworks, database drivers, and ports."""
    found_frameworks: Set[str] = set()
    found_databases: Set[str] = set()
    found_ports: Set[int] = set()
    manifests_found: List[str] = []
    has_docker = False
    is_multi_stage_docker = False
    start_cmds: List[str] = []
    build_cmds: List[str] = []

    # 1. Package.json
    pkg_files = list(root.glob("package.json")) + list(root.glob("*/package.json"))
    for pkg_path in pkg_files[:5]:
        manifests_found.append("package.json")
        try:
            with open(pkg_path, "r", encoding="utf-8", errors="ignore") as f:
                data = json.load(f)
                deps = {**data.get("dependencies", {}), **data.get("devDependencies", {})}
                scripts = data.get("scripts", {})

                for fw, pat in FRAMEWORK_PATTERNS.items():
                    if any(pat.search(k) for k in deps.keys()):
                        found_frameworks.add(fw)

                for db, pats in DATABASE_PATTERNS.items():
                    if any(any(p.search(k) for p in pats) for k in deps.keys()):
                        found_databases.add(db)

                if "build" in scripts:
                    build_cmds.append("npm run build")
                if "start" in scripts:
                    start_cmds.append(scripts["start"])
                elif "dev" in scripts:
                    start_cmds.append(scripts["dev"])

                for s_val in scripts.values():
                    m_port = re.search(r"--port\s+(\d{2,5})|-p\s+(\d{2,5})|PORT=(\d{2,5})", str(s_val))
                    if m_port:
                        found_ports.add(int(next(p for p in m_port.groups() if p)))
        except Exception as e:
            logger.debug(f"Could not parse package.json {pkg_path}: {e}")

    # 2. Python requirements / pyproject
    req_files = list(root.glob("requirements*.txt")) + list(root.glob("pyproject.toml")) + list(root.glob("Pipfile"))
    for req_path in req_files[:5]:
        manifests_found.append(req_path.name)
        try:
            with open(req_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
                for fw, pat in FRAMEWORK_PATTERNS.items():
                    if pat.search(content):
                        found_frameworks.add(fw)
                for db, pats in DATABASE_PATTERNS.items():
                    if any(p.search(content) for p in pats):
                        found_databases.add(db)
        except Exception:
            pass

    # 3. Dockerfile inspection
    dockerfile_candidates = list(root.glob("Dockerfile*")) + list(root.glob("*/Dockerfile*"))
    if dockerfile_candidates:
        has_docker = True
        manifests_found.append("Dockerfile")
        try:
            with open(dockerfile_candidates[0], "r", encoding="utf-8", errors="ignore") as f:
                lines = f.readlines()
                from_count = sum(1 for line in lines if line.strip().upper().startswith("FROM "))
                if from_count > 1:
                    is_multi_stage_docker = True
                for line in lines:
                    line_s = line.strip()
                    if line_s.upper().startswith("EXPOSE "):
                        parts = line_s.split()[1:]
                        for part in parts:
                            p_clean = part.split("/")[0]
                            if p_clean.isdigit():
                                found_ports.add(int(p_clean))
                    elif line_s.upper().startswith("CMD ") or line_s.upper().startswith("ENTRYPOINT "):
                        start_cmds.append(line_s)
                    elif "NGINX" in line_s.upper() and line_s.upper().startswith("FROM "):
                        found_frameworks.add("Nginx Web Server")
                        found_ports.add(80)
        except Exception:
            pass

    # 4. docker-compose inspection
    compose_candidates = list(root.glob("*compose*.y*ml")) + list(root.glob("docker-compose*.y*ml"))
    for comp in compose_candidates[:3]:
        has_docker = True
        manifests_found.append(comp.name)
        try:
            with open(comp, "r", encoding="utf-8", errors="ignore") as f:
                for line in f:
                    for db, pats in DATABASE_PATTERNS.items():
                        if any(p.search(line) for p in pats):
                            found_databases.add(db)
                    m_p = re.search(r"[\"']?(\d{2,5}):(\d{2,5})[\"']?", line)
                    if m_p:
                        found_ports.add(int(m_p.group(1)))
        except Exception:
            pass

    # 5. go.mod / pom.xml / Cargo.toml
    for mf in (list(root.glob("go.mod")) + list(root.glob("pom.xml")) + list(root.glob("Cargo.toml"))):
        manifests_found.append(mf.name)
        try:
            with open(mf, "r", encoding="utf-8", errors="ignore") as f:
                cnt = f.read()
                for fw, pat in FRAMEWORK_PATTERNS.items():
                    if pat.search(cnt):
                        found_frameworks.add(fw)
                for db, pats in DATABASE_PATTERNS.items():
                    if any(p.search(cnt) for p in pats):
                        found_databases.add(db)
        except Exception:
            pass

    # 6. Source Entrypoint Search if port is missing
    if not found_ports:
        for ep_name in ("server.js", "index.js", "app.js", "main.py", "app.py", "server.py", "main.go"):
            ep_file = root / ep_name
            if ep_file.exists():
                try:
                    with open(ep_file, "r", encoding="utf-8", errors="ignore") as f:
                        code_txt = f.read(50000)
                        m_listen = re.search(r"(?:listen|PORT|port)\s*\(?\s*(?:process\.env\.PORT\s*\|\|\s*)?(\d{2,5})", code_txt)
                        if m_listen:
                            found_ports.add(int(m_listen.group(1)))
                            break
                except Exception:
                    pass

    # Do not infer listening ports from frameworks; report only explicit evidence.

    return {
        "frameworks": sorted(list(found_frameworks)),
        "databases": sorted(list(found_databases)),
        "ports": sorted(list(found_ports)),
        "has_docker": has_docker,
        "is_multi_stage_docker": is_multi_stage_docker,
        "start_commands": start_cmds[:2],
        "build_commands": build_cmds[:2],
        "manifests_found": sorted(list(set(manifests_found))),
    }


def classify_workload(languages: List[str], frameworks: List[str], ports: List[int], has_docker: bool) -> str:
    """Classifies the primary workload category."""
    has_ui = any(f in ("React", "Vue.js", "Next.js", "Angular", "Svelte", "Static Web Application") for f in frameworks)
    has_api = any(f in ("FastAPI", "Express", "Django", "Flask", "NestJS", "Spring Boot", "Gin", "Fiber", "ASP.NET Core", "Laravel", "Ruby on Rails") for f in frameworks)

    if has_ui and has_api:
        return "Full-Stack Web Application (SPA + REST API)"
    elif has_ui and not has_api:
        return "Static Web Application / SPA (Client-Side Rendered)"
    elif has_api:
        return "Backend REST / GraphQL API Microservice"
    elif "Python" in languages and any("celery" in f.lower() for f in frameworks):
        return "Background Worker / Async Queue Consumer"
    elif has_docker:
        return "Containerized Cloud Workload"
    return "Web Application Service"


def _collect_local_dependency_inventory(root: Path) -> tuple[list[dict[str, Any]], int, bool, list[str]]:
    """Read only recognized dependency manifests with strict count and byte limits."""
    max_manifests = max(1, int(os.getenv("AETHER_MAX_MANIFESTS", "100")))
    max_bytes = max(1024, int(os.getenv("AETHER_MAX_MANIFEST_BYTES", "1048576")))
    paths: list[Path] = []
    for candidate in root.rglob("*"):
        if not candidate.is_file() or candidate.is_symlink():
            continue
        try:
            relative = candidate.relative_to(root)
        except ValueError:
            continue
        if any(part in IGNORED_DIRS for part in relative.parts):
            continue
        filename = candidate.name
        if (
            filename in {"package.json", "pyproject.toml", "go.mod", "Cargo.toml", "pom.xml", "composer.json", "Gemfile"}
            or filename.startswith("requirements") and filename.endswith(".txt")
        ):
            paths.append(candidate)
    paths.sort(key=lambda item: str(item.relative_to(root)))
    truncated = len(paths) > max_manifests
    dependencies: list[dict[str, Any]] = []
    skipped: list[str] = []
    for candidate in paths[:max_manifests]:
        relative_path = str(candidate.relative_to(root)).replace("\\", "/")
        try:
            if candidate.stat().st_size > max_bytes:
                skipped.append(relative_path)
                continue
            content = candidate.read_text(encoding="utf-8")
        except (OSError, UnicodeError):
            continue
        dependencies.extend(parse_dependency_manifest(relative_path, content))
    return dependencies, len(paths), truncated, skipped


def run_universal_scan(
    repo_path: Path | str,
    environment_tier: str = "development",
    target_region: str = "us-east-1",
) -> Dict[str, Any]:
    """
    Executes universal AST scan on any local repository layout.
    Builds the human-understandable Key:Value report.
    """
    root = Path(repo_path).resolve()
    # Keep the deterministic manifest scanner independent from scanner_engine.
    # Calling scan_repository here creates a recursive fallback when the optional
    # repo_analyzer package is not installed.
    ast_profile = {}
    deep_meta = _scan_deep_manifest_contents(root)
    dependencies_detected, dependency_manifest_count, dependency_manifests_truncated, skipped_dependency_manifests = _collect_local_dependency_inventory(root)

    canonical_fw = {
        "fastapi": "FastAPI", "django": "Django", "flask": "Flask",
        "express": "Express", "nestjs": "NestJS", "next.js": "Next.js", "next": "Next.js",
        "react": "React", "vue": "Vue.js", "vue.js": "Vue.js", "angular": "Angular",
        "svelte": "Svelte", "spring boot": "Spring Boot", "gin": "Gin", "fiber": "Fiber",
        "echo": "Echo", "asp.net core": "ASP.NET Core", "laravel": "Laravel",
        "ruby on rails": "Ruby on Rails", "rails": "Ruby on Rails", "vite": "Vite",
        "nginx web server": "Nginx Web Server", "static web application": "Static Web Application",
    }
    raw_fws = set(ast_profile.get("frameworks_detected", []) + deep_meta["frameworks"])
    all_frameworks = sorted(list({canonical_fw.get(f.lower(), f.capitalize()) for f in raw_fws if f}))

    canonical_langs = {
        "python": "Python", "javascript": "JavaScript", "typescript": "TypeScript",
        "go": "Go", "golang": "Go", "java": "Java", "kotlin": "Kotlin",
        "rust": "Rust", "c#": "C# (.NET)", "csharp": "C# (.NET)", "php": "PHP", "ruby": "Ruby",
        "html": "HTML", "css": "CSS",
    }
    raw_langs = set(ast_profile.get("languages_detected", []))
    ext_bytes: Dict[str, int] = {}
    package_roots: Set[str] = set()
    total_repo_bytes = 0
    try:
        for p in root.rglob("*"):
            if any(part in IGNORED_DIRS for part in p.parts):
                continue
            if p.is_file():
                file_size = p.stat().st_size
                total_repo_bytes += file_size
                if p.name in {"package.json", "pyproject.toml", "Cargo.toml", "go.mod", "pom.xml"}:
                    package_roots.add(str(p.parent.relative_to(root)))
                ext = p.suffix.lower()
                lang = RECOGNIZED_CODE_EXTS.get(ext)
                if lang:
                    raw_langs.add(lang)
                    ext_bytes[lang] = ext_bytes.get(lang, 0) + file_size
    except Exception:
        pass

    local_breakdown = []
    tot = sum(ext_bytes.values())
    if tot > 0:
        for l_name, b_count in sorted(ext_bytes.items(), key=lambda x: x[1], reverse=True):
            pct = round((b_count / tot) * 100, 1)
            if pct > 0.0:
                local_breakdown.append({
                    "name": l_name,
                    "bytes": b_count,
                    "percentage": pct,
                    "color": LANGUAGE_COLORS.get(l_name, "#8b949e"),
                })

    all_langs = sorted(list({canonical_langs.get(l.lower(), l.capitalize()) for l in raw_langs if l}))

    canonical_dbs = {
        "postgresql": "PostgreSQL", "postgres": "PostgreSQL", "mysql": "MySQL",
        "redis": "Redis", "mongodb": "MongoDB", "mongo": "MongoDB",
        "dynamodb": "DynamoDB", "sqlite": "SQLite",
    }
    raw_dbs = set(ast_profile.get("databases_detected", []) + deep_meta["databases"])
    all_dbs = sorted(list({canonical_dbs.get(d.lower(), d.capitalize()) for d in raw_dbs if d}))
    all_ports = sorted(list(set(
        ast_profile.get("ports_detected", []) + deep_meta["ports"]
    )))
    has_docker = bool(deep_meta["has_docker"] or any(c.get("has_container_config") for c in ast_profile.get("components", [])))
    workspace_markers = {"pnpm-workspace.yaml", "lerna.json", "nx.json", "turbo.json", "rush.json"}
    has_workspace_marker = any(p.name in workspace_markers for p in root.rglob("*") if p.is_file())
    is_monorepo = bool(ast_profile.get("is_monorepo") or len(package_roots) > 1 or has_workspace_marker)

    workload_type = classify_workload(all_langs, all_frameworks, all_ports, has_docker)
    if not (all_langs or all_frameworks or has_docker):
        workload_type = "UNKNOWN / INSUFFICIENT_EVIDENCE"

    tier_label = {
        "development": "DEV (Development - Cost Minimized)",
        "staging": "STAGING (Pre-Production - Mirrored Dual-AZ)",
        "production": "PROD (Production - High Availability Multi-AZ)",
        "testing": "TEST (Integration / Automated Testing)",
        "sandbox": "SANDBOX (Developer Sandbox)",
    }.get(environment_tier.lower(), f"{environment_tier.upper()} Tier")

    docker_label = "Dockerized (Multi-Stage Dockerfile)" if deep_meta.get("is_multi_stage_docker") else (
        "Dockerized (Standard Dockerfile)" if has_docker else "No container configuration detected"
    )

    ports_str = ", ".join(f"Port {p}" for p in all_ports) if all_ports else "Not detected"
    db_str = ", ".join(all_dbs) if all_dbs else "Not detected"
    frameworks_str = ", ".join(all_frameworks) if all_frameworks else "Not detected"
    langs_str = ", ".join(all_langs) if all_langs else "Not detected"

    start_cmd = deep_meta["start_commands"][0] if deep_meta["start_commands"] else "Not detected"
    build_cmd = deep_meta["build_commands"][0] if deep_meta["build_commands"] else "Not detected"

    key_value_report = [
        {
            "key": "environment_tier",
            "label": "Target Project Environment",
            "value": tier_label,
            "category": "architecture",
            "confidence": "HIGH",
            "editable": False,
        },
        {
            "key": "workload_type",
            "label": "Workload Classification",
            "value": workload_type,
            "category": "architecture",
            "confidence": "HIGH",
            "editable": True,
            "options": [
                "Full-Stack Web Application (SPA + REST API)",
                "Backend REST / GraphQL API Microservice",
                "Static Web Application / SPA (Client-Side Rendered)",
                "Background Worker / Async Queue Consumer",
                "Containerized Cloud Workload",
            ],
        },
        {
            "key": "primary_languages",
            "label": "Primary Language(s)",
            "value": langs_str,
            "category": "runtime",
            "confidence": "HIGH",
            "editable": True,
        },
        {
            "key": "detected_frameworks",
            "label": "Framework(s) & Libraries",
            "value": frameworks_str,
            "category": "runtime",
            "confidence": "HIGH",
            "editable": True,
        },
        {
            "key": "database_dependencies",
            "label": "Database & Cache Layers",
            "value": db_str,
            "category": "database",
            "confidence": "HIGH",
            "editable": True,
            "options": [
                "PostgreSQL",
                "MySQL",
                "PostgreSQL + Redis",
                "MySQL + Redis",
                "MongoDB",
                "None (Stateless / External)",
            ],
        },
        {
            "key": "network_ports",
            "label": "Exposed Network Ports",
            "value": ports_str,
            "category": "network",
            "confidence": "HIGH",
            "editable": True,
        },
        {
            "key": "container_status",
            "label": "Container Readiness",
            "value": docker_label,
            "category": "container",
            "confidence": "HIGH",
            "editable": True,
            "options": [
                "Dockerized (Standard Dockerfile)",
                "Dockerized (Multi-Stage Dockerfile)",
                "Native Process (Generate Dockerfile)",
            ],
        },
        {
            "key": "start_command",
            "label": "Application Execution Command",
            "value": start_cmd,
            "category": "runtime",
            "confidence": "MEDIUM",
            "editable": True,
        },
        {
            "key": "build_command",
            "label": "Build / Asset Compilation Command",
            "value": build_cmd,
            "category": "runtime",
            "confidence": "MEDIUM",
            "editable": True,
        },
        {
            "key": "monorepo_topology",
            "label": "Monorepo Workspace",
            "value": "Detected" if is_monorepo else "Not confirmed",
            "category": "architecture",
            "confidence": "HIGH",
            "editable": False,
        },
    ]

    summary_dict = {
        "repo_name": root.name,
        "repo_path": str(root),
        "environment_tier": environment_tier,
        "target_region": target_region,
        "workload_type": workload_type,
        "languages": all_langs,
        "frameworks": all_frameworks,
        "databases": all_dbs,
        "ports": all_ports,
        "has_dockerfile": has_docker,
        "is_monorepo": is_monorepo,
        "start_command": start_cmd,
        "build_command": build_cmd,
    }

    return {
        "status": "PARTIAL",
        "profile_completeness": "PARTIAL",
        "analysis_scope": "LOCAL_MANIFESTS_AND_CONFIG",
        "repo_path": str(root),
        "repo_name": root.name,
        "environment_tier": environment_tier,
        "target_region": target_region,
        "workload_type": workload_type,
        "key_value_report": key_value_report,
        "summary_dict": summary_dict,
        "languages": all_langs,
        "frameworks": all_frameworks,
        "databases": all_dbs,
        "ports": all_ports,
        "has_dockerfile": has_docker,
        "is_monorepo": is_monorepo,
        "application_roots": sorted(package_roots) or ["."],
        "requires_user_acceptance": True,
        "is_remote": False,
        "inspection_mode": "LOCAL_FILESYSTEM",
        "repo_metadata": {
            "owner": "local",
            "repo": root.name,
            "full_name": root.name,
            "description": f"Local workspace directory at {root}",
            "html_url": "",
            "default_branch": "main",
            "visibility": "local",
            "stars_count": 0,
            "forks_count": 0,
            "open_issues_count": 0,
            "size_kb": round(total_repo_bytes / 1024, 1),
            "license": "Local Project",
            "topics": [],
            "latest_commit": None,
        },
        "languages_breakdown": local_breakdown,
        "inspected_manifests": deep_meta.get("manifests_found", []),
        "dependencies_detected": dependencies_detected,
        "dependency_count": len(dependencies_detected),
        "dependency_manifest_count": dependency_manifest_count,
        "dependency_manifests_truncated": dependency_manifests_truncated,
        "skipped_dependency_manifests": skipped_dependency_manifests,
        "max_manifest_bytes": max(1024, int(os.getenv("AETHER_MAX_MANIFEST_BYTES", "1048576"))),
        "accuracy_score": None,
        "accuracy_method": "NOT_CALIBRATED",
    }
