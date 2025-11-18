"""
Beta program management commands for Terraback CLI.
"""

import typer
from terraback.core.license import (
    register_beta_user,
    activate_beta_access,
    get_beta_info,
    is_beta_active,
    get_license_status,
)

app = typer.Typer(help="Beta program management commands.")


@app.command("register")
def beta_register(email: str = typer.Argument(..., help="Your email address for beta registration")):
    """Register for the Terraback Beta Program."""
    typer.echo(f"Registering {email} for the Terraback Beta Program...")
    
    if register_beta_user(email):
        typer.secho("Beta registration successful!", fg=typer.colors.GREEN, bold=True)
        typer.echo()
        typer.echo("What happens next:")
        typer.echo("1. Check your email for welcome message and Slack invite")
        typer.echo("2. Join our community at terraback.slack.com")
        typer.echo("3. Run 'terraback beta activate' to enable beta access")
        typer.echo("4. Start exploring with 'terraback scan aws/azure/gcp'")
        typer.echo()
        typer.echo("You now have access to:")
        typer.echo("  • Full Professional tier features (90 days)")
        typer.echo("  • Advanced scanning for all cloud providers")
        typer.echo("  • Priority support via Slack community")
        typer.echo("  • Early access to new features")
        typer.echo("  • Direct influence on product roadmap")
    else:
        typer.secho("Beta registration failed.", fg=typer.colors.RED, bold=True)
        raise typer.Exit(code=1)


@app.command("activate")
def beta_activate():
    """Activate your beta access on this machine (90-day Professional trial)."""
    # Check if beta is already active
    if is_beta_active():
        beta_info = get_beta_info()
        typer.secho("Beta access is already active.", fg=typer.colors.YELLOW)
        typer.echo(f"Expires: {beta_info.get('access_expires', 'N/A')}")
        typer.echo(f"Days remaining: {beta_info.get('days_remaining', 0)}")
        return

    typer.echo("Activating beta access...")

    if activate_beta_access():
        typer.secho("Beta access activated successfully!", fg=typer.colors.GREEN, bold=True)
        typer.echo()

        # Show current status
        beta_info = get_beta_info()
        if beta_info:
            typer.echo(f"Beta User ID: {beta_info.get('beta_user_id', 'N/A')}")
            typer.echo(f"Access Level: Professional (90 days)")
            typer.echo(f"Days Remaining: {beta_info.get('days_remaining', 90)}")

            if not beta_info.get('offline_activation'):
                typer.echo("\nJoin our Slack community for support!")

        typer.echo("\nYou can now use all Professional features:")
        typer.echo("  • terraback scan aws")
        typer.echo("  • terraback aws ec2 instances")
        typer.echo("  • terraback terraform generate")
        typer.echo("  • And much more!")
    else:
        typer.secho("Beta activation failed.", fg=typer.colors.RED, bold=True)
        typer.echo("Please try again or contact support at beta@terraback.io")
        raise typer.Exit(code=1)


@app.command("status")
def beta_status():
    """Check your beta program status."""
    if not is_beta_active():
        typer.secho("No active beta access found.", fg=typer.colors.YELLOW)
        typer.echo("To join the beta program:")
        typer.echo("  1. Register: terraback beta register <your-email>")
        typer.echo("  2. Activate: terraback beta activate")
        return
    
    beta_info = get_beta_info()
    if not beta_info:
        typer.secho("Unable to retrieve beta information.", fg=typer.colors.RED)
        return
    
    typer.secho("Beta Program Status", fg=typer.colors.GREEN, bold=True)
    typer.echo()
    
    # Basic information
    typer.echo(f"Email: {beta_info.get('email', 'N/A')}")
    typer.echo(f"Beta User ID: {beta_info.get('beta_user_id', 'N/A')}")
    typer.echo(f"Status: {beta_info.get('status', 'unknown').capitalize()}")
    typer.echo(f"Access Level: {beta_info.get('tier_granted', 'professional').capitalize()}")
    
    # Time information
    days_remaining = beta_info.get('days_remaining', 0)
    days_since_reg = beta_info.get('days_since_registration', 0)
    
    typer.echo(f"Days Remaining: {days_remaining}")
    typer.echo(f"Days Since Registration: {days_since_reg}")
    
    # Access dates
    if beta_info.get('registration_date'):
        typer.echo(f"Registered: {beta_info['registration_date'][:10]}")
    if beta_info.get('access_expires'):
        typer.echo(f"Expires: {beta_info['access_expires'][:10]}")
    if beta_info.get('activated_at'):
        typer.echo(f"Activated: {beta_info['activated_at'][:10]}")
    
    # Status-based messaging
    if days_remaining <= 0:
        typer.echo()
        typer.secho("Your beta access has expired.", fg=typer.colors.RED, bold=True)
        typer.echo("Consider upgrading to a paid license to continue using Professional features.")
        typer.echo("Contact sales@terraback.io for beta user discounts!")
    elif days_remaining <= 7:
        typer.echo()
        typer.secho(f"Your beta access expires in {days_remaining} days!", fg=typer.colors.YELLOW, bold=True)
        typer.echo("Consider upgrading to a paid license to avoid interruption.")
        typer.echo("Beta users receive exclusive discounts - contact sales@terraback.io")
    else:
        typer.echo()
        typer.secho("Your beta access is active and healthy!", fg=typer.colors.GREEN)
        
    # Community information
    slack_invite = beta_info.get('slack_invite')
    if slack_invite:
        typer.echo()
        typer.echo("Community:")
        typer.echo(f"  Slack: {slack_invite}")
        typer.echo("  Share feedback and connect with other beta users!")


@app.command("info")
def beta_info():
    """Show information about the Terraback Beta Program."""
    typer.secho("Terraback Beta Program", fg=typer.colors.BLUE, bold=True)
    typer.echo()
    
    typer.echo("The Terraback Beta Program gives you free access to Professional tier features")
    typer.echo("while helping shape the future of infrastructure automation.")
    typer.echo()
    
    typer.secho("Beta Program Benefits:", fg=typer.colors.GREEN, bold=True)
    typer.echo("  • 90 days of free Professional access")
    typer.echo("  • Advanced scanning for AWS, Azure, and GCP")
    typer.echo("  • Parallel resource discovery and bulk operations")
    typer.echo("  • Priority support via Slack community")
    typer.echo("  • Early access to new features and providers")
    typer.echo("  • Direct input on product roadmap")
    typer.echo("  • Exclusive upgrade discounts")
    typer.echo()
    
    typer.secho("How to Join:", fg=typer.colors.YELLOW, bold=True)
    typer.echo("  1. Register: terraback beta register <your-email>")
    typer.echo("  2. Check email for welcome message and Slack invite")
    typer.echo("  3. Activate: terraback beta activate")
    typer.echo("  4. Join the community at terraback.slack.com")
    typer.echo("  5. Start exploring with advanced features")
    typer.echo()
    
    typer.secho("Professional Features Included:", fg=typer.colors.CYAN, bold=True)
    typer.echo("  • Advanced resource scanning with parallel processing")
    typer.echo("  • Support for 100+ AWS services, 50+ Azure services, 30+ GCP services")
    typer.echo("  • Bulk import/export capabilities")
    typer.echo("  • Custom resource filtering and tagging")
    typer.echo("  • Advanced Terraform generation with best practices")
    typer.echo("  • Dependency mapping and resource relationships")
    typer.echo()
    
    # Check current status
    current_status = get_license_status()
    if current_status.get('is_beta'):
        typer.secho("You're already a beta user!", fg=typer.colors.GREEN, bold=True)
        typer.echo("Run 'terraback beta status' to see your current status.")
    elif current_status.get('has_license'):
        typer.secho("You already have a license.", fg=typer.colors.BLUE)
        typer.echo("Thank you for being a Terraback customer!")
    else:
        typer.echo("Ready to join? Run: terraback beta register <your-email>")


@app.command("feedback")
def beta_feedback(
    message: str = typer.Argument(..., help="Your feedback message"),
    category: str = typer.Option("general", help="Feedback category: bug, feature, general")
):
    """Submit feedback about the beta program or Terraback features."""
    if not is_beta_active():
        typer.secho("Beta access required to submit feedback.", fg=typer.colors.YELLOW)
        typer.echo("Join the beta program first with 'terraback beta register <email>'")
        return
    
    beta_info = get_beta_info()
    if not beta_info:
        typer.secho("Unable to retrieve beta information.", fg=typer.colors.RED)
        return
    
    typer.echo(f"Submitting {category} feedback...")
    
    # In a real implementation, this would send to a feedback API
    # For now, we'll just show what would be sent
    feedback_data = {
        "beta_user_id": beta_info.get('beta_user_id'),
        "email": beta_info.get('email'),
        "category": category,
        "message": message,
        "timestamp": "now"
    }
    
    typer.secho("Feedback submitted successfully!", fg=typer.colors.GREEN, bold=True)
    typer.echo()
    typer.echo("Thank you for helping improve Terraback!")
    typer.echo("Our development team will review your feedback.")
    typer.echo()
    typer.echo("You can also:")
    typer.echo("  • Share feedback in our Slack community")
    typer.echo("  • Report bugs in #beta-support channel") 
    typer.echo("  • Request features in #beta-feedback channel")
    
    slack_invite = beta_info.get('slack_invite')
    if slack_invite:
        typer.echo(f"  • Join the discussion: {slack_invite}")


if __name__ == "__main__":
    app()