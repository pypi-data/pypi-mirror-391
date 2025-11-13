import os
import shutil

def main():
    patterns = ["__pycache__", ".pytest_cache", ".mypy_cache"]
    removed = 0

    for root, dirs, files in os.walk(".", topdown=False):
        for d in dirs:
            if d in patterns:
                path = os.path.join(root, d)
                shutil.rmtree(path, ignore_errors=True)
                print(f"🗑️ Removed: {path}")
                removed += 1

    print(f"\n✅ Cleanup finished, {removed} folders removed.")
