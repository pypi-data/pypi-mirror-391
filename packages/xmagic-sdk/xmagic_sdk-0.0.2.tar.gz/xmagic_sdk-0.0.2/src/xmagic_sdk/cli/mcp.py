import os
import subprocess
import click
import asyncio
from typing import Optional, Dict
from pathlib import Path
import bson

from xmagic_sdk.mcp.mcp_api import run_mcp_server
from xmagic_sdk.mcp.deploy_mcp import (
    deploy_and_monitor,
    list_mcp_server_deployments,
    delete_mcp_server_deployment,
    stop_mcp_server_deployment,
    stream_mcp_server_deployment_logs,
    get_mcp_server_deployment_status,
    get_mcp_server_deployment_logs,
    update_mcp_server_deployment,
    validate_mcp_server_code,
    _format_logs_for_display,
)
from xmagic_sdk.utils.config_utils import get_api_key
from xmagic_sdk.config import Config


def validate_deployment_id(deployment_id: str) -> bool:
    """
    Validate if the provided string is a valid BSON ObjectID.

    Args:
        deployment_id: The deployment ID to validate

    Returns:
        True if valid, False otherwise
    """
    try:
        bson.ObjectId(deployment_id)
        return True
    except:
        return False


@click.group(name="mcp")
def mcp_command():
    """Manage MCP (Model Context Protocol) servers"""
    pass


@mcp_command.command(name="run")
@click.option(
    "-f",
    "--entry-point-file-path",
    type=click.Path(exists=True, file_okay=True),
    required=True,
    help="Path to the entry point file (your MCP server script)",
)
@click.option(
    "--port",
    default=8000,
    type=int,
    help="Port to run the server on (default: 8000)",
)
@click.option(
    "--cloud",
    is_flag=True,
    help="Deploy to cloud instead of running locally",
)
@click.option(
    "-n",
    "--name",
    help="Name for cloud deployment (auto-generated if not provided)",
)
@click.option(
    "-d",
    "--code-directory",
    type=click.Path(exists=True, file_okay=False, dir_okay=True),
    help="Path to code directory (required for cloud deployment)",
)
@click.option(
    "--description",
    help="Description of the MCP server",
)
@click.option(
    "--show-logs/--no-show-logs",
    default=True,
    help="Show logs after cloud deployment (default: True)",
)
@click.option(
    "--ram",
    type=float,
    default=0.5,
    help="RAM allocation in GB for cloud deployment (default: 0.5)",
)
@click.option(
    "--cpu",
    type=int,
    default=500,
    help="CPU allocation in millicores for cloud deployment (default: 500)",
)
@click.option(
    "--replicas",
    type=int,
    default=1,
    help="Number of replicas for cloud deployment (default: 1)",
)
@click.option(
    "--env-var",
    "-e",
    multiple=True,
    help="Environment variable in format KEY=VALUE (can be used multiple times)",
)
@click.option(
    "--secret-env-var",
    "-s",
    multiple=True,
    help="Secret environment variable in format KEY=VALUE (can be used multiple times)",
)
@click.option(
    "--docker-image",
    default="python:3.11",
    help="Docker image to use (default: python:3.11)",
)
@click.option(
    "--command",
    multiple=True,
    help="Override container entrypoint command (can be used multiple times)",
)
@click.option(
    "--args",
    multiple=True,
    help="Override container args (can be used multiple times)",
)
@click.option(
    "--health-path",
    default="/v1/health",
    help="Health check endpoint path (default: /v1/health)",
)
@click.option(
    "--code-mount-path",
    default="/code",
    help="Path to mount code in container (default: /code)",
)
def run_command(
    entry_point_file_path: str,
    port: int,
    cloud: bool,
    name: Optional[str],
    code_directory: Optional[str],
    description: Optional[str],
    show_logs: bool,
    ram: float,
    cpu: int,
    replicas: int,
    env_var: tuple,
    secret_env_var: tuple,
    docker_image: str,
    command: tuple,
    args: tuple,
    health_path: str,
    code_mount_path: str,
):
    """
    Run an MCP server locally or deploy to cloud.

    Examples:

    \b
    # Run locally (default)
    xmagic mcp run -p "My MCP server"

    \b
    # Run locally on custom port
    xmagic mcp run -p "My MCP server" --port 9000

    \b
    # Deploy to cloud with auto-generated name
    xmagic mcp run -p "My MCP server" --cloud -d ./my_mcp_code

    \b
    # Deploy to cloud with specific name
    xmagic mcp run -p "My MCP server" --cloud -n my-server -d ./my_mcp_code

    \b
    # Deploy to cloud with custom resources
    xmagic mcp run -p "My MCP server" --cloud -d ./code --ram 1.0 --cpu 1000 --replicas 2
    """
    if cloud:
        xchat_api_key = get_api_key()

        if not xchat_api_key:
            click.secho(
                "[!] API key not found. Please configure your API key using the 'xmagic configure' command.",
                fg="red",
                bold=True,
            )
            return

    if not entry_point_file_path and not code_directory:
        click.secho(
            "[!] Either --entry-point-file-path or --code-directory is required",
            fg="red",
            bold=True,
        )
        return

    if not entry_point_file_path and code_directory:
        # Make sure a mcp_server.py file exists in the code directory
        entry_point_file_path = str(Path(code_directory) / "mcp_server.py")
        if not Path(entry_point_file_path).exists():
            click.secho(
                "[!] Could not find 'mcp_server.py' in the code directory",
                fg="red",
                bold=True,
            )
            return

    if cloud and not code_directory:
        if entry_point_file_path:
            click.secho(
                f"[*] Inferring code directory from entry point file: {entry_point_file_path}",
                fg="cyan",
                bold=True,
            )
            code_directory = str(Path(entry_point_file_path).parent)

        if not code_directory:
            click.secho(
                "[!] --code-directory is required for cloud deployment",
                fg="red",
                bold=True,
            )
            return

    # Parse environment variables from tuples to dict
    env_vars = {}
    if env_var:
        for ev in env_var:
            if "=" in ev:
                key, value = ev.split("=", 1)
                env_vars[key] = value
            else:
                click.secho(
                    f"[!] Invalid environment variable format: {ev}. Use KEY=VALUE",
                    fg="red",
                    bold=True,
                )
                return

    secret_env_vars = {}
    if secret_env_var:
        for sev in secret_env_var:
            if "=" in sev:
                key, value = sev.split("=", 1)
                secret_env_vars[key] = value
            else:
                click.secho(
                    f"[!] Invalid secret environment variable format: {sev}. Use KEY=VALUE",
                    fg="red",
                    bold=True,
                )
                return

    # Convert tuples to lists or None
    command_list = list(command) if command else None
    args_list = list(args) if args else None

    try:
        if cloud:
            click.secho(
                f"[*] Deploying MCP server to cloud...",
                fg="cyan",
                bold=True,
            )
        else:
            click.secho(
                f"[*] Starting MCP server locally on port {port}...",
                fg="cyan",
                bold=True,
            )

        if cloud:
            asyncio.run(
                deploy_and_monitor(
                    xchat_api_key=xchat_api_key,
                    name=name,  # Can be None, will auto-generate
                    code_directory=code_directory,
                    entry_point_file_path=entry_point_file_path,
                    port=port,
                    description=description,
                    env_vars=env_vars if env_vars else None,
                    secret_env_vars=secret_env_vars if secret_env_vars else None,
                    show_logs=show_logs,
                    docker_image=docker_image,
                    command=command_list,
                    args=args_list,
                    health_path=health_path,
                    code_mount_path=code_mount_path,
                    ram_memory_gb=ram,
                    cpu_millicores=cpu,
                    replicas=replicas,
                )
            )
        else:
            # Run python entry_point_file_path command and pass the env RUN_LOCALLY_FROM_CLI=true only for that shell process
            env = os.environ.copy()
            env["RUN_LOCALLY_FROM_CLI"] = "true"
            subprocess.run(["python", entry_point_file_path], env=env)

        if not cloud:
            click.secho(
                "[+] MCP server started successfully",
                fg="green",
                bold=True,
            )

    except Exception as e:
        click.secho(f"[!] Error: {str(e)}", fg="red", bold=True)
        raise


@mcp_command.command(name="list")
@click.option(
    "--format",
    type=click.Choice(["table", "json"], case_sensitive=False),
    default="table",
    help="Output format (default: table)",
)
def list_command(format: str):
    """
    List all MCP server deployments on the cloud.

    Examples:

    \b
    # List deployments in table format
    xmagic mcp list

    \b
    # List deployments in JSON format
    xmagic mcp list --format json

    \b
    # Use specific API key
    xmagic mcp list -k your-api-key
    """
    xchat_api_key = get_api_key()

    if not xchat_api_key:
        click.secho(
            "[!] API key not found. Please configure your API key using the 'xmagic configure' command.",
            fg="red",
            bold=True,
        )
        return

    try:
        click.secho("[*] Fetching MCP server deployments...", fg="cyan", bold=True)

        deployments = asyncio.run(list_mcp_server_deployments(xchat_api_key))

        if not deployments:
            click.secho(
                "[*] No MCP server deployments found",
                fg="yellow",
                bold=True,
            )
            return

        if format == "json":
            import json

            click.echo(json.dumps(deployments, indent=2))
        else:
            # Table format
            click.secho(
                f"\n[+] Found {len(deployments)} MCP server deployment(s):\n",
                fg="green",
                bold=True,
            )

            # Print header
            header = f"{'NAME':<30} {'ID':<40} {'STATUS':<15} {'CREATED':<20}"
            click.secho(header, fg="white", bold=True)
            click.secho("-" * len(header), fg="white")

            # Print deployments
            for deployment in deployments:
                name = deployment.get("name", "N/A")[:29]
                deployment_id = deployment.get("id", "N/A")[:39]
                status = deployment.get("status", "N/A")[:14]
                created = deployment.get("created_at", "N/A")[:19]

                # Color code status
                if status == "running":
                    status_colored = click.style(status, fg="green")
                elif status in ["deploying", "deployed"]:
                    status_colored = click.style(status, fg="yellow")
                elif status == "failed":
                    status_colored = click.style(status, fg="red")
                else:
                    status_colored = status

                click.echo(
                    f"{name:<30} {deployment_id:<40} {status_colored:<24} {created:<20}"
                )

    except Exception as e:
        click.secho(f"[!] Error: {str(e)}", fg="red", bold=True)
        raise


@mcp_command.command(name="delete")
@click.argument("deployment_id")
@click.option(
    "-y",
    "--yes",
    is_flag=True,
    help="Skip confirmation prompt",
)
def delete_command(deployment_id: str, yes: bool):
    """
    Delete an MCP server deployment from the cloud.

    Examples:

    \b
    # Delete with confirmation
    xmagic mcp delete <deployment-id>

    \b
    # Delete without confirmation
    xmagic mcp delete <deployment-id> -y

    \b
    # Use specific API key
    xmagic mcp delete <deployment-id> -k your-api-key
    """
    xchat_api_key = get_api_key()

    if not xchat_api_key:
        click.secho(
            "[!] API key not found. Please configure your API key using the 'xmagic configure' command.",
            fg="red",
            bold=True,
        )
        return

    # Validate deployment_id format
    if not validate_deployment_id(deployment_id):
        click.secho(
            f"[!] Invalid deployment ID format: '{deployment_id}'",
            fg="red",
            bold=True,
        )
        click.secho(
            "[!] The deployment ID should be provided, NOT the NAME.",
            fg="red",
            bold=True,
        )
        click.secho(
            "[*] Use 'xmagic mcp list' to see all deployments and their IDs.",
            fg="cyan",
        )
        return

    if not yes:
        if not click.confirm(
            f"Are you sure you want to delete deployment '{deployment_id}'?"
        ):
            click.secho("[*] Deletion cancelled", fg="yellow")
            return

    try:
        click.secho(
            f"[*] Deleting MCP server deployment: {deployment_id}...",
            fg="cyan",
            bold=True,
        )

        result = asyncio.run(delete_mcp_server_deployment(xchat_api_key, deployment_id))

        click.secho(
            f"[+] MCP server deployment deleted successfully",
            fg="green",
            bold=True,
        )

    except Exception as e:
        click.secho(f"[!] Error: {str(e)}", fg="red", bold=True)
        raise


@mcp_command.command(name="logs")
@click.argument("deployment_id")
@click.option(
    "-f",
    "--follow",
    is_flag=True,
    help="Stream logs continuously (like 'tail -f')",
)
@click.option(
    "--interval",
    type=int,
    default=5,
    help="Time between log checks when streaming in seconds (default: 5)",
)
def logs_command(deployment_id: str, follow: bool, interval: int):
    """
    Get logs from an MCP server deployment.

    Examples:

    \b
    # Get current logs
    xmagic mcp logs <deployment-id>

    \b
    # Stream logs continuously
    xmagic mcp logs <deployment-id> -f

    \b
    # Stream logs with custom interval
    xmagic mcp logs <deployment-id> -f --interval 2

    \b
    # Use specific API key
    xmagic mcp logs <deployment-id> -k your-api-key
    """
    xchat_api_key = get_api_key()

    if not xchat_api_key:
        click.secho(
            "[!] API key not found. Please configure your API key using the 'xmagic configure' command.",
            fg="red",
            bold=True,
        )
        return

    # Validate deployment_id format
    if not validate_deployment_id(deployment_id):
        click.secho(
            f"[!] Invalid deployment ID format: '{deployment_id}'",
            fg="red",
            bold=True,
        )
        click.secho(
            "[!] The deployment ID should be provided, NOT the NAME.",
            fg="red",
            bold=True,
        )
        click.secho(
            "[*] Use 'xmagic mcp list' to see all deployments and their IDs.",
            fg="cyan",
        )
        return

    try:
        if follow:
            click.secho(
                f"[*] Streaming logs for deployment: {deployment_id}",
                fg="cyan",
                bold=True,
            )
            click.secho(
                "[*] Press Ctrl+C to stop streaming",
                fg="cyan",
            )
            asyncio.run(
                stream_mcp_server_deployment_logs(
                    xchat_api_key, deployment_id, check_interval=interval
                )
            )
        else:
            click.secho(
                f"[*] Fetching logs for deployment: {deployment_id}",
                fg="cyan",
                bold=True,
            )
            logs = asyncio.run(
                get_mcp_server_deployment_logs(xchat_api_key, deployment_id)
            )

            # Format logs for display
            formatted_logs = _format_logs_for_display(logs)

            click.secho("\n" + "=" * 60, fg="white")
            click.secho("📋 Deployment Logs", fg="green", bold=True)
            click.secho("=" * 60 + "\n", fg="white")
            click.echo(formatted_logs)

    except Exception as e:
        click.secho(f"[!] Error: {str(e)}", fg="red", bold=True)
        raise


@mcp_command.command(name="stop")
@click.argument("deployment_id")
@click.option(
    "-y",
    "--yes",
    is_flag=True,
    help="Skip confirmation prompt",
)
def stop_command(deployment_id: str, yes: bool):
    """
    Stop an MCP server deployment.

    This stops the deployment without deleting it, allowing you to restart it later.

    Examples:

    \b
    # Stop with confirmation
    xmagic mcp stop <deployment-id>

    \b
    # Stop without confirmation
    xmagic mcp stop <deployment-id> -y

    \b
    # Use specific API key
    xmagic mcp stop <deployment-id> -k your-api-key
    """
    xchat_api_key = get_api_key()

    if not xchat_api_key:
        click.secho(
            "[!] API key not found. Please configure your API key using the 'xmagic configure' command.",
            fg="red",
            bold=True,
        )
        return

    # Validate deployment_id format
    if not validate_deployment_id(deployment_id):
        click.secho(
            f"[!] Invalid deployment ID format: '{deployment_id}'",
            fg="red",
            bold=True,
        )
        click.secho(
            "[!] The deployment ID should be provided, NOT the NAME.",
            fg="red",
            bold=True,
        )
        click.secho(
            "[*] Use 'xmagic mcp list' to see all deployments and their IDs.",
            fg="cyan",
        )
        return

    if not yes:
        if not click.confirm(
            f"Are you sure you want to stop deployment '{deployment_id}'?"
        ):
            click.secho("[*] Operation cancelled", fg="yellow")
            return

    try:
        click.secho(
            f"[*] Stopping MCP server deployment: {deployment_id}...",
            fg="cyan",
            bold=True,
        )

        # Stop the deployment using the /stop endpoint
        result = asyncio.run(stop_mcp_server_deployment(xchat_api_key, deployment_id))

        click.secho(
            f"[+] MCP server deployment stopped successfully",
            fg="green",
            bold=True,
        )
        click.secho(
            f"[*] To restart, use: xmagic mcp start {deployment_id}",
            fg="cyan",
        )

    except Exception as e:
        click.secho(f"[!] Error: {str(e)}", fg="red", bold=True)
        raise


@mcp_command.command(name="validate")
@click.option(
    "-d",
    "--code-directory",
    type=click.Path(exists=True, file_okay=False, dir_okay=True),
    required=True,
    help="Path to code directory containing MCP server code",
)
@click.option(
    "--is-custom-tool/--no-custom-tool",
    default=True,
    help="Whether this is a custom tool (default: True)",
)
@click.option(
    "--show-feedback/--no-show-feedback",
    default=True,
    help="Display AI feedback in terminal (default: True)",
)
def validate_command(
    code_directory: str,
    is_custom_tool: bool,
    show_feedback: bool,
):
    """
    Validate MCP server code and get AI feedback before deployment.

    This command uploads your code, validates it, and provides AI-generated
    feedback on code quality, best practices, and potential issues.

    Examples:

    \b
    # Validate code directory
    xmagic mcp validate -d ./my_mcp_code

    \b
    # Validate non-custom-tool code
    xmagic mcp validate -d ./my_code --no-custom-tool

    \b
    # Validate without showing feedback
    xmagic mcp validate -d ./my_mcp_code --no-show-feedback
    """
    xchat_api_key = get_api_key()

    if not xchat_api_key:
        click.secho(
            "[!] API key not found. Please configure your API key using the 'xmagic configure' command.",
            fg="red",
            bold=True,
        )
        return

    try:
        click.secho(
            f"[*] Validating MCP server code from: {code_directory}",
            fg="cyan",
            bold=True,
        )

        result = asyncio.run(
            validate_mcp_server_code(
                xchat_api_key=xchat_api_key,
                code_directory=code_directory,
                is_custom_tool=is_custom_tool,
            )
        )

        # Check validation result
        is_valid = result.get("is_valid", False)
        message = result.get("message", "")
        ai_feedback = result.get("ai_feedback", "")
        files_extracted = result.get("files_extracted", 0)

        if is_valid:
            click.secho(
                f"\n[+] ✓ Code validation finished successfully!",
                fg="cyan",
                bold=True,
            )

            if files_extracted > 0:
                click.secho(
                    f"[*] Analyzed {files_extracted} file(s)",
                    fg="cyan",
                )

            if ai_feedback and show_feedback:
                click.secho("\n" + "=" * 60, fg="white")
                click.secho("🤖 AI Code Review Feedback", fg="blue", bold=True)
                click.secho("=" * 60 + "\n", fg="white")

                click.echo(ai_feedback)

                click.secho("\n" + "=" * 60 + "\n", fg="white")
            elif ai_feedback:
                click.secho(
                    "[*] AI feedback available but hidden (use --show-feedback to display)",
                    fg="cyan",
                )

            click.secho(
                "[*] Please review the comments provided by the AI",
                fg="green",
                bold=True,
            )
            click.secho(
                f"[*] Once your code is ready, you can deploy it with: xmagic mcp run -d {code_directory} --cloud",
                fg="cyan",
            )

        else:
            click.secho(
                f"\n[!] ✗ Code validation failed",
                fg="red",
                bold=True,
            )
            if message:
                click.secho(f"[!] Error: {message}", fg="red")

            click.secho(
                "\n[*] Please fix the issues and try again",
                fg="yellow",
                bold=True,
            )

    except Exception as e:
        click.secho(f"[!] Error: {str(e)}", fg="red", bold=True)
        raise


@mcp_command.command(name="start")
@click.argument("deployment_id")
@click.option(
    "--replicas",
    type=int,
    default=1,
    help="Number of replicas to start (default: 1)",
)
def start_command(deployment_id: str, replicas: int):
    """
    Start a stopped MCP server deployment (scales replicas from 0).

    Examples:

    \b
    # Start with 1 replica
    xmagic mcp start <deployment-id>

    \b
    # Start with multiple replicas
    xmagic mcp start <deployment-id> --replicas 3

    \b
    # Use specific API key
    xmagic mcp start <deployment-id> -k your-api-key
    """
    xchat_api_key = get_api_key()

    if not xchat_api_key:
        click.secho(
            "[!] API key not found. Please configure your API key using the 'xmagic configure' command.",
            fg="red",
            bold=True,
        )
        return

    # Validate deployment_id format
    if not validate_deployment_id(deployment_id):
        click.secho(
            f"[!] Invalid deployment ID format: '{deployment_id}'",
            fg="red",
            bold=True,
        )
        click.secho(
            "[!] The deployment ID should be provided, NOT the NAME.",
            fg="red",
            bold=True,
        )
        click.secho(
            "[*] Use 'xmagic mcp list' to see all deployments and their IDs.",
            fg="cyan",
        )
        return

    try:
        click.secho(
            f"[*] Starting MCP server deployment: {deployment_id}...",
            fg="cyan",
            bold=True,
        )

        # Start by scaling to desired replicas
        result = asyncio.run(
            update_mcp_server_deployment(
                xchat_api_key=xchat_api_key,
                deployment_id=deployment_id,
                replicas=replicas,
            )
        )

        click.secho(
            f"[+] MCP server deployment started successfully with {replicas} replica(s)",
            fg="green",
            bold=True,
        )
        click.secho(
            f"[*] To view logs, use: xmagic mcp logs {deployment_id} -f",
            fg="cyan",
        )

    except Exception as e:
        click.secho(f"[!] Error: {str(e)}", fg="red", bold=True)
        raise
