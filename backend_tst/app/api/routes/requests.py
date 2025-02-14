from fastapi import APIRouter, HTTPException
import requests
from typing import Any
from app.models.request import RequestModel

router = APIRouter()

@router.post("/send")
async def send_request(request_data: RequestModel) -> Any:
    try:
        response = requests.request(
            method=request_data.method,
            url=request_data.url,
            headers=request_data.headers,
            json=request_data.body if request_data.body else None
        )
        return {
            "status_code": response.status_code,
            "content": response.json()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))