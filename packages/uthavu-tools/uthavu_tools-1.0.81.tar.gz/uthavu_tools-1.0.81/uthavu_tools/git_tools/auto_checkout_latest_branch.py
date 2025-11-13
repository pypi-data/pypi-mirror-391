import os
import subprocess
from datetime import datetime

def run_git_command(repo_path, command):
    """Run a git command in a specific repo and return its output or None."""
    try:
        result = subprocess.run(
            ["git", "-C", repo_path] + command.split(),
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"⚠️  Error in {repo_path}: {e.stderr.strip()}")
        return None


def get_latest_branch(repo_path):
    """Find the branch with the latest commit date."""
    branches_raw = run_git_command(repo_path, "for-each-ref --sort=-committerdate refs/heads/ --format='%(refname:short)|%(committerdate:iso)'")
    if not branches_raw:
        return None, None

    branches = []
    for line in branches_raw.splitlines():
        try:
            name, date_str = line.strip("'").split("|", 1)
            commit_date = datetime.fromisoformat(date_str.strip())
            branches.append((name, commit_date))
        except Exception:
            continue

    if not branches:
        return None, None

    # Sort descending by commit date
    branches.sort(key=lambda x: x[1], reverse=True)
    return branches[0]


def checkout_branch(repo_path, branch):
    """Checkout the given branch safely."""
    current_branch = run_git_command(repo_path, "rev-parse --abbrev-ref HEAD")
    if current_branch == branch:
        print(f"✅ {os.path.basename(repo_path)} already on '{branch}'")
        return

    print(f"🔁 Checking out '{branch}' in {os.path.basename(repo_path)}...")
    run_git_command(repo_path, f"checkout {branch}")


def main(base_path="."):
    print(f"🔍 Scanning repositories under: {os.path.abspath(base_path)}\n")

    for root, dirs, _ in os.walk(base_path):
        if ".git" in dirs:
            repo = os.path.abspath(root)
            print(f"📁 Repo: {os.path.basename(repo)}")

            branch, date = get_latest_branch(repo)
            if not branch:
                print("⚠️  No valid branches found.\n")
                continue

            print(f"   🌿 Latest branch: {branch} ({date.date()})")
            checkout_branch(repo, branch)
            print()
            dirs[:] = []  # skip going deeper


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Automatically checkout latest branch in each repo")
    parser.add_argument("--path", type=str, default=".", help="Parent folder to scan (default: .)")
    args = parser.parse_args()
    main(args.path)
