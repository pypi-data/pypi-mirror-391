import subprocess
import sys

def run_cmd(cmd):
    """Run a shell command and return output"""
    result = subprocess.run(cmd, shell=True, text=True, capture_output=True)
    if result.returncode != 0:
        print(f"❌ Command failed: {cmd}\n{result.stderr}")
        sys.exit(result.returncode)
    return result.stdout.strip()

def main():
    print("🔄 Fetching and pruning remote branches...")
    run_cmd("git fetch -p")  # prune stale remote tracking refs

    # Get all local branches with tracking info
    output = run_cmd("git branch -vv")
    to_delete = []

    for line in output.splitlines():
        line = line.strip()
        if line.startswith("*"):  # Skip current branch
            continue
        if "[gone]" in line:  # marker: remote branch deleted
            branch = line.split()[0]
            to_delete.append(branch)

    if not to_delete:
        print("✅ No disconnected local branches found.")
        return

    print("🗑️ Disconnected branches found:")
    for b in to_delete:
        print(f"   - {b}")

    confirm = input("❓ Do you want to delete these branches? (y/N): ").lower()
    if confirm == "y":
        for b in to_delete:
            run_cmd(f"git branch -D {b}")
            print(f"🗑️ Deleted: {b}")
        print("✅ Cleanup complete.")
    else:
        print("❌ Aborted. No branches deleted.")

if __name__ == "__main__":
    main()
