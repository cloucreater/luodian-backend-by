from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database import get_db
from models import User
from schemas import UserCreate, UserLogin, UserUpdate, UserOut, Token
from auth import get_password_hash, verify_password, create_access_token, get_current_user

router = APIRouter()

@router.post('/register', response_model=Token)
async def register(user: UserCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.username == user.username))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail='用户名已存在')
    hashed = get_password_hash(user.password)
    new_user = User(username=user.username, password=hashed, email=user.email, bio='', avatar='')
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    access_token = create_access_token(data={'sub': str(new_user.id)})
    return Token(access_token=access_token, token_type='bearer')

@router.post('/login', response_model=Token)
async def login(user: UserLogin, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.username == user.username))
    db_user = result.scalar_one_or_none()
    if not db_user or not verify_password(user.password, db_user.password):
        raise HTTPException(status_code=401, detail='用户名或密码错误')
    access_token = create_access_token(data={'sub': str(db_user.id)})
    return Token(access_token=access_token, token_type='bearer')

@router.get('/info', response_model=UserOut)
async def get_user_info(current_user: User = Depends(get_current_user)):
    return current_user

@router.put('/info', response_model=UserOut)
async def update_user_info(update: UserUpdate, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    if update.bio is not None:
        current_user.bio = update.bio
    if update.email is not None:
        current_user.email = update.email
    if update.avatar is not None:
        current_user.avatar = update.avatar
    await db.commit()
    await db.refresh(current_user)
    return current_user
