import subprocess
import sys

# Server details
HOST = "72.60.97.244"   # Debian server
USER = "root"           # SSH user
NGINX_SITES_AVAILABLE = "/etc/nginx/sites-available"
NGINX_SITES_ENABLED = "/etc/nginx/sites-enabled"

# Inline Nginx template with HTTPS + proxy
NGINX_TEMPLATE = """
server {
    listen 80;
    server_name {DOMAIN} www.{DOMAIN};

    location / {
        proxy_pass http://127.0.0.1:{PORT};
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
"""

def run_remote(cmd):
    """Run a remote SSH command and return exit code"""
    full_cmd = f"ssh {USER}@{HOST} {cmd}"
    print(f"👉 Running on {HOST}: {full_cmd}")  
    result = subprocess.run(full_cmd, shell=True, text=True)
    return result.returncode

def create_remote_config(domain, port):
    config_content = NGINX_TEMPLATE.replace("{DOMAIN}", domain).replace("{PORT}", str(port))
    remote_conf_path = f"{NGINX_SITES_AVAILABLE}/{domain}.conf"
    remote_enabled_path = f"{NGINX_SITES_ENABLED}/{domain}.conf"

    # Step 1: Pipe the config content to tee (works from Windows too)
    cmd = f"type nul | ssh {USER}@{HOST} \"sudo tee {remote_conf_path} > /dev/null\""
    process = subprocess.Popen(["ssh", f"{USER}@{HOST}", f"sudo tee {remote_conf_path} > /dev/null"], 
                               stdin=subprocess.PIPE, text=True)
    process.communicate(input=config_content)
    if process.returncode != 0:
        print("❌ Failed to write config file on server.")
        sys.exit(1)

    # Step 2: Create symlink
    cmd = f"ssh {USER}@{HOST} \"sudo ln -sf {remote_conf_path} {remote_enabled_path}\""
    subprocess.run(cmd, shell=True, text=True, check=True)

    print(f"✅ Config created for {domain} and enabled.")


def main():
    print("🌐 Remote Nginx Config Generator")

    domain = input("👉 Enter domain name (e.g. test.uthavu.com): ").strip()
    port = input("👉 Enter port number (e.g. 8080): ").strip()

    if not domain or not port.isdigit():
        print("❌ Invalid input. Please provide a domain and numeric port.")
        sys.exit(1)

    # Step 1: Create remote config
    create_remote_config(domain, port)

    # Step 2: Test nginx configuration
    if run_remote("sudo nginx -t") != 0:
        print("❌ Nginx configuration test failed. Not reloading.")
        sys.exit(1)

    # Step 3: Reload nginx
    if run_remote("sudo systemctl reload nginx") != 0:
        print("❌ Failed to reload Nginx.")
        sys.exit(1)

    print("✅ Config for", domain, "added and Nginx reloaded successfully 🚀")
    print(f"👉 Next: Run certbot to enable SSL:\n   sudo certbot --nginx -d {domain} -d www.{domain}")

if __name__ == "__main__":
    main()
