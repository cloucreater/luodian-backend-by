# 非遗螺钿文化平台 - 后端 API

## 环境要求
- Python 3.10+
- 虚拟环境 (推荐 venv)

## 安装与运行

1. 创建虚拟环境
   ```bash
   python -m venv venv
   source venv/bin/activate   # Linux/Mac
   venv\Scripts\activate      # Windows
   ```
2. 安装依赖
   ```bash
   pip install -r requirements.txt
   ```
3. 配置环境变量
   ```bash
   cp .env.example .env
   # 编辑 .env 文件，填入真实密钥
   ```
4. 运行
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 3001
   ```
5. 访问 API 文档
   http://localhost:3001/docs

## 目录结构
见项目文件。

## 主要功能
- 用户注册/登录/JWT认证
- 文章增删改查（管理员权限）
- 评论与点赞
- 收藏功能
- 社区动态（发布、评论、点赞）
- AI 智能问答（支持 OpenAI/智谱/本地模型）

## 前端对接
前端需将 API 请求代理到后端地址，并在请求头添加 `Authorization: Bearer <token>`。
