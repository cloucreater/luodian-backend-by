# inheritor.py
from flask import Blueprint, jsonify, request

from database import db
from models import Inheritor

inheritor_bp = Blueprint("inheritor", __name__, url_prefix="/api/inheritor")

DEFAULT_INHERITORS = [
    {
        "name": "邵益达",
        "title": "螺钿工艺代表性传承人",
        "level": "国家级",
        "avatar": "/uploads/default/inheritor_1.png",
        "video_url": "/uploads/default/inheritor_1.mp4",
        "description": "长期从事螺钿工艺保护、研究与传承，注重传统技法与现代传播结合。",
        "achievement": "参与多项非遗展示、教学和工艺创新工作。",
    },
    {
        "name": "李明",
        "title": "螺钿工艺市级传承人",
        "level": "市级",
        "avatar": "/uploads/default/inheritor_2.png",
        "video_url": "/uploads/default/inheritor_2.mp4",
        "description": "擅长螺片切割、镶嵌和漆面处理，长期开展社区非遗教学。",
        "achievement": "推动螺钿工艺进入校园和公共文化空间。",
    },
    {
        "name": "陈雅",
        "title": "青年螺钿工艺创作者",
        "level": "新锐",
        "avatar": "/uploads/default/inheritor_3.png",
        "video_url": "/uploads/default/inheritor_3.mp4",
        "description": "关注数字化展示与文创设计，将螺钿纹样应用于现代生活用品。",
        "achievement": "参与螺钿数字化传播与文创设计项目。",
    },
]

def success(data=None, msg="success"):
    """统一成功返回"""
    return jsonify({"code": 200, "msg": msg, "data": data})

def fail(msg="请求失败", code=400):
    """统一失败返回"""
    return jsonify({"code": code, "msg": msg, "data": None}), code

def init_default_inheritors():
    """初始化默认传承人数据"""
    for item in DEFAULT_INHERITORS:
        exists = Inheritor.query.filter_by(name=item["name"]).first()
        if not exists:
            db.session.add(Inheritor(
                name=item["name"],
                title=item["title"],
                level=item["level"],
                avatar=item["avatar"],
                video_url=item["video_url"],
                description=item["description"],
                achievement=item["achievement"],
            ))
    db.session.commit()

@inheritor_bp.route("/list", methods=["GET"])
def list_inheritors():
    """获取传承人列表，支持 keyword 和 level 搜索"""
    keyword = request.args.get("keyword", "").strip()
    level = request.args.get("level", "").strip()

    query = Inheritor.query

    if keyword:
        query = query.filter(
            db.or_(
                Inheritor.name.contains(keyword),
                Inheritor.title.contains(keyword),
                Inheritor.description.contains(keyword),
                Inheritor.level.contains(keyword),
            )
        )

    if level:
        query = query.filter(Inheritor.level.contains(level))

    return success([item.to_dict() for item in query.order_by(Inheritor.id.asc()).all()])

@inheritor_bp.route("/detail/<int:inheritor_id>", methods=["GET"])
def inheritor_detail(inheritor_id):
    """获取传承人详情"""
    inheritor = Inheritor.query.get(inheritor_id)
    if not inheritor:
        return fail("传承人不存在", 404)

    return success(inheritor.to_dict())