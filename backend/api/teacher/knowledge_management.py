#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
知识点管理接口
"""
import requests
import json
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from ..common.database import get_db_connection
from datetime import datetime
from typing import Optional, List
import time

class CreateKnowledgeRequest(BaseModel):
    node_name: str
    node_difficulty: float
    level: int
    node_learning: str
    prerequisites: Optional[List[str]] = []

class UpdateKnowledgeRequest(BaseModel):
    node_id: int
    node_name: Optional[str] = None
    node_difficulty: Optional[float] = None
    level: Optional[int] = None
    node_learning: Optional[str] = None

class CreateKnowledgeEdgeRequest(BaseModel):
    source_node_id: str
    target_node_id: str
    relation_type: str = "指向"

class DeleteKnowledgeEdgeRequest(BaseModel):
    source_node_id: str
    target_node_id: str
    relation_type: str = "指向"

router = APIRouter(prefix="/knowledge", tags=["知识点管理"])

@router.post("/create")
async def create_knowledge_point(request: CreateKnowledgeRequest):
    """创建知识点"""
    try:
        conn = get_db_connection()
        
        # 检查知识点是否已存在
        cursor = conn.execute("""
            SELECT node_id FROM knowledge_nodes WHERE node_name = ?
        """, (request.node_name,))
        existing_node = cursor.fetchone()
        
        if existing_node:
            conn.close()
            raise HTTPException(status_code=400, detail="知识点名称已存在")
        
        # 验证难度值范围
        if request.node_difficulty is not None and (request.node_difficulty < 0.0 or request.node_difficulty > 1.0):
            raise HTTPException(status_code=400, detail="知识点难度必须在0.0-1.0之间")
        
        # 创建知识点
        cursor = conn.execute("""
            INSERT INTO knowledge_nodes 
            (node_name, node_difficulty, level, node_learning)
            VALUES (?, ?, ?, ?)
        """, (request.node_name, request.node_difficulty, request.level, request.node_learning))
        
        # 获取自动生成的node_id
        node_id = cursor.lastrowid
        
        # 添加前置知识点关系
        if request.prerequisites:
            for prerequisite in request.prerequisites:
                # 查找前置知识点ID
                prereq_cursor = conn.execute("""
                    SELECT node_id FROM knowledge_nodes WHERE node_name = ? OR node_id = ?
                """, (prerequisite, prerequisite))
                prereq_node = prereq_cursor.fetchone()
                
                if prereq_node:
                    # 使用默认的teacher用户ID (假设为3，根据初始数据)
                    conn.execute("""
                        INSERT INTO knowledge_edges (source_node_id, target_node_id, relation_type, created_by)
                        VALUES (?, ?, '指向', 3)
                    """, (prereq_node["node_id"], node_id))
        
        conn.commit()
        conn.close()
        
        return {
            "status": "success",
            "node_id": str(node_id),
            "message": "知识点创建成功"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建知识点失败: {str(e)}")

@router.get("/list")
async def get_knowledge_points(
    level: Optional[str] = None,
    min_difficulty: Optional[float] = None,
    max_difficulty: Optional[float] = None
):
    """获取知识点列表"""
    try:
        conn = get_db_connection()
        
        # 构建查询条件
        conditions = []
        params = []
        
        if level:
            conditions.append("level = ?")
            params.append(level)
        
        if min_difficulty is not None:
            conditions.append("node_difficulty >= ?")
            params.append(min_difficulty)
            
        if max_difficulty is not None:
            conditions.append("node_difficulty <= ?")
            params.append(max_difficulty)
        
        where_clause = " WHERE " + " AND ".join(conditions) if conditions else ""
        
        cursor = conn.execute(f"""
            SELECT 
                node_id,
                node_name,
                node_difficulty,
                level,
                node_learning
            FROM knowledge_nodes
            {where_clause}
            ORDER BY level, node_name
        """, params)
        
        knowledge_points = []
        for row in cursor.fetchall():
            knowledge_points.append({
                "node_id": row["node_id"],
                "node_name": row["node_name"],
                "node_difficulty": row["node_difficulty"],
                "level": row["level"],
                "node_learning": row["node_learning"]
            })
        
        conn.close()
        return {"knowledge_points": knowledge_points}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取知识点列表失败: {str(e)}")

@router.put("/update/{node_id}")
async def update_knowledge_point(
    request: UpdateKnowledgeRequest
):
    """更新知识点信息"""
    try:
        # print(request)
        node_id = int(request.node_id)
        conn = get_db_connection()
        # print(f"Received data: node_id={node_id}, request={request}")
        
        # 验证难度值范围
        if request.node_difficulty is not None and (request.node_difficulty < 0.0 or request.node_difficulty > 1.0):
            raise HTTPException(status_code=400, detail="知识点难度必须在0.0-1.0之间")
        
        update_fields = []
        params = []
        
        if request.node_name:
            update_fields.append("node_name = ?")
            params.append(request.node_name)
        if request.node_difficulty is not None:
            update_fields.append("node_difficulty = ?")
            params.append(request.node_difficulty)
        if request.level:
            update_fields.append("level = ?")
            params.append(request.level)
        if request.node_learning:
            update_fields.append("node_learning = ?")
            params.append(request.node_learning)
        
        if update_fields:
            params.append(node_id)
            query = f"UPDATE knowledge_nodes SET {', '.join(update_fields)} WHERE node_id = ?"
            conn.execute(query, params)
            conn.commit()
        
        conn.close()
        
        return {
            "status": "success",
            "message": "知识点更新成功"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新知识点失败: {str(e)}")

@router.delete("/delete/{node_id}")
async def delete_knowledge_point(node_id: str):
    """删除知识点"""
    try:
        conn = get_db_connection()
        
        # 检查是否有学生掌握度记录
        cursor = conn.execute("""
            SELECT COUNT(*) as count FROM user_node_mastery WHERE node_id = ?
        """, (node_id,))
        mastery_count = cursor.fetchone()["count"]
        
        if mastery_count > 0:
            conn.close()
            raise HTTPException(status_code=400, detail="该知识点已有学生学习记录，无法删除")
        
        # 删除相关边
        conn.execute("""
            DELETE FROM knowledge_edges 
            WHERE source_node_id = ? OR target_node_id = ?
        """, (node_id, node_id))
        
        # 删除知识点
        conn.execute("""
            DELETE FROM knowledge_nodes WHERE node_id = ?
        """, (node_id,))
        
        conn.commit()
        conn.close()
        
        return {
            "status": "success",
            "message": "知识点删除成功"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除知识点失败: {str(e)}")

@router.get("/prerequisites/{node_id}")
async def get_knowledge_prerequisites(node_id: str):
    """获取知识点的前置条件"""
    try:
        conn = get_db_connection()
        cursor = conn.execute("""
            SELECT 
                kn.node_id,
                kn.node_name,
                kn.node_difficulty,
                kn.level,
                kn.node_learning
            FROM knowledge_nodes kn
            JOIN knowledge_edges ke ON kn.node_id = ke.source_node_id
            WHERE ke.target_node_id = ? AND ke.relation_type = '指向'
            ORDER BY kn.level, kn.node_name
        """, (node_id,))
        
        prerequisites = []
        for row in cursor.fetchall():
            prerequisites.append({
                "node_id": row["node_id"],
                "node_name": row["node_name"],
                "node_difficulty": row["node_difficulty"],
                "level": row["level"],
                "node_learning": row["node_learning"]
            })
        
        conn.close()
        return {"prerequisites": prerequisites}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取前置知识点失败: {str(e)}")

@router.get("/detail/{node_id}")
async def get_knowledge_detail(node_id: str):
    """获取知识点详细信息"""
    try:
        conn = get_db_connection()
        
        # 获取知识点基本信息
        cursor = conn.execute("""
            SELECT node_id, node_name, node_difficulty, level, node_learning
            FROM knowledge_nodes WHERE node_id = ?
        """, (node_id,))
        node_info = cursor.fetchone()
        
        if not node_info:
            raise HTTPException(status_code=404, detail="知识点不存在")
        
        # 获取前置知识点
        cursor = conn.execute("""
            SELECT kn.node_id, kn.node_name
            FROM knowledge_nodes kn
            JOIN knowledge_edges ke ON kn.node_id = ke.source_node_id
            WHERE ke.target_node_id = ? AND ke.relation_type = '指向'
        """, (node_id,))
        prerequisites = [dict(row) for row in cursor.fetchall()]
        
        # 获取后续知识点
        cursor = conn.execute("""
            SELECT kn.node_id, kn.node_name
            FROM knowledge_nodes kn
            JOIN knowledge_edges ke ON kn.node_id = ke.target_node_id
            WHERE ke.source_node_id = ? AND ke.relation_type = '指向'
        """, (node_id,))
        next_nodes = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        
        return {
            "node_info": {
                "node_id": node_info["node_id"],
                "node_name": node_info["node_name"],
                "node_difficulty": node_info["node_difficulty"],
                "level": node_info["level"],
                "node_learning": node_info["node_learning"]
            },
            "prerequisites": prerequisites,
            "next_nodes": next_nodes
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取知识点详情失败: {str(e)}")

@router.get("/edges")
async def get_knowledge_edges():
    """获取所有知识点关系"""
    try:
        conn = get_db_connection()
        cursor = conn.execute("""
            SELECT 
                ke.edge_id,
                ke.source_node_id,
                ke.target_node_id,
                ke.relation_type,
                ke.status,
                sn.node_name as source_name,
                tn.node_name as target_name
            FROM knowledge_edges ke
            JOIN knowledge_nodes sn ON ke.source_node_id = sn.node_id
            JOIN knowledge_nodes tn ON ke.target_node_id = tn.node_id
            ORDER BY ke.edge_id
        """)
        
        edges = []
        for row in cursor.fetchall():
            edges.append({
                "id": row["edge_id"],
                "source_node_id": row["source_node_id"],
                "target_node_id": row["target_node_id"],
                "relation_type": row["relation_type"],
                "status": row["status"],
                "source_name": row["source_name"],
                "target_name": row["target_name"]
            })
        
        conn.close()
        return {"edges": edges}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取知识点关系失败: {str(e)}")

@router.post("/edges")
async def create_knowledge_edge(request: CreateKnowledgeEdgeRequest):
    """创建知识点关系"""
    try:
        conn = get_db_connection()
        
        # 检查源节点和目标节点是否存在
        cursor = conn.execute("""
            SELECT node_id FROM knowledge_nodes WHERE node_id = ?
        """, (request.source_node_id,))
        if not cursor.fetchone():
            conn.close()
            raise HTTPException(status_code=400, detail="源知识点不存在")
        
        cursor = conn.execute("""
            SELECT node_id FROM knowledge_nodes WHERE node_id = ?
        """, (request.target_node_id,))
        if not cursor.fetchone():
            conn.close()
            raise HTTPException(status_code=400, detail="目标知识点不存在")
        
        # 检查关系是否已存在
        cursor = conn.execute("""
            SELECT edge_id FROM knowledge_edges 
            WHERE source_node_id = ? AND target_node_id = ? AND relation_type = ?
        """, (request.source_node_id, request.target_node_id, request.relation_type))
        if cursor.fetchone():
            conn.close()
            raise HTTPException(status_code=400, detail="该知识点关系已存在")
        
        # 创建关系
        cursor = conn.execute("""
            INSERT INTO knowledge_edges (source_node_id, target_node_id, relation_type, created_by)
            VALUES (?, ?, ?, 3)
        """, (request.source_node_id, request.target_node_id, request.relation_type))
        
        edge_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return {
            "status": "success",
            "edge_id": edge_id,
            "message": "知识点关系创建成功"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建知识点关系失败: {str(e)}")

@router.delete("/edges")
async def delete_knowledge_edge(request: DeleteKnowledgeEdgeRequest):
    """删除知识点关系"""
    try:
        conn = get_db_connection()
        
        # 删除关系
        cursor = conn.execute("""
            DELETE FROM knowledge_edges 
            WHERE source_node_id = ? AND target_node_id = ? AND relation_type = ?
        """, (request.source_node_id, request.target_node_id, request.relation_type))
        
        if cursor.rowcount == 0:
            conn.close()
            raise HTTPException(status_code=404, detail="知识点关系不存在")
        
        conn.commit()
        conn.close()
        
        return {
            "status": "success",
            "message": "知识点关系删除成功"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除知识点关系失败: {str(e)}")

@router.get("/graph-data")
async def get_knowledge_graph_data():
    """获取知识图谱数据"""
    try:
        conn = get_db_connection()
        
        # 获取所有节点
        cursor = conn.execute("""
            SELECT node_id, node_name, node_difficulty, level, node_type
            FROM knowledge_nodes
            ORDER BY level, node_name
        """)
        nodes = []
        for row in cursor.fetchall():
            nodes.append({
                "id": str(row["node_id"]),
                "name": row["node_name"],
                "difficulty": row["node_difficulty"],
                "level": row["level"],
                "node_type": row["node_type"]
            })
        
        # 获取所有边
        cursor = conn.execute("""
            SELECT source_node_id, target_node_id, relation_type
            FROM knowledge_edges
            WHERE status = 'published'
        """)
        edges = []
        for row in cursor.fetchall():
            edges.append({
                "source": str(row["source_node_id"]),
                "target": str(row["target_node_id"]),
                "relation": row["relation_type"]
            })
        
        conn.close()
        return {
            "nodes": nodes,
            "edges": edges
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取知识图谱数据失败: {str(e)}")

@router.post("/generate-learning-objective")
async def generate_learning_objective(request: dict):
    """AI生成学习目标（模拟接口）"""
    try:
        url = "https://xingchen-api.xf-yun.com/workflow/v1/chat/completions"

        payload = json.dumps({
        "flow_id": "7355086692730109954",
        "parameters": {
            "AGENT_USER_INPUT": request['node_name']
        },
        "ext": {
            "bot_id": "workflow",
            "caller": "workflow"
        },
        "stream": False,
        })
        headers = {
        'Authorization': 'Bearer 4cec7267c3353726a2f1656cb7c0ec37:NDk0MDk0N2JiYzg0ZTgxMzVlNmRkM2Fh',
        'Content-Type': 'application/json',
        'Accept': '*/*',
        'Host': 'xingchen-api.xf-yun.com',
        'Connection': 'keep-alive'
        }

        response = requests.request("POST", url, headers=headers, data=payload).json()
        # 检查响应是否成功
        if 'choices' not in response or not response['choices'] or 'delta' not in response['choices'][0]:
            raise HTTPException(status_code=500, detail="AI生成学习目标失败：响应格式错误")
            
        content = response['choices'][0]['delta'].get('content')
        if not content:
            raise HTTPException(status_code=500, detail="AI生成学习目标失败：未生成内容")
            
        # print(content)
        return {
            "status": "success",
            "learning_objective": content
        }

      
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"生成学习目标失败: {str(e)}")