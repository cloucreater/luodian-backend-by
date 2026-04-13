from fastapi import FastAPI
from database import engine, Base
from routers import article, comment, user, post, favorite, ai

app = FastAPI()

# 注册路由
app.include_router(user.router, prefix="/api/user", tags=["user"])
app.include_router(article.router, prefix="/api/articles", tags=["articles"])
app.include_router(comment.router, prefix="/api/comments", tags=["comments"])
app.include_router(favorite.router, prefix="/api/favorites", tags=["favorites"])
app.include_router(post.router, prefix="/api/posts", tags=["posts"])
app.include_router(ai.router, prefix="/api/ai", tags=["ai"])

@app.on_event("startup")
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)