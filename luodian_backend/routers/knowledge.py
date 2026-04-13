# knowledge.py
from flask import Blueprint, jsonify, request

from database import db
from models import Knowledge
from ai_client import generate_knowledge

knowledge_bp = Blueprint("knowledge", __name__, url_prefix="/api/knowledge")

KNOWLEDGE_NAV = [
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

DEFAULT_KNOWLEDGE = {
    "history": {
        "title": "螺钿工艺历史总览",
        "summary": "螺钿工艺是中国传统髹漆与镶嵌工艺的重要组成部分。",
        "content": "螺钿工艺以贝壳、螺片等天然材料为装饰媒介，通过切割、打磨、镶嵌、髹漆与抛光等工序，形成独特的纹理与光彩效果。它不仅是一种装饰技术，也承载着传统审美、礼制文化与手工精神。"
    },
    "origin": {
        "title": "起源与早期发展",
        "summary": "螺钿工艺源于人们对贝壳天然光泽的利用。",
        "content": "在早期社会中，人们发现贝壳具有天然的色泽和光感，于是逐步将其运用到器物装饰之中。随着漆器工艺的发展，贝壳与髹漆结合，螺钿工艺逐渐形成。"
    },
    "tang": {
        "title": "唐代的鼎盛",
        "summary": "唐代螺钿工艺华丽开放，反映盛唐气象。",
        "content": "唐代是工艺美术高度繁荣的时期，螺钿广泛用于漆器、铜镜、乐器和生活器物。题材丰富，色彩华美，体现出开放、繁盛和兼容并包的时代风貌。"
    },
    "song": {
        "title": "宋代的雅致",
        "summary": "宋代螺钿工艺趋于细腻、典雅、含蓄。",
        "content": "宋代器物审美强调文雅和内敛，螺钿装饰也更注重细节、比例和气韵的统一。工匠在材料处理和图案布局上更加考究。"
    },
    "mingqing": {
        "title": "明清的巅峰",
        "summary": "明清时期螺钿工艺应用广泛，制作成熟。",
        "content": "明清时期，螺钿广泛用于家具、屏风、文房器具和礼器之中，工艺更加成熟，图案更加繁复，成为传统器物装饰的重要形式。"
    },
    "modern": {
        "title": "近现代的传承",
        "summary": "现代螺钿工艺在保护与创新中延续发展。",
        "content": "近现代以来，螺钿工艺在非遗保护、院校教学、文创开发和数字展示中逐步焕发新生，成为连接传统工艺与现代传播的重要桥梁。"
    },
    "techniques": {
        "title": "技法演变",
        "summary": "螺钿技法包括选材、切割、打磨、镶嵌、髹漆、抛光等环节。",
        "content": "螺钿制作通常包括原料筛选、螺片切割、纹样修整、器物开槽、镶嵌、反复上漆和表面抛光等步骤。不同地域和流派在技法上各有特色。"
    },
    "materials": {
        "title": "材料与工具",
        "summary": "螺钿材料主要包括贝壳、螺片、漆料和打磨工具。",
        "content": "常见材料有夜光贝、鲍鱼贝、珍珠贝等，辅助材料则包括漆料、胶料和底胎。常见工具包括刻刀、锉刀、磨具、镊子等。"
    },
    "influence": {
        "title": "文化影响",
        "summary": "螺钿工艺体现了中国传统工艺审美和非遗价值。",
        "content": "螺钿工艺不仅服务于器物装饰，也反映了中国传统文化中关于自然材料、手工秩序和审美表达的理解。今天，它仍在教育、展览和数字传播中发挥作用。"
    },
}

def success(data=None, msg="success"):
    """统一成功返回"""
    return jsonify({"code": 200, "msg": msg, "data": data})

def fail(msg="请求失败", code=400):
    """统一失败返回"""
    return jsonify({"code": code, "msg": msg, "data": None}), code

def init_default_knowledge():
    """初始化默认知识库数据"""
    for section_id, item in DEFAULT_KNOWLEDGE.items():
        exists = Knowledge.query.filter_by(section_id=section_id).first()
        if not exists:
            db.session.add(Knowledge(
                section_id=section_id,
                title=item["title"],
                name=item["title"],
                summary=item["summary"],
                content=item["content"],
                category="螺钿知识",
                source="system",
            ))
    db.session.commit()

@knowledge_bp.route("/detail/nav", methods=["GET"])
def get_nav():
    """获取知识库导航"""
    return success(KNOWLEDGE_NAV)

@knowledge_bp.route("/detail/<string:section_id>", methods=["GET"])
def get_detail(section_id):
    """获取知识库详情"""
    knowledge = Knowledge.query.filter_by(section_id=section_id).first()

    if not knowledge and section_id in DEFAULT_KNOWLEDGE:
        item = DEFAULT_KNOWLEDGE[section_id]
        return success({
            "sectionId": section_id,
            "title": item["title"],
            "name": item["title"],
            "summary": item["summary"],
            "content": item["content"],
            "source": "default",
        })

    if not knowledge:
        return fail("知识内容不存在", 404)

    return success(knowledge.to_dict())

@knowledge_bp.route("/search", methods=["GET"])
def search():
    """搜索知识库"""
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
        )
    ).order_by(Knowledge.updated_at.desc())

    return success([item.to_dict() for item in query.all()])

@knowledge_bp.route("/add", methods=["POST"])
def add_knowledge():
    """新增知识库内容"""
    data = request.get_json(silent=True) or {}
    name = (data.get("name") or data.get("title") or "").strip()

    if not name:
        return fail("name不能为空")

    knowledge = Knowledge(
        section_id=(data.get("sectionId") or data.get("section_id") or "").strip(),
        title=(data.get("title") or name).strip(),
        name=name,
        summary=(data.get("summary") or "").strip(),
        content=(data.get("content") or "").strip(),
        cover=(data.get("cover") or "").strip(),
        category=(data.get("category") or "").strip(),
        inheritor=(data.get("inheritor") or "").strip(),
        content_file_name=(data.get("contentFileName") or "").strip(),
        file_url=(data.get("fileUrl") or "").strip(),
        source=(data.get("source") or "manual").strip(),
    )

    db.session.add(knowledge)
    db.session.commit()
    return success(knowledge.to_dict(), "新增成功")

@knowledge_bp.route("/edit", methods=["POST"])
def edit_knowledge():
    """编辑知识库内容"""
    data = request.get_json(silent=True) or {}
    knowledge_id = data.get("id")

    if not knowledge_id:
        return fail("id不能为空")

    knowledge = Knowledge.query.get(knowledge_id)
    if not knowledge:
        return fail("知识内容不存在", 404)

    knowledge.cover = data.get("cover", knowledge.cover)
    knowledge.name = data.get("name", knowledge.name)
    knowledge.title = data.get("title", data.get("name", knowledge.title))
    knowledge.category = data.get("category", knowledge.category)
    knowledge.inheritor = data.get("inheritor", knowledge.inheritor)
    knowledge.content_file_name = data.get("contentFileName", knowledge.content_file_name)
    knowledge.file_url = data.get("fileUrl", knowledge.file_url)
    knowledge.summary = data.get("summary", knowledge.summary)
    knowledge.content = data.get("content", knowledge.content)
    knowledge.section_id = data.get("sectionId", knowledge.section_id)

    db.session.commit()
    return success(knowledge.to_dict(), "修改成功")

@knowledge_bp.route("/ai-generate", methods=["POST"])
def ai_generate():
    """AI 生成知识库内容"""
    data = request.get_json(silent=True) or {}

    keyword = (data.get("keyword") or "").strip()
    topic = (data.get("topic") or "").strip()
    section = (data.get("section") or "").strip()
    prompt = (data.get("prompt") or "").strip()
    save = bool(data.get("save", False))

    if not any([keyword, topic, section, prompt]):
        return fail("keyword、topic、section、prompt 至少填写一个")

    result = generate_knowledge(
        keyword=keyword,
        topic=topic,
        section=section,
        prompt=prompt,
    )

    if save:
        knowledge = Knowledge(
            section_id=result.get("section", "ai-generated"),
            title=result.get("title", "AI生成知识内容"),
            name=result.get("title", "AI生成知识内容"),
            summary=result.get("summary", ""),
            content=result.get("content", ""),
            category="AI生成",
            source="ai",
        )
        db.session.add(knowledge)
        db.session.commit()
        result["id"] = knowledge.id

    return success(result, "AI生成成功")