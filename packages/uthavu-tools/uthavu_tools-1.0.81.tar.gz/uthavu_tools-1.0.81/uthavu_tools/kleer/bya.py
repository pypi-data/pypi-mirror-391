import subprocess
import sys
import os

# --- Configuration ---
CONTAINER_NAME = "services-database-1"
DB_USER = "root"
DB_NAME = "bya"
# ---------------------

def main():
    """
    Executes the docker exec command to connect to the psql client.
    """
    print(f"Attempting to connect to container '{CONTAINER_NAME}' as user '{DB_USER}' to database '{DB_NAME}'...")

    # The command to execute in the host OS
    # We use shlex.split() or a list to safely handle arguments, but here a simple string list works well.
    docker_command = [
        "docker", "exec", "-it",
        CONTAINER_NAME,
        "psql", "-U", DB_USER, "-d", DB_NAME
    ]

    try:
        # subprocess.run executes the command and waits for it to complete.
        # It uses the terminal (stdin/stdout/stderr) of the current Python script.
        # We use a separate Popen call with sys.stdin/out/err to maintain the interactive terminal
        # experience required for psql.
        
        # Use Popen for interactive shell commands
        process = subprocess.Popen(docker_command, stdin=sys.stdin, stdout=sys.stdout, stderr=sys.stderr)
        process.wait() 
        
    except FileNotFoundError:
        print("\nERROR: 'docker' command not found.")
        print("Please ensure Docker is running and available in your system's PATH.")
        sys.exit(1)
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()