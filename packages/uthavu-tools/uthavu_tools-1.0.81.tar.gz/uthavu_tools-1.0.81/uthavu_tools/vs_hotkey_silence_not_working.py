import os
import sys

def install_vscode_launcher():
    """Create a global 'vsc' command that opens VS Code silently (no console)."""
    vbs_content = r'''Set shell = CreateObject("WScript.Shell")
Set env = shell.Environment("Process")
cmd = "cmd /c code ."
shell.Run cmd, 0, False
'''

    launcher_name = "vsc.vbs"

    # Pick a writable folder from PATH
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

    # Write the VBS launcher
    with open(launcher_path, "w", encoding="utf-8") as f:
        f.write(vbs_content)

    print(f"✅ Installed 'vsc' command.")
    print("Now you can type 'vsc' in File Explorer's address bar to open this folder in VS Code — silently.")
    print(f"Installed at: {launcher_path}")

def main():
    install_vscode_launcher()

if __name__ == "__main__":
    main()
