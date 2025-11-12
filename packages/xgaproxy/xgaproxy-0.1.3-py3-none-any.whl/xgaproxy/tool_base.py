from typing import Optional, List, Literal, TypedDict
from dataclasses import dataclass

class XGAError(Exception):
    """Custom exception for errors in the XGA system."""
    pass

class XGAAgentResult(TypedDict, total=False):
    type: Literal["ask", "answer", "error"]
    content: str
    attachments: Optional[List[str]]


class XGAToolResult(TypedDict):
    success: bool
    output: str