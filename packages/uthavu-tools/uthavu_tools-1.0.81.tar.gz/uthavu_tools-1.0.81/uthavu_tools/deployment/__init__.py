import subprocess
import os
import click

@click.command()
@click.option("--path", default="/var/www/adangal", help="Path to app repo on server")
@click.option("--service", default="adangal-api", help="Backend systemd service name")
@click.option("--frontend", is_flag=True, help="Also deploy frontend (npm build)")
def aud(path, service, frontend):
    """
    Auto Update & Deploy (AUD)
    Pulls latest code and restarts services.
    """
    try:
        os.chdir(path)
        click.echo(f"📂 Switching to {path}")
        
        subprocess.run(["git", "fetch", "origin", "main"], check=True)
        subprocess.run(["git", "reset", "--hard", "origin/main"], check=True)

        if frontend:
            click.echo("⚡ Updating frontend...")
            subprocess.run(["npm", "install", "--omit=dev"], check=True)
            subprocess.run(["npm", "run", "build"], check=True)
            subprocess.run(["pm2", "restart", "adangal-frontend"], check=False)

        click.echo("⚡ Updating backend...")
        subprocess.run(["pip", "install", "-r", "requirements.txt"], check=True)
        subprocess.run(["systemctl", "restart", service], check=True)

        click.echo("✅ Deployment complete")

    except subprocess.CalledProcessError as e:
        click.echo(f"❌ Error: {e}")
