from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from schemas import AIRequest, AIResponse
from ai_client import ai_client
from models import User
from auth import get_current_user

router = APIRouter()

@router.post('/chat', response_model=AIResponse)
async def ai_chat(req: AIRequest, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    try:
        reply = await ai_client.chat(req.message, req.history)
        return AIResponse(reply=reply)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'AI 服务出错: {str(e)}')
