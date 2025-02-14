from pydantic import BaseModel
from typing import Dict, Any, Optional

class RequestModel(BaseModel):
    method: str
    url: str
    headers: Optional[Dict[str, str]] = None
    body: Optional[Dict[str, Any]] = None