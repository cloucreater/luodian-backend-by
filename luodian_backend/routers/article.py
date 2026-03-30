from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import Optional, List
from database import get_db
from models import Article, Comment, User
from schemas import ArticleCreate, ArticleUpdate, ArticleOut, CommentOut
from auth import get_current_user

router = APIRouter()

@router.get('/', response_model=List[ArticleOut])
async def get_articles(page: int = Query(1, ge=1), limit: int = Query(10, ge=1, le=50), category: Optional[str] = None, keyword: Optional[str] = None, db: AsyncSession = Depends(get_db)):
    offset = (page - 1) * limit
    conditions = []
    if category:
        conditions.append(Article.category == category)
    if keyword:
        conditions.append(Article.title.contains(keyword) | Article.content.contains(keyword))
    query = select(Article).where(and_(*conditions)).order_by(Article.created_at.desc()).offset(offset).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()

@router.get('/search')
async def search_articles(keyword: str = Query(...), db: AsyncSession = Depends(get_db)):
    conditions = [Article.title.contains(keyword) | Article.content.contains(keyword)]
    query = select(Article).where(and_(*conditions)).order_by(Article.created_at.desc())
    result = await db.execute(query)
    return result.scalars().all()

@router.get('/{article_id}', response_model=ArticleOut)
async def get_article_detail(article_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Article).where(Article.id == article_id))
    article = result.scalar_one_or_none()
    if not article:
        raise HTTPException(status_code=404, detail='文章不存在')
    article.views += 1
    await db.commit()
    await db.refresh(article)
    return article

@router.post('/', response_model=ArticleOut)
async def create_article(article: ArticleCreate, current_user = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    if current_user.role != 'admin':
        raise HTTPException(status_code=403, detail='无权限')
    new_article = Article(**article.dict())
    db.add(new_article)
    await db.commit()
    await db.refresh(new_article)
    return new_article

@router.put('/{article_id}', response_model=ArticleOut)
async def update_article(article_id: int, article_update: ArticleUpdate, current_user = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    if current_user.role != 'admin':
        raise HTTPException(status_code=403, detail='无权限')
    result = await db.execute(select(Article).where(Article.id == article_id))
    article = result.scalar_one_or_none()
    if not article:
        raise HTTPException(status_code=404, detail='文章不存在')
    for key, value in article_update.dict(exclude_unset=True).items():
        setattr(article, key, value)
    await db.commit()
    await db.refresh(article)
    return article

@router.delete('/{article_id}')
async def delete_article(article_id: int, current_user = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    if current_user.role != 'admin':
        raise HTTPException(status_code=403, detail='无权限')
    result = await db.execute(select(Article).where(Article.id == article_id))
    article = result.scalar_one_or_none()
    if not article:
        raise HTTPException(status_code=404, detail='文章不存在')
    await db.delete(article)
    await db.commit()
    return {'message': '删除成功'}

@router.get('/{article_id}/comments', response_model=List[CommentOut])
async def get_article_comments(article_id: int, db: AsyncSession = Depends(get_db)):
    query = select(Comment, User).join(User, Comment.user_id == User.id).where(Comment.article_id == article_id).order_by(Comment.created_at.desc())
    result = await db.execute(query)
    comments = []
    for comment, user in result:
        comments.append(CommentOut(
            id=comment.id, article_id=comment.article_id, user_id=comment.user_id,
            content=comment.content, likes=comment.likes, created_at=comment.created_at,
            username=user.username, avatar=user.avatar
        ))
    return comments
