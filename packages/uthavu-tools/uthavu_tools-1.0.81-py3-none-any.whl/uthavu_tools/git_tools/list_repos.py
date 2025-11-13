import os

def main(base_path="."):
    print(f"🔍 Searching for Git repositories under: {os.path.abspath(base_path)}\n")

    repo_list = []
    for root, dirs, files in os.walk(base_path):
        if ".git" in dirs:
            repo_list.append(os.path.abspath(root))
            # skip walking into subdirectories of a repo
            dirs[:] = []

    if not repo_list:
        print("⚠️  No Git repositories found.")
    else:
        print("📁 Found repositories:")
        for idx, repo in enumerate(repo_list, start=1):
            print(f"{idx:2}. {repo}")

if __name__ == "__main__":
    # Change '.' to any parent path you want, e.g. 'C:\\projects'
    main(".")
