import subprocess
import click
import time

@click.command()
@click.option("--host", default="root@72.60.97.244", help="SSH host (e.g. user@ip)")
@click.option("--path", default="/var/www/adangal", help="Path to app repo on server")
@click.option("--a", "deploy_all", is_flag=True, help="Deploy both backend (API) and frontend")
@click.option("--fe", "deploy_fe", is_flag=True, help="Deploy frontend only")
@click.option("--be", "deploy_be", is_flag=True, help="Deploy backend (API) only")
@click.option("--verbose", is_flag=True, help="Show detailed logs (default is silent)")
def main(host, path, deploy_all, deploy_fe, deploy_be, verbose):
    """
    Auto Update & Deploy (AUD)
    SSH into server, pull latest code and restart services.
    """
    
    if not (deploy_all or deploy_fe or deploy_be):
        click.echo("⚠️  Please specify a flag: --a (all) | --fe (frontend) | --be (backend)")
        return
    
    click.echo(f"\n🚀 Starting deployment on {host}")
    click.echo("──────────────────────────────────────────────")
    
    # Base deploy commands
    commands = [
        f"cd {path}",
        "git fetch origin main",
        "git reset --hard origin/main",
        
    ]

    # Add frontend steps if requested
    if deploy_all or deploy_fe:
        commands.append(f"cd {path}/front-end && npm install --omit=dev && npm run build && pm2 restart adangal-frontend")
        
    # Backend deploy block
    if deploy_all or deploy_be:
        commands.append(f"cd {path}/back-end && pip3 install --break-system-packages --ignore-installed -r requirements.txt && pm2 restart adangal-api"
    )
    
     # If no flags passed, show a warning
    if not (deploy_all or deploy_fe or deploy_be):
        click.echo("⚠️  Please specify a flag:  --a  (all) | --fe  (frontend) | --be  (backend)")
        return

    # Join commands into one shell script
    remote_cmd = " && ".join(commands)
    
    # Step-by-step user feedback
    steps = []
    if deploy_all or deploy_fe:
        steps.append("🌐 Updating Frontend")
    if deploy_all or deploy_be:
        steps.append("⚙️  Updating Backend")
    steps.append("🔄 Restarting Services")
    
    for step in steps:
        click.echo(step)
        time.sleep(0.8)
        
    click.echo("📦 Pulling latest code from GitHub...")
    time.sleep(1)

    click.echo("🛠️  Deploying changes, please wait...")

    #click.echo(f"🚀 Deploying on {host}:{path}")
    
    if verbose:
        # Show full logs
        result = subprocess.run(["ssh", host, remote_cmd])
    else:
        # Run silently (no stdout/stderr)
        result = subprocess.run(
            ["ssh", host, remote_cmd],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

    if result.returncode == 0:
        click.echo("✅ Deployment complete.")
    else:
        click.echo("❌ Deployment failed!")
        if not verbose:
            click.echo("💡 Tip: Run again with `--verbose` to see full logs.")

    #ssh_command = ["ssh", host, remote_cmd if verbose else f"{remote_cmd} >/dev/null 2>&1"]
    # try:
    #     #subprocess.run(["ssh", host, remote_cmd], check=True)
    #     subprocess.run(ssh_command, check=True)
    #     click.echo("✅ Deployment complete")
    # except subprocess.CalledProcessError as e:
    #     click.echo("❌ Deployment failed!")
    #     if not verbose:
    #         click.echo("💡 Tip: Run again with `--verbose` to see full logs.")
    #     else:
    #         click.echo(f"Error details:\n{e}")


if __name__ == "__main__": 
    main()