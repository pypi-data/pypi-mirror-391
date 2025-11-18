import typer
from enode_quant.config import set_credentials, delete_credentials
from enode_quant.client import run_query
from enode_quant.errors import (
    AuthenticationError,
    APIConnectionError,
    InvalidQueryError,
    MissingCredentialsError,
)

app = typer.Typer()


def login():
    """
    Interactive login command.

    Prompts the user for:
        - API URL
        - API Key (hidden input)

    Workflow:
        1) Accept user input
        2) Validate basic formatting
        3) Store credentials temporarily
        4) Test them via run_query("SELECT 1;")
        5) Roll back on failure
        6) On success → persist credentials

    This command never prints stack traces, only human-friendly messages.
    """

    typer.echo("🔐 Enode Quant — Login\n")

    # ------------------------
    # 1. Prompt user input
    # ------------------------
    api_url = typer.prompt("API URL").strip()
    api_key = typer.prompt("API Key", hide_input=True).strip()

    # ------------------------
    # 2. Validate basic URL shape
    # ------------------------
    if not api_url.lower().startswith(("http://", "https://")):
        typer.echo("❌ API URL must start with http:// or https://")
        raise typer.Exit(code=1)

    if len(api_key) == 0:
        typer.echo("❌ API Key cannot be empty.")
        raise typer.Exit(code=1)

    # ------------------------
    # 3. Store credentials temporarily
    # ------------------------
    set_credentials(api_url, api_key)
    typer.echo("🔎 Validating credentials...")

    # ------------------------
    # 4. Test credentials via run_query
    # ------------------------
    try:
        run_query("SELECT 1;")
    except AuthenticationError:
        delete_credentials()
        typer.echo("❌ Invalid API key.")
        raise typer.Exit(code=1)
    except APIConnectionError:
        delete_credentials()
        typer.echo("❌ Could not connect to API endpoint.")
        raise typer.Exit(code=1)
    except InvalidQueryError:
        delete_credentials()
        typer.echo("❌ Server rejected validation query.")
        raise typer.Exit(code=1)
    except Exception:
        delete_credentials()
        typer.echo("❌ Unexpected error during login.")
        raise typer.Exit(code=1)

    # ------------------------
    # 5. Success
    # ------------------------
    typer.echo(f"✅ Logged in successfully!")
    typer.echo(f"🔗 API endpoint: {api_url}")
