#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
用户管理接口
"""

from fastapi import APIRouter, HTTPException
from .database import get_db_connection

router = APIRouter(prefix="/users", tags=["用户管理"])

@router.get("/")
async def get_users():
    """获取用户列表"""
    try:
        conn = get_db_connection()
        cursor = conn.execute("SELECT user_id, username, role FROM users")
        users = [{"user_id": row["user_id"], "username": row["username"], "role": row["role"]} for row in cursor.fetchall()]
        conn.close()
        return users
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取用户列表失败: {str(e)}") 