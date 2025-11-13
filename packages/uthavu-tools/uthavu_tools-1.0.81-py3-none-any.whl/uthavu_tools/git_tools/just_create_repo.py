import os
import requests
import sys
import subprocess

# =====================================
# CONFIGURATION
# =====================================
GITLAB_URL = os.getenv("GITLAB_URL", "https://gitlab.com")
GITLAB_TOKEN = "glpat-hg7epYFgilXsXsvB8WQPyW86MQp1Omd4cmVkCw.01.121252fpx" #os.getenv("GITLAB_TOKEN")  # Use env var for security
DEFAULT_GROUP_ID = int(os.getenv("GITLAB_GROUP_ID", "115815064"))


# -------------------------------------
# Helper to run shell commands
# -------------------------------------
def run(cmd):
    """Run a shell command and return its output"""
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"⚠️ Command failed: {cmd}\n{result.stderr}")
    return result.stdout.strip()

# -------------------------------------
# Create GitLab project
# -------------------------------------
def create_gitlab_project(project_name, project_desc, visibility, group_id):
    headers = {"PRIVATE-TOKEN": GITLAB_TOKEN}
    data = {
        "name": project_name,
        "description": project_desc,
        "visibility": visibility,
        "namespace_id": group_id,
    }

    print(f"🔧 Creating GitLab project '{project_name}'...")
    response = requests.post(f"{GITLAB_URL}/api/v4/projects", headers=headers, data=data)

    if response.status_code == 201:
        project = response.json()
        print("✅ Project created successfully!")
        print(f"🌐 Web URL: {project['web_url']}")
        print(f"📦 Repo URL: {project['http_url_to_repo']}")
        return project
    else:
        print(f"❌ Failed to create project: {response.status_code}")
        print(response.text)
        sys.exit(1)

# -------------------------------------
# Push local files to GitLab repo
# -------------------------------------
def push_code_to_repo(repo_url):
    print("\n🚀 Uploading local files to GitLab repository...")

    # Initialize git if not exists
    if not os.path.exists(".git"):
        run("git init")

    run("git add .")
    status = run("git diff --cached --quiet || echo 'changes'")
    if "changes" in status:
        run('git commit -m "Initial commit"')
    else:
        print("ℹ️ Nothing new to commit, skipping commit step.")

    run("git branch -M main")

    # Build remote URL with token for authentication
    remote_url = repo_url.replace("https://", f"https://oauth2:{GITLAB_TOKEN}@")

    # ✅ Windows-safe way to remove 'origin' if it exists
    result = subprocess.run(["git", "remote"], capture_output=True, text=True)
    if "origin" in result.stdout.split():
        run("git remote remove origin")

    run(f"git remote add origin {remote_url}")
    run("git push -u origin main")
    print("✅ Code pushed to main branch.")


# -------------------------------------
# Main
# -------------------------------------
def main():
    if not GITLAB_TOKEN:
        print("❌ Missing GitLab token. Please set GITLAB_TOKEN environment variable.")
        sys.exit(1)

    print("👉 Enter project details:")
    project_name = input("Project name: ").strip()
    if not project_name:
        print("❌ Project name is required.")
        sys.exit(1)

    project_desc = input("Description [default = same as name]: ").strip() or project_name
    visibility = input("Visibility (private/internal/public) [default=private]: ").strip() or "private"
    group_id_input = input(f"Group ID [default = {DEFAULT_GROUP_ID}]: ").strip()
    group_id = int(group_id_input) if group_id_input else DEFAULT_GROUP_ID

    # Create project on GitLab
    project = create_gitlab_project(project_name, project_desc, visibility, group_id)
    repo_url = project["http_url_to_repo"]

    # Push local files
    push_code_to_repo(repo_url)

    print("\n🎉 Done! Repo created and code uploaded successfully.")
    print(f"🌐 {project['web_url']}")


if __name__ == "__main__":
    main()
