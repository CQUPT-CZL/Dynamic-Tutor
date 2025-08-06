#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
答案诊断接口
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Request
from fastapi.exceptions import RequestValidationError
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

class ImageDiagnosisRequest(BaseModel):
    """图片答案诊断请求模型"""
    user_id: str
    question_id: str
    time_spent: Optional[int] = None
    confidence: Optional[float] = None

router = APIRouter(prefix="/diagnose", tags=["答案诊断"])

@router.post("/")
async def diagnose_answer(request: DiagnosisRequest):
    """诊断文本答案"""
    try:
        # 根据题目ID从数据库获取题目信息
        conn = get_db_connection()
        
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
            conn.close()
            raise HTTPException(status_code=404, detail=f"题目ID {request.question_id} 不存在")
        

        
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
        # 插入答题记录
        try:
            conn.execute("""
                INSERT INTO user_answers 
                (user_id, question_id, user_answer, is_correct, time_spent, confidence, timestamp, diagnosis_json)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (request.user_id, request.question_id, request.answer, is_correct,
                  request.time_spent or 0, request.confidence or 0.5, datetime.now().isoformat(), json.dumps(diagnosis_result, ensure_ascii=False)))
            conn.commit()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"插入答题记录失败: {str(e)}")
        
        # 更新用户知识点掌握度
        try:
            # 获取题目关联的知识点和题目难度
            cursor = conn.execute("""
                SELECT qm.node_id, q.difficulty 
                FROM question_to_node_mapping qm
                JOIN questions q ON qm.question_id = q.question_id
                WHERE qm.question_id = ?
            """, (request.question_id,))
            
            knowledge_nodes = cursor.fetchall()
            
            for node in knowledge_nodes:
                node_id = node['node_id']
                difficulty = node['difficulty'] or 0.5  # 默认难度0.5
                
                # 根据题目难度计算掌握度变化幅度
                # 难题答对奖励更多，简单题答错惩罚更少
                if is_correct:
                    # 答对：难度越高，奖励越多 (0.05 - 0.15)
                    score_change = 0.05 + difficulty * 0.1
                else:
                    # 答错：难度越低，惩罚越多 (0.02 - 0.12)
                    score_change = -(0.02 + (1 - difficulty) * 0.1)
                
                # 检查是否已有掌握度记录
                cursor = conn.execute("""
                    SELECT mastery_score FROM user_node_mastery 
                    WHERE user_id = ? AND node_id = ?
                """, (request.user_id, node_id))
                
                existing = cursor.fetchone()
                
                if existing:
                    # 更新现有记录，确保掌握度在0-1之间
                    new_score = max(0.0, min(1.0, existing['mastery_score'] + score_change))
                    conn.execute("""
                        UPDATE user_node_mastery 
                        SET mastery_score = ?, updated_at = CURRENT_TIMESTAMP
                        WHERE user_id = ? AND node_id = ?
                    """, (new_score, request.user_id, node_id))

                else:
                    # 创建新记录，初始掌握度0.5，然后应用变化
                    initial_score = max(0.0, min(1.0, 0.5 + score_change))
                    conn.execute("""
                        INSERT INTO user_node_mastery (user_id, node_id, mastery_score, updated_at)
                        VALUES (?, ?, ?, CURRENT_TIMESTAMP)
                    """, (request.user_id, node_id, initial_score))

            
            conn.commit()
            
        except Exception as e:
            # 掌握度更新失败不影响主要流程，只记录错误
            pass
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
                conn.commit()  # 提交事务
            else:
                # 创建新的错题记录
                try:
                    conn.execute("""
                        INSERT INTO wrong_questions 
                        (user_id, question_id, wrong_count, last_wrong_time, status)
                        VALUES (?, ?, ?, ?, '未掌握')
                    """, (request.user_id, request.question_id, 1, datetime.now().isoformat()))
                    conn.commit()
                except Exception as e:
                    raise HTTPException(status_code=500, detail=f"插入错题记录失败: {str(e)}")
        
        conn.close()
        return diagnosis_result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"诊断失败: {str(e)}")

@router.post("/image")
async def diagnose_image_answer(request: Request):
    """诊断图片答案"""
    
    try:
        form_data = await request.form()
        
        user_id = form_data.get('user_id')
        question_id = form_data.get('question_id')
        image = form_data.get('image')
        time_spent = form_data.get('time_spent')
        confidence = form_data.get('confidence')
        
        if not user_id or not question_id or not image:
            raise HTTPException(status_code=400, detail="缺少必要参数")
        
        # 转换类型
        time_spent_int = None
        confidence_float = None
        if time_spent and time_spent.strip():
            time_spent_int = int(time_spent)
        if confidence and confidence.strip():
            confidence_float = float(confidence)
        
        # 根据题目ID从数据库获取题目信息
        conn = get_db_connection()
        
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
            conn.close()
            raise HTTPException(status_code=404, detail=f"题目ID {question_id} 不存在")
        
        question_text = question_info["question_text"]
        question_type = question_info["question_type"]
        correct_answer = question_info["answer"]
        analysis = question_info["analysis"]
        difficulty = question_info["difficulty"]
        knowledge_points = question_info["knowledge_points"] or ""
        
        # 保存上传的图片
        import os
        from datetime import datetime
        
        upload_dir = "../backend/uploads"
        os.makedirs(upload_dir, exist_ok=True)
        
        # 生成唯一文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_extension = os.path.splitext(image.filename)[1] if image.filename else ".jpg"
        filename = f"answer_{user_id}_{question_id}_{timestamp}{file_extension}"
        file_path = os.path.join(upload_dir, filename)
        
        # 保存文件
        with open(file_path, "wb") as buffer:
            content = await image.read()
            buffer.write(content)
        
        # 使用假的图片转文字函数
        recognized_text = _fake_image_to_text(file_path)
        
        # 使用相同的诊断逻辑
        diagnosis_result = _diagnose_answer_logic(recognized_text, correct_answer, question_text)
        is_correct = diagnosis_result['is_correct']
        
        # 保存答题记录到数据库
        
        try:
            conn.execute("""
                INSERT INTO user_answers 
                (user_id, question_id, user_answer, is_correct, time_spent, confidence, timestamp, diagnosis_json)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (user_id, question_id, recognized_text, is_correct,
                  time_spent_int or 0, confidence_float or 0.5, datetime.now().isoformat(), json.dumps(diagnosis_result, ensure_ascii=False)))
            conn.commit()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"插入答题记录失败: {str(e)}")
        
        # 更新用户知识点掌握度
        try:
            # 获取题目关联的知识点和题目难度
            cursor = conn.execute("""
                SELECT qm.node_id, q.difficulty 
                FROM question_to_node_mapping qm
                JOIN questions q ON qm.question_id = q.question_id
                WHERE qm.question_id = ?
            """, (question_id,))
            
            knowledge_nodes = cursor.fetchall()
            
            for node in knowledge_nodes:
                node_id = node['node_id']
                difficulty = node['difficulty'] or 0.5  # 默认难度0.5
                
                # 根据题目难度计算掌握度变化幅度
                # 难题答对奖励更多，简单题答错惩罚更少
                if is_correct:
                    # 答对：难度越高，奖励越多 (0.05 - 0.15)
                    score_change = 0.05 + difficulty * 0.1
                else:
                    # 答错：难度越低，惩罚越多 (0.02 - 0.12)
                    score_change = -(0.02 + (1 - difficulty) * 0.1)
                
                # 检查是否已有掌握度记录
                cursor = conn.execute("""
                    SELECT mastery_score FROM user_node_mastery 
                    WHERE user_id = ? AND node_id = ?
                """, (user_id, node_id))
                
                existing = cursor.fetchone()
                
                if existing:
                    # 更新现有记录，确保掌握度在0-1之间
                    new_score = max(0.0, min(1.0, existing['mastery_score'] + score_change))
                    conn.execute("""
                        UPDATE user_node_mastery 
                        SET mastery_score = ?, updated_at = CURRENT_TIMESTAMP
                        WHERE user_id = ? AND node_id = ?
                    """, (new_score, user_id, node_id))

                else:
                    # 创建新记录，初始掌握度0.5，然后应用变化
                    initial_score = max(0.0, min(1.0, 0.5 + score_change))
                    conn.execute("""
                        INSERT INTO user_node_mastery (user_id, node_id, mastery_score, updated_at)
                        VALUES (?, ?, ?, CURRENT_TIMESTAMP)
                    """, (user_id, node_id, initial_score))

            
            conn.commit()
            
        except Exception as e:
            # 掌握度更新失败不影响主要流程，只记录错误
            pass
        
        # 如果答错了，更新错题记录
        if not is_correct:
            cursor = conn.execute("""
                SELECT wrong_id, wrong_count FROM wrong_questions 
                WHERE user_id = ? AND question_id = ?
            """, (user_id, question_id))
            
            existing = cursor.fetchone()
            if existing:
                conn.execute("""
                    UPDATE wrong_questions 
                    SET wrong_count = wrong_count + 1, last_wrong_time = ?
                    WHERE wrong_id = ?
                """, (datetime.now().isoformat(), existing["wrong_id"]))
                conn.commit()
            else:
                try:
                    conn.execute("""
                        INSERT INTO wrong_questions 
                        (user_id, question_id, wrong_count, last_wrong_time, status)
                        VALUES (?, ?, ?, ?, '未掌握')
                    """, (user_id, question_id, 1, datetime.now().isoformat()))
                    conn.commit()
                except Exception as e:
                    pass
        
        conn.close()
        
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
        
        response = requests.request("POST", url, headers=headers, data=payload).json()
        # 检查响应是否成功
        if 'choices' not in response or not response['choices'] or 'delta' not in response['choices'][0]:
            raise HTTPException(status_code=500, detail="AI生成学习目标失败：响应格式错误")
            
        content = response['choices'][0]['delta'].get('content')
        if not content:
            raise HTTPException(status_code=500, detail="AI诊断失败")
            
        # print(f"✅ AI诊断内容: {content}")
        
        # 解析AI响应
        parts = content.split("##")
        if len(parts) < 3:
            raise HTTPException(status_code=500, detail="AI响应格式错误")
            
        is_correct = parts[0].strip().lower() == 'yes'
        reason = parts[1].strip()

        # 检查是否有评分部分
        if len(parts) >= 3 and parts[2].strip():
            try:
                # 尝试解析JSON评分数组
                scores_json = parts[2].strip()
                scores = json.loads(scores_json)
            except json.JSONDecodeError as e:
                # 评分解析失败不影响主要结果
                pass
        
        # result = {
        #     "is_correct": is_correct,
        #     "assessment_dimensions": scores,
        #     "overall_summary": reason,
        # }
        
        result = {
            "is_correct": is_correct,
            "reason": reason,
            "scores": scores,
        }
        
        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"诊断失败: {str(e)}")

def _fake_image_to_text(image_path: str) -> str:
    """
    调用API进行图片转文字识别
    
    Args:
        image_path: 图片文件路径
    
    Returns:
        str: OCR识别的文字内容
    """
    try:
        import os
        import mimetypes
        
        # 检查文件是否存在
        if not os.path.exists(image_path):
            return "图片文件不存在"
        
        # 获取文件的MIME类型
        mime_type, _ = mimetypes.guess_type(image_path)
        if not mime_type or not mime_type.startswith('image/'):
            return "不支持的图片格式"
        
        # 准备API请求
        url = "https://xingchen-api.xf-yun.com/workflow/v1/upload_file"
        api_key = "4cec7267c3353726a2f1656cb7c0ec37:NDk0MDk0N2JiYzg0ZTgxMzVlNmRkM2Fh"
        
        headers = {
            'Authorization': f'Bearer {api_key}'
        }
        
        # 准备文件上传
        with open(image_path, 'rb') as f:
            files = {
                'file': (os.path.basename(image_path), f, mime_type)
            }
            
            response = requests.post(url, headers=headers, files=files)
            
            if response.status_code == 200:
                result = response.json()
                
                # 根据API响应格式提取识别的文字
                # 这里需要根据实际API响应格式调整
                image_url = result['data']['url']

                url = "https://xingchen-api.xf-yun.com/workflow/v1/chat/completions"
        
                payload = json.dumps({
                    "flow_id": "7358509673684582402",
                    "parameters": {
                        "AGENT_USER_INPUT": "图片转文字",
                        "image": image_url,
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

                return content
            else:
                return f"OCR识别失败: {response.text}"
                
    except Exception as e:
        return f"图片处理异常: {str(e)}"