# models.py
from datetime import datetime

from database import db

class User(db.Model):
    """用户表"""
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, comment="用户名")
    password = db.Column(db.String(255), nullable=False, comment="密码")
    role = db.Column(db.String(30), default="user", comment="角色：admin/master/user")
    avatar = db.Column(db.String(255), default="", comment="头像")
    created_at = db.Column(db.DateTime, default=datetime.utcnow, comment="创建时间")

    def to_dict(self):
        """用户序列化"""
        return {
            "id": self.id,
            "username": self.username,
            "role": self.role,
            "avatar": self.avatar,
            "createdAt": self.created_at.strftime("%Y-%m-%d %H:%M:%S") if self.created_at else "",
        }

class Article(db.Model):
    """文章表"""
    __tablename__ = "articles"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False, comment="文章标题")
    content = db.Column(db.Text, nullable=False, comment="文章内容")
    cover = db.Column(db.String(255), default="", comment="封面")
    author = db.Column(db.String(80), default="系统", comment="作者")
    category = db.Column(db.String(80), default="", comment="分类")
    views = db.Column(db.Integer, default=0, comment="浏览量")
    created_at = db.Column(db.DateTime, default=datetime.utcnow, comment="创建时间")
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")

    def to_dict(self):
        """文章序列化"""
        return {
            "id": self.id,
            "title": self.title,
            "content": self.content,
            "cover": self.cover,
            "author": self.author,
            "category": self.category,
            "views": self.views,
            "createdAt": self.created_at.strftime("%Y-%m-%d %H:%M:%S") if self.created_at else "",
            "updatedAt": self.updated_at.strftime("%Y-%m-%d %H:%M:%S") if self.updated_at else "",
        }

class Comment(db.Model):
    """评论表"""
    __tablename__ = "comments"

    id = db.Column(db.Integer, primary_key=True)
    article_id = db.Column(db.Integer, default=0, comment="文章ID")
    post_id = db.Column(db.Integer, default=0, comment="帖子ID")
    user_id = db.Column(db.Integer, default=0, comment="用户ID")
    username = db.Column(db.String(80), default="", comment="用户名")
    content = db.Column(db.Text, nullable=False, comment="评论内容")
    created_at = db.Column(db.DateTime, default=datetime.utcnow, comment="创建时间")

    def to_dict(self):
        """评论序列化"""
        return {
            "id": self.id,
            "articleId": self.article_id,
            "postId": self.post_id,
            "userId": self.user_id,
            "username": self.username,
            "content": self.content,
            "createdAt": self.created_at.strftime("%Y-%m-%d %H:%M:%S") if self.created_at else "",
        }

class Favorite(db.Model):
    """收藏表"""
    __tablename__ = "favorites"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, default=0, comment="用户ID")
    target_id = db.Column(db.Integer, default=0, comment="目标ID")
    target_type = db.Column(db.String(50), default="article", comment="类型：article/post")
    created_at = db.Column(db.DateTime, default=datetime.utcnow, comment="创建时间")

    def to_dict(self):
        """收藏序列化"""
        return {
            "id": self.id,
            "userId": self.user_id,
            "targetId": self.target_id,
            "targetType": self.target_type,
            "createdAt": self.created_at.strftime("%Y-%m-%d %H:%M:%S") if self.created_at else "",
        }

class Post(db.Model):
    """帖子表"""
    __tablename__ = "posts"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False, comment="帖子标题")
    content = db.Column(db.Text, nullable=False, comment="帖子内容")
    user_id = db.Column(db.Integer, default=0, comment="用户ID")
    username = db.Column(db.String(80), default="", comment="用户名")
    cover = db.Column(db.String(255), default="", comment="封面")
    created_at = db.Column(db.DateTime, default=datetime.utcnow, comment="创建时间")
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")

    def to_dict(self):
        """帖子序列化"""
        return {
            "id": self.id,
            "title": self.title,
            "content": self.content,
            "userId": self.user_id,
            "username": self.username,
            "cover": self.cover,
            "createdAt": self.created_at.strftime("%Y-%m-%d %H:%M:%S") if self.created_at else "",
            "updatedAt": self.updated_at.strftime("%Y-%m-%d %H:%M:%S") if self.updated_at else "",
        }
class PostComment(db.Model):
    """帖子评论表"""
    __tablename__ = "post_comments"

    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, nullable=False, comment="帖子ID")
    user_id = db.Column(db.Integer, nullable=False, comment="用户ID")
    content = db.Column(db.Text, nullable=False, comment="评论内容")
    created_at = db.Column(db.DateTime, default=datetime.utcnow, comment="创建时间")

    def to_dict(self):
        return {
            "id": self.id,
            "postId": self.post_id,
            "userId": self.user_id,
            "content": self.content,
            "createdAt": self.created_at.strftime("%Y-%m-%d %H:%M:%S") if self.created_at else "",
        }
class Knowledge(db.Model):
    """知识库表"""
    __tablename__ = "knowledge"

    id = db.Column(db.Integer, primary_key=True)
    section_id = db.Column(db.String(80), index=True, default="", comment="章节ID")
    title = db.Column(db.String(200), nullable=False, comment="标题")
    summary = db.Column(db.Text, default="", comment="摘要")
    content = db.Column(db.Text, nullable=False, default="", comment="正文")
    cover = db.Column(db.String(255), default="", comment="封面")
    name = db.Column(db.String(200), default="", comment="兼容前端名称")
    category = db.Column(db.String(80), default="", comment="分类")
    inheritor = db.Column(db.String(100), default="", comment="传承人")
    content_file_name = db.Column(db.String(255), default="", comment="内容文件名")
    file_url = db.Column(db.String(255), default="", comment="文件地址")
    source = db.Column(db.String(50), default="manual", comment="来源：manual/ai/master/system")
    created_at = db.Column(db.DateTime, default=datetime.utcnow, comment="创建时间")
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")
    status = db.Column(db.String(20), default='published', comment='状态：published/draft/pending/rejected')
    def to_dict(self):
        """知识库序列化"""
        return {
            "id": self.id,
            "sectionId": self.section_id,
            "title": self.title,
            "summary": self.summary,
            "content": self.content,
            "cover": self.cover,
            "name": self.name or self.title,
            "category": self.category,
            "inheritor": self.inheritor,
            "contentFileName": self.content_file_name,
            "fileUrl": self.file_url,
            "source": self.source,
            "createTime": self.created_at.strftime("%Y/%m/%d %H:%M:%S") if self.created_at else "",
            "updateTime": self.updated_at.strftime("%Y/%m/%d %H:%M:%S") if self.updated_at else "",
        }

class Inheritor(db.Model):
    """传承人表"""
    __tablename__ = "inheritors"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, comment="姓名")
    title = db.Column(db.String(200), default="", comment="称号")
    level = db.Column(db.String(80), default="", comment="级别")
    avatar = db.Column(db.String(255), default="", comment="头像")
    video_url = db.Column(db.String(255), default="", comment="视频地址")
    description = db.Column(db.Text, default="", comment="简介")
    achievement = db.Column(db.Text, default="", comment="成就")
    created_at = db.Column(db.DateTime, default=datetime.utcnow, comment="创建时间")

    def to_dict(self):
        """传承人序列化"""
        return {
            "id": self.id,
            "name": self.name,
            "title": self.title,
            "level": self.level,
            "avatar": self.avatar,
            "videoUrl": self.video_url,
            "description": self.description,
            "achievement": self.achievement,
            "createTime": self.created_at.strftime("%Y/%m/%d %H:%M:%S") if self.created_at else "",
        }

class ARRecord(db.Model):
    """AR 生成记录表"""
    __tablename__ = "ar_records"

    id = db.Column(db.Integer, primary_key=True)
    image_url = db.Column(db.String(255), nullable=False, comment="上传图片地址")
    model_url = db.Column(db.String(255), nullable=False, comment="模型地址")
    preview_url = db.Column(db.String(255), default="", comment="预览地址")
    status = db.Column(db.String(50), default="success", comment="状态")
    created_at = db.Column(db.DateTime, default=datetime.utcnow, comment="创建时间")

    def to_dict(self):
        """AR记录序列化"""
        return {
            "id": self.id,
            "imageUrl": self.image_url,
            "modelUrl": self.model_url,
            "previewUrl": self.preview_url,
            "status": self.status,
            "createTime": self.created_at.strftime("%Y/%m/%d %H:%M:%S") if self.created_at else "",
        }

class MasterKnowledge(db.Model):
    """传承人提交知识记录表"""
    __tablename__ = "master_knowledge"

    id = db.Column(db.Integer, primary_key=True)
    cover = db.Column(db.String(255), default="", comment="封面")
    name = db.Column(db.String(200), nullable=False, comment="标题")
    category = db.Column(db.String(80), default="", comment="分类")
    inheritor = db.Column(db.String(100), default="", comment="传承人")
    content_file_name = db.Column(db.String(255), default="", comment="内容文件名")
    file_url = db.Column(db.String(255), default="", comment="文件地址")
    status = db.Column(db.String(50), default="待审核", comment="状态")
    status_class = db.Column(db.String(50), default="pending", comment="状态样式")
    create_time = db.Column(db.DateTime, default=datetime.utcnow, comment="创建时间")
    update_time = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")

    def to_dict(self):
        """传承人发布记录序列化"""
        return {
            "id": self.id,
            "cover": self.cover,
            "name": self.name,
            "category": self.category,
            "inheritor": self.inheritor,
            "contentFileName": self.content_file_name,
            "fileUrl": self.file_url,
            "status": self.status,
            "statusClass": self.status_class,
            "createTime": self.create_time.strftime("%Y/%m/%d %H:%M:%S") if self.create_time else "",
            "updateTime": self.update_time.strftime("%Y/%m/%d %H:%M:%S") if self.update_time else "",
        }