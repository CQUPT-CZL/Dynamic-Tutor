#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
作业管理接口
"""

from fastapi import APIRouter, HTTPException
from ..common.database import get_db_connection
from datetime import datetime
from typing import List, Optional

router = APIRouter(prefix="/assignment", tags=["作业管理"])

@router.post("/create")
async def create_assignment(
    teacher_id: str,
    class_id: str,
    title: str,
    description: str,
    knowledge_points: List[str],
    due_date: str,
    question_count: int = 10
):
    """创建作业"""
    try:
        conn = get_db_connection()
        
        # 创建作业记录
        cursor = conn.execute("""
            INSERT INTO assignments 
            (teacher_id, class_id, title, description, due_date, question_count, created_at, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, 'active')
        """, (teacher_id, class_id, title, description, due_date, question_count, datetime.now().isoformat()))
        
        assignment_id = cursor.lastrowid
        
        # 关联知识点
        for knowledge_point in knowledge_points:
            conn.execute("""
                INSERT INTO assignment_knowledge_points (assignment_id, knowledge_point)
                VALUES (?, ?)
            """, (assignment_id, knowledge_point))
        
        conn.commit()
        conn.close()
        
        return {
            "status": "success",
            "assignment_id": assignment_id,
            "message": "作业创建成功"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建作业失败: {str(e)}")

@router.get("/list/{teacher_id}")
async def get_teacher_assignments(teacher_id: str):
    """获取教师的作业列表"""
    try:
        conn = get_db_connection()
        cursor = conn.execute("""
            SELECT 
                a.assignment_id,
                a.title,
                a.description,
                a.due_date,
                a.question_count,
                a.created_at,
                a.status,
                c.class_name
            FROM assignments a
            JOIN classes c ON a.class_id = c.class_id
            WHERE a.teacher_id = ?
            ORDER BY a.created_at DESC
        """, (teacher_id,))
        
        assignments = []
        for row in cursor.fetchall():
            assignments.append({
                "assignment_id": row["assignment_id"],
                "title": row["title"],
                "description": row["description"],
                "due_date": row["due_date"],
                "question_count": row["question_count"],
                "created_at": row["created_at"],
                "status": row["status"],
                "class_name": row["class_name"]
            })
        
        conn.close()
        return {"assignments": assignments}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取作业列表失败: {str(e)}")

@router.get("/submissions/{assignment_id}")
async def get_assignment_submissions(assignment_id: str):
    """获取作业提交情况"""
    try:
        conn = get_db_connection()
        
        # 获取作业信息
        cursor = conn.execute("""
            SELECT title, due_date, question_count
            FROM assignments WHERE assignment_id = ?
        """, (assignment_id,))
        assignment_info = cursor.fetchone()
        
        # 获取提交情况
        cursor = conn.execute("""
            SELECT 
                u.username,
                asub.submitted_at,
                asub.score,
                asub.completion_rate,
                asub.status
            FROM assignment_submissions asub
            JOIN users u ON asub.student_id = u.user_id
            WHERE asub.assignment_id = ?
            ORDER BY asub.submitted_at DESC
        """, (assignment_id,))
        
        submissions = []
        for row in cursor.fetchall():
            submissions.append({
                "username": row["username"],
                "submitted_at": row["submitted_at"],
                "score": row["score"],
                "completion_rate": row["completion_rate"],
                "status": row["status"]
            })
        
        conn.close()
        
        return {
            "assignment_info": {
                "title": assignment_info["title"],
                "due_date": assignment_info["due_date"],
                "question_count": assignment_info["question_count"]
            },
            "submissions": submissions,
            "statistics": {
                "total_submissions": len(submissions),
                "average_score": sum(s["score"] for s in submissions if s["score"]) / len(submissions) if submissions else 0
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取作业提交情况失败: {str(e)}")

@router.put("/update/{assignment_id}")
async def update_assignment(
    assignment_id: str,
    title: Optional[str] = None,
    description: Optional[str] = None,
    due_date: Optional[str] = None,
    status: Optional[str] = None
):
    """更新作业信息"""
    try:
        conn = get_db_connection()
        
        update_fields = []
        params = []
        
        if title:
            update_fields.append("title = ?")
            params.append(title)
        if description:
            update_fields.append("description = ?")
            params.append(description)
        if due_date:
            update_fields.append("due_date = ?")
            params.append(due_date)
        if status:
            update_fields.append("status = ?")
            params.append(status)
        
        if update_fields:
            params.append(assignment_id)
            query = f"UPDATE assignments SET {', '.join(update_fields)} WHERE assignment_id = ?"
            conn.execute(query, params)
            conn.commit()
        
        conn.close()
        
        return {
            "status": "success",
            "message": "作业更新成功"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新作业失败: {str(e)}")