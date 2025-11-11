from fastapi import HTTPException, status, APIRouter
from pydantic import BaseModel
from digital_life.model_public import MemoryCard
from digital_life.core import UserInfo

router = APIRouter(tags=["user"])

userinfo = UserInfo(model_name = "doubao-1-5-pro-256k-250115")


class UseroverviewRequests(BaseModel):
    action: str
    old_overview: str
    memory_cards: list[MemoryCard]

@router.post("/user_overview")
async def user_overview_server(request: UseroverviewRequests):
    """
    用户概述
    """
    try:
        result = await userinfo.auser_overview(
            action = request.action,
            old_overview=request.old_overview, 
            memory_cards=request.model_dump()["memory_cards"]
        )  # 包裹的内核函数

        return {"overview": result}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error Info: {e}",
        )


class UserRelationshipExtractionRequest(BaseModel):
    text: str

@router.post("/user_relationship_extraction", description="用户关系提取")
async def user_relationship_extraction_server(request: UserRelationshipExtractionRequest,):
    try:
        result = await userinfo.auser_relationship_extraction(text=request.text)
        return {"relation": result}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error Info: {e}",
        )
