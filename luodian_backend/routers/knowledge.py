import os
import uuid
from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
from database import db
from models import Knowledge, MasterKnowledge
from auth_utils import admin_required, login_required
from ai_client import ai_client
import asyncio

knowledge_bp = Blueprint("knowledge", __name__, url_prefix="/api/knowledge")


# ---------- 通用函数 ----------
def success(data=None, msg="success"):
    return jsonify({"code": 200, "msg": msg, "data": data})


def fail(msg="请求失败", code=400):
    return jsonify({"code": code, "msg": msg, "data": None}), code


def allowed_file(filename):
    ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
    return ext in {'png', 'jpg', 'jpeg', 'gif', 'webp', 'pdf', 'txt', 'md', 'mp4', 'mov'}


# ---------- 文件上传（管理员） ----------
@knowledge_bp.route("/upload", methods=["POST"])
@admin_required
def upload_file(current_user):
    if "file" not in request.files:
        return fail("请上传文件")
    file = request.files["file"]
    if file.filename == "":
        return fail("文件名为空")
    if not allowed_file(file.filename):
        return fail("不支持的文件类型")

    upload_folder = current_app.config.get("UPLOAD_FOLDER", "uploads")
    target_dir = os.path.join(upload_folder, "knowledge")
    os.makedirs(target_dir, exist_ok=True)

    ext = secure_filename(file.filename).rsplit('.', 1)[1].lower()
    new_name = f"{uuid.uuid4().hex}.{ext}"
    save_path = os.path.join(target_dir, new_name)
    file.save(save_path)
    file_url = f"/uploads/knowledge/{new_name}"
    return success({"url": file_url, "name": new_name}, "上传成功")


# ---------- 前台知识库展示接口 ----------
@knowledge_bp.route("/info", methods=["GET"])
def get_knowledge_info():
    """获取知识殿堂首页展示内容（示例返回固定结构）"""
    data = {
        "title": "螺钿的千年之旅",
        "content": "螺钿技艺起源于商周时期...",
        "mainImage": "/images/h1.png",
        "subImages": ["/images/h2.png", "/images/h3.png"],
        "quote": "螺纹为饰，器物其质..."
    }
    return success(data)


@knowledge_bp.route("/tags", methods=["GET"])
def get_tags():
    tags = ["历史溯源", "技艺解析", "材料工具", "螺钿分类", "精品鉴赏", "文献资料"]
    return success(tags)


@knowledge_bp.route("/by-tag", methods=["GET"])
def get_by_tag():
    tag = request.args.get("tag", "").strip()
    if not tag:
        return fail("缺少 tag 参数")
    # 根据 tag 返回对应分类的已发布内容
    query = Knowledge.query.filter(Knowledge.status == 'published')
    if tag == "历史溯源":
        query = query.filter(Knowledge.category.contains("历史"))
    elif tag == "技艺解析":
        query = query.filter(Knowledge.category.contains("技艺"))
    elif tag == "材料工具":
        query = query.filter(Knowledge.category.contains("材料"))
    elif tag == "螺钿分类":
        query = query.filter(Knowledge.category.contains("分类"))
    elif tag == "精品鉴赏":
        query = query.filter(Knowledge.category.contains("鉴赏"))
    elif tag == "文献资料":
        query = query.filter(Knowledge.category.contains("文献"))
    else:
        query = query.filter(Knowledge.category == tag)
    items = query.order_by(Knowledge.updated_at.desc()).all()
    return success([item.to_dict() for item in items])


@knowledge_bp.route("/search", methods=["GET"])
def search_knowledge():
    keyword = request.args.get("keyword", "").strip()
    if not keyword:
        return success([])
    query = Knowledge.query.filter(
        db.or_(
            Knowledge.title.contains(keyword),
            Knowledge.name.contains(keyword),
            Knowledge.summary.contains(keyword),
            Knowledge.content.contains(keyword),
            Knowledge.category.contains(keyword),
            Knowledge.inheritor.contains(keyword),
        ),
        Knowledge.status == 'published'
    ).order_by(Knowledge.updated_at.desc())
    return success([item.to_dict() for item in query.all()])


@knowledge_bp.route("/detail/<int:knowledge_id>", methods=["GET"])
def get_knowledge_detail(knowledge_id):
    knowledge = Knowledge.query.filter_by(id=knowledge_id, status='published').first()
    if not knowledge:
        return fail("知识不存在", 404)
    return success(knowledge.to_dict())


@knowledge_bp.route("/detail/nav", methods=["GET"])
def get_nav():
    nav = [
        {"id": "history", "name": "历史总览"},
        {"id": "origin", "name": "起源与早期发展"},
        {"id": "tang", "name": "唐代的鼎盛"},
        {"id": "song", "name": "宋代的雅致"},
        {"id": "mingqing", "name": "明清的巅峰"},
        {"id": "modern", "name": "近现代的传承"},
        {"id": "techniques", "name": "技法演变"},
        {"id": "materials", "name": "材料与工具"},
        {"id": "influence", "name": "文化影响"},
    ]
    return success(nav)


@knowledge_bp.route("/history", methods=["GET"])
def get_history_detail():
    """知识殿堂-历史溯源详情（示例）"""
    data = {
        "title": "螺钿的千年之旅",
        "sections": [
            {"id": "origin", "title": "起源与早期发展", "content": "商周时期...", "image": "", "caption": ""},
            {"id": "tang", "title": "唐代的鼎盛", "content": "唐代...", "image": "", "caption": ""}
        ]
    }
    return success(data)


@knowledge_bp.route("/technique", methods=["GET"])
def get_technique():
    """技艺解析页面数据"""
    data = {
        "title": "匠心工序 · 螺钿制作全流程",
        "steps": [
            {"name": "选材构图", "image": "", "content": "根据画稿在原贝壳上寻找合适部位取色..."},
            {"name": "裁切磨薄", "image": "", "content": "将贝壳裁割成小块，并打磨至极薄..."},
            {"name": "镶嵌上漆", "image": "", "content": "在漆底上刻划纹样，嵌入螺钿片..."},
            {"name": "推光揩漆", "image": "", "content": "多次反复揩漆打磨，使螺钿与漆面齐平..."}
        ],
        "detailed": {
            "title": "工艺详解",
            "image": "",
            "content": "螺钿制作是一项需要极高技艺的传统工艺..."
        }
    }
    return success(data)


@knowledge_bp.route("/materials", methods=["GET"])
def get_materials():
    """材料工具页面数据"""
    data = {
        "materials": [
            {"img": "", "name": "鲍鱼贝", "desc": "色彩丰富，有红、绿、蓝等多种颜色，是螺钿制作的主要材料之一。"}
        ],
        "tools": [
            {"img": "", "name": "裁剪刀", "desc": "用于裁切贝壳，需要锋利且精准。"}
        ]
    }
    return success(data)


@knowledge_bp.route("/classification", methods=["GET"])
def get_classification():
    """螺钿分类页面数据"""
    data = [
        {"id": 1, "name": "厚螺钿", "image": "", "desc": "采用较厚的贝壳片，质感强烈...",
         "features": ["厚度：0.5-1mm", "特点：立体感强"]},
        {"id": 2, "name": "薄螺钿", "image": "", "desc": "贝壳片打磨得非常薄...",
         "features": ["厚度：0.1-0.2mm", "特点：透明度高"]},
        {"id": 3, "name": "点螺", "image": "", "desc": "将贝壳打磨成细粉...",
         "features": ["工艺：点嵌", "特点：精细入微"]},
        {"id": 4, "name": "百宝嵌", "image": "", "desc": "除了螺钿外，还镶嵌宝石...",
         "features": ["材料：多种", "特点：奢华繁复"]}
    ]
    return success(data)


@knowledge_bp.route("/appreciation", methods=["GET"])
def get_appreciation():
    """精品鉴赏列表"""
    keyword = request.args.get("keyword", "").strip()
    # 这里从数据库获取，示例返回静态数据
    items = [
        {"img": "", "title": "唐代螺钿铜镜", "desc": "唐代螺钿工艺的代表作品...", "period": "唐代",
         "technique": "厚螺钿", "place": "故宫博物院"}
    ]
    if keyword:
        items = [i for i in items if keyword in i['title'] or keyword in i['desc']]
    return success(items)


# ---------- 文献资料相关（书籍/论文）----------
@knowledge_bp.route("/literature/books", methods=["GET"])
def get_books():
    books = [
        {"id": 1, "title": "中国螺钿工艺史", "author": "佚名", "coverUrl": "", "publishYear": 2020, "pages": 280}
    ]
    return success(books)


@knowledge_bp.route("/literature/papers", methods=["GET"])
def get_papers():
    papers = [
        {"id": 1, "title": "唐代螺钿工艺研究", "author": "张教授", "journal": "文物", "year": 2018}
    ]
    return success(papers)


@knowledge_bp.route("/literature/all-books", methods=["GET"])
def get_all_books():
    return success([
        {"id": 1, "title": "髹饰录", "author": "黄成（明）", "coverUrl": "", "publishYear": 1520, "pages": 120},
        {"id": 2, "title": "中国漆器工艺史", "author": "王世襄", "coverUrl": "", "publishYear": 1988, "pages": 280}
    ])


@knowledge_bp.route("/literature/detail", methods=["GET"])
def get_literature_detail():
    title = request.args.get("title", "").strip()
    # 模拟返回
    return success({
        "title": f"《{title}》",
        "author": "作者：某人",
        "published": "古代",
        "content": [{"title": "简介", "paragraphs": ["内容..."]}]
    })


# ---------- 管理员后台知识库管理接口 ----------
@knowledge_bp.route("/admin/list", methods=["GET"])
@admin_required
def admin_list(current_user):
    page = request.args.get("page", 1, type=int)
    size = request.args.get("size", 10, type=int)
    keyword = request.args.get("keyword", "").strip()
    query = Knowledge.query
    if keyword:
        query = query.filter(
            db.or_(Knowledge.name.contains(keyword), Knowledge.id == keyword if keyword.isdigit() else False)
        )
    paginated = query.order_by(Knowledge.updated_at.desc()).paginate(page=page, per_page=size, error_out=False)
    return success({
        "total": paginated.total,
        "pages": paginated.pages,
        "current": page,
        "records": [item.to_dict() for item in paginated.items]
    })


@knowledge_bp.route("/admin/detail/<int:knowledge_id>", methods=["GET"])
@admin_required
def admin_detail(current_user, knowledge_id):
    knowledge = Knowledge.query.get(knowledge_id)
    if not knowledge:
        return fail("内容不存在", 404)
    return success(knowledge.to_dict())


@knowledge_bp.route("/admin/add", methods=["POST"])
@admin_required
def admin_add(current_user):
    data = request.get_json(silent=True) or {}
    name = data.get("name", "").strip()
    if not name:
        return fail("名称不能为空")
    knowledge = Knowledge(
        cover=data.get("cover", ""),
        name=name,
        title=data.get("title", name),
        category=data.get("category", ""),
        inheritor=data.get("inheritor", ""),
        content_file_name=data.get("contentFileName", ""),
        file_url=data.get("fileUrl", ""),
        summary=data.get("summary", ""),
        content=data.get("content", ""),
        section_id=data.get("sectionId", ""),
        source="manual",
        status="published"
    )
    db.session.add(knowledge)
    db.session.commit()
    return success({"id": knowledge.id}, "新增成功")


@knowledge_bp.route("/admin/edit", methods=["POST"])
@admin_required
def admin_edit(current_user):
    data = request.get_json(silent=True) or {}
    knowledge_id = data.get("id")
    if not knowledge_id:
        return fail("id不能为空")
    knowledge = Knowledge.query.get(knowledge_id)
    if not knowledge:
        return fail("内容不存在", 404)
    knowledge.cover = data.get("cover", knowledge.cover)
    knowledge.name = data.get("name", knowledge.name)
    knowledge.title = data.get("title", knowledge.name)
    knowledge.category = data.get("category", knowledge.category)
    knowledge.inheritor = data.get("inheritor", knowledge.inheritor)
    knowledge.content_file_name = data.get("contentFileName", knowledge.content_file_name)
    knowledge.file_url = data.get("fileUrl", knowledge.file_url)
    knowledge.summary = data.get("summary", knowledge.summary)
    knowledge.content = data.get("content", knowledge.content)
    knowledge.section_id = data.get("sectionId", knowledge.section_id)
    db.session.commit()
    return success(None, "编辑成功")


@knowledge_bp.route("/admin/delete", methods=["POST"])
@admin_required
def admin_delete(current_user):
    data = request.get_json(silent=True) or {}
    knowledge_id = data.get("id")
    if not knowledge_id:
        return fail("id不能为空")
    knowledge = Knowledge.query.get(knowledge_id)
    if not knowledge:
        return fail("内容不存在", 404)
    db.session.delete(knowledge)
    db.session.commit()
    return success(None, "删除成功")


@knowledge_bp.route("/admin/search", methods=["GET"])
@admin_required
def admin_search(current_user):
    keyword = request.args.get("keyword", "").strip()
    query = Knowledge.query
    if keyword:
        query = query.filter(
            db.or_(Knowledge.name.contains(keyword), Knowledge.id == keyword if keyword.isdigit() else False)
        )
    items = query.order_by(Knowledge.updated_at.desc()).all()
    return success([item.to_dict() for item in items])


# ---------- AI 生成知识 ----------
@knowledge_bp.route("/ai-generate", methods=["POST"])
@admin_required
def ai_generate(current_user):
    data = request.get_json(silent=True) or {}
    keyword = data.get("keyword", "").strip()
    topic = data.get("topic", "").strip()
    section = data.get("section", "").strip()
    prompt = data.get("prompt", "").strip()
    save = data.get("save", False)
    if not any([keyword, topic, section, prompt]):
        return fail("keyword、topic、section、prompt 至少填写一个")
    if prompt:
        user_msg = prompt
    elif keyword:
        user_msg = f"请介绍螺钿工艺中的【{keyword}】，包括定义、特点、历史和相关技法。"
    elif topic:
        user_msg = f"请围绕【{topic}】写一篇关于螺钿工艺的知识短文，要求结构清晰，包含标题、摘要和正文。"
    else:
        user_msg = f"请生成螺钿工艺中【{section}】的知识内容，包含标题、摘要和详细说明。"
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        reply = loop.run_until_complete(ai_client.chat(user_msg))
        loop.close()
    except Exception as e:
        return fail(f"AI 服务调用失败: {str(e)}", 500)
    lines = reply.strip().split("\n")
    title = lines[0].strip("# ").strip() if lines else "AI生成内容"
    summary = lines[1][:200] if len(lines) > 1 else ""
    content = reply
    result = {"title": title, "summary": summary, "content": content, "section": section}
    if save:
        knowledge = Knowledge(
            section_id=section or "ai-generated",
            title=title,
            name=title,
            summary=summary,
            content=content,
            category="AI生成",
            source="ai",
            status="published"
        )
        db.session.add(knowledge)
        db.session.commit()
        result["id"] = knowledge.id
    return success(result, "AI生成成功")


# ---------- 审核相关（针对传承人提交的 MasterKnowledge）----------
@knowledge_bp.route("/review/list", methods=["GET"])
@admin_required
def review_list(current_user):
    page = request.args.get("page", 1, type=int)
    size = request.args.get("size", 10, type=int)
    query = MasterKnowledge.query.filter_by(status="待审核")
    paginated = query.order_by(MasterKnowledge.create_time.desc()).paginate(page=page, per_page=size, error_out=False)
    return success({
        "total": paginated.total,
        "pages": paginated.pages,
        "current": page,
        "records": [item.to_dict() for item in paginated.items]
    })


@knowledge_bp.route("/review/detail/<int:master_id>", methods=["GET"])
@admin_required
def review_detail(current_user, master_id):
    item = MasterKnowledge.query.get(master_id)
    if not item:
        return fail("待审核内容不存在", 404)
    return success(item.to_dict())


@knowledge_bp.route("/review/pass", methods=["POST"])
@admin_required
def review_pass(current_user):
    data = request.get_json(silent=True) or {}
    master_id = data.get("id")
    if not master_id:
        return fail("id不能为空")
    master = MasterKnowledge.query.get(master_id)
    if not master:
        return fail("记录不存在", 404)
    if master.status != "待审核":
        return fail("该记录已处理过", 400)
    # 创建 Knowledge 记录
    knowledge = Knowledge(
        cover=master.cover,
        name=master.name,
        title=master.name,
        category=master.category,
        inheritor=master.inheritor,
        content_file_name=master.content_file_name,
        file_url=master.file_url,
        source="master",
        status="published"
    )
    db.session.add(knowledge)
    master.status = "已发布"
    master.status_class = "published"
    db.session.commit()
    return success(None, "审核通过，已发布")


@knowledge_bp.route("/review/reject", methods=["POST"])
@admin_required
def review_reject(current_user):
    data = request.get_json(silent=True) or {}
    master_id = data.get("id")
    if not master_id:
        return fail("id不能为空")
    master = MasterKnowledge.query.get(master_id)
    if not master:
        return fail("记录不存在", 404)
    if master.status != "待审核":
        return fail("该记录已处理过", 400)
    master.status = "已退回"
    master.status_class = "rejected"
    db.session.commit()
    return success(None, "已退回")