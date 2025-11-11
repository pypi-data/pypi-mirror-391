import collections.abc
import inspect
import json
import os
from typing import Dict, List, Optional
from fastapi import Depends, FastAPI, HTTPException, Security
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.security.api_key import APIKeyHeader
from fastapi.encoders import jsonable_encoder
from starlette.status import HTTP_403_FORBIDDEN
import uvicorn
from xmagic_sdk.mcp.registry import MCPRegistry
from xmagic_sdk.mcp.mcp_models import ToolCall
from xmagic_sdk.logging.logging import configure_logger
from xmagic_sdk.config import Config
from xmagic_sdk.utils.config_utils import get_api_key
import asyncio
from xmagic_sdk.mcp.deploy_mcp import (
    deploy_and_monitor,
    deploy_mcp_server_to_cloud,
    validate_mcp_code_remote,
)

from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi import Request
import inspect


logger = configure_logger(__name__)

# Create a global registry instance
registry = MCPRegistry()


def _create_app(prompt: str, api_key: Optional[str] = None) -> FastAPI:
    app = FastAPI()

    # Set up API key authentication
    API_KEY_NAME = "X-API-Key"
    api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

    async def verify_api_key(api_key_header: str = Security(api_key_header)):
        if api_key is None:
            return  # No authentication required if no API key is set
        if api_key_header is None:
            raise HTTPException(
                status_code=HTTP_403_FORBIDDEN, detail="API key header is missing"
            )
        if api_key_header != api_key:
            raise HTTPException(
                status_code=HTTP_403_FORBIDDEN, detail="Invalid API key"
            )
        return api_key_header

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ):
        # Log the raw body and FastAPI’s detail so we always know *why* it failed
        try:
            body_bytes = await request.body()
            body = body_bytes.decode() or "<binary>"
        except Exception:
            body = "<unreadable>"

        logger.error(
            "422 on %s\n└─ BODY   %s\n└─ DETAIL %s",
            request.url.path,
            body,
            json.dumps(exc.errors(), indent=2),
        )
        # Pass FastAPI's default 422 payload back to the client
        return JSONResponse(status_code=422, content={"detail": exc.errors()})

    @app.get("/v1/health")
    async def health_check():
        return {"status": "ok"}

    @app.get("/v1/prompt")
    async def get_prompt(verified_api_key: str = Depends(verify_api_key)):
        return prompt

    @app.get("/v1/tools/")
    async def list_tools(verified_api_key: str = Depends(verify_api_key)):
        tools = registry.get_tool_specifications()
        return jsonable_encoder(tools)

    @app.get("/v1/files/{file_id}")
    async def get_file(file_id: str, verified_api_key: str = Depends(verify_api_key)):
        file_path = registry.get_file_path(file_id)
        if file_path is None:
            logger.debug(f"File {file_id} not found")
            raise HTTPException(status_code=404, detail="File not found")

        return FileResponse(
            file_path, filename=file_id, media_type="application/octet-stream"
        )

    @app.post("/v1/tools/")
    async def call_tool(
        tool_call: ToolCall, verified_api_key: str = Depends(verify_api_key)
    ):
        tool_call.parse_arguments()
        logger.debug(
            f"Calling tool {tool_call.tool_name} with arguments {tool_call.arguments}. Images: {tool_call.images}. Files: {tool_call.files}. Current message images: {tool_call.current_message_images}. Current message files: {tool_call.current_message_files}. Current agent ID: {tool_call.current_agent_id}. Current job ID: {tool_call.current_job_id}. Chat type: {tool_call.chat_type}. Chat ID: {tool_call.chat_id}. Message ID: {tool_call.message_id}. Custom args: {tool_call.custom_args}. User ID: {tool_call.user_id}. User Type: {tool_call.user_type}. Custom tool ID: {tool_call.custom_tool_id}"
        )
        result = await registry.execute_tool(
            tool_name=tool_call.tool_name,
            tool_args=tool_call.arguments,
            images=tool_call.images,
            files=tool_call.files,
            current_message_images=tool_call.current_message_images,
            current_message_files=tool_call.current_message_files,
            current_agent_id=tool_call.current_agent_id,
            current_job_id=tool_call.current_job_id,
            chat_type=tool_call.chat_type,
            custom_args=tool_call.custom_args,
            chat_id=tool_call.chat_id,
            message_id=tool_call.message_id,
            user_id=tool_call.user_id,
            user_type=tool_call.user_type,
            custom_tool_id=tool_call.custom_tool_id,
        )

        if isinstance(result, collections.abc.AsyncIterator):
            logger.debug(f"Tool {tool_call.tool_name} returned iterator")

            async def event_stream():
                async for item in result:
                    yield json.dumps(jsonable_encoder(item))

            return StreamingResponse(
                event_stream(),
                media_type="text/event-stream",
                headers={
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                },
            )
        else:
            logger.debug(f"Tool {tool_call.tool_name} returned: {result}")
            return jsonable_encoder(result)

    return app


def run_mcp_server(
    prompt: str,
    port: int = 8000,
    run_on_cloud: bool = False,
    xchat_api_key: Optional[str] = None,
    deployment_name: Optional[str] = None,
    code_directory: Optional[str] = None,
    entry_point_file_path: Optional[str] = None,
    env_vars: Optional[Dict[str, str]] = None,
    secret_env_vars: Optional[Dict[str, str]] = None,
    show_logs: bool = True,
    description: Optional[str] = None,
    docker_image: str = "python:3.11",
    command: Optional[List[str]] = None,
    args: Optional[List[str]] = None,
    health_path: str = "/v1/health",
    code_mount_path: str = "/code",
    ram_memory_gb: float = 0.5,
    cpu_millicores: int = 500,
    replicas: int = 1,
):
    """
    Run an MCP server locally or deploy it to Stochastic's cloud.

    Args:
        prompt: The prompt for the MCP server
        port: Port to run the server on (only used for local deployment)
        run_on_cloud: If True, deploy to Stochastic's cloud instead of running locally
        xchat_api_key: API key for authentication (optional for local, required for cloud)
        deployment_name: Name for cloud deployment (auto-generated if not provided)
        code_directory: Path to code directory (optional. If not provided, the directory where the script is located is used)
        env_vars: Non-sensitive environment variables (optional)
        secret_env_vars: Sensitive environment variables (optional)
        show_logs: Whether to show deployment logs after cloud deployment (default: True)
        description: Description of the MCP server (optional)
        docker_image: Docker image to use for cloud deployment (default: python:3.11)
        command: Command to run in the container (overrides default)
        args: Arguments for the command (overrides default)
        health_path: Health check endpoint path (default: /v1/health)
        code_mount_path: Path to mount code in the container (default: /code)
        ram_memory_gb: RAM allocation in GB for cloud deployment (default: 0.5)
        cpu_millicores: CPU allocation in millicores for cloud deployment (default:
            500)
        replicas: Number of replicas for cloud deployment (default: 1)

    Examples:
        # Run locally
        run_mcp_server(prompt="My MCP server", port=8000)

        # Deploy to cloud with auto-generated name
        run_mcp_server(
            prompt="My MCP server",
            run_on_cloud=True,
            code_directory="./my_mcp_code"
        )

        # Deploy to cloud with specific name
        run_mcp_server(
            prompt="My MCP server",
            run_on_cloud=True,
            deployment_name="my-mcp-server",
            code_directory="./my_mcp_code"
        )

        # Deploy to cloud with custom configuration
        run_mcp_server(
            prompt="My MCP server",
            run_on_cloud=True,
            deployment_name="my-mcp-server",
            code_directory="./my_mcp_code",
            ram_memory_gb=1.0,
            cpu_millicores=1000,
            replicas=2,
            env_vars={"LOG_LEVEL": "INFO"}
        )
    """
    if run_on_cloud and not Config.MCP_RUN_LOCALLY and not Config.RUN_LOCALLY_FROM_CLI:
        xchat_api_key = get_api_key()

        if not xchat_api_key and not Config.XCHAT_API_KEY:
            raise ValueError(
                "API key is required for cloud deployment. "
                "Set XCHAT_API_KEY environment variable or pass xchat_api_key parameter."
            )

        if not xchat_api_key and Config.XCHAT_API_KEY:
            xchat_api_key = Config.XCHAT_API_KEY

        if not entry_point_file_path:
            frame = inspect.stack()[1]
            logger.debug(f"Inferring entry point file from caller: {frame.filename}")
            entry_point_file_path = frame.filename

        if not code_directory and entry_point_file_path:
            code_directory = os.path.dirname(entry_point_file_path)
            logger.debug(
                f"Using inferred code directory from entry point: {code_directory}"
            )

        if not code_directory:
            # If no code directory is provided, we assume it is the caller of this function
            frame = inspect.stack()[1]
            logger.debug(f"Inferring code directory from caller: {frame.filename}")
            code_directory = os.path.dirname(frame.filename)
            logger.debug(f"Using inferred code directory: {code_directory}")

        is_valid, err = asyncio.run(
            validate_mcp_code_remote(
                xchat_api_key=xchat_api_key,
                code_directory=code_directory,
                is_custom_tool=True,
                entry_point_file_path=entry_point_file_path,
            )
        )

        if not is_valid:
            raise ValueError(f"MCP code validation failed: {err}")

        # Use xchat_api_key from args or environment
        xchat_api_key = xchat_api_key or Config.XCHAT_API_KEY
        if not xchat_api_key:
            raise ValueError(
                "API key is required for cloud deployment. "
                "Set XCHAT_API_KEY environment variable or pass xchat_api_key parameter."
            )

        # Deploy and monitor with local-like experience
        result = asyncio.run(
            deploy_and_monitor(
                xchat_api_key=xchat_api_key,
                name=deployment_name,  # Can be None, will auto-generate
                code_directory=code_directory,
                entry_point_file_path=entry_point_file_path,
                port=port,
                description=description,
                env_vars=env_vars,
                secret_env_vars=secret_env_vars,
                show_logs=show_logs,
                docker_image=docker_image,
                command=command,
                args=args,
                health_path=health_path,
                code_mount_path=code_mount_path,
                ram_memory_gb=ram_memory_gb,
                cpu_millicores=cpu_millicores,
                replicas=replicas,
            )
        )

        return result
    else:
        # Run locally
        app = _create_app(prompt)
        logger.info("=" * 60)
        logger.info(f"🚀 Starting MCP server locally on port {port}...")
        logger.info("=" * 60)
        uvicorn.run(app, host="0.0.0.0", port=port)
