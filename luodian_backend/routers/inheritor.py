import os
import uuid
from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
from database import db
from models import Inheritor
from auth_utils import admin_required

inheritor_bp = Blueprint("inheritor", __name__, url_prefix="/api/inheritor")

# ---------- 通用 ----------
def success(data=None, msg="success"):
    return jsonify({"code": 200, "msg": msg, "data": data})

def fail(msg="请求失败", code=400):
    return jsonify({"code": code, "msg": msg, "data": None}), code

def allowed_image(filename):
    ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
    return ext in {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_video(filename):
    ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
    return ext in {'mp4', 'mov', 'avi', 'webm'}

# ---------- 文件上传（管理员）----------
@inheritor_bp.route("/upload", methods=["POST"])
@admin_required
def upload_file(current_user):
    if "file" not in request.files:
        return fail("请上传文件")
    file = request.files["file"]
    if file.filename == "":
        return fail("文件名为空")
    if allowed_image(file.filename):
        subdir = "avatars"
    elif allowed_video(file.filename):
        subdir = "videos"
    else:
        return fail("不支持的文件类型，仅支持图片或视频")
    upload_folder = current_app.config.get("UPLOAD_FOLDER", "uploads")
    target_dir = os.path.join(upload_folder, "inheritor", subdir)
    os.makedirs(target_dir, exist_ok=True)
    ext = secure_filename(file.filename).rsplit('.', 1)[1].lower()
    new_name = f"{uuid.uuid4().hex}.{ext}"
    save_path = os.path.join(target_dir, new_name)
    file.save(save_path)
    file_url = f"/uploads/inheritor/{subdir}/{new_name}"
    return success({"url": file_url, "name": new_name}, "上传成功")

# ---------- 前台展示接口 ----------
@inheritor_bp.route("/list", methods=["GET"])
def list_inheritors():
    page = request.args.get("page", 1, type=int)
    size = request.args.get("size", 10, type=int)
    keyword = request.args.get("keyword", "").strip()
    level = request.args.get("level", "").strip()
    query = Inheritor.query
    if keyword:
        query = query.filter(Inheritor.name.contains(keyword))
    if level:
        query = query.filter(Inheritor.level == level)
    paginated = query.order_by(Inheritor.id.asc()).paginate(page=page, per_page=size, error_out=False)
    return success({
        "total": paginated.total,
        "pages": paginated.pages,
        "current": page,
        "items": [item.to_dict() for item in paginated.items]
    })

@inheritor_bp.route("/national", methods=["GET"])
def get_national():
    name = request.args.get("name", "").strip()
    query = Inheritor.query.filter_by(level="国家级")
    if name:
        query = query.filter(Inheritor.name.contains(name))
    items = query.all()
    return success([item.to_dict() for item in items])

@inheritor_bp.route("/provincial", methods=["GET"])
def get_provincial():
    name = request.args.get("name", "").strip()
    query = Inheritor.query.filter_by(level="省级")
    if name:
        query = query.filter(Inheritor.name.contains(name))
    items = query.all()
    return success([item.to_dict() for item in items])

@inheritor_bp.route("/city-level", methods=["GET"])
def get_city_level():
    name = request.args.get("name", "").strip()
    query = Inheritor.query.filter_by(level="市级")
    if name:
        query = query.filter(Inheritor.name.contains(name))
    items = query.all()
    return success([item.to_dict() for item in items])

@inheritor_bp.route("/young", methods=["GET"])
def get_young():
    name = request.args.get("name", "").strip()
    query = Inheritor.query.filter_by(level="新锐")
    if name:
        query = query.filter(Inheritor.name.contains(name))
    items = query.all()
    return success([item.to_dict() for item in items])

@inheritor_bp.route("/detail/<int:inheritor_id>", methods=["GET"])
def inheritor_detail(inheritor_id):
    inheritor = Inheritor.query.get(inheritor_id)
    if not inheritor:
        return fail("传承人不存在", 404)
    return success(inheritor.to_dict())

@inheritor_bp.route("/video/<int:inheritor_id>", methods=["GET"])
def get_video_url(inheritor_id):
    inheritor = Inheritor.query.get(inheritor_id)
    if not inheritor or not inheritor.video_url:
        return fail("视频不存在", 404)
    return success({"videoUrl": inheritor.video_url})

# ---------- 管理员后台管理接口 ----------
@inheritor_bp.route("/admin/list", methods=["GET"])
@admin_required
def admin_list(current_user):
    page = request.args.get("page", 1, type=int)
    size = request.args.get("size", 10, type=int)
    keyword = request.args.get("keyword", "").strip()
    query = Inheritor.query
    if keyword:
        query = query.filter(Inheritor.name.contains(keyword))
    paginated = query.order_by(Inheritor.id.asc()).paginate(page=page, per_page=size, error_out=False)
    return success({
        "total": paginated.total,
        "pages": paginated.pages,
        "current": page,
        "list": [item.to_dict() for item in paginated.items]
    })

@inheritor_bp.route("/admin/add", methods=["POST"])
@admin_required
def admin_add(current_user):
    data = request.get_json(silent=True) or {}
    name = data.get("name", "").strip()
    if not name:
        return fail("姓名不能为空")
    inheritor = Inheritor(
        name=name,
        title=data.get("title", ""),
        level=data.get("level", ""),
        avatar=data.get("avatar", ""),
        video_url=data.get("videoUrl", ""),
        description=data.get("description", ""),
        achievement=data.get("achievement", "")
    )
    db.session.add(inheritor)
    db.session.commit()
    return success(inheritor.to_dict(), "创建成功")

@inheritor_bp.route("/admin/edit", methods=["POST"])
@admin_required
def admin_edit(current_user):
    data = request.get_json(silent=True) or {}
    inheritor_id = data.get("id")
    if not inheritor_id:
        return fail("id不能为空")
    inheritor = Inheritor.query.get(inheritor_id)
    if not inheritor:
        return fail("传承人不存在", 404)
    inheritor.name = data.get("name", inheritor.name)
    inheritor.title = data.get("title", inheritor.title)
    inheritor.level = data.get("level", inheritor.level)
    inheritor.avatar = data.get("avatar", inheritor.avatar)
    inheritor.video_url = data.get("videoUrl", inheritor.video_url)
    inheritor.description = data.get("description", inheritor.description)
    inheritor.achievement = data.get("achievement", inheritor.achievement)
    db.session.commit()
    return success(inheritor.to_dict(), "更新成功")

@inheritor_bp.route("/admin/delete", methods=["POST"])
@admin_required
def admin_delete(current_user):
    data = request.get_json(silent=True) or {}
    inheritor_id = data.get("id")
    if not inheritor_id:
        return fail("id不能为空")
    inheritor = Inheritor.query.get(inheritor_id)
    if not inheritor:
        return fail("传承人不存在", 404)
    db.session.delete(inheritor)
    db.session.commit()
    return success(None, "删除成功")