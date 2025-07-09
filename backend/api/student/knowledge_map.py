#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
知识图谱接口
"""

from fastapi import APIRouter, HTTPException
from ..common.database import get_db_connection

router = APIRouter(prefix="/knowledge-map", tags=["知识图谱"])

@router.get("/{user_id}")
async def get_knowledge_map(user_id: str):
    """获取用户知识图谱"""
    try:
        conn = get_db_connection()
        cursor = conn.execute("""
            SELECT 
                kn.node_id,
                kn.node_name,
                kn.node_difficulty,
                kn.level,
                COALESCE(unm.mastery_score, 0.0) as mastery_score
            FROM knowledge_nodes kn
            LEFT JOIN user_node_mastery unm ON kn.node_id = unm.node_id AND unm.user_id = ?
            ORDER BY kn.node_id
        """, (1,))
        knowledge_map = []
        for row in cursor.fetchall():
            knowledge_map.append({
                "node_id": row["node_id"],
                "node_name": row["node_name"],
                "difficulty": row["node_difficulty"],
                "level": row["level"],
                "mastery": row["mastery_score"]
            })
        print(knowledge_map)
        
        conn.close()
        return knowledge_map
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取知识图谱失败: {str(e)}")

@router.get("/get-nodes")
async def get_knowledge_nodes():
    """获取所有知识节点"""
    try:
        print('huoquezhishidian')
        conn = get_db_connection()
        cursor = conn.execute("SELECT node_id, node_name, node_difficulty FROM knowledge_nodes")
        
        nodes = {}
        for row in cursor.fetchall():
            nodes[row["node_id"]] = row["node_name"]
        # print('---111')
        # print(nodes)
        conn.close()
        return {"nodes": nodes}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取知识节点失败: {str(e)}")

@router.get("/mastery/{user_id}/{node_name}")
async def get_user_mastery(user_id: str, node_name: str):
    """获取用户掌握度"""
    try:
        conn = get_db_connection()
        cursor = conn.execute("""
            SELECT unm.mastery_score 
            FROM user_node_mastery unm
            JOIN knowledge_nodes kn ON unm.node_id = kn.node_id
            WHERE unm.user_id = ? AND kn.node_name = ?
        """, (user_id, node_name))
        
        row = cursor.fetchone()
        mastery = row["mastery_score"] if row else 0.0
        
        conn.close()
        return {"mastery": mastery}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取掌握度失败: {str(e)}")

@router.post("/mastery/{user_id}/{node_name}")
async def update_user_mastery(user_id: str, node_name: str, mastery_score: float):
    """更新用户掌握度"""
    try:
        conn = get_db_connection()
        
        # 获取知识点ID
        cursor = conn.execute("SELECT node_id FROM knowledge_nodes WHERE node_name = ?", (node_name,))
        node_row = cursor.fetchone()
        if not node_row:
            raise HTTPException(status_code=404, detail=f"知识点 '{node_name}' 不存在")
        
        node_id = node_row["node_id"]
        
        # 检查是否已有掌握度记录
        cursor = conn.execute("""
            SELECT mastery_id FROM user_node_mastery 
            WHERE user_id = ? AND node_id = ?
        """, (user_id, node_id))
        
        existing = cursor.fetchone()
        if existing:
            # 更新现有记录
            conn.execute("""
                UPDATE user_node_mastery 
                SET mastery_score = ? 
                WHERE user_id = ? AND node_id = ?
            """, (mastery_score, user_id, node_id))
        else:
            # 创建新记录
            conn.execute("""
                INSERT INTO user_node_mastery (user_id, node_id, mastery_score)
                VALUES (?, ?, ?)
            """, (user_id, node_id, mastery_score))
        
        conn.commit()
        conn.close()
        
        return {"status": "success", "mastery": mastery_score}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新掌握度失败: {str(e)}")