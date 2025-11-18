import typer
from terraback.core.license import start_free_trial, is_trial_active, get_trial_info

app = typer.Typer(help="Free trial management")


@app.command("start")
def trial_start():
    """Start a free 30-day Professional trial if available."""
    if is_trial_active():
        info = get_trial_info()
        typer.secho("Trial is already active.", fg=typer.colors.YELLOW)
        typer.echo(f"Expires: {info.get('end_date', 'N/A')}")
        typer.echo(f"Days remaining: {info.get('days_remaining', 0)}")
        return
    if start_free_trial():
        typer.secho("Free trial activated!", fg=typer.colors.GREEN)
        info = get_trial_info()
        if info:
            typer.echo(f"Expires: {info.get('end_date', 'N/A')}")
            typer.echo(f"Days remaining: {info.get('days_remaining', 0)}")
    else:
        typer.secho("Could not start free trial.", fg=typer.colors.RED)
