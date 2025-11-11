import json
import time
from bson import ObjectId
import requests
from typing import Dict, Optional
from xmagic_sdk.logging.logging import configure_logger
from xmagic_sdk.config import Config
from xmagic_sdk.utils.config_utils import get_api_key
from xmagic_sdk.models.chatting import Message


logger = configure_logger(__name__)


def _get_chat_id(chatbot_id: str):
    url = f"{Config.XCHAT_BASE_PATH}/v1/chatbots/{chatbot_id}"
    headers = {"x-api-key": get_api_key()}

    response = requests.get(
        url=url,
        headers=headers,
    )
    response.raise_for_status()

    output_json = response.json()

    return output_json["data"]["chatbot"]["chatId"]


def create_new_chat(
    agent_id: str,
    title: str = "Test chat - SDK",
    chat_mode: str = "web",
    chat_type: str = "playground",
):
    """Create a new chat for either a persona or chatbot.

    Args:
        agent_id: The persona ID or chatbot ID
        is_persona: If True, creates chat for persona; if False, creates chat for chatbot
        title: Title for the chat
        chat_mode: Chat mode (e.g., "web", "text")
        chat_type: Chat type (e.g., "playground")

    Returns:
        The created chat ID
    """
    url = f"{Config.XMAGIC_BASE_PATH}/v1/personas/{agent_id}/chats"

    headers = {"x-api-key": get_api_key()}

    response = requests.post(
        url=url,
        headers=headers,
        json={
            "title": title,
            "chat_mode": chat_mode,
            "chat_type": chat_type,
        },
    )
    response.raise_for_status()
    output_json = response.json()

    chat_id = output_json["data"]["chat"]["id"]

    return chat_id


def chat(
    agent_id: str,
    chat_id: str,
    query: str,
    job_id: Optional[str] = None,
    simulate_voice: bool = False,
    stream: bool = False,
):
    """Send a query to a chat session.

    Args:
        agent_id: The persona ID or chatbot ID
        chat_id: The chat session ID
        query: The user query
        job_id: Optional job ID for routing
        simulate_voice: If True, simulates voice interaction
        stream: If True, streams the response to stdout

    Returns:
        Message object with the response
    """

    url = f"{Config.XMAGIC_BASE_PATH}/v1/personas/{agent_id}/chats/{chat_id}/query"

    message_sender_id = str(ObjectId())
    message_id = str(ObjectId())

    body = {
        "message_id": message_id,
        "message_sender_id": message_sender_id,
        "message_type": "ai_chat",
        "model_type": "open_source",
        "query": query,
        "is_stream": True,
        "is_regenerate": False,
        "parse_response": True,
        "is_voice": simulate_voice,
    }

    if job_id:
        body["subagent_id"] = job_id

    headers = {
        "x-api-key": get_api_key(),
        "Accept": "text/event-stream",  # Explicitly request event stream
    }

    is_first_token_from_response = True
    is_first_token_from_reasoning = True

    try:
        if not stream:
            raise NotImplementedError("Non-streaming mode is not implemented yet.")
        else:
            with requests.post(
                url=url, headers=headers, json=body, stream=True
            ) as response:
                response.raise_for_status()

                for chunk in response.iter_content(
                    chunk_size=None, decode_unicode=True
                ):
                    if chunk:
                        json_object = json.loads(chunk)

                        if json_object.get("type") == "reasoning":
                            if is_first_token_from_reasoning:
                                print("\033[92m\n\nReasoning:\033[0m")
                                is_first_token_from_reasoning = False
                            reasoning_token = json_object["text"]
                            print(reasoning_token, end="", flush=True)
                        elif json_object.get("type") == "response":
                            if is_first_token_from_response:
                                print("\033[93m\n\nResponse:\033[0m")
                                is_first_token_from_response = False
                            response_token = json_object["text"]
                            print(response_token, end="", flush=True)
                        elif json_object.get("type") == "ping":
                            pass
                        elif json_object.get("type") == "error":
                            print(f"\n\nError: {json_object.get('text')}")
                            break
                        elif json_object.get("type") == "live_update":
                            print(
                                "\033[92m\n\nLive update:\033[0m",
                                json_object.get("text", "") + "\n\n",
                            )

    except requests.exceptions.RequestException as e:
        logger.error(f"Streaming error: {e}")
        raise

    print("")

    # Get the message info once it has finished the streaming to return it
    url = f"{Config.XMAGIC_BASE_PATH}/v1/personas/{agent_id}/chats/{chat_id}/messages/{message_id}"

    headers = {
        "x-api-key": get_api_key(),
    }
    response = requests.get(url=url, headers=headers)
    logger.debug(response.text)
    response.raise_for_status()
    output_json = response.json()["data"]
    message = Message.model_validate(output_json)

    return message
