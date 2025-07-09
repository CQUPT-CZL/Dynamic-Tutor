#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
系统相关接口
"""

from fastapi import APIRouter
from datetime import datetime
from .database import get_db_connection

router = APIRouter(tags=["系统"])

@router.get("/")
async def root():
    """API根路径"""
    return {
        "message": "🎓 AI智慧学习平台API",
        "version": "1.0.0",
        "docs": "/docs",
        "status": "running"
    }

@router.get("/health")
async def health_check():
    """健康检查"""
    try:
        conn = get_db_connection()
        conn.execute("SELECT 1")
        conn.close()
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "database": "connected"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "timestamp": datetime.now().isoformat(),
            "database": "disconnected",
            "error": str(e)
        } 