from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from database import engine, Base
from routers import user, article, comment, favorite, post, ai
from config import settings

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield

app = FastAPI(title='非遗螺钿文化平台 API', version='1.0.0', lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['http://localhost:3000', 'http://127.0.0.1:3000'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

app.include_router(user.router, prefix='/api/user', tags=['用户'])
app.include_router(article.router, prefix='/api/articles', tags=['文章'])
app.include_router(comment.router, prefix='/api/comments', tags=['评论'])
app.include_router(favorite.router, prefix='/api/favorites', tags=['收藏'])
app.include_router(post.router, prefix='/api/posts', tags=['动态'])
app.include_router(ai.router, prefix='/api/ai', tags=['AI'])

@app.get('/')
async def root():
    return {'message': '螺钿文化平台 API 已启动'}
