import paramiko
import click

@click.command()
@click.option("--host", default="debian@dev2.kleer.ai", help="SSH host (e.g. user@ip)")
@click.option("--path", default="/home/debian/system/config/services/web/nginx/conf/app.conf", help="Full path to Nginx conf")
@click.option("--old", "use_old", is_flag=True, help="Use old route (frontend active)")
@click.option("--new", "use_new", is_flag=True, help="Use new route (backend active)")
def main(host, path, use_old, use_new):
    """
    Toggle Nginx proxy routes between frontend and backend.
    Example:
        python switch_nginx_route.py --old   # frontend active
        python switch_nginx_route.py --new   # backend active
    """
    if not (use_old or use_new):
        click.echo("⚠️  Please specify a flag:  --old  (frontend active) | --new  (backend active)")
        return

    click.echo(f"🔗 Connecting to {host} ...")

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname=host.split("@")[1], username=host.split("@")[0])

    sftp = ssh.open_sftp()
    with sftp.open(path, "r") as f:
        lines = f.readlines()

    new_lines = []
    app_server_updated = False
    
    for line in lines:
         # Frontend line (kleer_front)
        if "proxy_pass http://kleer_front:3000" in line:
            if use_new:
                # enable frontend
                line = "        proxy_pass http://kleer_front:3000/;\n"
            elif use_old:
                # disable frontend
                line = "        #proxy_pass http://kleer_front:3000/;\n"
        # Backend line (app_server)
        elif "proxy_pass http://appserver:8000" in line and not app_server_updated:
            if use_new:
                # disable backend
                line = "        #proxy_pass http://appserver:8000;\n"
            elif use_old:
                # enable backend
                line = "        proxy_pass http://appserver:8000;\n"
            app_server_updated = True
        new_lines.append(line)

    # Upload modified file
    backup_path = f"{path}.bak"
    ssh.exec_command(f"sudo cp {path} {backup_path}")
    with sftp.open(path, "w") as f:
        f.writelines(new_lines)

    click.echo("📝 Configuration updated and uploaded.")

    # Test & reload Nginx
    click.echo("🔍 Testing Nginx configuration...")
    stdin, stdout, stderr = ssh.exec_command("sudo nginx -t")
    output = stdout.read().decode() + stderr.read().decode()
    click.echo(output)

    if "test is successful" in output:
        click.echo("♻️  Reloading Nginx...")
        ssh.exec_command("sudo systemctl reload nginx")
        click.echo("✅ Nginx reloaded successfully!")
    else:
        click.echo("❌ Nginx test failed! Restoring backup...")
        ssh.exec_command(f"sudo mv {backup_path} {path}")
        
        
    # Restart Docker container
    click.echo("♻️  Restarting Nginx container (kleer-webserver-1) ...")
    stdin, stdout, stderr = ssh.exec_command("docker restart kleer-webserver-1")
    result = stdout.read().decode().strip()
    errors = stderr.read().decode().strip()

    if errors:
        click.echo(f"⚠️  Docker restart warning:\n{errors}")
    else:
        click.echo(f"✅ Container restarted successfully: {result}")


    sftp.close()
    ssh.close()

if __name__ == "__main__":
    main()
