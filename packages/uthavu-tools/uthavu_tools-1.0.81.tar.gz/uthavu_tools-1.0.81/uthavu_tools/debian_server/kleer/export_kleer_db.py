import os
import sys
import paramiko
from scp import SCPClient
from datetime import datetime

# --- Configuration ---
REMOTE_HOST = "dev2.kleer.ai"
REMOTE_USER = "debian"
SSH_KEY_PATH = r"C:\Users\Jawahar\.ssh\id_rsa"  # Your private key
CONTAINER_NAME = "services-database-1"
DB_NAME = "demo"
DB_USER = "root"
DB_PASSWORD = "fgL<]~WUD:@CU8ZX?j@@2Ku2x"

REMOTE_BACKUP_PATH = f"/home/debian/bya_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.sql"
LOCAL_DEST_DIR = r"C:\Users\Jawahar\Downloads"

# --- Progress display callback ---
def progress(filename, size, sent):
    # size and sent are in bytes
    if size == 0:
        percent = 0
    else:
        percent = float(sent) / float(size) * 100

    # Create a simple progress bar
    bar_length = 40
    filled_length = int(bar_length * percent / 100)
    bar = "█" * filled_length + "-" * (bar_length - filled_length)
    sys.stdout.write(
        f"\r⬇️  Downloading {os.path.basename(filename)} |{bar}| {percent:6.2f}% ({sent/1024/1024:.2f}/{size/1024/1024:.2f} MB)"
    )
    sys.stdout.flush()

def create_ssh_client(host, user, key_path):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname=host, username=user, key_filename=key_path)
    return ssh

def main():
    print(f"🚀 Connecting to {REMOTE_HOST} via SSH key ...")
    ssh = create_ssh_client(REMOTE_HOST, REMOTE_USER, SSH_KEY_PATH)

    dump_cmd = (
        f"docker exec -e PGPASSWORD='{DB_PASSWORD}' -i {CONTAINER_NAME} "
        f"pg_dump -U {DB_USER} -d {DB_NAME} > {REMOTE_BACKUP_PATH}"
    )

    print("📦 Running database dump inside Docker container...")
    stdin, stdout, stderr = ssh.exec_command(dump_cmd)
    exit_code = stdout.channel.recv_exit_status()

    if exit_code == 0:
        print(f"✅ Database dump created at {REMOTE_BACKUP_PATH}")
    else:
        print("❌ Dump failed!")
        print(stderr.read().decode())
        ssh.close()
        return

    print("\n⬇️  Starting file download...\n")
    local_file_path = os.path.join(LOCAL_DEST_DIR, os.path.basename(REMOTE_BACKUP_PATH))

    with SCPClient(ssh.get_transport(), progress=progress) as scp:
        scp.get(REMOTE_BACKUP_PATH, local_file_path)

    print(f"\n✅ File downloaded successfully to {local_file_path}")

    # Optional: delete remote file
    # ssh.exec_command(f"rm -f {REMOTE_BACKUP_PATH}")
    # print("🧹 Remote dump file deleted.")

    ssh.close()
    print("🎉 Done!")

if __name__ == "__main__":
    main()
