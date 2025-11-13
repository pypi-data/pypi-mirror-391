# uthavu_tools/git_tools/mergedevmain.py
import sys
from git import Repo, GitCommandError

def main():
    REPO_PATH = "."  # current directory by default
    repo = Repo(REPO_PATH)

    if repo.is_dirty(untracked_files=True):
        print("⚠️ You have uncommitted changes. Please commit/stash before merging.")
        sys.exit(1)

    try:
        print("👉 Switching to main...")
        repo.git.checkout("main")
        print("👉 Pulling latest main...")
        repo.git.pull("origin", "main")

        print("👉 Merging dev into main...")
        repo.git.merge("dev")

        print("👉 Pushing main...")
        repo.git.push("origin", "main")

        print("👉 Switching back to dev...")
        repo.git.checkout("dev")

        print("✅ Merge completed and switched back to dev!")

    except GitCommandError as e:
        print("❌ Merge conflict! Resolve manually.")
        print(e)
        sys.exit(1)
