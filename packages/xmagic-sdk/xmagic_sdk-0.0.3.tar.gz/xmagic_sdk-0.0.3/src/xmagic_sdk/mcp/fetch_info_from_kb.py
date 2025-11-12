from pathlib import Path
import tempfile
from typing import List
import uuid
import httpx
from xmagic_sdk.config import Config, DEFAULT_HTTPX_TIMEOUT
from xmagic_sdk.logging.logging import configure_logger

logger = configure_logger(__name__)


async def fetch_info_from_kb_v1(query: str, api_key: str, chatbot_id: str) -> dict:
    async with httpx.AsyncClient(timeout=DEFAULT_HTTPX_TIMEOUT) as client:
        response = await client.post(
            f"{Config.XCHAT_BASE_PATH}/v1/knowledge-bases/search",
            json={
                "query": query,
            },
            params={
                "chatbot_id": chatbot_id,
            },
            headers={"x-api-key": api_key},
        )
        response.raise_for_status()
        return response.json()


async def fetch_info_from_kb_v3(query: str, api_key: str, kb_ids: List[str]) -> dict:
    async with httpx.AsyncClient(timeout=DEFAULT_HTTPX_TIMEOUT) as client:
        response = await client.post(
            f"{Config.XMAGIC_BASE_PATH}/v1/knowledge-bases/search",
            json={"query": query, "knowledge_base_ids": kb_ids},
            headers={"x-api-key": api_key},
        )
        response.raise_for_status()
        return response.json()


async def get_data_sources_from_kb(
    api_key: str,
    knowledge_base_id: str,
):
    url = (
        f"{Config.XMAGIC_BASE_PATH}/v1/knowledge-bases/{knowledge_base_id}/data-sources"
    )
    async with httpx.AsyncClient(timeout=DEFAULT_HTTPX_TIMEOUT) as client:
        response = await client.get(
            url,
            headers={"x-api-key": api_key},
            params={
                "page_size": 1000,
            },
        )
        response.raise_for_status()
        data_sources_response = response.json()

        return data_sources_response["data"].get("data_sources", [])


async def download_data_source(
    api_key: str,
    knowledge_base_id: str,
    data_source_id: str,
    local_file_path: str = None,
):
    url = f"{Config.XMAGIC_BASE_PATH}/v1/knowledge-bases/{knowledge_base_id}/data-sources/{data_source_id}"
    async with httpx.AsyncClient(timeout=DEFAULT_HTTPX_TIMEOUT) as client:
        response = await client.get(
            url,
            headers={"x-api-key": api_key},
            params={"downloadable_link": "true"},
        )
        response.raise_for_status()
        data_source_response = response.json()["data"]

        if "downloadable_link" in data_source_response:
            downloadable_link = data_source_response["downloadable_link"]
            data_source_title = data_source_response["title"]

            # Download the file from the provided link
            async with httpx.AsyncClient(
                timeout=DEFAULT_HTTPX_TIMEOUT
            ) as download_client:
                download_response = await download_client.get(downloadable_link)
                download_response.raise_for_status()

                if local_file_path:
                    temp_file = local_file_path
                else:
                    temp_file = (
                        Path(tempfile.gettempdir())
                        / str(uuid.uuid4())
                        / str(data_source_title)
                    )
                    temp_file.parent.mkdir(parents=True, exist_ok=True)
                    temp_file = str(temp_file)

                with open(temp_file, "wb") as file:
                    file.write(download_response.content)

            logger.info(f"Data source {data_source_title} downloaded to {temp_file}")
            return temp_file
        else:
            raise ValueError("Data source is not downloadable.")


async def upload_data_source(
    api_key: str,
    knowledge_base_id: str,
    file_path: str,
    data_source_title: str,
    trigger_indexing: bool = False,
):
    file_id = None
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

    if not file_id:
        raise ValueError("File upload failed, no file ID returned.")

    url = f"{Config.XMAGIC_BASE_PATH}/v1/knowledge-bases/{knowledge_base_id}/data-sources/documents"
    async with httpx.AsyncClient(timeout=DEFAULT_HTTPX_TIMEOUT) as client:
        response = await client.post(
            url,
            headers={"x-api-key": api_key},
            json={
                "file_id": file_id,
                "data_source_title": data_source_title,
                "trigger_indexing": trigger_indexing,
            },
        )
        response.raise_for_status()
        return response.json()["data"]


async def update_data_source(
    api_key: str,
    knowledge_base_id: str,
    data_source_id: str,
    new_file_content_path: str,
    trigger_indexing: bool = False,
):
    file_id = None
    file_upload_url = f"{Config.XMAGIC_BASE_PATH}/v1/uploaded-files"
    async with httpx.AsyncClient(timeout=DEFAULT_HTTPX_TIMEOUT) as client:
        with open(new_file_content_path, "rb") as file:
            response = await client.post(
                file_upload_url,
                files={"file": (Path(new_file_content_path).name, file)},
                headers={"x-api-key": api_key},
            )
            response.raise_for_status()
            file_id = response.json()["data"]

    if not file_id:
        raise ValueError("File upload failed, no file ID returned.")

    url = f"{Config.XMAGIC_BASE_PATH}/v1/knowledge-bases/{knowledge_base_id}/data-sources/{data_source_id}/file-content"
    async with httpx.AsyncClient(timeout=DEFAULT_HTTPX_TIMEOUT) as client:
        response = await client.put(
            url,
            headers={"x-api-key": api_key},
            json={"file_id": file_id, "trigger_indexing": trigger_indexing},
        )
        response.raise_for_status()
        return response.json()["data"]


async def delete_data_source(
    api_key: str,
    knowledge_base_id: str,
    data_source_id: str,
):
    url = f"{Config.XMAGIC_BASE_PATH}/v1/knowledge-bases/{knowledge_base_id}/data-sources/{data_source_id}"
    async with httpx.AsyncClient(timeout=DEFAULT_HTTPX_TIMEOUT) as client:
        response = await client.delete(
            url,
            headers={"x-api-key": api_key},
        )
        response.raise_for_status()
        return response.json()


async def get_data_sources_from_kb_v1(
    api_key: str, knowledge_base_id: str, chatbot_id: str
):
    url = f"{Config.XCHAT_BASE_PATH}/v1/knowledge-base/{knowledge_base_id}/data-sources"
    async with httpx.AsyncClient(timeout=DEFAULT_HTTPX_TIMEOUT) as client:
        response = await client.get(
            url,
            headers={"x-api-key": api_key},
            params={"page_size": 1000, "chatbot_id": chatbot_id},
        )
        response.raise_for_status()
        data_sources_response = response.json()

        return data_sources_response["data"].get("data_sources", [])


async def update_data_source_v1(
    api_key: str,
    knowledge_base_id: str,
    data_source_id: str,
    new_file_content_path: str,
    chatbot_id: str,
    trigger_indexing: bool = False,
):
    file_id = None
    file_upload_url = f"{Config.XCHAT_BASE_PATH}/v1/uploaded-files"
    async with httpx.AsyncClient(timeout=DEFAULT_HTTPX_TIMEOUT) as client:
        with open(new_file_content_path, "rb") as file:
            response = await client.post(
                file_upload_url,
                files={"file": (Path(new_file_content_path).name, file)},
                headers={"x-api-key": api_key},
            )
            response.raise_for_status()
            file_id = response.json()["data"]

    if not file_id:
        raise ValueError("File upload failed, no file ID returned.")

    url = f"{Config.XCHAT_BASE_PATH}/v1/knowledge-base/{knowledge_base_id}/data-sources/{data_source_id}/file-content"
    async with httpx.AsyncClient(timeout=DEFAULT_HTTPX_TIMEOUT) as client:
        response = await client.put(
            url,
            params={"chatbot_id": chatbot_id},
            headers={"x-api-key": api_key},
            json={"file_id": file_id, "trigger_indexing": trigger_indexing},
        )
        response.raise_for_status()
        return response.json()["data"]
