#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
答案诊断接口
"""

from fastapi import APIRouter, HTTPException, UploadFile, File
from typing import Optional
from datetime import datetime
from ..common.models import DiagnosisRequest
from ..common.database import get_db_connection

router = APIRouter(prefix="/diagnose", tags=["答案诊断"])

@router.post("/")
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

@router.post("/image")
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