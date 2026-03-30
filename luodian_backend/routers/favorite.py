from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, and_
from database import get_db
from models import Favorite, Article, User
from schemas import FavoriteCreate
from auth import get_current_user

router = APIRouter()

@router.get('/')
async def get_favorites(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Favorite, Article)
        .join(Article, Favorite.article_id == Article.id)
        .where(Favorite.user_id == current_user.id)
        .order_by(Favorite.created_at.desc())
    )
    favorites = []
    for fav, article in result:
        favorites.append({
            'id': fav.id, 'article_id': article.id, 'title': article.title,
            'summary': article.summary, 'cover': article.cover, 'created_at': fav.created_at
        })
    return favorites

@router.post('/')
async def add_favorite(fav: FavoriteCreate, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    article_result = await db.execute(select(Article).where(Article.id == fav.article_id))
    if not article_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail='文章不存在')
    existing = await db.execute(select(Favorite).where(and_(Favorite.user_id == current_user.id, Favorite.article_id == fav.article_id)))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail='已经收藏过')
    new_fav = Favorite(user_id=current_user.id, article_id=fav.article_id)
    db.add(new_fav)
    await db.commit()
    return {'message': '收藏成功'}

@router.delete('/{article_id}')
async def remove_favorite(article_id: int, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(delete(Favorite).where(and_(Favorite.user_id == current_user.id, Favorite.article_id == article_id)))
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail='收藏不存在')
    await db.commit()
    return {'message': '取消收藏成功'}
