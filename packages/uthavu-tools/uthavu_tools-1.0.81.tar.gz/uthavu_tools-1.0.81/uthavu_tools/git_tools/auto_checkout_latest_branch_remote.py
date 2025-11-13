import os
import subprocess
from datetime import datetime
import argparse

def run_git_command(repo_path, command):
    """Run a git command and return output."""
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
    """Find the latest branch (local or remote) by commit date."""
    # Fetch latest info
    run_git_command(repo_path, "fetch --all --prune")

    # Get both local and remote branches sorted by latest commit date
    branches_raw = run_git_command(
        repo_path,
        "for-each-ref --sort=-committerdate refs/heads/ refs/remotes/origin/ "
        "--format='%(refname:short)|%(committerdate:iso)'"
    )

    if not branches_raw:
        return None, None

    branches = []
    for line in branches_raw.splitlines():
        line = line.strip("'").strip()
        if not line or "->" in line:
            continue  # skip symbolic refs
        try:
            name, date_str = line.split("|", 1)
            commit_date = datetime.fromisoformat(date_str.strip())
            branches.append((name.strip(), commit_date))
        except Exception:
            continue

    if not branches:
        return None, None

    # Sort newest first
    branches.sort(key=lambda x: x[1], reverse=True)
    return branches[0]  # (branch_name, datetime)


def checkout_branch(repo_path, branch):
    """Checkout branch; create local tracking if needed."""
    current_branch = run_git_command(repo_path, "rev-parse --abbrev-ref HEAD")
    if current_branch == branch:
        print(f"✅ {os.path.basename(repo_path)} already on '{branch}'")
        return

    # If it's a remote branch (starts with origin/...), create local branch tracking it
    if branch.startswith("origin/"):
        local_branch = branch.split("/", 1)[1]
        print(f"🌿 Creating tracking branch '{local_branch}' from {branch}")
        run_git_command(repo_path, f"checkout -B {local_branch} {branch}")
    else:
        print(f"🔁 Checking out '{branch}'...")
        run_git_command(repo_path, f"checkout {branch}")


def main(base_path="."):
    print(f"🔍 Scanning repositories under: {os.path.abspath(base_path)}\n")

    for root, dirs, _ in os.walk(base_path):
        if ".git" in dirs:
            repo = os.path.abspath(root)
            repo_name = os.path.basename(repo)
            print(f"📁 Repo: {repo_name}")

            branch, date = get_latest_branch(repo)
            if not branch:
                print("⚠️  No valid branches found.\n")
                continue

            print(f"   🌿 Latest branch: {branch} ({date.date()})")
            checkout_branch(repo, branch)
            print()
            dirs[:] = []  # stop deeper traversal


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Checkout the latest branch (local or remote) in each repo")
    parser.add_argument("--path", type=str, default=".", help="Parent folder to scan (default: .)")
    args = parser.parse_args()
    main(args.path)
