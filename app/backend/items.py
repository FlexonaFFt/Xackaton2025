from fastapi import APIRouter

router = APIRouter(
    prefix="/items",
    tags=["items"]
)

@router.get("/")
async def get_items():
    return {"message": "Hello from items!"}

@router.get("/test")
async def test_endpoint():
    return {"message": "This is a test endpoint"}

@router.get("/{item_id}")
async def get_item(item_id: int):
    return {
        "message": f"Hello! You requested item #{item_id}",
        "item_id": item_id
    }