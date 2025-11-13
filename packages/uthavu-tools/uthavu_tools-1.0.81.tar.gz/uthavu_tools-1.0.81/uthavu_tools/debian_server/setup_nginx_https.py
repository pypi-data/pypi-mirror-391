import subprocess
import sys

# Server details
HOST = "72.60.97.244"   # your Debian server IP / domain
USER = "root"           # SSH user

def run_remote(cmd):
    """Run a remote SSH command and return exit code"""
    full_cmd = f"ssh {USER}@{HOST} {cmd}"
    print(f"👉 Running on {HOST}: {full_cmd}")
    result = subprocess.run(full_cmd, shell=True, text=True)
    return result.returncode

def main():
    print("🔒 SSL Certificate Setup via Certbot")

    domain = input("👉 Enter main domain (e.g. uthavu.com): ").strip()
    www_domain = input("👉 Enter www domain (e.g. www.uthavu.com): ").strip()

    if not domain or not www_domain:
        print("❌ Invalid input. Please provide both domain and www domain.")
        sys.exit(1)

    # Build certbot command
    cmd = f"sudo certbot --nginx -d {domain} -d {www_domain}"
    if run_remote(cmd) != 0:
        print("❌ Certbot command failed.")
        sys.exit(1)

    print("✅ SSL certificates installed & configured successfully 🚀")

if __name__ == "__main__":
    main()
