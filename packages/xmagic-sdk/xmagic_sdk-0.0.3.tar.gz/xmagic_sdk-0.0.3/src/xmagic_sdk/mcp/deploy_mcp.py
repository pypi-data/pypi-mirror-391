import os
import zipfile
import tempfile
import random
import asyncio
import time
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import httpx

from xmagic_sdk.agents.agents import (
    create_custom_tool_config,
    get_custom_tool_config_by_name,
    update_custom_tool_config_by_name,
    delete_custom_tool_config_by_name,
)
from xmagic_sdk.config import Config, DEFAULT_HTTPX_TIMEOUT
from xmagic_sdk.logging.logging import configure_logger

logger = configure_logger(__name__)

# Cross-platform deployment name cache file
DEPLOYMENT_NAME_CACHE_FILE = Path.home() / ".xmagic" / "mcp_deployment_names.json"

# Friendly name generation
ADJECTIVES = [
    "happy",
    "clever",
    "bright",
    "swift",
    "gentle",
    "brave",
    "calm",
    "wise",
    "lucky",
    "noble",
    "quick",
    "smart",
    "kind",
    "proud",
    "bold",
]

NOUNS = [
    "falcon",
    "phoenix",
    "dragon",
    "wolf",
    "eagle",
    "tiger",
    "bear",
    "lion",
    "hawk",
    "fox",
    "owl",
    "raven",
    "puma",
    "lynx",
    "cobra",
]


def generate_friendly_name() -> str:
    """Generate a friendly random name like 'happy-falcon-42'."""
    adjective = random.choice(ADJECTIVES)
    noun = random.choice(NOUNS)
    number = random.randint(10, 99)
    return f"{adjective}-{noun}-{number}"


def _get_deployment_name_cache() -> Dict[str, str]:
    """
    Load deployment name cache from disk.
    Returns a dict mapping code_directory -> deployment_name.
    """
    if not DEPLOYMENT_NAME_CACHE_FILE.exists():
        return {}

    try:
        with open(DEPLOYMENT_NAME_CACHE_FILE, "r") as f:
            return json.load(f)
    except Exception as e:
        logger.debug(f"Could not load deployment name cache: {e}")
        return {}


def _save_deployment_name_cache(cache: Dict[str, str]) -> None:
    """Save deployment name cache to disk."""
    try:
        # Ensure directory exists
        DEPLOYMENT_NAME_CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)

        with open(DEPLOYMENT_NAME_CACHE_FILE, "w") as f:
            json.dump(cache, f, indent=2)

        logger.debug(f"Saved deployment name cache to {DEPLOYMENT_NAME_CACHE_FILE}")
    except Exception as e:
        logger.warning(f"Could not save deployment name cache: {e}")


def get_or_create_deployment_name(code_directory: str) -> str:
    """
    Get cached deployment name for a code directory, or create a new one.

    This helps avoid creating multiple deployments when the user runs
    the same code directory multiple times without specifying a name.

    Args:
        code_directory: Path to the code directory

    Returns:
        Deployment name (either cached or newly generated)
    """
    # Normalize path for consistency across platforms
    normalized_path = str(Path(code_directory).resolve())

    cache = _get_deployment_name_cache()

    if normalized_path in cache:
        cached_name = cache[normalized_path]
        logger.info(f"Reusing cached deployment name: {cached_name}")
        return cached_name

    # Generate new name and cache it
    new_name = generate_friendly_name()
    cache[normalized_path] = new_name
    _save_deployment_name_cache(cache)

    logger.info(f"Generated and cached new deployment name: {new_name}")
    return new_name


def clear_deployment_name_cache(code_directory: Optional[str] = None) -> None:
    """
    Clear deployment name cache.

    Args:
        code_directory: If provided, only clear the cache for this directory.
                       If None, clear entire cache.
    """
    if code_directory is None:
        # Clear entire cache
        if DEPLOYMENT_NAME_CACHE_FILE.exists():
            DEPLOYMENT_NAME_CACHE_FILE.unlink()
            logger.info("Cleared entire deployment name cache")
    else:
        # Clear specific directory
        normalized_path = str(Path(code_directory).resolve())
        cache = _get_deployment_name_cache()

        if normalized_path in cache:
            del cache[normalized_path]
            _save_deployment_name_cache(cache)
            logger.info(f"Cleared deployment name cache for: {code_directory}")
        else:
            logger.debug(f"No cached deployment name found for: {code_directory}")


def _format_logs_for_display(logs_data) -> str:
    """
    Format logs data for display. Handles both dict and string formats.

    Args:
        logs_data: Can be a string (old format) or dict (new format with pod/container structure)

    Returns:
        Formatted log string
    """
    if isinstance(logs_data, str):
        # Simple string format
        return logs_data

    if isinstance(logs_data, dict):
        # New format: {pod_name: {container_name: logs}} or {pod_name: logs}
        formatted_parts = []

        for pod_name, containers in logs_data.items():
            if isinstance(containers, dict):
                # Multi-container format
                for container_name, logs in containers.items():
                    if logs:
                        formatted_parts.append(
                            f"[{pod_name}/{container_name}]:\n{logs}"
                        )
            elif isinstance(containers, str):
                # Single container format
                if containers:
                    formatted_parts.append(f"[{pod_name}]:\n{containers}")

        return "\n\n".join(formatted_parts) if formatted_parts else "No logs available"

    # Fallback for unexpected format
    return str(logs_data)


async def _upload_code_zip(xchat_api_key: str, zip_path: str) -> str:
    """Upload a zip file containing the MCP server code and return the uploaded file ID."""
    file_upload_url = f"{Config.XMAGIC_BASE_PATH}/v1/uploaded-files"

    async with httpx.AsyncClient(timeout=DEFAULT_HTTPX_TIMEOUT) as client:
        with open(zip_path, "rb") as file:
            response = await client.post(
                file_upload_url,
                files={"file": (Path(zip_path).name, file)},
                headers={"x-api-key": xchat_api_key},
            )
            response.raise_for_status()
            file_id = response.json()["data"]

    if not file_id:
        raise ValueError("File upload failed, no file ID returned.")

    logger.info(f"Successfully uploaded code zip file with ID: {file_id}")
    return file_id


def validate_mcp_code_locally(
    code_directory: str,
    is_custom_tool: bool = True,
    entry_point_file_path: Optional[str] = None,
) -> Tuple[bool, str]:
    """
    Validate MCP server code locally before deployment.

    Args:
        code_directory: Path to the code directory
        is_custom_tool: Whether this is a custom tool (requires mcp_server.py or entry point file)
        entry_point_file_path: Optional path to entry point file (will be renamed to mcp_server.py)

    Returns:
        Tuple of (is_valid, error_message)
    """
    code_path = Path(code_directory)

    if not code_path.exists():
        return False, f"Code directory does not exist: {code_directory}"

    if not code_path.is_dir():
        return False, f"Path is not a directory: {code_directory}"

    # Check for required files
    if is_custom_tool:
        # Look for mcp_server.py or the specified entry point file
        entry_point_found = False

        # If entry_point_file_path is provided, check if it exists
        if entry_point_file_path:
            entry_point_abs = Path(entry_point_file_path).resolve()
            if entry_point_abs.exists() and entry_point_abs.is_file():
                # Verify it's within the code directory
                try:
                    code_dir_abs = code_path.resolve()
                    entry_point_abs.relative_to(code_dir_abs)
                    entry_point_found = True
                    logger.debug(f"Found entry point file: {entry_point_file_path}")
                except ValueError:
                    return (
                        False,
                        f"Entry point file {entry_point_file_path} is not within code directory {code_directory}",
                    )
            else:
                return (
                    False,
                    f"Entry point file {entry_point_file_path} does not exist or is not a file",
                )
        else:
            # Look for mcp_server.py
            for root, dirs, files in os.walk(code_directory):
                if "mcp_server.py" in files:
                    entry_point_found = True
                    logger.debug(f"Found mcp_server.py in {root}")
                    break

        if not entry_point_found:
            return False, (
                "Custom tool validation failed: 'mcp_server.py' not found in the code directory. "
                "Please ensure your code directory contains an 'mcp_server.py' file as the entry point, "
                "or specify an entry point file path that will be renamed to 'mcp_server.py' during deployment."
            )

    # Check for requirements.txt (warning, not error)
    requirements_found = False
    for root, dirs, files in os.walk(code_directory):
        if "requirements.txt" in files:
            requirements_found = True
            break

    if not requirements_found:
        logger.warning(
            "No requirements.txt found. If your code has dependencies, "
            "please add a requirements.txt file."
        )

    # Check if directory is empty
    has_files = False
    for root, dirs, files in os.walk(code_directory):
        if files:
            has_files = True
            break

    if not has_files:
        return False, "Code directory is empty. Please add your MCP server code."

    return True, "Code validation passed"


async def validate_mcp_code_remote(
    xchat_api_key: str,
    code_directory: str,
    is_custom_tool: bool = True,
    entry_point_file_path: Optional[str] = None,
) -> Tuple[bool, str]:
    """
    Validate MCP server code by uploading to the server for validation.

    This performs the same validation as the deployment process but without
    actually creating a deployment.

    Args:
        xchat_api_key: Your Stochastic API key
        code_directory: Path to the code directory
        is_custom_tool: Whether this is a custom tool (requires mcp_server.py)
        entry_point_file_path: Optional path to entry point file (will be renamed to mcp_server.py)

    Returns:
        Tuple of (is_valid, error_message)
    """
    # First do local validation
    is_valid_local, error_msg = validate_mcp_code_locally(
        code_directory, is_custom_tool, entry_point_file_path
    )
    if not is_valid_local:
        return False, error_msg

    # Create and upload zip for server-side validation
    logger.info("Performing server-side code validation...")
    zip_path = await _create_code_zip(
        code_directory, entry_point_file_path=entry_point_file_path
    )

    try:
        file_id = await _upload_code_zip(xchat_api_key, zip_path)

        # Call validation endpoint
        validation_url = f"{Config.XMAGIC_BASE_PATH}/v1/mcp-servers/validate-code"

        payload = {
            "code_zip_upload_file_id": file_id,
            "is_custom_tool": is_custom_tool,
        }

        async with httpx.AsyncClient(timeout=DEFAULT_HTTPX_TIMEOUT) as client:
            response = await client.post(
                validation_url,
                headers={"x-api-key": xchat_api_key},
                json=payload,
            )
            response.raise_for_status()
            result = response.json()["data"]

        is_valid = result.get("is_valid", False)
        message = result.get("message", "")

        if is_valid:
            logger.info("✅ Server-side validation passed")
        else:
            logger.error(f"❌ Server-side validation failed: {message}")

        return is_valid, message

    finally:
        # Clean up temp zip file
        if os.path.exists(zip_path):
            os.remove(zip_path)
            logger.debug(f"Cleaned up temporary zip file: {zip_path}")


async def validate_mcp_server_code(
    xchat_api_key: str,
    code_directory: str,
    is_custom_tool: bool = True,
    entry_point_file_path: Optional[str] = None,
) -> Dict:
    """
    Validate MCP server code and get AI feedback without deploying.

    This function performs comprehensive validation including:
    1. Local validation (file structure, requirements)
    2. Server-side validation (zip upload and structural checks)
    3. AI-powered code review and feedback

    Args:
        xchat_api_key: Your Stochastic API key
        code_directory: Path to the code directory
        is_custom_tool: Whether this is a custom tool (requires mcp_server.py)
        entry_point_file_path: Optional path to entry point file

    Returns:
        Dictionary with validation results:
        {
            "is_valid": bool,
            "message": str,
            "ai_feedback": str (markdown formatted),
            "files_extracted": int
        }
    """
    # First do local validation
    logger.info("Performing local code validation...")
    is_valid_local, error_msg = validate_mcp_code_locally(
        code_directory, is_custom_tool, entry_point_file_path
    )
    if not is_valid_local:
        return {
            "is_valid": False,
            "message": error_msg,
            "ai_feedback": None,
            "files_extracted": 0,
        }

    logger.info("✓ Local validation passed")

    # Create and upload zip for server-side validation
    logger.info("Uploading code for server-side validation...")
    zip_path = await _create_code_zip(
        code_directory, entry_point_file_path=entry_point_file_path
    )

    try:
        file_id = await _upload_code_zip(xchat_api_key, zip_path)
        logger.info("✓ Code uploaded successfully")

        # Call validation endpoint
        validation_url = f"{Config.XMAGIC_BASE_PATH}/v1/mcp-servers/validate-code"

        payload = {
            "code_zip_upload_file_id": file_id,
            "is_custom_tool": is_custom_tool,
        }

        logger.info("Performing server-side validation and AI analysis...")
        async with httpx.AsyncClient(timeout=httpx.Timeout(120.0)) as client:
            response = await client.post(
                validation_url,
                headers={"x-api-key": xchat_api_key},
                json=payload,
            )
            response.raise_for_status()
            result = response.json()["data"]

        is_valid = result.get("is_valid", False)
        message = result.get("message", "")
        ai_feedback = result.get("ai_feedback", "")
        files_extracted = result.get("files_extracted", 0)

        if is_valid:
            logger.info("✓ Server-side validation passed")
            if ai_feedback:
                logger.info("✓ AI code review completed")
        else:
            logger.error(f"✗ Server-side validation failed: {message}")

        return {
            "is_valid": is_valid,
            "message": message,
            "ai_feedback": ai_feedback,
            "files_extracted": files_extracted,
        }

    finally:
        # Clean up temp zip file
        if os.path.exists(zip_path):
            os.remove(zip_path)
            logger.debug(f"Cleaned up temporary zip file: {zip_path}")


async def _create_code_zip(
    code_directory: str,
    output_path: Optional[str] = None,
    entry_point_file_path: Optional[str] = None,
) -> str:
    """Create a zip file from the code directory.

    If an entry point file is specified and it's not named 'mcp_server.py',
    it will be renamed to 'mcp_server.py' in the zip file.

    Args:
        code_directory: Path to the code directory
        output_path: Optional output path for the zip file
        entry_point_file_path: Optional path to the entry point file (will be renamed to mcp_server.py)
    """
    if output_path is None:
        # Create temp zip file
        temp_dir = tempfile.gettempdir()
        output_path = os.path.join(temp_dir, "mcp_server_code.zip")

    code_path = Path(code_directory)

    if not code_path.exists():
        raise ValueError(f"Code directory does not exist: {code_directory}")

    logger.info(f"Creating zip file from directory: {code_directory}")

    # Determine the entry point file relative path if provided
    entry_point_relative = None
    if entry_point_file_path:
        entry_point_abs = Path(entry_point_file_path).resolve()
        code_dir_abs = code_path.resolve()
        try:
            entry_point_relative = str(entry_point_abs.relative_to(code_dir_abs))
            logger.info(f"Entry point file: {entry_point_relative}")
            if entry_point_relative != "mcp_server.py":
                logger.info(
                    f"Will rename '{entry_point_relative}' to 'mcp_server.py' in zip file"
                )
        except ValueError:
            logger.warning(
                f"Entry point file {entry_point_file_path} is not within {code_directory}"
            )
            entry_point_relative = None

    with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(code_directory):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, code_directory)

                # If this is the entry point file and it's not named mcp_server.py, rename it
                if entry_point_relative and arcname.replace(
                    "\\", "/"
                ) == entry_point_relative.replace("\\", "/"):
                    # Get the directory part of the entry point (if any)
                    entry_dir = os.path.dirname(entry_point_relative)
                    if entry_dir:
                        arcname = os.path.join(entry_dir, "mcp_server.py")
                    else:
                        arcname = "mcp_server.py"
                    logger.debug(f"Renaming {entry_point_relative} to {arcname} in zip")

                zipf.write(file_path, arcname)

    logger.info(f"Zip file created at: {output_path}")
    return output_path


async def _check_deployment_exists(xchat_api_key: str, name: str) -> Optional[Dict]:
    """Check if a deployment with the given name already exists."""
    try:
        deployments = await list_mcp_server_deployments(xchat_api_key)
        for deployment in deployments:
            if deployment.get("name") == name:
                return deployment
    except Exception as e:
        logger.debug(f"Error checking existing deployments: {e}")
    return None


async def _update_deployment(
    xchat_api_key: str,
    deployment_id: str,
    code_directory: Optional[str] = None,
    entry_point_file_path: Optional[str] = None,
    description: Optional[str] = None,
    env_vars: Optional[Dict[str, str]] = None,
    secret_env_vars: Optional[Dict[str, str]] = None,
    docker_image: Optional[str] = None,
    port: Optional[int] = None,
    command: Optional[List[str]] = None,
    args: Optional[List[str]] = None,
    health_path: Optional[str] = None,
    code_mount_path: Optional[str] = None,
    ram_memory_gb: Optional[float] = None,
    cpu_millicores: Optional[int] = None,
    replicas: Optional[int] = None,
) -> Dict:
    """
    Update an existing MCP server deployment.

    Args:
        xchat_api_key: Your Stochastic API key
        deployment_id: The deployment ID to update
        code_directory: Optional path to new code directory
        description: Optional new description
        env_vars: Optional new environment variables (non-sensitive)
        secret_env_vars: Optional new environment variables (sensitive)
        docker_image: Optional new Docker image
        port: Optional new port
        command: Optional new container command
        args: Optional new container args
        health_path: Optional new health check path
        code_mount_path: Optional new code mount path
        ram_memory_gb: Optional new RAM allocation in GB
        cpu_millicores: Optional new CPU allocation in millicores
        replicas: Optional new number of replicas (1-8)

    Returns:
        Updated deployment information
    """
    logger.info(f"Updating existing deployment with ID: {deployment_id}")

    payload = {}
    zip_path = None

    try:
        # Handle code update if provided
        if code_directory is not None:
            # Create zip file from code directory
            logger.info(f"Preparing updated code from directory: {code_directory}")
            zip_path = await _create_code_zip(
                code_directory, entry_point_file_path=entry_point_file_path
            )

            # Upload zip file
            logger.info("Uploading updated code to Stochastic cloud...")
            file_id = await _upload_code_zip(xchat_api_key, zip_path)
            payload["code_zip_upload_file_id"] = file_id

        # Add all other optional updates
        if description is not None:
            payload["description"] = description
        if env_vars is not None:
            payload["env_vars"] = env_vars
        if secret_env_vars is not None:
            payload["secret_env_vars"] = secret_env_vars
        if docker_image is not None:
            payload["docker_image"] = docker_image
        if port is not None:
            payload["port"] = port
        if command is not None:
            payload["command"] = command
        if args is not None:
            payload["args"] = args
        if health_path is not None:
            payload["health_path"] = health_path
        if code_mount_path is not None:
            payload["code_mount_path"] = code_mount_path
        if ram_memory_gb is not None:
            payload["ram_memory_gb"] = ram_memory_gb
        if cpu_millicores is not None:
            payload["cpu_milllicores"] = cpu_millicores
        if replicas is not None:
            payload["replicas"] = max(1, min(8, replicas))

        if not payload:
            logger.warning("No update parameters provided")
            raise ValueError("At least one parameter must be provided for update")

        # Log what's being updated
        logger.info(f"Updating deployment with fields: {list(payload.keys())}")

        # Update deployment
        update_url = f"{Config.XMAGIC_BASE_PATH}/v1/mcp-servers/{deployment_id}"

        async with httpx.AsyncClient(timeout=DEFAULT_HTTPX_TIMEOUT) as client:
            response = await client.patch(
                update_url,
                headers={"x-api-key": xchat_api_key},
                json=payload,
            )
            response.raise_for_status()
            result = response.json()["data"]

        logger.info(f"MCP server deployment updated successfully")
        return result

    finally:
        # Clean up temp zip file if created
        if zip_path is not None and os.path.exists(zip_path):
            os.remove(zip_path)
            logger.debug(f"Cleaned up temporary zip file: {zip_path}")


async def deploy_mcp_server_to_cloud(
    xchat_api_key: str,
    name: Optional[str] = None,
    code_directory: str = None,
    entry_point_file_path: Optional[str] = None,
    description: Optional[str] = None,
    docker_image: str = "python:3.11",
    port: int = 8000,
    env_vars: Optional[Dict[str, str]] = None,
    secret_env_vars: Optional[Dict[str, str]] = None,
    command: Optional[List[str]] = None,
    args: Optional[List[str]] = None,
    health_path: str = "/v1/health",
    code_mount_path: str = "/code",
    ram_memory_gb: float = 0.5,
    cpu_millicores: int = 500,
    replicas: int = 1,
    update_if_exists: bool = True,
    # create_api_key: bool = True,
) -> Dict:
    """
    Deploy an MCP server to Stochastic's cloud infrastructure.

    Args:
        xchat_api_key: Your Stochastic API key
        name: Name for the MCP server deployment (auto-generated if not provided)
        code_directory: Path to the directory containing your MCP server code
        description: Optional description of the MCP server
        docker_image: Docker image to use (default: python:3.11)
        port: Port the server will run on (default: 8000)
        env_vars: Environment variables (non-sensitive)
        secret_env_vars: Environment variables (sensitive, will be stored securely)
        command: Override container entrypoint (default: ["/bin/sh", "-c"])
        args: Override container command args (default: install requirements and run)
        health_path: Health check endpoint path (default: /v1/health)
        code_mount_path: Where to mount code in container (default: /code)
        ram_memory_gb: RAM allocation in GB (default: 0.5)
        cpu_millicores: CPU allocation in millicores (default: 500)
        replicas: Number of replicas (default: 1, max: 8)
        update_if_exists: If True, update existing deployment instead of failing (default: True)

    Returns:
        Dictionary with deployment information including deployment_id and status
    """
    # Validate inputs
    if not xchat_api_key:
        raise ValueError(
            "API key is required. Set XCHAT_API_KEY environment variable or pass it directly."
        )

    if not code_directory:
        raise ValueError("Code directory is required.")

    # Get or generate deployment name
    if not name:
        name = get_or_create_deployment_name(code_directory)
        logger.info(f"Using deployment name: {name}")  # Set defaults
    if env_vars is None:
        env_vars = {}
    if secret_env_vars is None:
        secret_env_vars = {}
    if command is None:
        command = ["/bin/sh", "-c"]
    if args is None:
        args = [
            "pip install --no-cache-dir -r requirements.txt && python /code/mcp_server.py"
        ]

    # Check if deployment already exists
    existing_deployment = await _check_deployment_exists(xchat_api_key, name)

    if existing_deployment and update_if_exists:
        logger.info(f"Deployment '{name}' already exists. Updating...")
        return await _update_deployment(
            xchat_api_key=xchat_api_key,
            deployment_id=existing_deployment["id"],
            code_directory=code_directory,
            entry_point_file_path=entry_point_file_path,
            description=description,
            env_vars=env_vars,
            secret_env_vars=secret_env_vars,
            docker_image=docker_image,
            port=port,
            command=command,
            args=args,
            health_path=health_path,
            code_mount_path=code_mount_path,
            ram_memory_gb=ram_memory_gb,
            cpu_millicores=cpu_millicores,
            replicas=replicas,
        )
    elif existing_deployment and not update_if_exists:
        raise ValueError(
            f"Deployment with name '{name}' already exists. "
            "Set update_if_exists=True to update it."
        )

    # Create zip file from code directory
    logger.info(f"Preparing code from directory: {code_directory}")
    zip_path = await _create_code_zip(
        code_directory, entry_point_file_path=entry_point_file_path
    )

    try:
        # Upload zip file
        logger.info("Uploading code to Stochastic cloud...")
        file_id = await _upload_code_zip(xchat_api_key, zip_path)

        # Create MCP server deployment
        logger.info(f"Creating MCP server deployment: {name}")
        deployment_url = f"{Config.XMAGIC_BASE_PATH}/v1/mcp-servers"

        payload = {
            "name": name,
            "description": description,
            "mcp_server_type": "custom_tool",  # Default to custom_tool as specified
            "code_zip_upload_file_id": file_id,
            "docker_image": docker_image,
            "port": port,
            "env_vars": env_vars,
            "secret_env_vars": secret_env_vars,
            "command": command,
            "args": args,
            "health_path": health_path,
            "code_mount_path": code_mount_path,
            "ram_memory_gb": ram_memory_gb,
            "cpu_milllicores": cpu_millicores,
            "replicas": max(1, min(8, replicas)),  # Ensure replicas is between 1-8
            # "create_api_key": create_api_key,
        }

        async with httpx.AsyncClient(timeout=DEFAULT_HTTPX_TIMEOUT) as client:
            response = await client.post(
                deployment_url,
                headers={"x-api-key": xchat_api_key},
                json=payload,
            )
            response.raise_for_status()
            result = response.json()["data"]

        logger.info(
            f"MCP server deployment created successfully with ID: {result.get('id')}"
        )
        logger.info(f"Status: {result.get('status')}")

        return result

    finally:
        # Clean up temp zip file
        if os.path.exists(zip_path):
            os.remove(zip_path)
            logger.debug(f"Cleaned up temporary zip file: {zip_path}")


async def get_mcp_server_deployment_status(
    xchat_api_key: str, deployment_id: str
) -> Dict:
    """
    Get the status of an MCP server deployment.

    Args:
        xchat_api_key: Your Stochastic API key
        deployment_id: The deployment ID returned from deploy_mcp_server_to_cloud

    Returns:
        Dictionary with deployment status and details
    """
    url = f"{Config.XMAGIC_BASE_PATH}/v1/mcp-servers/{deployment_id}"

    async with httpx.AsyncClient(timeout=DEFAULT_HTTPX_TIMEOUT) as client:
        response = await client.get(
            url,
            headers={"x-api-key": xchat_api_key},
        )
        response.raise_for_status()
        return response.json()["data"]


async def get_mcp_server_deployment_logs(xchat_api_key: str, deployment_id: str) -> str:
    """
    Get logs for an MCP server deployment.

    Args:
        xchat_api_key: Your Stochastic API key
        deployment_id: The deployment ID

    Returns:
        String containing the logs
    """
    url = f"{Config.XMAGIC_BASE_PATH}/v1/mcp-servers/{deployment_id}/logs"

    async with httpx.AsyncClient(timeout=DEFAULT_HTTPX_TIMEOUT) as client:
        response = await client.get(
            url,
            headers={"x-api-key": xchat_api_key},
        )
        response.raise_for_status()
        return response.json()["data"]


async def stream_mcp_server_deployment_logs(
    xchat_api_key: str,
    deployment_id: str,
    check_interval: int = 5,
) -> None:
    """
    Continuously stream logs from an MCP server deployment, showing only new logs.

    This function runs indefinitely until interrupted (Ctrl+C).
    It tracks logs from all replicas (pods) and shows only new log lines.

    Args:
        xchat_api_key: Your Stochastic API key
        deployment_id: The deployment ID
        check_interval: Time between log checks in seconds (default: 2)
    """
    # Track the last seen logs for each pod/container
    # Structure: {pod_name: {container_name: last_log_content}}
    last_logs = {}

    logger.info("=" * 60)
    logger.info("📋 Streaming Deployment Logs (Press Ctrl+C to stop)")
    logger.info("=" * 60)

    try:
        while True:
            try:
                url = f"{Config.XMAGIC_BASE_PATH}/v1/mcp-servers/{deployment_id}/logs"

                async with httpx.AsyncClient(timeout=DEFAULT_HTTPX_TIMEOUT) as client:
                    response = await client.get(
                        url,
                        headers={"x-api-key": xchat_api_key},
                    )
                    response.raise_for_status()
                    logs_data = response.json()["data"]

                # logs_data is a dict: {pod_name: {container_name: logs}}
                if isinstance(logs_data, dict):
                    for pod_name, containers in logs_data.items():
                        if isinstance(containers, dict):
                            for container_name, logs in containers.items():
                                # Create unique key for this pod/container
                                key = f"{pod_name}:{container_name}"

                                # Get the last seen logs for this pod/container
                                last_log = last_logs.get(key, "")

                                # Only show new logs
                                if logs != last_log:
                                    # If we have previous logs, find the new content
                                    if last_log and logs.startswith(last_log):
                                        new_logs = logs[len(last_log) :]
                                    elif last_log:
                                        # Logs were replaced (pod restart?), show all
                                        new_logs = logs
                                        print(
                                            f"\n🔄 [{pod_name}] [{container_name}] Pod restarted or logs reset\n"
                                        )
                                    else:
                                        # First time seeing logs
                                        new_logs = logs

                                    # Print new logs if any
                                    if new_logs.strip():
                                        # Show pod/container header if multiple replicas
                                        if len(logs_data) > 1 or len(containers) > 1:
                                            print(
                                                f"\n📦 [{pod_name}] [{container_name}]"
                                            )
                                        print(new_logs, end="", flush=True)

                                    # Update last seen logs
                                    last_logs[key] = logs
                        else:
                            # Handle case where logs_data[pod_name] is a string (old format)
                            if isinstance(containers, str):
                                key = pod_name
                                last_log = last_logs.get(key, "")

                                if containers != last_log:
                                    if last_log and containers.startswith(last_log):
                                        new_logs = containers[len(last_log) :]
                                    elif last_log:
                                        new_logs = containers
                                        print(f"\n🔄 [{pod_name}] Logs reset\n")
                                    else:
                                        new_logs = containers

                                    if new_logs.strip():
                                        if len(logs_data) > 1:
                                            print(f"\n📦 [{pod_name}]")
                                        print(new_logs, end="", flush=True)

                                    last_logs[key] = containers
                else:
                    # Handle case where logs_data is a string (single replica, old format)
                    if isinstance(logs_data, str):
                        key = "default"
                        last_log = last_logs.get(key, "")

                        if logs_data != last_log:
                            if last_log and logs_data.startswith(last_log):
                                new_logs = logs_data[len(last_log) :]
                            else:
                                new_logs = logs_data

                            if new_logs.strip():
                                print(new_logs, end="", flush=True)

                            last_logs[key] = logs_data

            except httpx.HTTPStatusError as e:
                if e.response.status_code == 404:
                    logger.error("❌ Deployment not found")
                    break
                else:
                    logger.error(f"Error fetching logs: {e}")
            except Exception as e:
                logger.debug(f"Error in log streaming: {e}")

            # Wait before next check
            await asyncio.sleep(check_interval)

    except KeyboardInterrupt:
        logger.info("\n\n" + "=" * 60)
        logger.info("🛑 Log streaming stopped")
        logger.info("=" * 60)


async def list_mcp_server_deployments(xchat_api_key: str) -> List[Dict]:
    """
    List all MCP server deployments for your organization.

    Args:
        xchat_api_key: Your Stochastic API key

    Returns:
        List of deployment dictionaries
    """
    url = f"{Config.XMAGIC_BASE_PATH}/v1/mcp-servers"

    async with httpx.AsyncClient(timeout=DEFAULT_HTTPX_TIMEOUT) as client:
        response = await client.get(
            url,
            headers={"x-api-key": xchat_api_key},
        )
        response.raise_for_status()
        return response.json()["data"]


async def update_mcp_server_deployment(
    xchat_api_key: str,
    deployment_id: str,
    code_directory: Optional[str] = None,
    entry_point_file_path: Optional[str] = None,
    description: Optional[str] = None,
    env_vars: Optional[Dict[str, str]] = None,
    secret_env_vars: Optional[Dict[str, str]] = None,
    docker_image: Optional[str] = None,
    port: Optional[int] = None,
    command: Optional[List[str]] = None,
    args: Optional[List[str]] = None,
    health_path: Optional[str] = None,
    code_mount_path: Optional[str] = None,
    ram_memory_gb: Optional[float] = None,
    cpu_millicores: Optional[int] = None,
    replicas: Optional[int] = None,
) -> Dict:
    """
    Update an existing MCP server deployment.

    Args:
        xchat_api_key: Your Stochastic API key
        deployment_id: The deployment ID to update
        code_directory: Optional path to new code directory (will upload and replace existing code)
        description: Optional new description
        env_vars: Optional new environment variables (non-sensitive)
        secret_env_vars: Optional new environment variables (sensitive)
        docker_image: Optional new Docker image to use
        port: Optional new port the server will run on
        command: Optional new container entrypoint
        args: Optional new container command args
        health_path: Optional new health check endpoint path
        code_mount_path: Optional new code mount path in container
        ram_memory_gb: Optional new RAM allocation in GB
        cpu_millicores: Optional new CPU allocation in millicores
        replicas: Optional new number of replicas (1-8)

    Returns:
        Dictionary with updated deployment information

    Example:
        # Update just the resources
        result = await update_mcp_server_deployment(
            xchat_api_key="your-api-key",
            deployment_id="deployment-id",
            ram_memory_gb=1.0,
            cpu_millicores=1000,
            replicas=2
        )

        # Update code and environment variables
        result = await update_mcp_server_deployment(
            xchat_api_key="your-api-key",
            deployment_id="deployment-id",
            code_directory="/path/to/updated/code",
            env_vars={"NEW_VAR": "value"},
        )
    """
    return await _update_deployment(
        xchat_api_key=xchat_api_key,
        deployment_id=deployment_id,
        code_directory=code_directory,
        entry_point_file_path=entry_point_file_path,
        description=description,
        env_vars=env_vars,
        secret_env_vars=secret_env_vars,
        docker_image=docker_image,
        port=port,
        command=command,
        args=args,
        health_path=health_path,
        code_mount_path=code_mount_path,
        ram_memory_gb=ram_memory_gb,
        cpu_millicores=cpu_millicores,
        replicas=replicas,
    )


async def delete_mcp_server_deployment(xchat_api_key: str, deployment_id: str) -> Dict:
    """
    Delete an MCP server deployment and its associated custom tool configuration.

    Args:
        xchat_api_key: Your Stochastic API key
        deployment_id: The deployment ID to delete

    Returns:
        Dictionary with deletion confirmation
    """
    # First, get the deployment details to retrieve the deployment name
    try:
        deployment_status = await get_mcp_server_deployment_status(
            xchat_api_key, deployment_id
        )
        deployment_name = deployment_status.get("name")

        # Check if there's a custom tool configuration for this deployment
        if deployment_name:
            logger.debug(
                f"Checking for custom tool configuration with name: {deployment_name}"
            )
            try:
                existing_config = get_custom_tool_config_by_name(deployment_name)

                if existing_config:
                    logger.debug(
                        f"Found custom tool configuration: {existing_config.get('name')}. Deleting it."
                    )
                    delete_custom_tool_config_by_name(deployment_name)
                    logger.debug(f"Custom tool configuration deleted successfully.")
                else:
                    logger.debug(
                        "No custom tool configuration found for this deployment."
                    )
            except Exception as e:
                logger.debug("No custom tool configuration found for this deployment.")

    except Exception as e:
        logger.warning(f"Could not retrieve deployment details before deletion: {e}")

    # Now delete the MCP server deployment
    url = f"{Config.XMAGIC_BASE_PATH}/v1/mcp-servers/{deployment_id}"

    async with httpx.AsyncClient(timeout=DEFAULT_HTTPX_TIMEOUT) as client:
        response = await client.delete(
            url,
            headers={"x-api-key": xchat_api_key},
        )
        response.raise_for_status()
        result = response.json()["data"]

    logger.info(f"MCP server deployment deleted successfully.")
    return result


async def stop_mcp_server_deployment(xchat_api_key: str, deployment_id: str) -> Dict:
    """
    Stop an MCP server deployment by hitting the /stop endpoint.

    Args:
        xchat_api_key: Your Stochastic API key
        deployment_id: The deployment ID to stop

    Returns:
        Dictionary with stop confirmation
    """
    url = f"{Config.XMAGIC_BASE_PATH}/v1/mcp-servers/{deployment_id}/stop"

    async with httpx.AsyncClient(timeout=DEFAULT_HTTPX_TIMEOUT) as client:
        response = await client.post(
            url,
            headers={"x-api-key": xchat_api_key},
        )
        response.raise_for_status()
        result = response.json()["data"]

    logger.info(f"MCP server deployment stopped successfully.")
    return result


async def monitor_deployment_until_ready(
    xchat_api_key: str,
    deployment_id: str,
    max_wait_seconds: int = 300,
    check_interval: int = 5,
) -> Dict:
    """
    Monitor a deployment until it's ready (running) or failed.

    Args:
        xchat_api_key: Your Stochastic API key
        deployment_id: The deployment ID to monitor
        max_wait_seconds: Maximum time to wait in seconds (default: 300 = 5 minutes)
        check_interval: Time between status checks in seconds (default: 5)

    Returns:
        Final deployment status dictionary

    Raises:
        TimeoutError: If deployment doesn't become ready within max_wait_seconds
        RuntimeError: If deployment fails
    """
    start_time = time.time()

    logger.info(f"🚀 Starting deployment monitoring...")
    logger.info(f"📦 Deployment ID: {deployment_id}")

    while True:
        elapsed = time.time() - start_time

        if elapsed > max_wait_seconds:
            raise TimeoutError(
                f"Deployment did not become ready within {max_wait_seconds} seconds"
            )

        try:
            status = await get_mcp_server_deployment_status(
                xchat_api_key, deployment_id
            )
            current_status = status.get("status")

            # Only log if status changed
            if current_status in ["deploying", "deployed"]:
                logger.info(f"⏳ Deployment in progress...")
            elif current_status == "running":
                logger.info(f"✅ Deployment is running!")
                return status
            elif current_status == "failed":
                logger.error(f"❌ Deployment failed!")
                # Try to get logs for debugging
                try:
                    logs = await get_mcp_server_deployment_logs(
                        xchat_api_key, deployment_id
                    )
                    # Format logs properly - extract string content from dict structure
                    formatted_logs = _format_logs_for_display(logs)
                    logger.error(f"📋 Deployment logs:\n{formatted_logs}")
                except Exception:
                    pass
                raise RuntimeError("Deployment failed. Check logs for details.")
            else:
                logger.info(f"📊 Status: {current_status}")
        except (TimeoutError, RuntimeError):
            raise
        except Exception as e:
            logger.debug(f"Error checking deployment status: {e}")

        await asyncio.sleep(check_interval)


async def deploy_and_monitor(
    xchat_api_key: str,
    name: Optional[str] = None,
    code_directory: str = None,
    entry_point_file_path: Optional[str] = None,
    description: Optional[str] = None,
    env_vars: Optional[Dict[str, str]] = None,
    secret_env_vars: Optional[Dict[str, str]] = None,
    port: int = 8000,
    show_logs: bool = True,
    **kwargs,
) -> Dict:
    """
    Deploy an MCP server and monitor until ready, then show logs.

    This provides a local-like experience where you see the deployment progress
    and logs as if running locally.

    Args:
        xchat_api_key: Your Stochastic API key
        name: Deployment name (auto-generated if not provided)
        code_directory: Path to code directory
        entry_point_file_path: Optional path to entry point file (will be renamed to mcp_server.py)
        description: Optional description
        env_vars: Non-sensitive environment variables
        secret_env_vars: Sensitive environment variables
        show_logs: Whether to show logs after deployment is ready (default: True)
        **kwargs: Additional deployment parameters

    Returns:
        Dictionary with deployment information and logs
    """
    # Deploy
    logger.info("=" * 60)
    logger.info("🌟 Starting MCP Server Deployment")
    logger.info("=" * 60)

    result = await deploy_mcp_server_to_cloud(
        xchat_api_key=xchat_api_key,
        name=name,
        code_directory=code_directory,
        entry_point_file_path=entry_point_file_path,
        description=description,
        env_vars=env_vars,
        secret_env_vars=secret_env_vars,
        port=port,
        **kwargs,
    )

    deployment_id = result.get("id")
    deployment_name = result.get("name")

    logger.info(f"📝 Deployment Name: {deployment_name}")
    logger.info(f"🆔 Deployment ID: {deployment_id}")

    # Monitor until ready
    try:
        final_status = await monitor_deployment_until_ready(
            xchat_api_key=xchat_api_key,
            deployment_id=deployment_id,
        )

        logger.info("")
        logger.info("=" * 60)
        logger.info("✨ Deployment Complete!")
        logger.info("=" * 60)
        logger.info(f"🌐 Your MCP server is now running in the cloud")

        # Get the actual endpoint URL from the deployment object
        endpoint_url = final_status.get("url")
        if endpoint_url:
            logger.info(f"📍 Endpoint: {endpoint_url}")
        else:
            # Fallback to constructed URL if not available
            logger.info(
                f"📍 Endpoint: {Config.XMAGIC_BASE_PATH}/v1/mcp-servers/{deployment_id}"
            )

        logger.info("=" * 60)

        logger.info("Creating custom tool configuration on the cloud")
        try:
            existing_config = get_custom_tool_config_by_name(deployment_name)
            logger.info(
                f"Custom tool configuration already exists with name '{deployment_name}'. Updating it."
            )
            update_custom_tool_config_by_name(
                prev_name=deployment_name,
                name=deployment_name,
                description=description,
                server_url=endpoint_url,
                api_key=None,
            )
            logger.info(
                f"Custom tool configuration '{deployment_name}' updated successfully."
            )
        except Exception as e:
            logger.info("Creating new custom tool configuration.")

            create_custom_tool_config(
                name=deployment_name,
                description=description,
                server_url=endpoint_url,
                api_key=None,
            )

            logger.info(
                f"Custom tool configuration for deployment '{deployment_name}' created successfully."
            )

        # Stream logs if requested
        if show_logs:
            logger.info("")
            try:
                await stream_mcp_server_deployment_logs(xchat_api_key, deployment_id)
            except Exception as e:
                logger.warning(f"Could not stream logs: {e}")

        return {
            **final_status,
            "logs_shown": show_logs,
        }

    except Exception as e:
        logger.error(f"❌ Deployment failed: {e}")
        raise
