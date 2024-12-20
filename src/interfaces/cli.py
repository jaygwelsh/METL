# src/interfaces/cli.py

import click
import os
from core.metadata import MetadataEngine
from core.rbac import check_permission
from utils.logger import get_logger
from utils.auth import authenticate_user

logger = get_logger(__name__)

@click.group()
@click.option('--token', prompt='User Token', help='Authentication token to determine user role.')
@click.pass_context
def cli(ctx, token):
    user_info = authenticate_user(token)
    ctx.ensure_object(dict)
    ctx.obj['role'] = user_info['role']

    # Initialize engine and keys
    ctx.obj['engine'] = MetadataEngine()
    ctx.obj['private_key'] = ctx.obj['engine'].load_private_key()
    ctx.obj['public_key'] = ctx.obj['engine'].load_public_key()

@cli.command()
@click.argument('file_path')
@click.option('--policy', default=None, help='Policy to apply to metadata')
@click.pass_context
def embed(ctx, file_path, policy):
    """Embed metadata by creating a sidecar JSON file."""
    if not check_permission(ctx.obj['role'], 'embed'):
        click.echo("Permission denied. You do not have embed rights.")
        return
    if not os.path.exists(file_path):
        click.echo("File not found.")
        return

    engine = ctx.obj['engine']
    with open(file_path, "r", errors='ignore') as f:
        content = f.read()
    suggestions = engine.suggest_metadata(content)
    signed_meta = engine.embed_metadata(file_path, suggestions, ctx.obj['private_key'])
    if signed_meta:
        click.echo("Metadata embedded successfully.")
    else:
        click.echo("Failed to embed metadata.")

@cli.command()
@click.argument('file_path')
@click.pass_context
def verify(ctx, file_path):
    """Verify metadata from the sidecar JSON file."""
    if not check_permission(ctx.obj['role'], 'verify'):
        click.echo("Permission denied. You do not have verify rights.")
        return
    if not os.path.exists(file_path):
        click.echo("File not found.")
        return

    engine = ctx.obj['engine']
    verified = engine.verify_metadata(file_path, ctx.obj['public_key'])
    if verified:
        click.echo("Metadata verified successfully.")
    else:
        click.echo("Metadata verification failed.")

if __name__ == '__main__':
    cli()
