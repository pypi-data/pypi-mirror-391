import os
import datetime
from uthavu_tools.utils. ssh_clients import connect_to_prod_server, execute_ssh_command
# Assuming execute_ssh_command is also available via ssh_clients import
from typing import Optional

# --- CONFIGURATION (UPDATE THESE VALUES) ---
CONTAINER_NAME = "adangal-app-adangal_db-1"
DB_NAME = "Adangal"
DB_PASS = 'YourStrong!Pass123'  # CRITICAL: Use single quotes if your password contains '!'
REMOTE_BACKUP_HOST_DIR = "/opt/mssql/backup" # The host directory where the .bak file lands
LOCAL_BACKUP_PATH = os.path.expanduser("~/backups/adangal_sql") # Local path to save the backup
KEY_FILE = None # Set to None to use SSH Agent/Defaults
# -------------------------------------------

def perform_remote_sql_backup() -> Optional[str]:
    """
    Connects to the PROD server, executes SQL backup inside Docker, and downloads the file via SFTP.
    """
    
    # Generate timestamped filename
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    REMOTE_BACKUP_FILENAME = f"{DB_NAME}_{timestamp}.bak"
    
    # This is the path inside the container where the SQL engine saves the file
    REMOTE_CONTAINER_PATH = f"/var/opt/mssql/backup/{REMOTE_BACKUP_FILENAME}"
    # This is the corresponding host path for SFTP download
    REMOTE_HOST_PATH = f"{REMOTE_BACKUP_HOST_DIR}/{REMOTE_BACKUP_FILENAME}"
    LOCAL_FILE_PATH = os.path.join(LOCAL_BACKUP_PATH, REMOTE_BACKUP_FILENAME)

    # 1. Get SSH Client Instance
    ssh_client = connect_to_prod_server(private_key_path=KEY_FILE)
    if not ssh_client:
        return None

    try:
        # 2. Construct and Execute the Backup Command on the VPS
        # The command saves the file to the internal container path, which bind-mounts to REMOTE_BACKUP_HOST_DIR
        # Assuming you are using the structure from full_remote_backup.py
# --- INSIDE THE perform_remote_sql_backup function ---

# 1. Update the flags: Use -t (pseudo-TTY) but REMOVE -i (interactive)
# 2. Add the /bin/bash -c wrapper for reliable execution of the complex string.

        # --- INSIDE THE perform_remote_sql_backup function ---

# 1. Define the full command as a single, multi-line Python string.
        BACKUP_COMMAND = f"""
        sudo docker exec -t {CONTAINER_NAME} /opt/mssql-tools/bin/sqlcmd \
        -U sa \
        -P '{DB_PASS}' \
        -Q "BACKUP DATABASE {DB_NAME} TO DISK = N'{REMOTE_CONTAINER_PATH}' \
        WITH NOFORMAT, NOINIT, NAME = N'{DB_NAME}-Full', SKIP, NOREWIND, NOUNLOAD, STATS = 10"
        """

        # 2. Execute the command using the SSH utility method
        check_command = f"sudo docker exec adangal-app-adangal_db-1 /bin/bash -c 'test -f /opt/mssql-tools/bin/sqlcmd && echo OK || echo FAIL'"
        success, output, error = execute_ssh_command(ssh_client, check_command)

        if "FAIL" in output:
            print("\n🚨 CRITICAL ERROR: The SQL client tool (sqlcmd) is NOT installed in the container.")
            print("ACTION: You must modify the SQL Server Dockerfile to install 'mssql-tools' and redeploy the container.")
            return None # Exit the script
        success, output, error = execute_ssh_command(ssh_client, BACKUP_COMMAND)

        if not success:
            # Check for the specific error indicating sqlcmd is missing
            if "no such file or directory" in error:
                print("❌ CRITICAL ERROR: SQL Server client tools (sqlcmd) are missing from the container.")
                print("   ACTION: You must update the SQL Server Dockerfile to install 'mssql-tools' and redeploy the container.")
            else:
                print(f"❌ Backup FAILED on VPS. Error: {error}")
            return None

# If successful, the script proceeds to the download via SFTP (Step 3)
        print("✅ Database backup created successfully on VPS host.")
        
        # 3. Use SFTP to Download the Backup File
        if not os.path.exists(LOCAL_BACKUP_PATH):
            os.makedirs(LOCAL_BACKUP_PATH)
            
        print(f"\n⬇️ Starting secure file download of {REMOTE_BACKUP_FILENAME}...")
        
        sftp_client = ssh_client.open_sftp()
        sftp_client.get(REMOTE_HOST_PATH, LOCAL_FILE_PATH)
        sftp_client.close()
        
        print(f"🎉 SUCCESS: Backup saved locally at {LOCAL_FILE_PATH}")
        return LOCAL_FILE_PATH

    except Exception as e:
        print(f"An error occurred during file transfer or execution: {e}")
        return None
    finally:
        ssh_client.close()
        print("Connection closed.")

if __name__ == "__main__":
    perform_remote_sql_backup()