#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
学生学习分析接口
"""

from fastapi import APIRouter, HTTPException
from ..common.database import get_db_connection
from datetime import datetime, timedelta

router = APIRouter(prefix="/analytics", tags=["学生分析"])

@router.get("/class/{class_id}/overview")
async def get_class_overview(class_id: str):
    """获取班级学习概览"""
    try:
        conn = get_db_connection()
        
        # 获取班级基本信息
        cursor = conn.execute("""
            SELECT class_name, grade, student_count
            FROM classes WHERE class_id = ?
        """, (class_id,))
        class_info = cursor.fetchone()
        
        # 获取班级平均掌握度
        cursor = conn.execute("""
            SELECT AVG(unm.mastery_score) as avg_mastery
            FROM user_node_mastery unm
            JOIN class_students cs ON unm.user_id = cs.student_id
            WHERE cs.class_id = ?
        """, (class_id,))
        avg_mastery = cursor.fetchone()["avg_mastery"] or 0.0
        
        # 获取活跃学生数
        week_ago = (datetime.now() - timedelta(days=7)).isoformat()
        cursor = conn.execute("""
            SELECT COUNT(DISTINCT ua.user_id) as active_students
            FROM user_answers ua
            JOIN class_students cs ON ua.user_id = cs.student_id
            WHERE cs.class_id = ? AND ua.timestamp > ?
        """, (class_id, week_ago))
        active_students = cursor.fetchone()["active_students"] or 0
        
        conn.close()
        
        return {
            "class_info": {
                "class_name": class_info["class_name"],
                "grade": class_info["grade"],
                "total_students": class_info["student_count"]
            },
            "statistics": {
                "average_mastery": round(avg_mastery, 2),
                "active_students_week": active_students,
                "activity_rate": round(active_students / class_info["student_count"] * 100, 1) if class_info["student_count"] > 0 else 0
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取班级概览失败: {str(e)}")

@router.get("/student/{student_id}/progress")
async def get_student_progress(student_id: str):
    """获取学生学习进度"""
    try:
        conn = get_db_connection()
        
        # 获取学生基本信息
        cursor = conn.execute("""
            SELECT username FROM users WHERE user_id = ?
        """, (student_id,))
        student_info = cursor.fetchone()
        
        # 获取知识点掌握情况
        cursor = conn.execute("""
            SELECT kn.node_name, unm.mastery_score
            FROM knowledge_nodes kn
            LEFT JOIN user_node_mastery unm ON kn.node_id = unm.node_id AND unm.user_id = ?
            ORDER BY kn.level, kn.node_id
        """, (student_id,))
        
        knowledge_progress = []
        for row in cursor.fetchall():
            knowledge_progress.append({
                "knowledge_point": row["node_name"],
                "mastery_score": row["mastery_score"] or 0.0
            })
        
        # 获取最近答题记录
        cursor = conn.execute("""
            SELECT question_id, is_correct, timestamp
            FROM user_answers
            WHERE user_id = ?
            ORDER BY timestamp DESC
            LIMIT 10
        """, (student_id,))
        
        recent_answers = []
        for row in cursor.fetchall():
            recent_answers.append({
                "question_id": row["question_id"],
                "is_correct": row["is_correct"],
                "timestamp": row["timestamp"]
            })
        
        conn.close()
        
        return {
            "student_info": {
                "username": student_info["username"],
                "user_id": student_id
            },
            "knowledge_progress": knowledge_progress,
            "recent_answers": recent_answers
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取学生进度失败: {str(e)}")

@router.get("/class/{class_id}/weak-points")
async def get_class_weak_points(class_id: str):
    """获取班级薄弱知识点"""
    try:
        conn = get_db_connection()
        cursor = conn.execute("""
            SELECT 
                kn.node_name,
                AVG(COALESCE(unm.mastery_score, 0)) as avg_mastery,
                COUNT(cs.student_id) as student_count
            FROM knowledge_nodes kn
            CROSS JOIN class_students cs
            LEFT JOIN user_node_mastery unm ON kn.node_id = unm.node_id AND unm.user_id = cs.student_id
            WHERE cs.class_id = ?
            GROUP BY kn.node_id, kn.node_name
            HAVING avg_mastery < 0.6
            ORDER BY avg_mastery ASC
            LIMIT 10
        """, (class_id,))
        
        weak_points = []
        for row in cursor.fetchall():
            weak_points.append({
                "knowledge_point": row["node_name"],
                "average_mastery": round(row["avg_mastery"], 2),
                "student_count": row["student_count"]
            })
        
        conn.close()
        return {"weak_points": weak_points}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取薄弱知识点失败: {str(e)}")