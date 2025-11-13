import subprocess

def run(cmd):
    """Run a shell command and return its output (or print errors)."""
    print(f"> {cmd}")
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout.strip())
    except subprocess.CalledProcessError as e:
        print(e.stderr.strip())

def main():
    print("🔍 Cleaning current Git branch...")

    # 1. Verify Git repo
    run("git rev-parse --is-inside-work-tree")

    # 2. Get current branch name
    branch = subprocess.getoutput("git rev-parse --abbrev-ref HEAD").strip()
    print(f"📦 Current branch: {branch}")

    # 3. Fetch latest from origin
    run("git fetch origin")

    # 4. Reset to remote branch (discard all commits and changes)
    run(f"git reset --hard origin/{branch}")

    # 5. Clean untracked files and directories
    run("git clean -fd")

    print("✅ Branch cleaned and reset to remote state!")

if __name__ == "__main__":
    main()
