import os
import subprocess

def get_current_branch(repo_path):
    """Return the current Git branch name, or 'detached/no branch' if not found."""
    try:
        result = subprocess.run(
            ["git", "-C", repo_path, "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return "⚠️  Not a valid branch (detached HEAD or error)"

def main(base_path="."):
    print(f"🔍 Searching for Git repositories under: {os.path.abspath(base_path)}\n")

    repo_list = []
    for root, dirs, files in os.walk(base_path):
        if ".git" in dirs:
            branch = get_current_branch(root)
            repo_list.append((os.path.abspath(root), branch))
            # skip going into subfolders once a repo is found
            dirs[:] = []

    if not repo_list:
        print("⚠️  No Git repositories found.")
    else:
        print("📁 Found repositories:\n")
        for idx, (repo, branch) in enumerate(repo_list, start=1):
            print(f"{idx:2}. {repo}")
            print(f"    🌿 Branch: {branch}\n")

if __name__ == "__main__":
    # Change '.' to another path if needed, e.g. 'C:\\projects'
    main(".")