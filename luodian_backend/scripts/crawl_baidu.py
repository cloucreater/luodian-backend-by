import requests
from bs4 import BeautifuluiyySoup
import re
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.orm import sessionmaker, declarative_base
from datetime import datetime

# 数据库连接（使用你的项目数据库）
DATABASE_URL = "sqlite:///../database.sqlite"  # 根据实际路径调整
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()
Base = declarative_base()


# 定义 Article 模型（与 models.py 一致）
class Article(Base):
    __tablename__ = 'articles'
    id = Column(Integer, primary_key=True)
    title = Column(String(200))
    content = Column(Text)
    category = Column(String(50))
    summary = Column(String(500))
    cover = Column(String(255))
    views = Column(Integer, default=0)
    likes = Column(Integer, default=0)
    comments_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.now)


# 爬取百度百科词条
def crawl_baike(keyword):
    url = f"https://baike.baidu.com/item/{keyword}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        resp.encoding = 'utf-8'
        soup = BeautifulSoup(resp.text, 'html.parser')

        # 获取标题
        title = soup.find('h1').get_text().strip()

        # 获取摘要（百度百科的概要部分）
        summary_elem = soup.find('div', class_='lemma-summary')
        if not summary_elem:
            summary_elem = soup.find('div', class_='summary')
        summary = summary_elem.get_text().strip() if summary_elem else ""

        # 获取正文（主要段落）
        content_elems = soup.find_all('div', class_='para')
        content = "\n".join([p.get_text().strip() for p in content_elems])

        # 分类（可根据关键词简单归类）
        category = "历史渊源"
        if "点螺" in title or "薄螺钿" in title:
            category = "技艺解析"
        elif "材料" in title or "工具" in title:
            category = "材料工具"
        elif "鉴赏" in title:
            category = "精品鉴赏"

        # 检查是否已存在
        existing = session.query(Article).filter(Article.title == title).first()
        if existing:
            print(f"已存在: {title}")
            return

        # 存入数据库
        article = Article(
            title=title,
            content=content,
            summary=summary[:500],
            category=category,
            cover=None,
            created_at=datetime.now()
        )
        session.add(article)
        session.commit()
        print(f"成功爬取: {title}")

        # 提取相关词条链接（可选）
        related_links = soup.find_all('a', href=re.compile(r'/item/[^/]+'))
        for link in related_links[:5]:  # 限制深度
            href = link.get('href')
            if href and not href.startswith('http'):
                full_url = 'https://baike.baidu.com' + href
                # 这里可以递归爬取，但注意避免循环
                # 简单起见，只爬取一次，不深入
        return article
    except Exception as e:
        print(f"爬取失败 {keyword}: {e}")
        return None


if __name__ == "__main__":
    # 爬取主词条
    crawl_baike("螺钿")
    crawl_baike("点螺")
    crawl_baike("螺钿漆器")
    crawl_baike("扬州漆器")
    crawl_baike("螺钿镶嵌")
    # 关闭会话
    session.close()