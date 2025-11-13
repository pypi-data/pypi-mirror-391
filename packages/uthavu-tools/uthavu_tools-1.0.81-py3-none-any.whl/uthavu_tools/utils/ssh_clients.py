import paramiko
import os
from typing import Optional, Union, Tuple

# --- BASE CONNECTION FUNCTION ---

def _create_ssh_client(
    host: str,
    user: str,
    private_key_path: Optional[str],
    password: Optional[str] = None
) -> Optional[paramiko.SSHClient]:
    """Internal function to handle the Paramiko connection logic."""
    
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        print(f"\n🔐 Attempting SSH connection to {user}@{host}...")
        
        auth_params = {
            'hostname': host,
            'username': user,
            'timeout': 10
        }
        
        # Load key file if path is provided
        if private_key_path:
            key_path = os.path.expanduser(private_key_path)
            auth_params['key_filename'] = key_path
        elif password:
            auth_params['password'] = password

        ssh_client.connect(**auth_params)
        print(f"✅ SSH connection established to {host}.")
        return ssh_client

    except paramiko.AuthenticationException:
        print(f"❌ Authentication failed for {user}@{host}. Check key/password.")
        return None
    except paramiko.SSHException as e:
        print(f"❌ SSH error for {host}: {e}")
        return None
    except Exception as e:
        print(f"❌ Connection error for {host}: {e}")
        return None

# --- ENVIRONMENT-SPECIFIC UTILITIES ---

def connect_to_dev_server(private_key_path: str) -> Optional[paramiko.SSHClient]:
    """Connects to the Debian Development Server."""
    
    DEV_HOST = "dev2.kleer.ai"
    DEV_USER = "debian"
    
    return _create_ssh_client(DEV_HOST, DEV_USER, private_key_path)

def connect_to_prod_server(private_key_path: str) -> Optional[paramiko.SSHClient]:
    """Connects to the Production Server as root."""
    
    PROD_HOST = "72.60.97.244"
    PROD_USER = "root"
    
    return _create_ssh_client(PROD_HOST, PROD_USER, private_key_path)

# --- REUSABLE EXECUTION HELPER ---

def execute_ssh_command(ssh_client: paramiko.SSHClient, command: str) -> Tuple[bool, str, str]:
    """Executes a command on the remote host and returns status, stdout, and stderr."""
    
    print(f"\nExecuting command: {command}")
    
    # Use get_transport().open_session() for better error handling and execution
    try:
        channel = ssh_client.get_transport().open_session()
        channel.exec_command(command)
        
        # Read output streams
        output = channel.makefile('r', -1).read().decode().strip()
        error = channel.makefile_stderr('r', -1).read().decode().strip()
        
        # Get exit status
        exit_code = channel.recv_exit_status()
        success = exit_code == 0
        
        return success, output, error
    except Exception as e:
        return False, "", f"Execution Error: {e}"