import subprocess
import sys
import os

def run_cmd(cmd, check=True):
    """Run a shell command and print output live"""
    print(f"👉 Running: {cmd}")
    result = subprocess.run(cmd, shell=True, text=True)
    if check and result.returncode != 0:
        print(f"❌ Command failed: {cmd}")
        sys.exit(result.returncode)

def get_current_branch():
    """Return current branch name"""
    result = subprocess.run(
        "git rev-parse --abbrev-ref HEAD", shell=True, text=True, capture_output=True
    )
    return result.stdout.strip()

def bump_version(version: str, bump_type: str = "patch") -> str:
    """Bump semantic version based on bump_type"""
    major, minor, patch = map(int, version.split("."))
    if bump_type == "major":
        major += 1
        minor = 0
        patch = 0
    elif bump_type == "minor":
        minor += 1
        patch = 0
    else:  # patch
        patch += 1
    return f"{major}.{minor}.{patch}"

def get_latest_tag():
    """Return the latest tag, or v0.0.0 if none exist"""
    result = subprocess.run(
        "git describe --tags --abbrev=0",
        shell=True,
        text=True,
        capture_output=True,
    )
    if result.returncode != 0:
        return "0.0.0"
    return result.stdout.strip().lstrip("v")

def main():
    if len(sys.argv) < 2:
        print("❌ Usage: release \"Your commit message here\" [patch|minor|major]")
        sys.exit(1)

    commit_msg = sys.argv[1]
    bump_type = sys.argv[2] if len(sys.argv) > 2 else "patch"

    # ✅ Step 1: Ensure we are on dev
    branch = get_current_branch()
    if branch != "dev":
        print(f"❌ You are on branch '{branch}', please switch to 'dev'")
        sys.exit(1)

    # Step 2: commit + push dev
    run_cmd("git add .")
    run_cmd(f'git commit -m "{commit_msg}" || echo \"✅ Nothing to commit\"')
    run_cmd("git push origin dev")

    # Step 3: checkout main + merge dev
    run_cmd("git checkout main")
    run_cmd("git pull origin main")
    run_cmd("git merge dev")
    run_cmd("git push origin main")

    # Step 4: bump version
    latest_version = get_latest_tag()
    new_version = bump_version(latest_version, bump_type)
    new_tag = f"v{new_version}"
    print(f"🔖 Bumping version: {latest_version} → {new_version}")
    run_cmd(f"git tag {new_tag}")
    run_cmd(f"git push origin {new_tag}")

    # Step 5: build package
    run_cmd("python -m pip install --upgrade build twine")
    run_cmd("python -m build")

    # Step 6: upload to PyPI
    pypi_username = os.getenv("PYPI_USERNAME", "__token__")
    pypi_password = os.getenv("PYPI_PASSWORD")
    if not pypi_password:
        print("❌ PYPI_PASSWORD not set. Please export it first1.")
        sys.exit(1)

    run_cmd(f"python -m twine upload dist/* -u {pypi_username} -p {pypi_password}")

    # Step 7: return to dev
    run_cmd("git checkout dev")

    print(f"\n🚀 Release {new_version} complete! Code merged into main, tagged, and published to PyPI.")

if __name__ == "__main__":
    main()
