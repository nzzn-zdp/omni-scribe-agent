from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def get_content():
    return {"message": "内容生产接口"}