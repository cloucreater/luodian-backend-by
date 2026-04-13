from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, func
from flask_sqlalchemy import SQLAlchemy
from config import settings

# ---------- Flask-SQLAlchemy 实例（供 models.py 和 main.py 使用）----------
db = SQLAlchemy()

# ---------- 异步 SQLAlchemy 部分（供 FastAPI 路由使用）----------
engine = create_async_engine(
    settings.DATABASE_URL.replace('sqlite:///', 'sqlite+aiosqlite:///'),
    echo=True
)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

Base = declarative_base()

async def get_db():
    """FastAPI 依赖项：获取异步数据库会话"""
    async with AsyncSessionLocal() as session:
        yield session