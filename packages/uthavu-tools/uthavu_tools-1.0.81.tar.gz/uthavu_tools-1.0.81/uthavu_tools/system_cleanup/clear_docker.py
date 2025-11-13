import docker
from docker.errors import ImageNotFound, APIError

def delete_all_docker_images():
    """Connects to Docker and removes ALL images."""
    try:
        # Client connects using environment variables or default settings
        client = docker.from_env()
        print("Connected to Docker daemon.")

        images = client.images.list()
        
        if not images:
            print("✅ No images found to delete.")
            return

        print(f"Found {len(images)} images to delete...")
        
        for image in images:
            for tag in image.tags:
                try:
                    # Force removal ('force=True') is often needed if containers reference the image
                    client.images.remove(image=tag, force=True)
                    print(f"🗑️ Successfully deleted image: {tag}")
                except (ImageNotFound, APIError) as e:
                    print(f"⚠️ Could not delete image {tag}. Error: {e}")
                
    except Exception as e:
        print(f"❌ An error occurred during Docker connection or operation: {e}")

# Uncomment the line below to run the function:
delete_all_docker_images()