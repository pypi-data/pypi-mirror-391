"""
Lineage CLI Commands
Provides commands to query lineage relationships
"""

import click
import json as json_module
from adxp_cli.auth.service import get_credential
from adxp_sdk.lineage import LineageClient
from adxp_sdk.auth.credentials import ApiKeyCredentials


def get_lineage_client():
    """Get initialized LineageClient"""
    headers, config = get_credential()
    
    credentials = ApiKeyCredentials(
        api_key=config.token,
        base_url=config.base_url
    )
    
    return LineageClient(
        credentials=credentials,
        base_url=config.base_url
    )


def print_lineage(lineage_data, title=""):
    """Print lineage data in a formatted way"""
    if not lineage_data:
        click.echo("No lineage relationships found.")
        return
    
    if title:
        click.secho(f"\n{title}", fg="cyan", bold=True)
        click.echo("=" * 80)
    
    for i, dep in enumerate(lineage_data, 1):
        click.echo(f"\n{i}. Relationship:")
        click.echo(f"   Source: {dep.get('source_type', 'Unknown')} ({dep.get('source_key', 'Unknown')})")
        click.echo(f"   Target: {dep.get('target_type', 'Unknown')} ({dep.get('target_key', 'Unknown')})")
        click.echo(f"   Action: {dep.get('action', 'Unknown')}")
        click.echo(f"   Depth: {dep.get('depth', 'Unknown')}")
    
    click.echo("")


@click.group("lineage")
def lineage_group():
    """Lineage commands to query object relationships"""
    pass


@lineage_group.command()
@click.argument('object_key')
@click.option('--direction', type=click.Choice(['downstream', 'upstream']), default='downstream', 
              help='Direction to traverse (default: downstream)')
@click.option('--action', type=click.Choice(['USE', 'CREATE']), default='USE', 
              help='Type of relationship to query (default: USE)')
@click.option('--max-depth', type=int, default=5, 
              help='Maximum depth to traverse (default: 5, min: 1, max: 10)')
@click.option('--json', is_flag=True, help='Output in JSON format')
def get(object_key, direction, action, max_depth, json):
    """
    Get lineage information for an object
    
    OBJECT_KEY: The object key (UUID or name, e.g., model UUID, deployment name, training ID)
    
    Examples:
        # Check downstream dependencies (what uses this object)
        adxp-cli lineage get model-uuid-123 --direction downstream
        
        # Check upstream dependencies (what this object uses)
        adxp-cli lineage get deployment-name --direction upstream
        
        # Use CREATE action instead of USE
        adxp-cli lineage get model-uuid-123 --action CREATE
        
        # Limit depth to 3
        adxp-cli lineage get model-uuid-123 --max-depth 3
    """
    try:
        client = get_lineage_client()
        
        # Validate max_depth
        if max_depth < 1 or max_depth > 10:
            click.secho("Error: max-depth must be between 1 and 10", fg="red")
            return
        
        result = client.get_lineage(
            object_key=object_key,
            direction=direction,
            action=action,
            max_depth=max_depth
        )
        
        if json:
            click.echo(json_module.dumps(result, indent=2))
        else:
            dir_label = "Downstream" if direction == "downstream" else "Upstream"
            title = f"[LINEAGE] {dir_label} dependencies for {object_key}"
            print_lineage(result, title=title)
        
    except Exception as e:
        error_msg = str(e)
        if "401" in error_msg or "Unauthorized" in error_msg:
            raise click.ClickException(
                "Unauthorized: Please login again. \n Run Either One of the Following Commands \n 1. adxp-cli auth login \n 2. adxp-cli auth refresh"
            )
        raise click.ClickException(f"Failed to get lineage: {e}")

