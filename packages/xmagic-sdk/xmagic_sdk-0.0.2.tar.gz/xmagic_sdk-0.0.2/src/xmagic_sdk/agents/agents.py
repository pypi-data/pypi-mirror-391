from typing import Dict, Any, Optional
import requests
from xmagic_sdk.logging.logging import configure_logger
from xmagic_sdk.config import Config
from xmagic_sdk.utils.config_utils import get_api_key

logger = configure_logger(__name__)


def get_persona_by_id(persona_id: str):
    response = requests.get(
        url=f"{Config.XMAGIC_BASE_PATH}/v1/personas/{persona_id}",
        headers={"x-api-key": get_api_key()},
    )

    response.raise_for_status()

    persona_json = response.json()["data"]
    return persona_json


def get_temporary_config_id_from_agent(agent_id: str):
    personda_data = get_persona_by_id(agent_id)
    temporary_config_id = personda_data["temporary_config_id"]

    return temporary_config_id


def get_deployed_config_id_from_agent(agent_id: str):
    personda_data = get_persona_by_id(agent_id)
    deployed_config_id = personda_data["deployed_config_id"]

    return deployed_config_id


def get_tools_from_job(agent_id: str, job_id: str, config_id: str):
    response = requests.get(
        url=f"{Config.XMAGIC_BASE_PATH}/v1/personas/{agent_id}/configs/{config_id}/subagents/{job_id}/tools",
        headers={"x-api-key": get_api_key()},
    )

    response.raise_for_status()

    return response.json()["data"]


def get_tool_from_job(agent_id: str, job_id: str, config_id: str, tool_id: str):
    response = requests.get(
        url=f"{Config.XMAGIC_BASE_PATH}/v1/personas/{agent_id}/configs/{config_id}/subagents/{job_id}/tools/{tool_id}",
        headers={"x-api-key": get_api_key()},
    )

    response.raise_for_status()

    return response.json()["data"]


def create_custom_tool_config(
    name: str,
    description: str,
    server_url: str,
    api_key: str = None,
):
    response = requests.post(
        url=f"{Config.XMAGIC_BASE_PATH}/v1/custom-tool-configs",
        headers={"x-api-key": get_api_key()},
        json={
            "name": name,
            "description": description,
            "server_url": server_url,
            "api_key": api_key,
        },
    )
    response.raise_for_status()
    return response.json()["data"]


def get_custom_tool_config_by_name(name: str):
    response = requests.get(
        url=f"{Config.XMAGIC_BASE_PATH}/v1/custom-tool-configs/name",
        params={"name": name},
        headers={"x-api-key": get_api_key()},
    )
    response.raise_for_status()
    return response.json()["data"]


def delete_custom_tool_config_by_name(name: str):
    response = requests.delete(
        url=f"{Config.XMAGIC_BASE_PATH}/v1/custom-tool-configs/name",
        params={"name": name},
        headers={"x-api-key": get_api_key()},
    )
    response.raise_for_status()
    return True


def update_custom_tool_config_by_name(
    prev_name: str,
    name: str,
    description: str,
    server_url: str,
    api_key: str = None,
):
    response = requests.put(
        url=f"{Config.XMAGIC_BASE_PATH}/v1/custom-tool-configs/name",
        headers={"x-api-key": get_api_key()},
        params={"name": prev_name},
        json={
            "name": name,
            "description": description,
            "server_url": server_url,
            "api_key": api_key,
        },
    )
    response.raise_for_status()
    return response.json()["data"]


def update_custom_tool_config(
    custom_tool_config_id: str,
    name: str,
    description: str,
    server_url: str,
    api_key: str = None,
):
    response = requests.put(
        url=f"{Config.XMAGIC_BASE_PATH}/v1/custom-tool-configs/{custom_tool_config_id}",
        headers={"x-api-key": get_api_key()},
        json={
            "name": name,
            "description": description,
            "server_url": server_url,
            "api_key": api_key,
        },
    )
    response.raise_for_status()
    return response.json()["data"]


def delete_custom_tool_config(custom_tool_config_id: str):
    response = requests.delete(
        url=f"{Config.XMAGIC_BASE_PATH}/v1/custom-tool-configs/{custom_tool_config_id}",
        headers={"x-api-key": get_api_key()},
    )
    response.raise_for_status()
    return True


def create_custom_tool(
    agent_id: str,
    job_id: str,
    config_id: str,
    custom_tool_config_id: str,
):
    response = requests.post(
        url=f"{Config.XMAGIC_BASE_PATH}/v1/personas/{agent_id}/configs/{config_id}/subagents/{job_id}/tools/custom",
        headers={"x-api-key": get_api_key()},
        json={
            "custom_tool_config_id": custom_tool_config_id,
        },
    )
    response.raise_for_status()
    return response.json()["data"]


def delete_tool_from_agent(agent_id: str, config_id: str, job_id: str, tool_id: str):
    response = requests.delete(
        url=f"{Config.XMAGIC_BASE_PATH}/v1/personas/{agent_id}/configs/{config_id}/subagents/{job_id}/tools/{tool_id}",
        headers={"x-api-key": get_api_key()},
    )
    response.raise_for_status()
    return True
