import os
import datetime
import paramiko
from uthavu_tools.utils.ssh_clients import connect_to_prod_server
from typing import Optional

# --- CONFIGURATION (UPDATE THESE VALUES) ---
REMOTE_BACKUP_HOST_DIR = "/opt/mssql/data" # The VPS directory containing the .bak files
LOCAL_BACKUP_PATH = os.path.expanduser("~/backups/adangal_sql/restorable") # Local path to save the backup
DB_NAME = "Adangal" # Used for filtering the filename (optional)
KEY_FILE = None # Set to None to use SSH Agent/Defaults
# -------------------------------------------

def download_latest_db_file() -> Optional[str]:
    """
    Connects to the PROD server, finds the latest .bak file, and downloads it via SFTP.
    """
    
    ssh_client = connect_to_prod_server(private_key_path=KEY_FILE)
    if not ssh_client:
        return None

    try:
        # 1. FIND THE LATEST BACKUP FILE NAME ON THE VPS
        print("\n1. Searching for latest backup file on VPS...")
        
        # Use Bash to list files, sort by modified time, and pick the last (newest) one
        # Filters for files starting with 'Adangal_' and ending with '.bak'
        find_latest_cmd = f"""
        ls -t {REMOTE_BACKUP_HOST_DIR}/{DB_NAME}.mdf | head -n 1
        """
        
        stdin, stdout, stderr = ssh_client.exec_command(find_latest_cmd)
        
        # The output is the full path of the newest file
        remote_file_path = stdout.read().decode().strip()
        error = stderr.read().decode().strip()

        if error or not remote_file_path or "No such file" in error:
            print(f"❌ Could not find backup file in {REMOTE_BACKUP_HOST_DIR}. Error: {error}")
            return None
            
        remote_filename = os.path.basename(remote_file_path)
        LOCAL_FILE_PATH = os.path.join(LOCAL_BACKUP_PATH, remote_filename)
        
        print(f"   Found file: {remote_filename}")

        # 2. DOWNLOAD THE FILE VIA SFTP
        if not os.path.exists(LOCAL_BACKUP_PATH):
            os.makedirs(LOCAL_BACKUP_PATH)
            
        print(f"\n2. Starting secure file download to {LOCAL_BACKUP_PATH}...")
        
        sftp_client = ssh_client.open_sftp()
        sftp_client.get(remote_file_path, LOCAL_FILE_PATH)
        sftp_client.close()
        
        print(f"🎉 SUCCESS: File downloaded locally at {LOCAL_FILE_PATH}")
        return LOCAL_FILE_PATH

    except Exception as e:
        print(f"An error occurred during file transfer or execution: {e}")
        return None
    finally:
        if ssh_client:
            ssh_client.close()

if __name__ == "__main__":
    download_latest_db_file()