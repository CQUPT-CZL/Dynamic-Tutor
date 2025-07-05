#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
用户统计接口
"""

from fastapi import APIRouter, HTTPException
from .database import get_db_connection

router = APIRouter(prefix="/stats", tags=["用户统计"])

@router.get("/{user_id}")
async def get_user_stats(user_id: str):
    """获取用户统计"""
    try:
        conn = get_db_connection()
        
        # 获取今日答题数
        cursor = conn.execute("""
            SELECT COUNT(*) as count 
            FROM user_answers 
            WHERE user_id = ? AND DATE(timestamp) = DATE('now')
        """, (user_id,))
        total_questions_answered = cursor.fetchone()["count"]
        
        # 获取正确率
        cursor = conn.execute("""
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN is_correct = 1 THEN 1 ELSE 0 END) as correct
            FROM user_answers 
            WHERE user_id = ?
        """, (user_id,))
        row = cursor.fetchone()
        correct_rate = row["correct"] / row["total"] if row["total"] > 0 else 0.0
        
        # 获取用户掌握的知识点数量
        cursor = conn.execute("""
            SELECT COUNT(*) as count 
            FROM user_node_mastery 
            WHERE user_id = ? AND mastery_score > 0.8
        """, (user_id,))
        mastered_nodes = cursor.fetchone()["count"]
        
        # 获取用户总的知识点数量
        cursor = conn.execute("""
            SELECT COUNT(*) as count 
            FROM user_node_mastery 
            WHERE user_id = ?
        """, (user_id,))
        total_nodes = cursor.fetchone()["count"]
        
        # 计算平均掌握度
        cursor = conn.execute("""
            SELECT AVG(mastery_score) as avg_mastery 
            FROM user_node_mastery 
            WHERE user_id = ?
        """, (user_id,))
        avg_mastery = cursor.fetchone()["avg_mastery"] or 0.0
        
        # 获取连续学习天数（基于答题记录）
        cursor = conn.execute("""
            SELECT COUNT(DISTINCT DATE(timestamp)) as days
            FROM user_answers 
            WHERE user_id = ?
        """, (user_id,))
        streak_days = cursor.fetchone()["days"]
        
        # 计算今日学习时长（基于答题记录的总用时）
        cursor = conn.execute("""
            SELECT COALESCE(SUM(time_spent), 0) as total_time
            FROM user_answers 
            WHERE user_id = ? AND DATE(timestamp) = DATE('now')
        """, (user_id,))
        study_time_today = cursor.fetchone()["total_time"] // 60  # 转换为分钟
        
        conn.close()
        
        return {
            "total_questions_answered": total_questions_answered,
            "correct_rate": correct_rate,
            "study_time_today": study_time_today,
            "streak_days": streak_days,
            "mastered_nodes": mastered_nodes,
            "total_nodes": total_nodes,
            "avg_mastery": avg_mastery
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取用户统计失败: {str(e)}") 