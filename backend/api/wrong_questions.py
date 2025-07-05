#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
错题集接口
"""
from fastapi import APIRouter, HTTPException
from .database import get_db_connection

router = APIRouter(prefix="/wrong-questions", tags=["错题集"])

@router.get("/{user_id}")
async def get_wrong_questions(user_id: str):
    # print(user_id)
    # return {"wrong_questions" : []}
    # ≈
    """获取错题集"""
    try:
        conn = get_db_connection()
        # cursor = conn.execute("""
        #     SELECT 
        #         wq.wrong_id,
        #         wq.question_id,
        #         q.question_text,
        #         wq.wrong_count,
        #         wq.first_wrong_time,
        #         wq.last_wrong_time,
        #         wq.status,
        #         kn.node_name as knowledge_points,
        #         q.difficulty
        #     FROM wrong_questions wq
        #     JOIN questions q ON wq.question_id = q.question_id
        #     LEFT JOIN question_to_node_mapping qtnm ON q.question_id = qtnm.question_id
        #     LEFT JOIN knowledge_nodes kn ON qtnm.node_id = kn.node_id
        #     WHERE wq.user_id = ?
        #     ORDER BY wq.last_wrong_time DESC
        # """, (user_id,))
        
        wrong_questions = [
            {
                "question_id": "1",
                "question_text": "1+1=几",
                "wrong_count": 2,
                "first_wrong_time": "2024-03-01 10:00:00",
                "last_wrong_time": "2024-03-02 15:30:00", 
                "knowledge_points": "代数",
                "difficulty": "简单",
                "status": 0
            }
        ]
        
        # for row in cursor.fetchall():
        #     wrong_questions.append({
        #         "question_id": str(row["question_id"]),
        #         "question_text": row["question_text"],
        #         "wrong_count": row["wrong_count"],
        #         "first_wrong_time": row["first_wrong_time"],
        #         "last_wrong_time": row["last_wrong_time"],
        #         "knowledge_points": row["knowledge_points"] or "未知",
        #         "difficulty": "简单" if row["difficulty"] < 0.4 else "中等" if row["difficulty"] < 0.7 else "困难",
        #         "status": row["status"]
        #     })
        
        conn.close()
        # print(wrong_questions)
        return {"wrong_questions": wrong_questions}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取错题集失败: {str(e)}") 