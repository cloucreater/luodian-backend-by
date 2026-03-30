from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database import get_db
from models import Comment, Article, User
from schemas import CommentCreate, CommentOut
from auth import get_current_user

router = APIRouter()

@router.post('/', response_model=CommentOut)
async def create_comment(comment_data: CommentCreate, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    article_result = await db.execute(select(Article).where(Article.id == comment_data.article_id))
    if not article_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail='文章不存在')
    new_comment = Comment(article_id=comment_data.article_id, user_id=current_user.id, content=comment_data.content)
    db.add(new_comment)
    article = article_result.scalar_one()
    article.comments_count += 1
    await db.commit()
    await db.refresh(new_comment)
    return CommentOut(
        id=new_comment.id, article_id=new_comment.article_id, user_id=new_comment.user_id,
        content=new_comment.content, likes=new_comment.likes, created_at=new_comment.created_at,
        username=current_user.username, avatar=current_user.avatar
    )

@router.post('/{comment_id}/like')
async def like_comment(comment_id: int, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Comment).where(Comment.id == comment_id))
    comment = result.scalar_one_or_none()
    if not comment:
        raise HTTPException(status_code=404, detail='评论不存在')
    comment.likes += 1
    await db.commit()
    return {'message': '点赞成功', 'likes': comment.likes}
