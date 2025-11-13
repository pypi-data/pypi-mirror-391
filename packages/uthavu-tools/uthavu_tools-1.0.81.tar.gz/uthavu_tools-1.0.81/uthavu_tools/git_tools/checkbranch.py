import subprocess

def main():
    result = subprocess.run(["git", "rev-parse", "--abbrev-ref", "HEAD"], capture_output=True, text=True)
    branch = result.stdout.strip()
    if branch == "main":
        print("✅ You are on the main branch")
    else:
        print(f"⚠️ You are on branch: {branch}")
