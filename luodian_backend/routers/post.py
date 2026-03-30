from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from database import get_db
from models import Post, PostComment, User
from schemas import PostCreate, PostOut, PostCommentCreate, PostCommentOut
from auth import get_current_user

router = APIRouter()

@router.get('/', response_model=List[PostOut])
async def get_posts(page: int = Query(1, ge=1), limit: int = Query(10, ge=1, le=50), db: AsyncSession = Depends(get_db)):
    offset = (page - 1) * limit
    query = select(Post, User).join(User, Post.user_id == User.id).order_by(Post.created_at.desc()).offset(offset).limit(limit)
    result = await db.execute(query)
    posts = []
    for post, user in result:
        posts.append(PostOut(
            id=post.id, user_id=post.user_id, content=post.content, images=post.images,
            likes=post.likes, comments_count=post.comments_count, created_at=post.created_at,
            username=user.username, avatar=user.avatar
        ))
    return posts

@router.post('/', response_model=PostOut)
async def create_post(post_data: PostCreate, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    new_post = Post(user_id=current_user.id, content=post_data.content, images=post_data.images)
    db.add(new_post)
    await db.commit()
    await db.refresh(new_post)
    return PostOut(
        id=new_post.id, user_id=new_post.user_id, content=new_post.content, images=new_post.images,
        likes=new_post.likes, comments_count=new_post.comments_count, created_at=new_post.created_at,
        username=current_user.username, avatar=current_user.avatar
    )

@router.post('/{post_id}/like')
async def like_post(post_id: int, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Post).where(Post.id == post_id))
    post = result.scalar_one_or_none()
    if not post:
        raise HTTPException(status_code=404, detail='动态不存在')
    post.likes += 1
    await db.commit()
    return {'message': '点赞成功', 'likes': post.likes}

@router.get('/{post_id}/comments', response_model=List[PostCommentOut])
async def get_post_comments(post_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(PostComment, User)
        .join(User, PostComment.user_id == User.id)
        .where(PostComment.post_id == post_id)
        .order_by(PostComment.created_at.desc())
    )
    comments = []
    for comment, user in result:
        comments.append(PostCommentOut(
            id=comment.id, user_id=comment.user_id, content=comment.content,
            created_at=comment.created_at, username=user.username, avatar=user.avatar
        ))
    return comments

@router.post('/{post_id}/comments', response_model=PostCommentOut)
async def add_post_comment(post_id: int, comment_data: PostCommentCreate, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    post_result = await db.execute(select(Post).where(Post.id == post_id))
    post = post_result.scalar_one_or_none()
    if not post:
        raise HTTPException(status_code=404, detail='动态不存在')
    new_comment = PostComment(post_id=post_id, user_id=current_user.id, content=comment_data.content)
    db.add(new_comment)
    post.comments_count += 1
    await db.commit()
    await db.refresh(new_comment)
    return PostCommentOut(
        id=new_comment.id, user_id=new_comment.user_id, content=new_comment.content,
        created_at=new_comment.created_at, username=current_user.username, avatar=current_user.avatar
    )
