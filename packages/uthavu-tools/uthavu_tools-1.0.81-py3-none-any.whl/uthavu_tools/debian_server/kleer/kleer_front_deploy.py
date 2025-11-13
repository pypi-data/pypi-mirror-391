#!/usr/bin/env python3
"""
🚀 Kleer Front Deployment Automation
Author: Jawahar (Uthavu Software – People’s Solution)
"""

import argparse
import os
import subprocess
import paramiko
from dotenv import load_dotenv

# ───────────────────────────────────────────────
# CONFIGURATION
# ───────────────────────────────────────────────
APP_NAME = "kleer_front"
REGISTRY = "registry.gitlab.com/kleer-tech/kleer_front"
REMOTE_HOST = "dev2.kleer.ai"
REMOTE_USER = "debian"
REMOTE_PATH = "system"
SERVICE_WEB = "webserver"
SERVICE_FRONT = "kleer_front"
REMOTE_FILE = f"/home/{REMOTE_USER}/{REMOTE_PATH}/docker-compose.yml"

load_dotenv()

def get_git_commit_hash():
    """Detect Git root automatically and return short commit hash."""
    try:
        # Detect Git repo root (works even if kfd is run elsewhere)
        git_root = subprocess.check_output(["git", "rev-parse", "--show-toplevel"], text=True).strip()
    except subprocess.CalledProcessError:
        # fallback: walk up directories until .git found
        current = os.getcwd()
        while current != os.path.dirname(current):
            if os.path.isdir(os.path.join(current, ".git")):
                git_root = current
                break
            current = os.path.dirname(current)
        else:
            raise RuntimeError("❌ No Git repository found.")
    
    try:
        commit_hash = subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], cwd=git_root, text=True).strip()
        print(f"🧠 Detected Git root: {git_root}")
        print(f"🔖 Using commit hash: {commit_hash}")
        return commit_hash
    except subprocess.CalledProcessError:
        raise RuntimeError("❌ Failed to get Git commit hash.")

# ───────────────────────────────────────────────
# HELPER FUNCTIONS
# ───────────────────────────────────────────────
def run_cmd(cmd, cwd=None):
    """Run a shell command and print output."""
    print(f"\n💻 Running: {cmd}")
    result = subprocess.run(cmd, shell=True, cwd=cwd, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"❌ Command failed: {cmd}")
    print("✅ Done.")
    
# ───────────────────────────────────────────────
# HELPER FUNCTIONS
# ───────────────────────────────────────────────
# ... (existing run_cmd and update_env_local functions)

def check_docker_running():
    """Check if the Docker daemon is running."""
    print("\n🔍 Checking Docker status...")
    try:
        # Run a simple, non-destructive Docker command (like 'docker info' or 'docker ps')
        # We capture output and error, but don't print them unless it fails.
        result = subprocess.run(
            ["docker", "info"],
            check=True,  # Raise an exception for non-zero exit codes
            capture_output=True,
            text=True
        )
        print("✅ Docker daemon is running.")
        return True
    except subprocess.CalledProcessError as e:
        print("❌ ERROR: Docker command failed. Is Docker Desktop/Service running?")
        # Print a concise error message for troubleshooting
        print(f"   Command: {e.cmd}")
        print(f"   Stderr: {e.stderr.splitlines()[0] if e.stderr else 'No output.'}")
        return False
    except FileNotFoundError:
        print("❌ ERROR: 'docker' command not found. Is Docker installed and in your PATH?")
        return False

# ... (existing ssh_edit_docker_compose function)


def update_env_local(new_version, env_file=".env.local"):
    """Update NEXT_PUBLIC_APP_VERSION and disable mock in .env.local"""
    if not os.path.exists(env_file):
        print(f"⚠️ {env_file} not found, skipping.")
        return

    updated_lines = []
    with open(env_file, "r") as f:
        for line in f:
            if line.startswith("NEXT_PUBLIC_APP_VERSION="):
                updated_lines.append(f"NEXT_PUBLIC_APP_VERSION={new_version}\n")
            elif line.startswith("NEXT_PUBLIC_USE_MOCK="):
                updated_lines.append("NEXT_PUBLIC_USE_MOCK=false\n")
            else:
                updated_lines.append(line)

    with open(env_file, "w") as f:
        f.writelines(updated_lines)

    print(f"🧩 Updated {env_file}: version={new_version}, mock=false")


def ssh_edit_docker_compose(new_version):
    """SSH into remote server, edit docker-compose.yml version, restart containers."""
    print(f"\n🔐 Connecting to {REMOTE_USER}@{REMOTE_HOST} ...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(REMOTE_HOST, username=REMOTE_USER)

    # sed_cmd = (
    #     f"sudo sed -i 's|registry.gitlab.com/kleer-tech/kleer_front:v[0-9.]*|"
    #     f"registry.gitlab.com/kleer-tech/kleer_front:{new_version}|' {REMOTE_FILE}"
    # )
    
    sed_cmd = (
        f"sudo sed -i 's|registry.gitlab.com/kleer-tech/kleer_front:[a-zA-Z0-9._-]*|"
        f"registry.gitlab.com/kleer-tech/kleer_front:{new_version}|' "
        f"/home/{REMOTE_USER}/{REMOTE_PATH}/docker-compose.yml"
    )

    restart_cmds = [
        f"cd /home/{REMOTE_USER}/{REMOTE_PATH}",
        sed_cmd,
        "echo '✅ Updated docker-compose.yml with new image tag.'",
        #"docker compose restart webserver",
        "docker compose up -d --force-recreate kleer_front",
        "echo '🎉 Containers restarted successfully.'"
    ]

    full_cmd = " && ".join(restart_cmds)
    stdin, stdout, stderr = ssh.exec_command(full_cmd)

    print("📡 Remote output:")
    for line in stdout:
        print(" ", line.strip())
    for line in stderr:
        print(" ", line.strip())

    ssh.close()
    print("✅ Remote deployment completed.")


# ───────────────────────────────────────────────
# MAIN DEPLOY LOGIC
# ───────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(
        description="Automate Kleer Front build, push, and deploy."
    )
    parser.add_argument("--version", "-v", help="Version number (e.g., 1.2.16)", required=False)
    parser.add_argument("--build", action="store_true", help="Build the Docker image only")
    parser.add_argument("--push", action="store_true", help="Push the Docker image only")
    parser.add_argument("--deploy", action="store_true", help="Deploy remotely only")
    parser.add_argument("--local", action="store_true", help="Only update .env.local (skip Docker & SSH)")
    parser.add_argument("--all", action="store_true", help="Run all steps (default)")
    parser.add_argument("--no-cache", action="store_true", help="Do not use Docker build cache.") # <-- NEW ARGUMENT

    args = parser.parse_args()

    # Normalize version
    #new_version = (args.version or input("Enter new version tag (e.g., 1.2.16): ")).strip().lstrip("v")
    new_version = get_git_commit_hash()
    print(f"🔖 Using Git commit hash as version tag → {new_version}")
    

    # Always update .env.local unless explicitly skipped
    update_env_local(new_version)
    
    
    # Local-only mode
    if args.local:
        print("🧩 Local mode enabled — skipping Docker build/push and remote deploy.")
        return

    # Default behavior → all steps
    if not any([args.build, args.push, args.deploy, args.all]):
        args.all = True
        
    if not check_docker_running():
            # If Docker is not running, exit the script gracefully.
            print("🛑 Cannot proceed without a running Docker daemon.")
            return # Exit the main function

    # Step 1: Git fetch/pull (common pre-step)
    run_cmd("git fetch")
    run_cmd("git pull")

    # Step 2: Docker Build
    if args.build or args.all:
        print("\n🐳 Building Docker image...")
        cache_flag = "--no-cache" if args.no_cache else ""
        build_cmd = (
            f"docker build {cache_flag} "
            #f"--build-arg NEXT_PUBLIC_API_URL={api_url} "
            #f"--build-arg NEXT_PUBLIC_API_TOKEN={api_token} "
            #f"--build-arg NEXT_PUBLIC_APP_VERSION={new_version} " 
            f"-t {APP_NAME}:{new_version} ."
        )
        #run_cmd(f"docker build {cache_flag} -t {APP_NAME}:{new_version} .")
        run_cmd(build_cmd)
        run_cmd(f"docker tag {APP_NAME}:{new_version} {REGISTRY}:{new_version}")

    # Step 3: Docker Push
    if args.push or args.all:
        print("\n📦 Pushing image to registry...")
        run_cmd(f"docker push {REGISTRY}:{new_version}")

    # Step 4: Deploy via SSH
    if args.deploy or args.all:
        print("\n🚀 Deploying to remote server...")
        ssh_edit_docker_compose(new_version)

    print("\n✅ Deployment automation completed successfully!")


if __name__ == "__main__":
    main()
