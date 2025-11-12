from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import httpx

from xmagic_sdk.config import Config, DEFAULT_HTTPX_TIMEOUT
from xmagic_sdk.logging.logging import configure_logger

logger = configure_logger(__name__)


async def upload_new_artifact(
    api_key: str,
    agent_id: str,
    description: str,
    file_path: Optional[Union[List[str], str]] = None,
    data: Optional[Dict[str, Any]] = None,
    chat_id: Optional[str] = None,
    message_id: Optional[str] = None,
    user_id: Optional[str] = None,
    user_type: Optional[str] = None,
    custom_tool_id: Optional[str] = None,
):
    file_ids = []

    file_paths = file_path

    if file_paths and isinstance(file_paths, str):
        file_paths = [file_paths]

    for file_path in file_paths:
        file_upload_url = f"{Config.XMAGIC_BASE_PATH}/v1/uploaded-files"
        async with httpx.AsyncClient(timeout=DEFAULT_HTTPX_TIMEOUT) as client:
            with open(file_path, "rb") as file:
                response = await client.post(
                    file_upload_url,
                    files={"file": (Path(file_path).name, file)},
                    headers={"x-api-key": api_key},
                )
                response.raise_for_status()
                file_id = response.json()["data"]
                file_ids.append(file_id)

    url = f"{Config.XMAGIC_BASE_PATH}/v1/personas/{agent_id}/datastore/upload-custom-artifact-custom-tool"
    async with httpx.AsyncClient(timeout=DEFAULT_HTTPX_TIMEOUT) as client:
        response = await client.post(
            url,
            headers={"x-api-key": api_key},
            json={
                "file_ids": file_ids,
                "data": data,
                "description": description,
                "chat_id": chat_id,
                "message_id": message_id,
                "user_id": user_id,
                "user_type": user_type,
                "custom_tool_id": custom_tool_id
            },
        )
        response.raise_for_status()
        return response.json()["data"]
