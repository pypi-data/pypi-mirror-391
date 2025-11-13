import docker
from docker.errors import NotFound, APIError

def delete_all_docker_containers():
    """Connects to Docker and removes ALL containers (running and stopped)."""
    
    try:
        # 1. Connect to the Docker client
        client = docker.from_env()
        print("Connected to Docker daemon.")

        # 2. List all containers (including stopped ones)
        # 'all=True' is crucial to see stopped containers as well
        containers = client.containers.list(all=True)
        
        if not containers:
            print("✅ No containers found to delete.")
            return

        print(f"Found {len(containers)} containers to process...")
        
        containers_deleted = 0
        
        for container in containers:
            name = container.name
            status = container.status
            
            print(f"\nProcessing container: **{name}** (Status: {status})")
            
            try:
                # 3. Stop the container if it's running
                if status == 'running':
                    print(f"Stopping container {name}...")
                    container.stop()
                    print(f"Container {name} stopped.")
                
                # 4. Remove the container
                # 'v=True' removes anonymous volumes associated with the container
                print(f"Removing container {name}...")
                container.remove(v=True, force=True) 
                print(f"🗑️ Successfully deleted container: **{name}**")
                containers_deleted += 1
                
            except NotFound:
                print(f"⚠️ Container {name} was not found (might have been removed by another process). Skipping.")
            except APIError as e:
                print(f"❌ Could not stop or delete container {name}. Error: {e}")
                
        print(f"\n---")
        print(f"**Cleanup Complete!** Total containers deleted: **{containers_deleted}**")
        
    except Exception as e:
        print(f"❌ An error occurred during Docker connection or operation: {e}")

# Call the function to execute the cleanup
delete_all_docker_containers()