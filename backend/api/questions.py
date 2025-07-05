#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
练习题目接口
"""

from fastapi import APIRouter, HTTPException
from .database import get_db_connection

router = APIRouter(prefix="/questions", tags=["练习题目"])

@router.get("/{node_name}")
async def get_questions_for_node(node_name: str):
    """获取知识点练习题"""
    try:
        conn = get_db_connection()
        cursor = conn.execute("""
            SELECT q.question_text 
            FROM questions q
            JOIN question_to_node_mapping qtnm ON q.question_id = qtnm.question_id
            JOIN knowledge_nodes kn ON qtnm.node_id = kn.node_id
            WHERE kn.node_name = ?
            ORDER BY RANDOM() 
            LIMIT 10
        """, (node_name,))
        
        questions = [row["question_text"] for row in cursor.fetchall()]
        conn.close()
        
        return {"questions": questions}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取练习题失败: {str(e)}") 