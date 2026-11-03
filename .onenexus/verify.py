"""Checks the packed OneNexus.* packages before they are published.

Usage: python3 -I .onenexus/verify.py <package-dir> <expected-commit-sha>
"""
import sys
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

# Upstream id -> assembly that must ship under lib/.
PACKAGES = {
    "Json.More.Net": "Json.More.dll",
    "JsonPointer.Net": "JsonPointer.Net.dll",
    "JsonLogic": "JsonLogic.dll",
    "JsonSchema.Net": "JsonSchema.Net.dll",
}
REPOSITORY = "https://github.com/onenexus-team/json-everything"


def check(path: Path, commit: str) -> list[str]:
    errors = []
    with zipfile.ZipFile(path) as z:
        names = z.namelist()
        nuspec_name = next(n for n in names if n.endswith(".nuspec") and "/" not in n)
        root = ET.fromstring(z.read(nuspec_name))
    ns = {"n": root.tag.split("}")[0].strip("{")}
    meta = root.find("n:metadata", ns)
    pkg_id = meta.findtext("n:id", namespaces=ns)
    upstream = pkg_id.removeprefix("OneNexus.")
    if pkg_id == upstream or upstream not in PACKAGES:
        return [f"{path.name}: unexpected id {pkg_id}"]

    for dep in meta.iter(f"{{{ns['n']}}}dependency"):
        if dep.get("id") in PACKAGES:
            errors.append(f"{pkg_id}: depends on upstream {dep.get('id')}")
    license = meta.find("n:license", ns)
    if license is None or license.get("type") != "file" or license.text != "LICENSE":
        errors.append(f"{pkg_id}: license is not the MIT LICENSE file")
    if meta.findtext("n:requireLicenseAcceptance", namespaces=ns) == "true":
        errors.append(f"{pkg_id}: requires license acceptance")
    if "LICENSE" not in names:
        errors.append(f"{pkg_id}: LICENSE missing")
    if any(n.upper().endswith("OSMFEULA.TXT") for n in names):
        errors.append(f"{pkg_id}: OSMFEULA.txt is packed")
    repo = meta.find("n:repository", ns)
    if repo is None or repo.get("url") != REPOSITORY or repo.get("commit") != commit:
        errors.append(f"{pkg_id}: repository is not {REPOSITORY}@{commit}")
    dlls = [n for n in names if n.startswith("lib/") and n.endswith("/" + PACKAGES[upstream])]
    if not dlls:
        errors.append(f"{pkg_id}: no {PACKAGES[upstream]} under lib/")
    print(f"{pkg_id} {meta.findtext('n:version', namespaces=ns)}: {', '.join(sorted(dlls))}")
    return errors


def main() -> int:
    directory, commit = Path(sys.argv[1]), sys.argv[2]
    packages = sorted(directory.glob("*.nupkg"))
    errors = [e for p in packages for e in check(p, commit)]
    if len(packages) != len(PACKAGES):
        errors.append(f"expected {len(PACKAGES)} packages, found {len(packages)}")
    for e in errors:
        print(f"::error::{e}")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
