import typer
from .server import server_cli
from .client import client_cli
from .save_files import copy_ec2

# Main CLI app
app = typer.Typer(
    help="selahx — Remote Access Tool — Fast and lightweight CLI experience.",
    add_completion=False
)

# ---------------------------
# Server command
# ---------------------------
@app.command("server", help="Start the selahx server.")
def run_server(
    host: str = typer.Option("0.0.0.0", "--host", help="Host for the server (default: listen on all interfaces)"),
    key_file: str = typer.Option(..., "--key-file", help="Path to the temporary SSH private key"),
    port: int = typer.Option(..., "--port", help="Local port for the server"),
    ssh_host: str = typer.Option(..., "--ssh-host", help="SSH host (e.g. ubuntu@ec2-instance)")
):
    """
    Launch the selahx server which listens for client connections and establishes
    a reverse SSH tunnel automatically once a client connects.
    """
    typer.secho(f"[SERVER] Starting on {host}:{port}", fg=typer.colors.GREEN)
    typer.secho(f"[SERVER] Using SSH key: {key_file}", fg=typer.colors.YELLOW)
    typer.secho(f"[SERVER] Will connect to SSH host: {ssh_host}", fg=typer.colors.CYAN)
    server_cli(host=host, port=port, key_file=key_file, ssh_host=ssh_host)


# ---------------------------
# Client command
# ---------------------------
@app.command("client", help="Start the selahx client.")
def run_client(
    username: str = typer.Option(..., "--username", help="Username for the client session"),
    port: int = typer.Option(..., "--port", help="Server port to connect to")
):
    """
    Launch the selahx client which connects to the server and sets up communication
    over the specified port.
    """
    typer.secho(f"[CLIENT] Starting as user '{username}'", fg=typer.colors.GREEN)
    typer.secho(f"[CLIENT] Connecting to server port {port}", fg=typer.colors.CYAN)
    client_cli(username=username, port=port)


# ---------------------------
# Save files from EC2 to Local
# ---------------------------
@app.command("save", help="Copy EC2 home directory to local machine")
def copy_ec2_command(
    key: str = typer.Option(..., "--key-file", "-k", help="Path to PEM SSH private key"),
    user: str = typer.Option(..., "--user", "-u", help="EC2 username (e.g., ubuntu)"),
    host: str = typer.Option(..., "--host", "-h", help="EC2 host (e.g., ec2-xx-xxx-xxx-xx.compute-1.amazonaws.com)"),
    dest: str = typer.Option(..., "--dest", "-d", help="Local destination directory")
):
    copy_ec2(key_file=key, ec2_user=user, ec2_host=host, local_dest=dest)


# Entry point
if __name__ == "__main__":
    app()