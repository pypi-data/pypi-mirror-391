import os
import shutil
import sys

def install_vscode_launcher():
    """Create a global 'vscode' command to open VS Code in current Explorer folder."""
    bat_content = "@echo off\ncode .\n"
    launcher_name = "vscode.bat"

    # Choose install directory — prefer a folder already in PATH
    possible_dirs = os.environ["PATH"].split(os.pathsep)
    target_dir = None
    for d in possible_dirs:
        if os.access(d, os.W_OK) and os.path.isdir(d):
            target_dir = d
            break

    if not target_dir:
        print("❌ No writable folder found in PATH. Try running as Administrator.")
        sys.exit(1)

    launcher_path = os.path.join(target_dir, launcher_name)

    # Write the launcher file
    with open(launcher_path, "w", encoding="utf-8") as f:
        f.write(bat_content)

    print(f"✅ VS Code launcher installed successfully!")
    print(f"Type `vscode` in File Explorer's address bar to open the current folder in VS Code.")
    print(f"Installed at: {launcher_path}")

def main():
    install_vscode_launcher()

if __name__ == "__main__":
    main()
