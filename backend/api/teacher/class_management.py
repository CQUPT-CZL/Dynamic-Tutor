#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
班级管理接口
"""

from fastapi import APIRouter, HTTPException
from ..common.database import get_db_connection

router = APIRouter(prefix="/class", tags=["班级管理"])

@router.get("/list/{teacher_id}")
async def get_teacher_classes(teacher_id: str):
    """获取教师的班级列表"""
    try:
        conn = get_db_connection()
        cursor = conn.execute("""
            SELECT class_id, class_name, grade, student_count
            FROM classes 
            WHERE teacher_id = ?
            ORDER BY grade, class_name
        """, (teacher_id,))
        
        classes = []
        for row in cursor.fetchall():
            classes.append({
                "class_id": row["class_id"],
                "class_name": row["class_name"],
                "grade": row["grade"],
                "student_count": row["student_count"]
            })
        
        conn.close()
        return {"classes": classes}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取班级列表失败: {str(e)}")

@router.get("/students/{class_id}")
async def get_class_students(class_id: str):
    """获取班级学生列表"""
    try:
        conn = get_db_connection()
        cursor = conn.execute("""
            SELECT u.user_id, u.username, cs.join_date
            FROM users u
            JOIN class_students cs ON u.user_id = cs.student_id
            WHERE cs.class_id = ? AND u.role = 'student'
            ORDER BY u.username
        """, (class_id,))
        
        students = []
        for row in cursor.fetchall():
            students.append({
                "user_id": row["user_id"],
                "username": row["username"],
                "join_date": row["join_date"]
            })
        
        conn.close()
        return {"students": students}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取学生列表失败: {str(e)}")

@router.post("/create")
async def create_class(teacher_id: str, class_name: str, grade: str):
    """创建新班级"""
    try:
        conn = get_db_connection()
        cursor = conn.execute("""
            INSERT INTO classes (teacher_id, class_name, grade, student_count)
            VALUES (?, ?, ?, 0)
        """, (teacher_id, class_name, grade))
        
        class_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return {
            "status": "success",
            "class_id": class_id,
            "message": "班级创建成功"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建班级失败: {str(e)}")