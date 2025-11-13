from uthavu_tools.utils.ssh_clients import connect_to_prod_server, execute_ssh_command

# --- CONFIGURATION ---
# NOTE: We are intentionally setting the key path to None to rely on the agent/defaults.
KEY_FILE = None 
# ---------------------

def test_prod_connection_auto_key():
    """
    Attempts to connect to the production server (72.60.97.244) as 'root'
    by letting Paramiko automatically find the SSH key.
    """
    print("--- Starting Production Server Connection Test (Automatic Key Lookup) ---")
    
    # 1. Get the SSH Client Instance for the PROD server
    # The function now passes None for the key path.
    prod_ssh = connect_to_prod_server(private_key_path=KEY_FILE)

    if prod_ssh:
        try:
            # 2. Execute a verification command
            print("\nVerification Command: whoami && hostname")
            success, out, err = execute_ssh_command(prod_ssh, "whoami && hostname")
            
            # 3. Report results
            if success:
                print("✅ CONNECTION TEST SUCCESSFUL!")
                print(f"   Execution verified as: {out.splitlines()}")
                print(f"   Connection established to: {prod_ssh.get_transport().get_username()}")
            else:
                print("❌ Command execution failed on remote server.")
                print(f"   Error: {err}")
                
        finally:
            # 4. Close the connection
            prod_ssh.close()
            print("\nProduction connection closed.")
    else:
        print("\n❌ FAILED: Could not establish SSH connection.")
        print("   If this failed, ensure your key is loaded into your SSH agent (ssh-add) or is in ~/.ssh/id_rsa.")

if __name__ == "__main__":
    test_prod_connection_auto_key()