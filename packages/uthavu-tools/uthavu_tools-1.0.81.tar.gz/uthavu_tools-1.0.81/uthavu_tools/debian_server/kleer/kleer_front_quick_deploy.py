import paramiko
import time
import sys
# getpass is no longer needed since we are not prompting for a password

# --- Configuration ---
REMOTE_HOST = 'dev2.kleer.ai' 
REMOTE_USER = 'debian'
# ---

def execute_remote_command_realtime_pty(command_to_run):
    """
    Connects using SSH keys (non-interactive), requests a Pty, executes the 
    command, and prints output in real-time.
    """
    ssh = None
    
    try:
        print(f"\n🔐 Connecting to {REMOTE_USER}@{REMOTE_HOST} using SSH Keys...")
        
        # Initialize and Connect SSH Client
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        # Connect using key authentication:
        ssh.connect(
            hostname=REMOTE_HOST, 
            username=REMOTE_USER,
            look_for_keys=True,  # Look in standard key locations (~/.ssh/)
            allow_agent=True,    # Use the local SSH Agent if a key is loaded
            timeout=10
        )
        print("✅ Connection established.")

        # 2. Setup Channel and PTY
        transport = ssh.get_transport()
        channel = transport.open_session()
        
        # Request a Pseudo-Terminal (Pty) to resolve buffering issues
        channel.get_pty() 
        
        # 3. Execute the Command
        # Use stdbuf -oL for extra assurance against buffering
        full_remote_command = f"cd /home/{REMOTE_USER}/system/kleer_front/scripts && stdbuf -oL {command_to_run}"
        print(f"▶️ Executing command with Pty: '{full_remote_command}'")
        
        channel.exec_command(full_remote_command)
        
        print("\n--- Real-Time Remote Output ---")

        # 4. Read Output in Real-Time (Non-Blocking Loop)
        exit_status = -1
        
        while True:
            # Read available data from STDOUT
            if channel.recv_ready():
                sys.stdout.write(channel.recv(1024).decode('utf-8', errors='ignore'))
                sys.stdout.flush()

            # Read available data from STDERR
            if channel.recv_stderr_ready():
                sys.stderr.write(channel.recv_stderr(1024).decode('utf-8', errors='ignore'))
                sys.stderr.flush()

            # Check if the command has finished
            if channel.exit_status_ready():
                exit_status = channel.recv_exit_status() 
                
                # Read any remaining output before breaking
                while channel.recv_ready() or channel.recv_stderr_ready():
                    if channel.recv_ready():
                        sys.stdout.write(channel.recv(1024).decode('utf-8', errors='ignore'))
                    if channel.recv_stderr_ready():
                        sys.stderr.write(channel.recv_stderr(1024).decode('utf-8', errors='ignore'))
                    sys.stdout.flush()
                break
                
            time.sleep(0.05) 

        # 5. Check Exit Status
        print("\n---")
        if exit_status == 0:
            print("✅ Command execution **COMPLETED SUCCESSFULLY** (Exit Status: 0)")
        else:
            print(f"❌ Command execution **FAILED** (Exit Status: {exit_status})")
            
        print(f"Final Exit Status: {exit_status}")

    except paramiko.AuthenticationException:
        print("❌ Authentication failed. Check your SSH keys and permissions on the server.")
    except paramiko.SSHException as e:
        print(f"❌ Could not establish SSH session or execute command: {e}")
    except Exception as e:
        print(f"❌ An unexpected error occurred: {e}")
    finally:
        # 6. Close the Connection
        if ssh:
            ssh.close()
            print("Connection closed.")

# --- Execute the Function ---
def main():
    TARGET_COMMAND = 'bash deploy_front.sh' 
    execute_remote_command_realtime_pty(TARGET_COMMAND)
    
if __name__ == "__main__":
    main()