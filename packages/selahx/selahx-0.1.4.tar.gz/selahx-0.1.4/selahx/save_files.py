import typer
import subprocess
from pathlib import Path

def copy_ec2(
    key_file: str,
    ec2_user: str,
    ec2_host: str,
    local_dest: str
):
    Path(local_dest).mkdir(parents=True, exist_ok=True)
    subprocess.run(["chmod", "400", key_file], check=True)
    rsync_cmd = [
        "rsync",
        "-avz",
        "-e", f"ssh -i {key_file}",
        "--exclude=.bash*",
        "--exclude=.profile",
        "--exclude=.sudo_as_admin_successful",
        "--exclude=.cache",
        "--exclude=.ssh",
        "--exclude=.npm",
        "--exclude=.local",
        "--exclude=venv",
        "--exclude=*.py",
        "--exclude=*.sh",
        f"{ec2_user}@{ec2_host}:/home/{ec2_user}/",
        local_dest
    ]
    subprocess.run(rsync_cmd, check=True)
    print(f"Files copied to {local_dest}")
