import requests
import sys

# GitLab Config
GITLAB_URL = "https://gitlab.com"
GITLAB_TOKEN = "YOUR_GITLAB_PERSONAL_ACCESS_TOKEN"  # ⚠️ Must have `api` scope

def delete_project(project_id_or_path):
    """Delete a GitLab project by ID or namespace/project_path"""
    url = f"{GITLAB_URL}/api/v4/projects/{requests.utils.quote(project_id_or_path, safe='')}"
    headers = {"PRIVATE-TOKEN": GITLAB_TOKEN}

    response = requests.delete(url, headers=headers)

    if response.status_code == 202:  # accepted for deletion
        print(f"✅ Project {project_id_or_path} scheduled for deletion.")
    elif response.status_code == 404:
        print(f"❌ Project {project_id_or_path} not found.")
    elif response.status_code == 403:
        print("❌ Forbidden: Check your GitLab token permissions.")
    else:
        print(f"❌ Failed: {response.status_code} {response.text}")

# if __name__ == "__main__":
#     if len(sys.argv) != 2:
#         print("Usage: python delete_gitlab_project.py <project_id_or_path>")
#         sys.exit(1)

#     project_id_or_path = sys.argv[1]  # e.g. "namespace/project_name" or numeric ID
#     delete_project(project_id_or_path)
    
    
def main():
    import sys
    if len(sys.argv) != 2:
        print("Usage: delete-project <project_id_or_path>")
        sys.exit(1)

    project_id_or_path = sys.argv[1]
    delete_project(project_id_or_path)


if __name__ == "__main__":
    main()