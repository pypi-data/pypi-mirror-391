import paramiko
import tempfile
import os
import sys

# ─────────────────────────────────────────────
# CONFIGURATION
# ─────────────────────────────────────────────
HOST = "dev2.kleer.ai"      # or "vps-02a4983f"
USERNAME = "debian"
REMOTE_PATH = "/home/debian/system/config/services/web/nginx/conf/app.conf"
SSH_KEY_PATH = os.path.join(os.path.dirname(__file__), "keys/ssh.pub")
#SSH_KEY_PATH = os.path.expanduser("id_rsa")  # adjust if you use a custom key
# ─────────────────────────────────────────────

def edit_remote_file():
    print(f"🔗 Connecting to {USERNAME}@{HOST} using SSH key...")
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        client.connect(
            HOST,
            username=USERNAME,
            key_filename=SSH_KEY_PATH,
            look_for_keys=True,
            timeout=10
        )
    except Exception as e:
        print(f"❌ SSH connection failed: {e}")
        return

    sftp = client.open_sftp()

    # 1️⃣ Download remote file
    with tempfile.NamedTemporaryFile(delete=False, mode="w+", encoding="utf-8") as tmp:
        print(f"📥 Downloading {REMOTE_PATH} ...")
        sftp.get(REMOTE_PATH, tmp.name)
        tmp.seek(0)
        original_content = tmp.read()

    print("\n───── Current File Content ─────")
    print(original_content)
    print("────────────────────────────────\n")

    # 2️⃣ Get new content interactively
    print("✏️  Enter new content (or press Enter to keep same):")
    print("(CTRL+D on Linux/macOS, CTRL+Z + Enter on Windows to finish)")
    print("-" * 50)
    try:
        new_content = sys.stdin.read()
    except KeyboardInterrupt:
        print("\n🚫 Cancelled.")
        client.close()
        return

    if not new_content.strip():
        print("⚠️ No new content entered. File left unchanged.")
        client.close()
        return

    # 3️⃣ Upload updated file
    with tempfile.NamedTemporaryFile(delete=False, mode="w", encoding="utf-8") as tmp_new:
        tmp_new.write(new_content)
        tmp_new_path = tmp_new.name

    print(f"📤 Uploading updated file to {REMOTE_PATH} ...")
    sftp.put(tmp_new_path, REMOTE_PATH)
    os.unlink(tmp_new_path)

    # 4️⃣ Reload Nginx
    print("🔄 Testing & reloading Nginx ...")
    stdin, stdout, stderr = client.exec_command("sudo nginx -t && sudo systemctl reload nginx")
    print(stdout.read().decode())
    print(stderr.read().decode())

    sftp.close()
    client.close()
    print("✅ Done!")

if __name__ == "__main__":
    edit_remote_file()
