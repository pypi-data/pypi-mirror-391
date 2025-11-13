from datetime import datetime
from textwrap import shorten
import os
import subprocess
import argparse
from textwrap import shorten

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
    except subprocess.CalledProcessError:
        return None


def get_repo_summary(repo_path):
    """Collect git info for a given repo path."""
    branch = run_git_command(repo_path, "rev-parse --abbrev-ref HEAD") or "N/A"
    author = run_git_command(repo_path, "log -1 --pretty=%an") or "N/A"
    commit_msg = run_git_command(repo_path, "log -1 --pretty=%s") or "N/A"
    commit_date = run_git_command(repo_path, "log -1 --date=short --pretty=%cd") or "N/A"
    remote_url = run_git_command(repo_path, "remote get-url origin") or "No remote"
    status_output = run_git_command(repo_path, "status --porcelain") or ""
    clean_status = "✅ Clean" if not status_output else "⚠️ Uncommitted changes"

    ahead_behind = run_git_command(repo_path, "rev-list --left-right --count HEAD...@{u}")
    if ahead_behind:
        try:
            behind, ahead = ahead_behind.split()
            sync_info = f"↑{ahead}/↓{behind}"
        except ValueError:
            sync_info = "N/A"
    else:
        sync_info = "N/A"

    return {
        "name": os.path.basename(repo_path),
        "branch": branch,
        "author": author,
        "commit": commit_msg,
        "date": commit_date,
        "remote": remote_url,
        "status": clean_status,
        "sync": sync_info,
    }


def list_git_repos(base_path="."):
    """Return list of repo info dicts."""
    repos = []
    for root, dirs, _ in os.walk(base_path):
        if ".git" in dirs:
            repos.append(os.path.abspath(root))
            dirs[:] = []
    return [get_repo_summary(path) for path in repos]



def print_table(repos):
    """Print repository info in table format (sorted by date descending)."""
    if not repos:
        print("⚠️  No Git repositories found.")
        return

    # Convert commit date string to datetime for sorting
    for repo in repos:
        try:
            repo["_sort_date"] = datetime.strptime(repo["date"], "%Y-%m-%d")
        except Exception:
            repo["_sort_date"] = datetime.min  # fallback for invalid/missing dates

        # Limit commit message length for readability
        repo["commit"] = shorten(repo["commit"], width=55, placeholder="…")

    # ✅ Sort by date descending
    repos.sort(key=lambda r: r["_sort_date"], reverse=True)

    headers = ["#", "Repo", "Branch", "Author", "Commit", "Date", "Sync", "Status"]
    col_widths = [4, 25, 35, 35, 55, 12, 10, 20]

    # Print header
    header_row = "".join(f"{h:<{w}}" for h, w in zip(headers, col_widths))
    print(header_row)
    print("-" * len(header_row))

    # Print rows
    for i, r in enumerate(repos, start=1):
        print(
            f"{i:<4}{r['name']:<25}{r['branch']:<35}{r['author']:<35}"
            f"{r['commit']:<55}{r['date']:<12}{r['sync']:<10}{r['status']:<20}"
        )



def print_normal(repos, horizontal=False):
    """Fallback for normal/horizontal layouts."""
    for i, r in enumerate(repos, start=1):
        if horizontal:
            print(
                f"{i:2}. 📦 {r['name']} | 🌿 {r['branch']} | 💬 {r['commit']} | "
                f"🧑 {r['author']} | 🕒 {r['date']} | 🔄 {r['sync']} | {r['status']}"
            )
        else:
            print(f"{i:2}. 📦 {r['name']}")
            print(f"    🌿 Branch: {r['branch']}")
            print(f"    💬 Commit: {r['commit']}")
            print(f"    🧑 Author: {r['author']}")
            print(f"    🕒 Date: {r['date']}")
            print(f"    🔄 Sync: {r['sync']}")
            print(f"    🧹 Status: {r['status']}\n")


def main():
    parser = argparse.ArgumentParser(description="List Git repositories in different formats")
    parser.add_argument("--path", type=str, default=".", help="Parent folder to search (default: .)")
    parser.add_argument("--horizontal", action="store_true", help="Show output in one line per repo")
    parser.add_argument("--table", action="store_true", help="Show output in table format")
    args = parser.parse_args()

    repos = list_git_repos(args.path)

    print(f"🔍 Searching for Git repositories under: {os.path.abspath(args.path)}\n")

    if args.table:
        print_table(repos)
    else:
        print_normal(repos, args.horizontal)


if __name__ == "__main__":
    main()
