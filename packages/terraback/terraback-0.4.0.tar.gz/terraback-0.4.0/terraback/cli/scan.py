from pathlib import Path
from typing import Optional

import typer

from terraback.cli import aws, azure, gcp
from terraback.core.license import require_professional, get_active_tier, Tier
from terraback.utils.scan_cache import get_scan_cache


def scan_all(
    provider: str,
    output_dir: Path = Path("generated"),
    profile: Optional[str] = None,
    region: Optional[str] = None,
    subscription_id: Optional[str] = None,
    project_id: Optional[str] = None,
    resource_group: Optional[str] = None,
    zone: Optional[str] = None,
    with_deps: bool = False,
    parallel: int = 1,
    check: bool = True,
    cache_ttl: int = 60,
):
    provider = provider.lower()
    from datetime import timedelta
    get_scan_cache(ttl=timedelta(minutes=cache_ttl))
    if parallel < 1:
        typer.echo("Warning: Parallel workers must be at least 1. Setting to 1.", err=True)
        parallel = 1
    elif parallel > 32:
        typer.echo("Warning: Limiting parallel workers to 32 for stability.", err=True)
        parallel = 32
    if parallel > 1:
        typer.secho(f"Parallel mode enabled with {parallel} workers", fg=typer.colors.BRIGHT_GREEN, bold=True)
    if with_deps:
        from terraback.core.license import check_feature_access
        if not check_feature_access(Tier.PROFESSIONAL):
            typer.echo("\nDependency scanning (--with-deps) requires a Professional license")
            typer.echo("Proceeding with independent scanning of each service...")
            typer.echo("To unlock dependency scanning: terraback license activate <key> or terraback trial start\n")
    if provider == "aws":
        aws.register()
        from terraback.cli.aws import scan_all_aws
        scan_all_aws(output_dir=output_dir, profile=profile, region=region, with_deps=with_deps, parallel=parallel, check=check)
    elif provider == "azure":
        azure.register()
        from terraback.cli.azure import scan_all_azure
        scan_all_azure(
            output_dir=output_dir,
            subscription_id=subscription_id,
            location=region,
            resource_group_name=resource_group,
            with_deps=with_deps,
            parallel=parallel,
            check=check,
        )
    elif provider == "gcp":
        gcp.register()
        from terraback.cli.gcp import scan_all_gcp
        scan_all_gcp(
            output_dir=output_dir,
            project_id=project_id,
            region=region,
            zone=zone,
            with_deps=with_deps,
            parallel=parallel,
            check=check,
        )
    else:
        typer.echo(f"Error: Unknown provider '{provider}'. Use 'aws', 'azure', or 'gcp'.", err=True)
        raise typer.Exit(code=1)


@require_professional
def scan_recursive(
    resource_type: str,
    output_dir: Path = Path("generated"),
    profile: Optional[str] = None,
    region: Optional[str] = None,
    subscription_id: Optional[str] = None,
    project_id: Optional[str] = None,
    zone: Optional[str] = None,
    use_cache: bool = True,
    cache_ttl: int = 60,
):
    from datetime import timedelta
    from terraback.utils.cross_scan_registry import base_recursive_scan
    resource_type_map = {
        'vm': 'azure_virtual_machine',
        'vms': 'azure_virtual_machine',
        'lb': 'azure_lb',
        'lbs': 'azure_lb',
        'rg': 'azure_resource_group',
        'rgs': 'azure_resource_group',
        'vnet': 'azure_virtual_network',
        'vpc': 'vpc',
        'subnet': 'azure_subnet',
        'subnets': 'azure_subnet',
        'nsg': 'azure_network_security_group',
        'nsgs': 'azure_network_security_group',
        'instance': 'ec2',
        'instances': 'ec2',
        'bucket': 's3_bucket',
        'buckets': 's3_bucket',
        'gcp_vm': 'gcp_instance',
        'gcp_vms': 'gcp_instance',
        'gcp_bucket': 'gcp_bucket',
        'gcp_buckets': 'gcp_bucket',
    }
    normalized_type = resource_type_map.get(resource_type.lower(), resource_type.lower())
    typer.echo(f"Starting Professional recursive scan for '{normalized_type}'...")
    is_azure = normalized_type.startswith('azure_')
    is_gcp = normalized_type.startswith('gcp_')
    if is_azure:
        azure.register()
    elif is_gcp:
        gcp.register()
    else:
        aws.register()
    kwargs = {'resource_type': normalized_type, 'output_dir': output_dir}
    if is_azure:
        from terraback.cli.azure.session import get_default_subscription_id
        if not subscription_id:
            subscription_id = get_default_subscription_id()
            if not subscription_id:
                typer.echo("Error: No Azure subscription found. Please run 'az login'", err=True)
                raise typer.Exit(code=1)
        kwargs['subscription_id'] = subscription_id
        kwargs['location'] = region
    elif is_gcp:
        from terraback.cli.gcp.session import get_default_project_id
        if not project_id:
            project_id = get_default_project_id()
            if not project_id:
                typer.echo("Error: No GCP project found. Please run 'gcloud config set project'", err=True)
                raise typer.Exit(code=1)
        kwargs['project_id'] = project_id
        kwargs['region'] = region
        kwargs['zone'] = zone
    else:
        from terraback.cli.common.defaults import get_aws_defaults
        defaults = get_aws_defaults()
        kwargs['profile'] = profile or defaults['profile']
        kwargs['region'] = region or defaults['region']
    if use_cache:
        cache = get_scan_cache(cache_dir=output_dir / '.terraback' / 'cache', ttl=timedelta(minutes=cache_ttl))
        typer.echo(f"Caching enabled (TTL: {cache_ttl} minutes)")
    base_recursive_scan(**kwargs)
    if use_cache:
        stats = cache.get_stats()
        typer.echo("\nCache Statistics:")
        typer.echo(f"  Hit Rate: {stats['hit_rate']}")
        typer.echo(f"  Cache Size: {stats['total_size_kb']} KB")


def check_auth() -> None:
    typer.echo("Checking cloud authentication status...\n")
    try:
        from terraback.cli.aws.session import get_boto_session
        session = get_boto_session()
        sts = session.client('sts')
        identity = sts.get_caller_identity()
        typer.echo("AWS: Authenticated")
        typer.echo(f"  Account: {identity['Account']}")
        typer.echo(f"  User/Role: {identity['Arn'].split('/')[-1]}")
        typer.echo(f"  Region: {session.region_name}")
    except Exception:
        typer.echo("AWS: Not authenticated (run: aws configure)")
    try:
        from terraback.cli.azure.session import get_default_subscription_id
        sub_id = get_default_subscription_id()
        if sub_id:
            typer.echo("\nAzure: Authenticated")
            typer.echo(f"  Subscription: {sub_id}")
        else:
            typer.echo("\nAzure: Not authenticated (run: az login)")
    except Exception:
        typer.echo("\nAzure: Not authenticated (run: az login)")
    try:
        from terraback.cli.gcp.session import get_default_project_id
        project_id = get_default_project_id()
        if project_id:
            typer.echo("\nGCP: Authenticated")
            typer.echo(f"  Project: {project_id}")
        else:
            typer.echo("\nGCP: Not authenticated (run: gcloud auth application-default login)")
    except Exception:
        typer.echo("\nGCP: Not authenticated (run: gcloud auth application-default login)")


def upgrade_info() -> None:
    current_tier = get_active_tier()
    if current_tier == Tier.COMMUNITY:
        typer.echo("Upgrade to Professional for Advanced Features\n")
        typer.echo("Your Current Plan: Community Edition (Free)")
        typer.echo("  - Unlimited core resources (EC2, VPC, S3, VMs, VNets, Storage)")
        typer.echo("  - Multi-cloud support (AWS, Azure, GCP)")
        typer.echo("  - Basic dependency mapping\n")
        typer.echo("Unlock with Migration Pass ($299 for 3 months):")
        typer.echo("  - Advanced AWS services (RDS, Lambda, EKS, ALB, Route53, etc.)")
        typer.echo("  - Recursive dependency scanning (--with-deps)")
        typer.echo("  - Multi-account/subscription support")
        typer.echo("  - Priority email support")
        typer.echo("  - Advanced caching and performance features\n")
        typer.echo("Get Migration Pass: https://terraback.io/pricing")
        typer.echo("Enterprise needs: sales@terraback.io")
        typer.echo("\nOr start your free 30-day trial: terraback trial start")
    elif current_tier == Tier.PROFESSIONAL:
        typer.secho("You have Professional access!", fg=typer.colors.GREEN, bold=True)
        typer.echo("All advanced features are unlocked.")
    elif current_tier == Tier.ENTERPRISE:
        typer.secho("You have Enterprise access!", fg=typer.colors.GREEN, bold=True)
        typer.echo("All features including enterprise support are available.")
