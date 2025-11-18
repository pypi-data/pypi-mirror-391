import typer
from enode_quant.cli.login import login
from enode_quant.cli.logout import logout
from enode_quant.cli.whoami import whoami

app = typer.Typer(help="Enode Quant — CLI Tools")

app.command()(login)
app.command()(logout)
app.command()(whoami)
