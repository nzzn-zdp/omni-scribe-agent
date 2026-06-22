from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def get_publish():
    return {"message": "多平台发布接口"}