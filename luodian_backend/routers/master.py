# master.py
from flask import Blueprint, jsonify, request

from database import db
from models import MasterKnowledge

master_bp = Blueprint("master", __name__, url_prefix="/api/master")

def success(data=None, msg="success"):
    """统一成功返回"""
    return jsonify({"code": 200, "msg": msg, "data": data})

def fail(msg="请求失败", code=400):
    """统一失败返回"""
    return jsonify({"code": code, "msg": msg, "data": None}), code

@master_bp.route("/publish", methods=["POST"])
def publish_knowledge():
    """传承人提交知识"""
    data = request.get_json(silent=True) or {}

    name = (data.get("name") or "").strip()
    if not name:
        return fail("标题不能为空")

    record = MasterKnowledge(
        cover=(data.get("cover") or "").strip(),
        name=name,
        category=(data.get("category") or "").strip(),
        inheritor=(data.get("inheritor") or "").strip(),
        content_file_name=(data.get("contentFileName") or "").strip(),
        file_url=(data.get("fileUrl") or "").strip(),
        status="待审核",
        status_class="pending",
    )

    db.session.add(record)
    db.session.commit()

    return success(record.to_dict(), "提交成功，等待审核")

@master_bp.route("/my-records", methods=["GET"])
def my_records():
    """获取我的提交记录"""
    inheritor = request.args.get("inheritor", "").strip()

    query = MasterKnowledge.query
    if inheritor:
        query = query.filter(MasterKnowledge.inheritor.contains(inheritor))

    records = query.order_by(MasterKnowledge.create_time.desc()).all()
    return success([item.to_dict() for item in records])

@master_bp.route("/update", methods=["POST"])
def update_knowledge():
    """修改已退回内容并重新提交"""
    data = request.get_json(silent=True) or {}
    record_id = data.get("id")

    if not record_id:
        return fail("id不能为空")

    record = MasterKnowledge.query.get(record_id)
    if not record:
        return fail("记录不存在", 404)

    record.cover = data.get("cover", record.cover)
    record.name = data.get("name", record.name)
    record.category = data.get("category", record.category)
    record.inheritor = data.get("inheritor", record.inheritor)
    record.content_file_name = data.get("contentFileName", record.content_file_name)
    record.file_url = data.get("fileUrl", record.file_url)
    record.status = "待审核"
    record.status_class = "pending"

    db.session.commit()

    return success(record.to_dict(), "修改成功，已重新提交审核")

@master_bp.route("/logout", methods=["POST"])
def master_logout():
    """传承人退出登录"""
    return success(None, "退出成功")