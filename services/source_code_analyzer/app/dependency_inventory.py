"""Deterministic extraction of declared direct dependencies from manifests."""
from __future__ import annotations

import hashlib
import json
import re
import tomllib
from datetime import datetime, timezone
import xml.etree.ElementTree as ET
from urllib.parse import quote
from typing import Any


def _exact_version(spec: str | None) -> str | None:
    if not spec:
        return None
    value = str(spec).strip()
    match = re.fullmatch(r"(?:==|=|v)?([0-9][0-9A-Za-z.+_-]*)", value)
    return match.group(1) if match else None


def _purl(ecosystem: str, name: str, version: str | None, namespace: str | None = None) -> str:
    safe_name = quote(name.strip(), safe="/.-_")
    if namespace:
        safe_namespace = quote(namespace.strip(), safe="/.-_")
        base = f"pkg:{ecosystem}/{safe_namespace}/{safe_name}"
    else:
        base = f"pkg:{ecosystem}/{safe_name}"
    return f"{base}@{quote(version, safe='.+-_')}" if version else base


def _dependency(ecosystem: str, name: str, declared: str | None, source: str, scope: str = "required", namespace: str | None = None) -> dict[str, Any]:
    version = _exact_version(declared)
    return {
        "ecosystem": ecosystem,
        "package_name": name,
        "version": version,
        "declared_version": declared,
        "purl": _purl(ecosystem, name, version, namespace),
        "source_path": source,
        "scope": scope,
        "is_direct": True,
    }


def parse_dependency_manifest(path: str, content: str) -> list[dict[str, Any]]:
    name = path.rsplit("/", 1)[-1]
    manifest_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()
    output: list[dict[str, Any]] = []
    try:
        if name == "package.json":
            data = json.loads(content)
            for section, scope in (("dependencies", "required"), ("optionalDependencies", "optional"), ("devDependencies", "excluded")):
                for package, version in (data.get(section) or {}).items():
                    output.append(_dependency("npm", package, str(version), path, scope))
        elif name.startswith("requirements") and name.endswith(".txt"):
            for line in content.splitlines():
                line = line.split("#", 1)[0].strip()
                if not line or line.startswith(("-r ", "--", "-e ")):
                    continue
                match = re.match(r"^([A-Za-z0-9_.-]+)(?:\[[^]]+\])?\s*(.*)$", line)
                if match:
                    package, spec = match.groups()
                    output.append(_dependency("pypi", package.lower().replace("_", "-"), spec or None, path))
        elif name == "pyproject.toml":
            data = tomllib.loads(content)
            project = data.get("project") or {}
            for item in project.get("dependencies") or []:
                match = re.match(r"^([A-Za-z0-9_.-]+)(?:\[[^]]+\])?\s*(.*)$", item)
                if match:
                    package, spec = match.groups()
                    output.append(_dependency("pypi", package.lower().replace("_", "-"), spec or None, path))
            for section, entries in (project.get("optional-dependencies") or {}).items():
                for item in entries:
                    match = re.match(r"^([A-Za-z0-9_.-]+)(?:\[[^]]+\])?\s*(.*)$", item)
                    if match:
                        package, spec = match.groups()
                        output.append(_dependency("pypi", package.lower().replace("_", "-"), spec or None, path, "optional"))
        elif name == "go.mod":
            in_require = False
            for line in content.splitlines():
                stripped = line.strip()
                if stripped.startswith("require ("):
                    in_require = True
                    continue
                if in_require and stripped == ")":
                    in_require = False
                    continue
                if stripped.startswith("require ") and "(" not in stripped:
                    parts = stripped.split()
                    if len(parts) >= 3:
                        output.append(_dependency("golang", parts[1], parts[2], path))
                elif in_require and stripped and not stripped.startswith("//"):
                    parts = stripped.split()
                    if len(parts) >= 2:
                        output.append(_dependency("golang", parts[0], parts[1], path))
        elif name == "Cargo.toml":
            data = tomllib.loads(content)
            for section, scope in (("dependencies", "required"), ("dev-dependencies", "excluded"), ("build-dependencies", "optional")):
                for package, value in (data.get(section) or {}).items():
                    spec = value.get("version") if isinstance(value, dict) else value
                    output.append(_dependency("cargo", package, str(spec) if spec else None, path, scope))
        elif name == "pom.xml":
            root = ET.fromstring(content)
            for dep in root.findall(".//{*}dependency"):
                group = dep.findtext("{*}groupId")
                artifact = dep.findtext("{*}artifactId")
                version = dep.findtext("{*}version")
                if group and artifact:
                    output.append(_dependency("maven", artifact, version, path, namespace=group))
        elif name == "composer.json":
            data = json.loads(content)
            for section, scope in (("require", "required"), ("require-dev", "excluded")):
                for package, version in (data.get(section) or {}).items():
                    if package.lower() not in {"php", "ext-json", "ext-curl"}:
                        output.append(_dependency("composer", package, str(version), path, scope))
        elif name == "Gemfile":
            for match in re.finditer(r"""gem\s+['"]([^'"]+)['"](?:\s*,\s*['"]([^'"]+)['"])?""", content):
                output.append(_dependency("gem", match.group(1), match.group(2), path))
    except (ValueError, TypeError, KeyError, ET.ParseError):
        return []

    unique: dict[tuple[str, str, str | None, str], dict[str, Any]] = {}
    for item in output:
        key = (item["ecosystem"], item["package_name"].lower(), item["version"], item["source_path"])
        unique[key] = item
    for item in unique.values():
        item["manifest_hash"] = manifest_hash
    return list(unique.values())


def build_sbom_documents(
    *,
    application_name: str,
    repository_url: str,
    commit_sha: str | None,
    dependencies: list[dict[str, Any]],
    created_at: datetime | None = None,
) -> dict[str, dict[str, Any]]:
    """Build honest declared-direct-dependency SBOMs; unresolved ranges remain unversioned."""
    components = []
    packages = []
    timestamp = (created_at or datetime.now(timezone.utc)).astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
    for index, dep in enumerate(dependencies, start=1):
        component = {
            "type": "library",
            "name": dep["package_name"],
            "purl": dep["purl"],
            "scope": dep.get("scope", "required"),
            "properties": [
                {"name": "aetherops:ecosystem", "value": dep["ecosystem"]},
                {"name": "aetherops:declaredVersion", "value": dep.get("declared_version") or ""},
                {"name": "aetherops:sourcePath", "value": dep["source_path"]},
            ],
        }
        if dep.get("version"):
            component["version"] = dep["version"]
        components.append(component)
        package = {
            "SPDXID": f"SPDXRef-Package-{index}",
            "name": dep["package_name"],
            "downloadLocation": "NOASSERTION",
            "filesAnalyzed": False,
            "licenseConcluded": "NOASSERTION",
            "licenseDeclared": "NOASSERTION",
            "copyrightText": "NOASSERTION",
            "externalRefs": [{
                "referenceCategory": "PACKAGE-MANAGER",
                "referenceType": "purl",
                "referenceLocator": dep["purl"],
            }],
        }
        if dep.get("version"):
            package["versionInfo"] = dep["version"]
        packages.append(package)

    metadata_properties = [
        {"name": "aetherops:completeness", "value": "DECLARED_DIRECT_DEPENDENCIES_ONLY"},
        {"name": "aetherops:transitiveDependenciesResolved", "value": "false"},
    ]
    if commit_sha:
        metadata_properties.append({"name": "aetherops:commitSha", "value": commit_sha})

    cyclonedx = {
        "bomFormat": "CycloneDX",
        "specVersion": "1.5",
        "version": 1,
        "metadata": {
            "component": {"type": "application", "name": application_name},
            "properties": metadata_properties,
            "tools": {"components": [{"type": "application", "name": "AetherOps Module 3"}]},
        },
        "components": components,
    }
    spdx = {
        "spdxVersion": "SPDX-2.3",
        "dataLicense": "CC0-1.0",
        "SPDXID": "SPDXRef-DOCUMENT",
        "name": f"{application_name}-declared-dependencies",
        "documentNamespace": f"{repository_url.rstrip('/')}/sbom/{commit_sha or 'profile'}-{_purl('generic', application_name)}",
        "creationInfo": {"creators": ["Tool: AetherOps Module 3"], "created": timestamp},
        "packages": packages,
        "externalDocumentRefs": [],
        "annotations": [{
            "annotationType": "OTHER",
            "annotator": "Tool: AetherOps Module 3",
            "comment": "Declared direct dependencies only; transitive dependencies and resolved lockfile versions are not included.",
            "annotationDate": timestamp,
        }],
    }
    return {"CYCLONEDX": cyclonedx, "SPDX": spdx}
