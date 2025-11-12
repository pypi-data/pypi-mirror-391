import asyncio
from dataclasses import dataclass
import inspect
import functools
from typing import (
    Any,
    Callable,
    Dict,
    List,
    Optional,
    Union,
    get_args,
    get_origin,
    get_type_hints,
)
from xmagic_sdk.logging.logging import configure_logger
from xmagic_sdk.mcp.mcp_models import ChatType, CustomToolArgs

logger = configure_logger(__name__)


INTERNAL_PARAMETERS = [
    # "images",
    # "files",
    # "current_message_images",
    # "current_message_files",
    "current_agent_id",
    "current_job_id",
    "chat_type",
    "chat_id",
    "message_id",
    "user_id",
    "user_type",
    "custom_tool_id",
]


@dataclass
class MCPRegistry:
    _tools: Dict[str, Dict[str, Any]] = None
    _files: Dict[str, str] = (
        None  # Key is the file name while the value is the file path
    )

    def __init__(self):
        self._tools = {}
        self._files = {}

    def register_file(self, file_id: str, file_path: str):
        self._files[file_id] = file_path

    def get_file_path(self, file_id: str) -> str:
        return self._files.get(file_id)

    def tool(self) -> Callable:
        def decorator(func: Callable) -> Callable:
            # Store the original function and its async status in the registry
            self._tools[func.__name__] = {
                "func": func,
                "is_async": inspect.iscoroutinefunction(func),
            }

            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)

            return wrapper

        return decorator

    def _get_schema_for_function(self, func: Callable) -> Dict[str, Any]:
        """Generate JSON schema for a function's parameters and return type."""
        sig = inspect.signature(func)

        try:
            type_hints = get_type_hints(func)
        except Exception:
            type_hints = {}

        properties = {}
        required = []

        for param_name, param in sig.parameters.items():
            if param_name in INTERNAL_PARAMETERS:
                continue

            # Skip *args and **kwargs
            if param.kind in (
                inspect.Parameter.VAR_POSITIONAL,
                inspect.Parameter.VAR_KEYWORD,
            ):
                continue

            # Get the type hint if available
            param_type = type_hints.get(param_name, Any)

            # Handle Optional[T] / Union[T, None]
            origin = get_origin(param_type)
            args = get_args(param_type)
            is_optional = False

            if origin is Union and type(None) in args:
                non_none_args = [a for a in args if a is not type(None)]
                if non_none_args:
                    param_type = non_none_args[0]
                else:
                    param_type = Any
                is_optional = True

            # Convert Python type to JSON schema type
            if param_type == int:
                param_schema = {"type": "integer"}
            elif param_type == str:
                param_schema = {"type": "string"}
            elif param_type == float:
                param_schema = {"type": "number"}
            elif param_type == bool:
                param_schema = {"type": "boolean"}
            elif get_origin(param_type) == dict:
                param_schema = {"type": "object"}  # could expand for keys/values
            else:
                param_schema = {"type": "object"}

            param_schema["title"] = param_name.replace("_", " ").title()
            properties[param_name] = param_schema

            # Required only if no default and not optional
            if param.default == param.empty and not is_optional:
                required.append(param_name)

        function_schema = {
            "title": f"{func.__name__}Arguments",
            "type": "object",
            "properties": properties,
        }

        if required:
            function_schema["required"] = required
        else:
            function_schema["required"] = []

        return function_schema

    def get_tool_specifications(self) -> List[Dict[str, Any]]:
        """Get specifications for all registered tools."""
        specs = []

        for name, tool_info in self._tools.items():
            func = tool_info["func"]
            spec = {
                "name": name,
                "description": inspect.getdoc(func) or "",
                "inputSchema": self._get_schema_for_function(func),
                "is_async": tool_info["is_async"],
            }
            specs.append(spec)

        logger.debug(f"Tool specifications: {specs}")

        return specs

    async def execute_tool(
        self,
        tool_name: str,
        tool_args: Dict[str, Any],
        images: Dict[str, str],
        files: Dict[str, str],
        current_message_images: Dict[str, str],
        current_message_files: Dict[str, str],
        current_agent_id: Optional[str] = None,
        current_job_id: Optional[str] = None,
        chat_type: Optional[ChatType] = ChatType.INTERACT,
        chat_id: Optional[str] = None,
        message_id: Optional[str] = None,
        user_id: Optional[str] = None,
        user_type: Optional[str] = None,
        custom_tool_id: Optional[str] = None,
        custom_args: Optional[List[CustomToolArgs]] = [],
    ) -> Any:
        """Execute a tool by name with given arguments."""
        if tool_name not in self._tools:
            raise ValueError(f"Tool '{tool_name}' not found")

        tool_info = self._tools[tool_name]
        func = tool_info["func"]
        is_async = tool_info["is_async"]

        # Check if the function accepts 'images' and 'files'
        signature = inspect.signature(func)
        func_params = signature.parameters

        # Add 'images' and 'files' to tool_args if the function expects them
        if "images" in func_params:
            tool_args["images"] = images
        if "files" in func_params:
            tool_args["files"] = files
        if "current_message_images" in func_params:
            tool_args["current_message_images"] = current_message_images
        if "current_message_files" in func_params:
            tool_args["current_message_files"] = current_message_files
        if "current_agent_id" in func_params:
            tool_args["current_agent_id"] = current_agent_id
        if "current_job_id" in func_params:
            tool_args["current_job_id"] = current_job_id
        if "chat_type" in func_params:
            tool_args["chat_type"] = chat_type
        if "custom_args" in func_params:
            tool_args["custom_args"] = custom_args
        if "chat_id" in func_params:
            tool_args["chat_id"] = chat_id
        if "message_id" in func_params:
            tool_args["message_id"] = message_id
        if "user_id" in func_params:
            tool_args["user_id"] = user_id
        if "user_type" in func_params:
            tool_args["user_type"] = user_type
        if "custom_tool_id" in func_params:
            tool_args["custom_tool_id"] = custom_tool_id

        if is_async:
            # Execute async function
            result = func(**tool_args)

            if inspect.isawaitable(result):
                # If the result is awaitable, await it
                return await result
            else:
                return result  # Async iterator
        else:
            # Execute sync function normally
            return await asyncio.to_thread(func, **tool_args)
