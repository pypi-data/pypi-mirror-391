from enum import Enum
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field


class ChatType(str, Enum):
    PLAYGROUND = "playground"
    INTERACT = "interact"
    CONFIGURATION = "configuration"
    STANDARD = "standard"


class CustomToolArgs(BaseModel):
    name: str
    value: str


class ToolCall(BaseModel):
    tool_name: str
    arguments: Dict[str, Any] = Field(default_factory=dict)
    images: Dict[str, str] = Field(default_factory=dict)  # All images
    files: Dict[str, str] = Field(default_factory=dict)  # All files
    current_message_images: Dict[str, str] = Field(
        default_factory=dict
    )  # Images in the current message
    current_message_files: Dict[str, str] = Field(
        default_factory=dict
    )  # Files in the current message
    current_agent_id: Optional[str] = None  # ID of the agent that sent the message
    current_job_id: Optional[str] = None  # ID of the job that sent the message
    chat_type: Optional[ChatType] = ChatType.INTERACT
    chat_id: Optional[str] = None  # ID of the chat
    message_id: Optional[str] = None  # ID of the message
    user_id: Optional[str] = None  # ID of the user
    user_type: Optional[str] = None  # Type of the user
    custom_tool_id: Optional[str] = None  # ID of the custom tool configuration
    custom_args: Optional[List[CustomToolArgs]] = Field(default_factory=list)

    def parse_arguments(self):
        """Parses argument values from str to int, float, bool, or keeps as str."""

        def parse_value(value: Any) -> Any:
            if isinstance(value, str):
                if value.startswith("+") and value[1:].isdigit():  # Phone numbers
                    return value

                # Try to parse as int
                if value.isdigit():
                    return int(value)
                # Try to parse as float
                try:
                    return float(value)
                except ValueError:
                    pass
                # Try to parse as bool
                lower_value = value.lower()
                if lower_value in {"true", "false"}:
                    return lower_value == "true"
                # Keep as str
                return value
            elif isinstance(value, list):
                return [parse_value(item) for item in value]
            elif isinstance(value, dict):
                return {k: parse_value(v) for k, v in value.items()}
            else:
                return value  # Non-str type, keep as-is

        # Apply parsing to all arguments
        self.arguments = {
            key: parse_value(value) for key, value in self.arguments.items()
        }


class MCPToolLiveUpdate(BaseModel):
    class_id: str = Field(default="MCPToolLiveUpdate")
    update: str


class MCPToolResult(BaseModel):
    class_id: str = Field(default="MCPToolResult")
    result: str
    files: List[str] = Field(default_factory=list)


class Resource(BaseModel):
    uri: str


class Prompt(BaseModel):
    name: str
    arguments: Dict[str, str]
