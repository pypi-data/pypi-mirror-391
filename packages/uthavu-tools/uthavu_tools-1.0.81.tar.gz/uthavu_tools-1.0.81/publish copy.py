import subprocess
import sys
import os
import shutil
import re

def run_cmd(cmd):
    """Run a shell command and print output live"""
    print(f"👉 Running: {cmd}")
    result = subprocess.run(cmd, shell=True, text=True)
    if result.returncode != 0:
        print(f"❌ Command failed: {cmd}")
        sys.exit(result.returncode)

def bump_version(file_path="pyproject.toml"):
    """Increment patch version in pyproject.toml"""
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    match = re.search(r'version\s*=\s*"(.*?)"', content)
    if not match:
        print("❌ No version field found in pyproject.toml")
        sys.exit(1)

    old_version = match.group(1)
    parts = old_version.split(".")
    if len(parts) != 3:
        print(f"❌ Unsupported version format: {old_version}")
        sys.exit(1)

    major, minor, patch = map(int, parts)
    patch += 1
    new_version = f"{major}.{minor}.{patch}"

    new_content = content.replace(f'version = "{old_version}"', f'version = "{new_version}"')

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(new_content)

    print(f"🔖 Version bumped: {old_version} → {new_version}")
    return new_version

def main():
    # Step 0: bump version
    version = bump_version()

    # Clean old builds
    if os.path.exists("dist"):
        shutil.rmtree("dist")
    if os.path.exists("build"):
        shutil.rmtree("build")

    # Step 1: build package
    run_cmd("python -m build")

    # Step 2: upload to PyPI
    pypi_username = os.getenv("PYPI_USERNAME", "__token__")
    print("🔑 Using PyPI username:", pypi_username)
    pypi_password = "pypi-AgEIcHlwaS5vcmcCJGMxNzgyODU2LTg4MDUtNGM2Yy04YTVjLWIyMWU5NDUwZTdkNgACFFsxLFsidXRoYXZ1LXRvb2xzIl1dAAIsWzIsWyJlM2NiYjI0My1mMWMxLTRmODItYjgwYi1jMmY1NTQ2NjIwYTIiXV0AAAYggpRxfPO8JPGPbq9ralnwUQJalq_5omaMLaarU6Vdxok"
    print("🔑 Using PyPI password from environment variable.")
    if not pypi_password:
        print("❌ PYPI_PASSWORD not set. Please export it first.")
        sys.exit(1)

    run_cmd(f"python -m twine upload dist/* -u {pypi_username} -p {pypi_password}")

    # Step 3: show installed files (optional)
    run_cmd("pip show -f uthavu-tools")

    print(f"\n🚀 Publish complete! Released version {version}")

if __name__ == "__main__":
    main()
