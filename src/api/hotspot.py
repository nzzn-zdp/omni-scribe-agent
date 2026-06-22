from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def get_hotspots():
    return {"message": "热点监控接口"}