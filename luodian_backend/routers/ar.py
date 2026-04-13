# ar.py
import os
import uuid

from flask import Blueprint, current_app, jsonify, request
from werkzeug.utils import secure_filename

from database import db
from models import ARRecord

ar_bp = Blueprint("ar", __name__, url_prefix="/api/ar")

ALLOWED_IMAGE_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp", "bmp"}

def success(data=None, msg="success"):
    """统一成功返回"""
    return jsonify({"code": 200, "msg": msg, "data": data})

def fail(msg="请求失败", code=400):
    """统一失败返回"""
    return jsonify({"code": code, "msg": msg, "data": None}), code

def allowed_image(filename):
    """校验图片扩展名"""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_IMAGE_EXTENSIONS

def ensure_ar_dirs():
    """确保 AR 相关目录存在"""
    upload_folder = current_app.config.get("UPLOAD_FOLDER", os.path.join(os.getcwd(), "uploads"))

    image_dir = os.path.join(upload_folder, "ar", "images")
    model_dir = os.path.join(upload_folder, "ar", "models")
    preview_dir = os.path.join(upload_folder, "ar", "preview")

    os.makedirs(image_dir, exist_ok=True)
    os.makedirs(model_dir, exist_ok=True)
    os.makedirs(preview_dir, exist_ok=True)

    return image_dir, model_dir, preview_dir

@ar_bp.route("/make", methods=["POST"])
def make_ar():
    """上传图片并生成 AR 资源"""
    if "image" not in request.files:
        return fail("请上传 image 文件")

    image_file = request.files["image"]

    if not image_file or image_file.filename == "":
        return fail("上传文件不能为空")

    if not allowed_image(image_file.filename):
        return fail("只支持 png、jpg、jpeg、gif、webp、bmp 图片格式")

    image_dir, model_dir, preview_dir = ensure_ar_dirs()

    raw_name = secure_filename(image_file.filename)
    ext = raw_name.rsplit(".", 1)[1].lower()
    image_name = f"{uuid.uuid4().hex}.{ext}"
    image_path = os.path.join(image_dir, image_name)
    image_file.save(image_path)

    image_url = f"/uploads/ar/images/{image_name}"

    # 目前没有真实 3D 服务时，先生成占位 glb 文件
    model_name = f"{uuid.uuid4().hex}.glb"
    model_path = os.path.join(model_dir, model_name)
    with open(model_path, "w", encoding="utf-8") as file_obj:
        file_obj.write("placeholder glb model file")

    model_url = f"/uploads/ar/models/{model_name}"

    # 当前预览图直接复用上传图片
    preview_url = image_url

    record = ARRecord(
        image_url=image_url,
        model_url=model_url,
        preview_url=preview_url,
        status="success",
    )
    db.session.add(record)
    db.session.commit()

    return success({
        "id": record.id,
        "imageUrl": image_url,
        "modelUrl": model_url,
        "previewUrl": preview_url,
        "status": "success",
    }, "AR资源生成成功")

@ar_bp.route("/start", methods=["GET"])
def start_ar():
    """启动 AR 展示"""
    model_id = request.args.get("modelId") or request.args.get("id")
    if not model_id:
        return fail("modelId不能为空")

    record = ARRecord.query.get(model_id)
    if not record:
        return fail("AR资源不存在", 404)

    return success({
        "id": record.id,
        "modelUrl": record.model_url,
        "previewUrl": record.preview_url,
        "imageUrl": record.image_url,
        "status": record.status,
        "arStatus": "ready",
    }, "AR启动成功")

@ar_bp.route("/list", methods=["GET"])
def ar_list():
    """获取 AR 记录列表"""
    records = ARRecord.query.order_by(ARRecord.created_at.desc()).all()
    return success([item.to_dict() for item in records])

@ar_bp.route("/detail/<int:record_id>", methods=["GET"])
def ar_detail(record_id):
    """获取 AR 记录详情"""
    record = ARRecord.query.get(record_id)
    if not record:
        return fail("AR资源不存在", 404)

    return success(record.to_dict())