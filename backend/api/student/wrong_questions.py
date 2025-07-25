#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
错题集接口
"""
from fastapi import APIRouter, HTTPException
from ..common.database import get_db_connection

router = APIRouter(prefix="/wrong-questions", tags=["错题集"])

@router.get("/{user_id}")
async def get_wrong_questions(user_id: str):
    """获取错题集"""
    try:
        conn = get_db_connection()
        cursor = conn.execute("""
            SELECT 
                wq.wrong_id,
                wq.question_id,
                q.question_text,
                wq.wrong_count,
                wq.last_wrong_time,
                wq.status,
                kn.node_name as knowledge_points,
                q.difficulty
            FROM wrong_questions wq
            JOIN questions q ON wq.question_id = q.question_id
            LEFT JOIN question_to_node_mapping qtnm ON q.question_id = qtnm.question_id
            LEFT JOIN knowledge_nodes kn ON qtnm.node_id = kn.node_id
            WHERE wq.user_id = ?
            ORDER BY wq.last_wrong_time DESC
        """, (user_id,))
        
        wrong_questions = []
        
        for row in cursor.fetchall():
            wrong_questions.append({
                "wrong_id": row["wrong_id"],
                "question_id": str(row["question_id"]),
                "question_text": row["question_text"],
                "wrong_count": row["wrong_count"],
                "last_wrong_time": row["last_wrong_time"],
                "knowledge_points": row["knowledge_points"] or "未知",
                "difficulty": "简单" if row["difficulty"] < 0.4 else "中等" if row["difficulty"] < 0.7 else "困难",
                "status": row["status"],
                "subject": row["knowledge_points"] or "未知",  # 为前端兼容性添加subject字段
                "date": row["last_wrong_time"]  # 为前端兼容性添加date字段
            })
        
        conn.close()
        return {"wrong_questions": wrong_questions}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取错题集失败: {str(e)}")