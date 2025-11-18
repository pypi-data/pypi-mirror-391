import typer
from enode_quant.config import (
    ensure_credentials_exist,
    get_api_url,
)
from enode_quant.client import run_query
from enode_quant.errors import (
    MissingCredentialsError,
    AuthenticationError,
    APIConnectionError,
)


def whoami():
    """
    Show information about the currently configured credentials.
    """

    # 1. Ensure credentials exist
    try:
        ensure_credentials_exist()
    except MissingCredentialsError:
        typer.echo("❌ Not logged in. Run `enode login`.")
        raise typer.Exit(1)

    api_url = get_api_url()

    typer.echo("🔎 Checking credentials for:")
    typer.echo(f"   {api_url}\n")

    # 2. Validate credentials
    try:
        run_query("SELECT 1;")
    except AuthenticationError:
        typer.echo("❌ Stored API key is invalid or expired.")
        typer.echo("   Run `enode login` to update credentials.")
        raise typer.Exit(1)
    except APIConnectionError:
        typer.echo("❌ Could not connect to the API endpoint.")
        typer.echo("   Check your network or API URL.")
        raise typer.Exit(1)
    except Exception:
        typer.echo("❌ Unexpected error while validating credentials.")
        raise typer.Exit(1)

    # 3. Success
    typer.echo("✅ You are logged in.")
    typer.echo(f"🔗 API endpoint: {api_url}")
    typer.echo("🔐 API key is valid and working.")
