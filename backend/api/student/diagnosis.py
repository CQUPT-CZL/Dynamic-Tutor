#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
答案诊断接口
"""

from fastapi import APIRouter, HTTPException, UploadFile, File
from typing import Optional
from datetime import datetime
from pydantic import BaseModel
import json
import requests
from ..common.database import get_db_connection


class DiagnosisRequest(BaseModel):
    """答案诊断请求模型"""
    user_id: str
    question_id: str
    answer: str
    time_spent: Optional[int] = None
    confidence: Optional[float] = None

router = APIRouter(prefix="/diagnose", tags=["答案诊断"])

@router.post("/")
async def diagnose_answer(request: DiagnosisRequest):
    """诊断文本答案"""
    try:
        # 根据题目ID从数据库获取题目信息
        print(f"📊 开始查询题目信息，题目ID: {request.question_id}")
        conn = get_db_connection()
        print("✅ 数据库连接成功")
        
        # 获取题目详细信息
        cursor = conn.execute("""
            SELECT q.question_text, q.question_type, q.answer, q.analysis, q.difficulty,
                   GROUP_CONCAT(kn.node_name) as knowledge_points
            FROM questions q
            LEFT JOIN question_to_node_mapping qm ON q.question_id = qm.question_id
            LEFT JOIN knowledge_nodes kn ON qm.node_id = kn.node_id
            WHERE q.question_id = ?
            GROUP BY q.question_id
        """, (request.question_id,))
        
        question_info = cursor.fetchone()
        
        if not question_info:
            print(f"❌ 题目ID {request.question_id} 不存在")
            conn.close()
            raise HTTPException(status_code=404, detail=f"题目ID {request.question_id} 不存在")
        
        print(f"✅ 成功获取题目信息: {question_info['question_text'][:50]}...")
        
        question_text = question_info["question_text"]
        correct_answer = question_info["answer"]
        analysis = question_info["analysis"]
        difficulty = question_info["difficulty"]


        # 基于题目内容进行智能诊断
        diagnosis_result = _diagnose_answer_logic(request.answer, correct_answer, question_text)
        is_correct = diagnosis_result['is_correct']
        # 生成诊断结果
        # diagnosis_result = {
        #     "status": "success",
        #     "diagnosis": "答案正确！解题思路清晰" if is_correct else "答案有误，请重新思考",
        #     "hint": "使用配方法：f(x) = (x+1)² - 4" if not is_correct else None,
        #     "correct_answer": "最小值为-4，当x=-1时取得",
        #     "next_recommendation": "可以尝试更复杂的二次函数问题" if is_correct else "建议复习二次函数的基本性质"
        # }
        
        # 保存答题记录到数据库
        print(f"💾 开始保存答题记录 - 用户ID: {request.user_id}, 题目ID: {request.question_id}, 答案正确性: {is_correct}")
        
        # 插入答题记录
        print('📝 后端诊断结果:', diagnosis_result)
        conn.execute("""
            INSERT INTO user_answers 
            (user_id, question_id, user_answer, is_correct, time_spent, confidence, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (request.user_id, request.question_id, request.answer, is_correct,
              request.time_spent or 0, request.confidence or 0.5, datetime.now().isoformat()))
        conn.commit()
        print('✅ 答题记录插入成功')
        # 如果答错了，更新错题记录
        if not is_correct:
            print(f"❌ 答案错误，开始处理错题记录")
            # 检查是否已有错题记录
            cursor = conn.execute("""
                SELECT wrong_id, wrong_count FROM wrong_questions 
                WHERE user_id = ? AND question_id = ?
            """, (request.user_id, request.question_id))
            
            existing = cursor.fetchone()
            if existing:
                # 更新错题记录
                print(f'🔄 更新已存在的错题记录，错题ID: {existing["wrong_id"]}, 当前错误次数: {existing["wrong_count"]}')
                conn.execute("""
                    UPDATE wrong_questions 
                    SET wrong_count = wrong_count + 1, last_wrong_time = ?
                    WHERE wrong_id = ?
                """, (datetime.now().isoformat(), existing["wrong_id"]))
                conn.commit()  # 提交事务
                print(f'✅ 错题记录更新成功，错误次数增加到: {existing["wrong_count"] + 1}')
            else:
                # 创建新的错题记录
                print('📝 创建新的错题记录')
                try:
                    conn.execute("""
                        INSERT INTO wrong_questions 
                        (user_id, question_id, wrong_count, last_wrong_time, status)
                        VALUES (?, ?, ?, ?, '未掌握')
                    """, (request.user_id, request.question_id, 1, datetime.now().isoformat()))
                    conn.commit() 
                    print('✅ 新错题记录创建成功')
                except Exception as e:
                    print(f"❌ 插入错题记录失败: {str(e)}")
                    raise HTTPException(status_code=500, detail=f"插入错题记录失败: {str(e)}")
        else:
            print(f"✅ 答案正确，无需记录错题")
        conn.close()
        print('🔒 数据库连接已关闭')
        print('🎯 最终诊断结果:', diagnosis_result)
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
        # 根据题目ID从数据库获取题目信息
        print(f"📊 [图片诊断] 开始查询题目信息，题目ID: {question_id}")
        conn = get_db_connection()
        print("✅ [图片诊断] 数据库连接成功")
        
        # 获取题目详细信息
        cursor = conn.execute("""
            SELECT q.question_text, q.question_type, q.answer, q.analysis, q.difficulty,
                   GROUP_CONCAT(kn.node_name) as knowledge_points
            FROM questions q
            LEFT JOIN question_to_node_mapping qm ON q.question_id = qm.question_id
            LEFT JOIN knowledge_nodes kn ON qm.node_id = kn.node_id
            WHERE q.question_id = ?
            GROUP BY q.question_id
        """, (question_id,))
        
        question_info = cursor.fetchone()
        
        if not question_info:
            print(f"❌ [图片诊断] 题目ID {question_id} 不存在")
            conn.close()
            raise HTTPException(status_code=404, detail=f"题目ID {question_id} 不存在")
        
        print(f"✅ [图片诊断] 成功获取题目信息: {question_info['question_text'][:50]}...")
        
        question_text = question_info["question_text"]
        question_type = question_info["question_type"]
        correct_answer = question_info["answer"]
        analysis = question_info["analysis"]
        difficulty = question_info["difficulty"]
        knowledge_points = question_info["knowledge_points"] or ""
        
        # 保存上传的图片
        import os
        from datetime import datetime
        
        print(f"📁 [图片诊断] 开始保存上传的图片文件")
        upload_dir = "../backend/uploads"
        os.makedirs(upload_dir, exist_ok=True)
        print(f"✅ [图片诊断] 上传目录准备完成: {upload_dir}")
        
        # 生成唯一文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_extension = os.path.splitext(image.filename)[1] if image.filename else ".jpg"
        filename = f"answer_{user_id}_{question_id}_{timestamp}{file_extension}"
        file_path = os.path.join(upload_dir, filename)
        print(f"📝 [图片诊断] 生成文件名: {filename}")
        
        # 保存文件
        with open(file_path, "wb") as buffer:
            content = await image.read()
            buffer.write(content)
        print(f"✅ [图片诊断] 图片文件保存成功: {file_path}")
        
        # 使用假的图片转文字函数
        print(f"🔍 [图片诊断] 开始OCR识别")
        recognized_text = _fake_image_to_text(file_path)
        print(f"✅ [图片诊断] OCR识别完成: {recognized_text}")
        
        # 使用相同的诊断逻辑
        diagnosis_result = _diagnose_answer_logic(recognized_text, correct_answer, question_type, question_text)
        
        # diagnosis_result = {
        #     "status": "success",
        #     "diagnosis": "图片答案识别成功，解题过程正确",
        #     "hint": None,
        #     "correct_answer": "最小值为-4，当x=-1时取得",
        #     "next_recommendation": "可以尝试更复杂的二次函数问题"
        # }
        return diagnosis_result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"图片诊断失败: {str(e)}")


def _diagnose_answer_logic(user_answer: str, correct_answer: str, question_text: str):
    """
    简化的答案诊断逻辑
    
    Args:
        user_answer: 用户答案
        correct_answer: 正确答案
        question_type: 题目类型
        question_text: 题目文本
    
    Returns:
        dict: 诊断结果
    """
    try:
        print(f"🤖 开始调用AI诊断API")
        print(f"📝 输入参数 - 题目: {question_text[:50]}..., 用户答案: {user_answer[:50]}...")
        
        url = "https://xingchen-api.xf-yun.com/workflow/v1/chat/completions"
        
        input_text = question_text + "##" + user_answer + "##" + str(60)
        payload = json.dumps({
        "flow_id": "7347650620700119042",
        "parameters": {
            "AGENT_USER_INPUT": input_text,
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
        
        print(f"🌐 发送API请求到: {url}")
        response = requests.request("POST", url, headers=headers, data=payload).json()
        print(f"📨 AI API响应: {response}")
        # 检查响应是否成功
        if 'choices' not in response or not response['choices'] or 'delta' not in response['choices'][0]:
            print("❌ AI API响应格式错误")
            raise HTTPException(status_code=500, detail="AI生成学习目标失败：响应格式错误")
            
        content = response['choices'][0]['delta'].get('content')
        if not content:
            print("❌ AI API返回内容为空")
            raise HTTPException(status_code=500, detail="AI诊断失败")
            
        print(f"✅ AI诊断内容: {content}")
        
        # 解析AI响应
        parts = content.split("##")
        if len(parts) < 3:
            print(f"❌ AI响应格式不正确，无法解析: {content}")
            raise HTTPException(status_code=500, detail="AI响应格式错误")
            
        is_correct = parts[0].strip().lower() == 'yes'
        reason = parts[1].strip()

        # 检查是否有评分部分
        if len(parts) >= 3 and parts[2].strip():
            try:
                # 尝试解析JSON评分数组
                scores_json = parts[2].strip()
                scores = json.loads(scores_json)
                print(f"📊 解析评分数据: {scores}")
            except json.JSONDecodeError as e:
                print(f"⚠️ 评分数据解析失败: {e}")
                # 评分解析失败不影响主要结果
                pass
        
        result = {
            "is_correct": is_correct,
            "reason": reason,
            "scores": scores
        }
        
        # result = {
        #     "is_correct": is_correct,
        #     "reason": reason
        # }
        
        print(f"🎯 解析后的诊断结果: 正确性={is_correct}, 原因={reason}, 其他维度：{scores}")
        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"诊断失败: {str(e)}")

def _fake_image_to_text(image_path: str):
    """
    假的图片转文字函数
    
    Args:
        image_path: 图片文件路径
    
    Returns:
        str: 模拟识别的文字内容
    """
    # 模拟OCR识别结果
    return "最小值为-4，当x=-1时取得"