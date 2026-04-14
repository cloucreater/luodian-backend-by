import os
from functools import wraps
from flask import request, jsonify
from jose import jwt, JWTError
from models import User
from database import db

SECRET_KEY = os.getenv("SECRET_KEY", "your_secret_key_here_change_in_production")
ALGORITHM = "HS256"

def get_token_from_header():
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return None
    return auth_header.split(" ")[1]

def get_current_user():
    token = get_token_from_header()
    if not token:
        return None
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if not user_id:
            return None
        user = User.query.get(int(user_id))
        return user
    except (JWTError, ValueError):
        return None

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        user = get_current_user()
        if not user:
            return jsonify({"code": 401, "msg": "未登录或登录已过期", "data": None}), 401
        return f(current_user=user, *args, **kwargs)
    return decorated

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        user = get_current_user()
        if not user:
            return jsonify({"code": 401, "msg": "未登录", "data": None}), 401
        if user.role != "admin":
            return jsonify({"code": 403, "msg": "无管理员权限", "data": None}), 403
        return f(current_user=user, *args, **kwargs)
    return decorated