import typer
from enode_quant.config import delete_credentials
from enode_quant.errors import MissingCredentialsError
from enode_quant.config import ensure_credentials_exist


def logout():
    """
    Logout command.

    Removes stored API credentials from ~/.enode_quant/.

    Behaviors:
    - If credentials exist → delete them and print success.
    - If credentials do NOT exist → inform user gracefully.
    """
    try:
        ensure_credentials_exist()
    except MissingCredentialsError:
        typer.echo("ℹ️  You are already logged out. No credentials found.")
        raise typer.Exit(code=0)

    # Delete credentials
    delete_credentials()
    typer.echo("✅ Logged out. Credentials removed.")
