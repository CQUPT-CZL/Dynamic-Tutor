#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
题目管理接口
"""

import json
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from ..common.database import get_db_connection
from datetime import datetime
from typing import Optional, List, Dict, Any

class CreateQuestionRequest(BaseModel):
    question_text: str
    question_type: str  # '选择题', '填空题', '解答题'
    difficulty: float  # 0.0 - 1.0
    options: Optional[str] = None  # JSON格式的选项，仅选择题使用
    answer: str
    analysis: str
    status: str = 'published'  # 'draft' 或 'published'
    created_by: int
    question_image_url: Optional[str] = None  # 题目图片URL

class UpdateQuestionRequest(BaseModel):
    question_id: int
    question_text: Optional[str] = None
    question_type: Optional[str] = None
    difficulty: Optional[float] = None
    options: Optional[str] = None
    answer: Optional[str] = None
    analysis: Optional[str] = None
    status: Optional[str] = None
    question_image_url: Optional[str] = None  # 题目图片URL

class QuestionNodeMappingRequest(BaseModel):
    question_id: int
    node_id: str

router = APIRouter(prefix="/question", tags=["题目管理"])

@router.post("/create")
async def create_question(request: CreateQuestionRequest):
    """创建题目"""
    print(f"[DEBUG] 创建题目接口收到数据: {request.dict()}")
    try:
        conn = get_db_connection()
        
        # 验证难度值范围
        if request.difficulty < 0.0 or request.difficulty > 1.0:
            raise HTTPException(status_code=400, detail="题目难度必须在0.0-1.0之间")
        
        # 验证题目类型
        valid_types = ['选择题', '填空题', '解答题']
        if request.question_type not in valid_types:
            raise HTTPException(status_code=400, detail=f"题目类型必须是: {', '.join(valid_types)}")
        
        # 验证状态
        valid_statuses = ['draft', 'published']
        if request.status not in valid_statuses:
            raise HTTPException(status_code=400, detail=f"状态必须是: {', '.join(valid_statuses)}")
        
        # 如果是选择题，验证options字段
        if request.question_type == '选择题' and not request.options:
            raise HTTPException(status_code=400, detail="选择题必须提供选项")
        
        # 如果提供了options，验证JSON格式
        if request.options:
            try:
                json.loads(request.options)
            except json.JSONDecodeError:
                raise HTTPException(status_code=400, detail="选项必须是有效的JSON格式")
        
        # 创建题目
        cursor = conn.execute("""
            INSERT INTO questions 
            (question_text, question_type, difficulty, options, answer, analysis, status, created_by, question_image_url)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (request.question_text, request.question_type, request.difficulty, 
               request.options, request.answer, request.analysis, request.status, request.created_by, request.question_image_url))
        
        question_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return {
            "status": "success",
            "question_id": question_id,
            "message": "题目创建成功"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建题目失败: {str(e)}")

@router.get("/list")
async def get_questions(
    page: int = 1,
    page_size: int = 100,
    question_type: Optional[str] = None,
    status: Optional[str] = None,
    created_by: Optional[int] = None,
    search: Optional[str] = None,
    min_difficulty: Optional[float] = None,
    max_difficulty: Optional[float] = None
):
    """获取题目列表"""
    print(f"[DEBUG] 获取题目列表接口收到参数: page={page}, page_size={page_size}, question_type={question_type}, status={status}, created_by={created_by}, search={search}, min_difficulty={min_difficulty}, max_difficulty={max_difficulty}")
    try:
        # 验证分页参数
        if page < 1:
            raise HTTPException(status_code=400, detail="页码必须大于0")
        if page_size < 1 or page_size > 1000:
            raise HTTPException(status_code=400, detail="每页数量必须在1-1000之间")
        
        conn = get_db_connection()
        
        # 构建查询条件
        conditions = []
        params = []
        
        if question_type:
            conditions.append("q.question_type = ?")
            params.append(question_type)
        
        if status:
            conditions.append("q.status = ?")
            params.append(status)
        
        if created_by:
            conditions.append("q.created_by = ?")
            params.append(created_by)
        
        if search:
            conditions.append("q.question_text LIKE ?")
            params.append(f"%{search}%")
        
        if min_difficulty is not None:
            conditions.append("q.difficulty >= ?")
            params.append(min_difficulty)
        
        if max_difficulty is not None:
            conditions.append("q.difficulty <= ?")
            params.append(max_difficulty)
        
        where_clause = " WHERE " + " AND ".join(conditions) if conditions else ""
        
        # 获取总数
        count_query = f"""
            SELECT COUNT(*) as total
            FROM questions q
            LEFT JOIN users u ON q.created_by = u.user_id
            {where_clause}
        """
        
        cursor = conn.execute(count_query, params)
        total = cursor.fetchone()["total"]
        
        # 计算分页
        offset = (page - 1) * page_size
        total_pages = (total + page_size - 1) // page_size
        
        # 获取分页数据
        query = f"""
            SELECT 
                q.question_id,
                q.question_text,
                q.question_image_url,
                q.question_type,
                q.difficulty,
                q.options,
                q.answer,
                q.analysis,
                q.status,
                q.created_by,
                u.username as creator_name
            FROM questions q
            LEFT JOIN users u ON q.created_by = u.user_id
            {where_clause}
            ORDER BY q.question_id DESC
            LIMIT ? OFFSET ?
        """
        
        params.extend([page_size, offset])
        cursor = conn.execute(query, params)
        
        questions = []
        for row in cursor.fetchall():
            question_data = {
                "question_id": row["question_id"],
                "question_text": row["question_text"],
                "question_image_url": row["question_image_url"],
                "question_type": row["question_type"],
                "difficulty": row["difficulty"],
                "options": json.loads(row["options"]) if row["options"] else None,
                "answer": row["answer"],
                "analysis": row["analysis"],
                "status": row["status"],
                "created_by": row["created_by"],
                "creator_name": row["creator_name"]
            }
            questions.append(question_data)
        
        conn.close()
        return {
            "questions": questions,
            "pagination": {
                "page": page,
                "page_size": page_size,
                "total": total,
                "total_pages": total_pages,
                "has_next": page < total_pages,
                "has_prev": page > 1
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取题目列表失败: {str(e)}")

@router.get("/detail/{question_id}")
async def get_question_detail(question_id: int):
    """获取题目详情"""
    print(f"[DEBUG] 获取题目详情接口收到参数: question_id={question_id}")
    try:
        conn = get_db_connection()
        cursor = conn.execute("""
            SELECT 
                q.question_id,
                q.question_text,
                q.question_image_url,
                q.question_type,
                q.difficulty,
                q.options,
                q.answer,
                q.analysis,
                q.status,
                q.created_by,
                u.username as creator_name
            FROM questions q
            LEFT JOIN users u ON q.created_by = u.user_id
            WHERE q.question_id = ?
        """, (question_id,))
        
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="题目不存在")
        
        question_data = {
            "question_id": row["question_id"],
            "question_text": row["question_text"],
            "question_image_url": row["question_image_url"],
            "question_type": row["question_type"],
            "difficulty": row["difficulty"],
            "options": json.loads(row["options"]) if row["options"] else None,
            "answer": row["answer"],
            "analysis": row["analysis"],
            "status": row["status"],
            "created_by": row["created_by"],
            "creator_name": row["creator_name"]
        }
        
        conn.close()
        return question_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取题目详情失败: {str(e)}")

@router.put("/update/{question_id}")
async def update_question(request: UpdateQuestionRequest):
    """更新题目信息"""
    print(f"[DEBUG] 更新题目接口收到数据: {request.dict()}")
    try:
        question_id = request.question_id
        conn = get_db_connection()
        
        # 验证题目是否存在
        cursor = conn.execute("SELECT question_id FROM questions WHERE question_id = ?", (question_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="题目不存在")
        
        update_fields = []
        params = []
        
        if request.question_text:
            update_fields.append("question_text = ?")
            params.append(request.question_text)
        
        if request.question_type:
            valid_types = ['选择题', '填空题', '解答题']
            if request.question_type not in valid_types:
                raise HTTPException(status_code=400, detail=f"题目类型必须是: {', '.join(valid_types)}")
            update_fields.append("question_type = ?")
            params.append(request.question_type)
        
        if request.difficulty is not None:
            if request.difficulty < 0.0 or request.difficulty > 1.0:
                raise HTTPException(status_code=400, detail="题目难度必须在0.0-1.0之间")
            update_fields.append("difficulty = ?")
            params.append(request.difficulty)
        
        if request.options is not None:
            if request.options:
                try:
                    json.loads(request.options)
                except json.JSONDecodeError:
                    raise HTTPException(status_code=400, detail="选项必须是有效的JSON格式")
            update_fields.append("options = ?")
            params.append(request.options)
        
        if request.answer:
            update_fields.append("answer = ?")
            params.append(request.answer)
        
        if request.analysis:
            update_fields.append("analysis = ?")
            params.append(request.analysis)
        
        if request.status:
            valid_statuses = ['draft', 'published']
            if request.status not in valid_statuses:
                raise HTTPException(status_code=400, detail=f"状态必须是: {', '.join(valid_statuses)}")
            update_fields.append("status = ?")
            params.append(request.status)
        
        if request.question_image_url is not None:
            update_fields.append("question_image_url = ?")
            params.append(request.question_image_url)
        
        if update_fields:
            params.append(question_id)
            query = f"UPDATE questions SET {', '.join(update_fields)} WHERE question_id = ?"
            conn.execute(query, params)
            conn.commit()
        
        conn.close()
        
        return {
            "status": "success",
            "message": "题目更新成功"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新题目失败: {str(e)}")

@router.delete("/delete/{question_id}")
async def delete_question(question_id: int):
    """删除题目"""
    print(f"[DEBUG] 删除题目接口收到参数: question_id={question_id}")
    try:
        conn = get_db_connection()
        
        # 检查题目是否存在
        cursor = conn.execute("SELECT question_id FROM questions WHERE question_id = ?", (question_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="题目不存在")
        
        # 检查是否有学生答题记录
        cursor = conn.execute("SELECT COUNT(*) as count FROM user_answers WHERE question_id = ?", (question_id,))
        answer_count = cursor.fetchone()["count"]
        
        if answer_count > 0:
            conn.close()
            raise HTTPException(status_code=400, detail="该题目已有学生答题记录，无法删除")
        
        # 删除题目与知识点的关联
        conn.execute("DELETE FROM question_to_node_mapping WHERE question_id = ?", (question_id,))
        
        # 删除题目
        conn.execute("DELETE FROM questions WHERE question_id = ?", (question_id,))
        
        conn.commit()
        conn.close()
        
        return {
            "status": "success",
            "message": "题目删除成功"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除题目失败: {str(e)}")



@router.post("/node-mapping")
async def create_question_to_node_mapping(request: QuestionNodeMappingRequest):
    """创建题目与知识点的关联"""
    print(f"[DEBUG] 创建题目知识点关联接口收到数据: {request.dict()}")
    try:
        conn = get_db_connection()
        
        # 检查题目是否存在
        cursor = conn.execute("SELECT question_id FROM questions WHERE question_id = ?", (request.question_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="题目不存在")
        
        # 检查知识点是否存在
        cursor = conn.execute("SELECT node_id FROM knowledge_nodes WHERE node_id = ?", (request.node_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="知识点不存在")
        
        # 检查关联是否已存在
        cursor = conn.execute("""
            SELECT * FROM question_to_node_mapping 
            WHERE question_id = ? AND node_id = ?
        """, (request.question_id, request.node_id))
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="关联关系已存在")
        
        # 创建关联
        conn.execute("""
            INSERT INTO question_to_node_mapping (question_id, node_id)
            VALUES (?, ?)
        """, (request.question_id, request.node_id))
        
        conn.commit()
        conn.close()
        
        return {
            "status": "success",
            "message": "关联创建成功"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建关联失败: {str(e)}")

@router.get("/node-mappings")
async def get_question_to_node_mappings():
    """获取题目与知识点的关联关系"""
    print(f"[DEBUG] 获取题目知识点关联列表接口被调用")
    try:
        conn = get_db_connection()
        cursor = conn.execute("""
            SELECT 
                qnm.question_id,
                q.question_text,
                qnm.node_id,
                kn.node_name
            FROM question_to_node_mapping qnm
            JOIN questions q ON qnm.question_id = q.question_id
            JOIN knowledge_nodes kn ON qnm.node_id = kn.node_id
            ORDER BY qnm.question_id, qnm.node_id
        """)
        
        mappings = []
        for row in cursor.fetchall():
            mappings.append({
                "question_id": row["question_id"],
                "question_text": row["question_text"][:50] + "..." if len(row["question_text"]) > 50 else row["question_text"],
                "node_id": row["node_id"],
                "node_name": row["node_name"]
            })
        
        conn.close()
        return {"mappings": mappings}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取关联关系失败: {str(e)}")

@router.delete("/node-mapping/{question_id}/{node_id}")
async def delete_question_to_node_mapping(question_id: int, node_id: str):
    """删除题目与知识点的关联"""
    print(f"[DEBUG] 删除题目知识点关联接口收到参数: question_id={question_id}, node_id={node_id}")
    try:
        conn = get_db_connection()
        
        # 检查关联是否存在
        cursor = conn.execute("""
            SELECT * FROM question_to_node_mapping 
            WHERE question_id = ? AND node_id = ?
        """, (question_id, node_id))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="关联关系不存在")
        
        # 删除关联
        conn.execute("""
            DELETE FROM question_to_node_mapping 
            WHERE question_id = ? AND node_id = ?
        """, (question_id, node_id))
        
        conn.commit()
        conn.close()
        
        return {
            "status": "success",
            "message": "关联删除成功"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除关联失败: {str(e)}")

@router.get("/stats")
async def get_question_stats():
    """获取题目统计信息"""
    print(f"[DEBUG] 获取题目统计信息接口被调用")
    try:
        conn = get_db_connection()
        
        # 总题目数
        cursor = conn.execute("SELECT COUNT(*) as total FROM questions")
        total_questions = cursor.fetchone()["total"]
        
        # 已发布题目数
        cursor = conn.execute("SELECT COUNT(*) as published FROM questions WHERE status = 'published'")
        published_questions = cursor.fetchone()["published"]
        
        # 草稿题目数
        cursor = conn.execute("SELECT COUNT(*) as draft FROM questions WHERE status = 'draft'")
        draft_questions = cursor.fetchone()["draft"]
        
        # 题目类型分布
        cursor = conn.execute("""
            SELECT question_type, COUNT(*) as count 
            FROM questions 
            GROUP BY question_type
        """)
        type_distribution = {}
        for row in cursor.fetchall():
            type_distribution[row["question_type"]] = row["count"]
        
        # 平均难度
        cursor = conn.execute("SELECT AVG(difficulty) as avg_difficulty FROM questions")
        avg_difficulty = cursor.fetchone()["avg_difficulty"] or 0.0
        
        # 本周新增题目数
        from datetime import datetime, timedelta
        week_ago = (datetime.now() - timedelta(days=7)).isoformat()
        cursor = conn.execute("""
            SELECT COUNT(*) as recent 
            FROM questions 
            WHERE question_id > (SELECT COALESCE(MAX(question_id), 0) - 50 FROM questions)
        """)
        recent_added = cursor.fetchone()["recent"]
        
        conn.close()
        
        return {
            "total_questions": total_questions,
            "published_questions": published_questions,
            "draft_questions": draft_questions,
            "type_distribution": type_distribution,
            "avg_difficulty": round(avg_difficulty, 2),
            "recent_added": recent_added
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取统计信息失败: {str(e)}")