import subprocess
import sys
import os
import shutil
import re
from pathlib import Path
import configparser

def run_cmd(cmd):
    """Run a shell command and print output live"""
    print(f"👉 Running: {cmd}")
    result = subprocess.run(cmd, shell=True, text=True)
    if result.returncode != 0:
        print(f"❌ Command failed: {cmd}")
        sys.exit(result.returncode)

def bump_version(file_path="pyproject.toml", bump_type="patch"):
    """Increment version in pyproject.toml (patch, minor, major)"""
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    match = re.search(r'version\s*=\s*"(.*?)"', content)
    if not match:
        print("❌ No version field found in pyproject.toml")
        sys.exit(1)

    old_version = match.group(1)
    major, minor, patch = map(int, old_version.split("."))

    if bump_type == "major":
        major, minor, patch = major + 1, 0, 0
    elif bump_type == "minor":
        minor, patch = minor + 1, 0
    else:  # default: patch
        patch += 1

    new_version = f"{major}.{minor}.{patch}"
    new_content = content.replace(f'version = "{old_version}"', f'version = "{new_version}"')

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(new_content)

    print(f"🔖 Version bumped: {old_version} → {new_version}")
    return new_version

def get_pypi_credentials():
    """Check ~/.pypirc first, then env vars"""
    pypirc_path = Path.home() / ".pypirc"
    if pypirc_path.exists():
        config = configparser.ConfigParser()
        config.read(pypirc_path)
        if "pypi" in config:
            username = config["pypi"].get("username")
            password = config["pypi"].get("password")
            if username and password:
                print("🔑 Using credentials from ~/.pypirc")
                return username, password

    # fallback to env vars
    username = os.getenv("PYPI_USERNAME", "__token__")
    password = os.getenv("PYPI_PASSWORD")
    if password:
        print("🔑 Using credentials from environment variables")
        return username, password

    print("❌ No PyPI credentials found. Set ~/.pypirc or PYPI_USERNAME/PYPI_PASSWORD")
    sys.exit(1)

def main():
    bump_type = sys.argv[1] if len(sys.argv) > 1 else "patch"
    version = bump_version(bump_type=bump_type)

    for folder in ["dist", "build"]:
        if os.path.exists(folder):
            shutil.rmtree(folder)

    run_cmd("python -m build")

    username, password = get_pypi_credentials()
    run_cmd(f"python -m twine upload dist/* -u {username} -p {password}")

    run_cmd("pip show -f uthavu-tools")

    print(f"\n🚀 Publish complete! Released version {version}")

if __name__ == "__main__":
    main()
