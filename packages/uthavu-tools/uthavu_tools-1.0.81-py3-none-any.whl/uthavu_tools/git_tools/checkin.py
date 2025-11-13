import subprocess
import sys

def run_cmd(cmd):
    """Run a shell command and print output live"""
    print(f"👉 Running: {cmd}")
    result = subprocess.run(cmd, shell=True, text=True)
    if result.returncode != 0:
        print(f"❌ Command failed: {cmd}")
        sys.exit(result.returncode)

def get_current_branch():
    """Return the current git branch name"""
    result = subprocess.run(
        "git rev-parse --abbrev-ref HEAD", shell=True, text=True, capture_output=True
    )
    return result.stdout.strip()

def main():
    if len(sys.argv) < 2:
        print("❌ Usage: checkin \"Your commit message here\"")
        sys.exit(1)

    commit_msg = sys.argv[1]
    branch = get_current_branch()

    print(f"📌 You are on branch: {branch}")

    # Step 1: git add .
    run_cmd("git add .")

    # Step 2: git commit with message
    run_cmd(f'git commit -m "{commit_msg}" || echo \"✅ Nothing to commit\"')

    # Step 3: push to current branch
    run_cmd(f"git push origin {branch}")

    print(f"\n✅ Changes committed and pushed to branch '{branch}' successfully!")

if __name__ == "__main__":
    main()
