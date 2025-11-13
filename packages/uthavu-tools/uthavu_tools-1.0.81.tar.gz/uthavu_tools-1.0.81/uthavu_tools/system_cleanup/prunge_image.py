import docker

def delete_dangling_images():
    """Removes only dangling images (untagged and unused)."""
    try:
        client = docker.from_env()
        print("Connected to Docker daemon.")
        
        print("Searching for and pruning dangling images...")
        
        # filters={'dangling': True} specifically targets the <none>:<none> images
        report = client.images.prune(filters={'dangling': True})
        
        deleted_images = report.get('ImagesDeleted', [])
        deleted_count = len(deleted_images)
        
        if deleted_count > 0:
            total_reclaimed = round(report.get('SpaceReclaimed', 0) / (1024**3), 2)
            print(f"✅ Successfully pruned **{deleted_count}** dangling images.")
            print(f"   Total space reclaimed: **{total_reclaimed} GB**")
        else:
            print("✅ No dangling images found to prune.")

    except Exception as e:
        print(f"❌ An error occurred: {e}")

# Run the function
delete_dangling_images()