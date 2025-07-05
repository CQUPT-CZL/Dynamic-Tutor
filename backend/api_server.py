#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI智慧学习平台 - 后端API服务器
使用FastAPI框架，提供RESTful API接口
"""

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Dict, List, Any, Optional
import sqlite3
import json
import time
from datetime import datetime
import uvicorn

# 创建FastAPI应用
app = FastAPI(
    title="AI智慧学习平台API",
    description="提供个性化学习推荐和智能诊断服务",
    version="1.0.0"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501"],  # Streamlit默认端口
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 数据模型
class DiagnosisRequest(BaseModel):
    user_id: str
    question_id: str
    answer: str
    answer_type: str = "text"
    time_spent: Optional[int] = None
    confidence: Optional[float] = None

class DiagnosisResponse(BaseModel):
    status: str
    diagnosis: str
    hint: Optional[str] = None
    correct_answer: str
    next_recommendation: Optional[str] = None

# 数据库连接
def get_db_connection():
    """获取数据库连接"""
    conn = sqlite3.connect('../data/my_database.db')
    print(conn)
    conn.row_factory = sqlite3.Row
    return conn

# 系统相关接口
@app.get("/")
async def root():
    """API根路径"""
    return {
        "message": "🎓 AI智慧学习平台API",
        "version": "1.0.0",
        "docs": "/docs",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    """健康检查"""
    try:
        conn = get_db_connection()
        conn.execute("SELECT 1")
        conn.close()
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "database": "connected"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "timestamp": datetime.now().isoformat(),
            "database": "disconnected",
            "error": str(e)
        }

# 用户管理接口
@app.get("/users")
async def get_users():
    """获取用户列表"""
    try:
        conn = get_db_connection()
        cursor = conn.execute("SELECT user_id, username FROM users")
        users = [{"user_id": row["user_id"], "username": row["username"]} for row in cursor.fetchall()]
        conn.close()
        return users
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取用户列表失败: {str(e)}")

# 学习推荐接口
@app.get("/recommendation/{user_id}")
async def get_recommendation(user_id: str):
    """获取用户学习推荐"""
    try:
        # 这里应该实现推荐算法，暂时返回模拟数据
        recommendation = {
            "mission_id": f"mission_{int(time.time())}",
            "type": "知识点练习",
            "reason": f"根据{user_id}的学习情况，建议加强二次函数的练习",
            "content": {
                "knowledge_point": "二次函数",
                "difficulty": "中等",
                "question_count": 5,
                "question_id": "q_001",
                "question_text": "求函数 f(x) = x² + 2x - 3 的最小值"
            }
        }
        return recommendation
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取推荐失败: {str(e)}")

# 答案诊断接口
@app.post("/diagnose")
async def diagnose_answer(request: DiagnosisRequest):
    """诊断文本答案"""
    try:
        # 这里应该实现AI诊断逻辑，暂时返回模拟结果
        # 简单判断：如果答案包含关键词，认为正确
        is_correct = "最小值" in request.answer or "x=-1" in request.answer
        
        diagnosis_result = {
            "status": "success",
            "diagnosis": "答案正确！解题思路清晰" if is_correct else "答案有误，请重新思考",
            "hint": "使用配方法：f(x) = (x+1)² - 4" if not is_correct else None,
            "correct_answer": "最小值为-4，当x=-1时取得",
            "next_recommendation": "可以尝试更复杂的二次函数问题" if is_correct else "建议复习二次函数的基本性质"
        }
        
        # 保存答题记录到数据库
        conn = get_db_connection()
        
        # 插入答题记录
        conn.execute("""
            INSERT INTO user_answers 
            (user_id, question_id, user_answer, is_correct, time_spent, confidence, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (request.user_id, request.question_id, request.answer, is_correct,
              request.time_spent or 0, request.confidence or 0.5, datetime.now().isoformat()))
        
        # 如果答错了，更新错题记录
        if not is_correct:
            # 检查是否已有错题记录
            cursor = conn.execute("""
                SELECT wrong_id, wrong_count FROM wrong_questions 
                WHERE user_id = ? AND question_id = ?
            """, (request.user_id, request.question_id))
            
            existing = cursor.fetchone()
            if existing:
                # 更新错题记录
                conn.execute("""
                    UPDATE wrong_questions 
                    SET wrong_count = wrong_count + 1, last_wrong_time = ?
                    WHERE wrong_id = ?
                """, (datetime.now().isoformat(), existing["wrong_id"]))
            else:
                # 创建新的错题记录
                conn.execute("""
                    INSERT INTO wrong_questions 
                    (user_id, question_id, wrong_count, first_wrong_time, last_wrong_time, status)
                    VALUES (?, ?, 1, ?, ?, '未掌握')
                """, (request.user_id, request.question_id, datetime.now().isoformat(), datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
        
        return diagnosis_result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"诊断失败: {str(e)}")

@app.post("/diagnose/image")
async def diagnose_image_answer(
    user_id: str,
    question_id: str,
    image: UploadFile = File(...),
    time_spent: Optional[int] = None,
    confidence: Optional[float] = None
):
    """诊断图片答案"""
    try:
        # 这里应该实现图片识别和诊断逻辑
        diagnosis_result = {
            "status": "success",
            "diagnosis": "图片答案识别成功，解题过程正确",
            "hint": None,
            "correct_answer": "最小值为-4，当x=-1时取得",
            "next_recommendation": "可以尝试更复杂的二次函数问题"
        }
        return diagnosis_result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"图片诊断失败: {str(e)}")

# 知识图谱接口
@app.get("/knowledge-map/{user_id}")
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
        """, (user_id,))
        
        knowledge_map = []
        for row in cursor.fetchall():
            knowledge_map.append({
                "node_id": row["node_id"],
                "node_name": row["node_name"],
                "difficulty": row["node_difficulty"],
                "level": row["level"],
                "mastery": row["mastery_score"]
            })
        
        conn.close()
        return knowledge_map
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取知识图谱失败: {str(e)}")

@app.get("/knowledge-nodes")
async def get_knowledge_nodes():
    """获取所有知识节点"""
    try:
        conn = get_db_connection()
        cursor = conn.execute("SELECT node_id, node_name, node_difficulty FROM knowledge_nodes")
        
        nodes = {}
        for row in cursor.fetchall():
            nodes[row["node_id"]] = row["node_name"]
        
        conn.close()
        return {"nodes": nodes}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取知识节点失败: {str(e)}")

@app.get("/mastery/{user_id}/{node_name}")
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

@app.post("/mastery/{user_id}/{node_name}")
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

# 练习题目接口
@app.get("/questions/{node_name}")
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

# 错题集接口
@app.get("/wrong-questions/{user_id}")
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
                wq.first_wrong_time,
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
                "question_id": str(row["question_id"]),
                "question_text": row["question_text"],
                "wrong_count": row["wrong_count"],
                "first_wrong_time": row["first_wrong_time"],
                "last_wrong_time": row["last_wrong_time"],
                "knowledge_points": row["knowledge_points"] or "未知",
                "difficulty": "简单" if row["difficulty"] < 0.4 else "中等" if row["difficulty"] < 0.7 else "困难",
                "status": row["status"]
            })
        
        conn.close()
        return {"wrong_questions": wrong_questions}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取错题集失败: {str(e)}")

# 用户统计接口
@app.get("/stats/{user_id}")
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

# 错误处理
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "error": "服务器内部错误",
            "detail": str(exc)
        }
    )

if __name__ == "__main__":
    print("🚀 启动AI智慧学习平台API服务器...")
    print("📖 API文档地址: http://localhost:8000/docs")
    print("🔗 前端地址: http://localhost:8501")
    
    uvicorn.run(
        "api_server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 