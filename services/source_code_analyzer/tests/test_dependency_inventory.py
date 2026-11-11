from app.dependency_inventory import build_sbom_documents, parse_dependency_manifest


def test_package_json_declared_dependencies_preserve_scope_and_exact_version():
    dependencies = parse_dependency_manifest(
        "apps/web/package.json",
        """{
          "dependencies": {"react": "^18.2.0", "zod": "3.22.4"},
          "devDependencies": {"vite": "~5.0.0"},
          "optionalDependencies": {"fsevents": "2.3.3"}
        }""",
    )
    by_name = {item["package_name"]: item for item in dependencies}
    assert by_name["react"]["version"] is None
    assert by_name["react"]["declared_version"] == "^18.2.0"
    assert by_name["zod"]["version"] == "3.22.4"
    assert by_name["vite"]["scope"] == "excluded"
    assert by_name["fsevents"]["scope"] == "optional"
    assert all(item["is_direct"] for item in dependencies)
    assert all(item["manifest_hash"] for item in dependencies)


def test_python_requirements_and_pyproject_are_parsed_without_cargo_false_positives():
    requirements = parse_dependency_manifest(
        "requirements-prod.txt",
        "fastapi==0.115.0\nhttpx>=0.27\n# comment\n-r base.txt\n",
    )
    assert {item["package_name"] for item in requirements} == {"fastapi", "httpx"}
    pyproject = parse_dependency_manifest(
        "pyproject.toml",
        """[project]
dependencies = ["sqlalchemy>=2.0", "pydantic==2.8.2"]
[project.optional-dependencies]
test = ["pytest>=8"]
""",
    )
    assert {item["ecosystem"] for item in pyproject} == {"pypi"}
    assert len(pyproject) == 3


def test_go_mod_and_maven_dependencies_are_parsed():
    go = parse_dependency_manifest(
        "go.mod",
        """module example.com/service
require (
  github.com/gin-gonic/gin v1.10.0
  golang.org/x/text v0.16.0
)
""",
    )
    assert len(go) == 2
    assert go[0]["ecosystem"] == "golang"
    maven = parse_dependency_manifest(
        "pom.xml",
        """<project xmlns="http://maven.apache.org/POM/4.0.0">
          <dependencies><dependency><groupId>org.slf4j</groupId>
          <artifactId>slf4j-api</artifactId><version>2.0.13</version>
          </dependency></dependencies></project>""",
    )
    assert len(maven) == 1
    assert maven[0]["purl"] == "pkg:maven/org.slf4j/slf4j-api@2.0.13"


def test_sbom_marks_scope_and_direct_only_completeness():
    deps = parse_dependency_manifest(
        "package.json",
        '{"dependencies":{"express":"4.19.2"},"devDependencies":{"jest":"29.7.0"}}',
    )
    docs = build_sbom_documents(
        application_name="sample",
        repository_url="https://github.com/example/sample",
        commit_sha="a" * 40,
        dependencies=deps,
    )
    cyclonedx = docs["CYCLONEDX"]
    assert cyclonedx["bomFormat"] == "CycloneDX"
    assert len(cyclonedx["components"]) == 2
    props = {item["name"]: item["value"] for item in cyclonedx["metadata"]["properties"]}
    assert props["aetherops:completeness"] == "DECLARED_DIRECT_DEPENDENCIES_ONLY"
    assert props["aetherops:transitiveDependenciesResolved"] == "false"
    spdx = docs["SPDX"]
    assert spdx["spdxVersion"] == "SPDX-2.3"
    assert len(spdx["packages"]) == 2
