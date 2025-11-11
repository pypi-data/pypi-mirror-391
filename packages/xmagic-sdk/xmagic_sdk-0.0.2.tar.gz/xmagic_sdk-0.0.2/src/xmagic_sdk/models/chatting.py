from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field

class SourceItem(BaseModel):
    id: Optional[str] = None
    type: Optional[str] = None
    value: Optional[str] = None
    page: Optional[Union[List[int], int]] = None
    title: Optional[str] = None


class Message(BaseModel):
    id: str
    query: str
    response: str
    tool_calls: Optional[List[Dict[str, Any]]] = Field(default_factory=list)
    sources: List[SourceItem] = Field(default_factory=list)
