# main.py
import os

from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS

from database import db

def create_app():
    """创建应用并注册所有蓝图"""
    app = Flask(__name__)

    # 数据库配置：优先读取环境变量，默认使用 SQLite
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", "sqlite:///app.db")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # 上传目录配置
    app.config["UPLOAD_FOLDER"] = os.path.join(os.getcwd(), "uploads")
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    # 开启跨域
    CORS(app, supports_credentials=True)

    # 初始化数据库
    db.init_app(app)

    # 注册已有模块
    try:
        from auth import auth_bp
        app.register_blueprint(auth_bp)
    except Exception as exc:
        print(f"[WARN] auth_bp register failed: {exc}")

    try:
        from .routers import user
        from routers.user import user_bp
        app.register_blueprint(user_bp)
    except Exception as exc:
        print(f"[WARN] user_bp register failed: {exc}")

    try:
        from routers import article
        from routers.article import article_bp
        app.register_blueprint(article_bp)
    except Exception as exc:
        print(f"[WARN] article_bp register failed: {exc}")

    try:
        from routers import comment
        from routers.comment import comment_bp
        app.register_blueprint(comment_bp)
    except Exception as exc:
        print(f"[WARN] comment_bp register failed: {exc}")

    try:
        from routers import favorite
        from routers.favorite import favorite_bp
        app.register_blueprint(favorite_bp)
    except Exception as exc:
        print(f"[WARN] favorite_bp register failed: {exc}")

    try:
        from routers import post
        from routers.post import post_bp
        app.register_blueprint(post_bp)
    except Exception as exc:
        print(f"[WARN] post_bp register failed: {exc}")

    try:
        from routers import ai
        from routers.ai import ai_bp
        app.register_blueprint(ai_bp)
    except Exception as exc:
        print(f"[WARN] ai_bp register failed: {exc}")

    # 注册新增模块
    from routers import knowledge
    from routers.knowledge import knowledge_bp, init_default_knowledge
    from routers import  inheritor
    from routers.inheritor import inheritor_bp, init_default_inheritors
    from routers import ar
    from routers.ar import ar_bp
    from routers import master
    from routers.master import master_bp

    app.register_blueprint(knowledge_bp)
    app.register_blueprint(inheritor_bp)
    app.register_blueprint(ar_bp)
    app.register_blueprint(master_bp)

    @app.route("/", methods=["GET"])
    def index():
        """根路由健康检查"""
        return jsonify({
            "code": 200,
            "msg": "success",
            "data": "Flask backend is running"
        })

    @app.route("/uploads/<path:filename>", methods=["GET"])
    def uploaded_file(filename):
        """提供上传文件访问能力"""
        return send_from_directory(app.config["UPLOAD_FOLDER"], filename)

    with app.app_context():
        # 确保模型加载后自动建表
        import models  # noqa: F401
        db.create_all()

        # 初始化默认数据
        init_default_knowledge()
        init_default_inheritors()

    return app

app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)