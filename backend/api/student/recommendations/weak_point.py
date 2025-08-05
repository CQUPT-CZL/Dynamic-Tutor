#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
弱点巩固类型的学习任务处理模块
"""

import json
import time
from ...common.database import get_db_connection

def handle_weak_point_consolidation(user_id: int, decision: dict, decision_reasoning: str = None):
    """
    处理"弱点巩固"任务 - 实现"靶向治疗"逻辑
    
    Args:
        user_id (int): 用户ID
        decision (dict): AI生成的战略决策
        
    Returns:
        dict: 包含学习任务详情的数据包
    """
    conn = get_db_connection()
    try:
        # 从decision中获取目标知识点信息
        target = decision.get('target', {})
        target_node_id = target.get('node_id')
        target_node_name = target.get('node_name')
        
        if not target_node_id or not target_node_name:
            raise ValueError("决策中未指定目标知识点ID或名称")

        print(f"执行战术: 弱点巩固 (靶向治疗), 目标知识点: {target_node_name} (ID: {target_node_id})")
        
        # 获取约束条件
        constraints = decision.get('constraints', {})
        difficulty_range = constraints.get('difficulty_range', [0.3, 0.7])  # 默认难度范围
        task_focus = constraints.get('task_focus', '理解概念')  # 默认任务焦点
        
        # 为这个知识点匹配合适的题目
        # 根据难度范围筛选题目，并获取题目的完整内容
        question_sql = """
            SELECT 
                q.question_id,
                q.question_text,
                q.question_image_url,
                q.question_type,
                q.difficulty,
                q.options,
                q.answer,
                q.analysis,
                q.skill_focus
            FROM questions q
            JOIN question_to_node_mapping qnm ON q.question_id = qnm.question_id
            WHERE qnm.node_id = ?
            AND q.difficulty BETWEEN ? AND ?
            ORDER BY q.difficulty ASC, RANDOM()
            LIMIT 5;
        """
        questions = conn.execute(question_sql, (target_node_id, difficulty_range[0], difficulty_range[1])).fetchall()
        
        # 如果找到题目,取出所有题目信息,否则为空列表
        question_details = []
        question_ids = []
        
        if questions:
            for q in questions:
                question_ids.append(q['question_id'])
                question_details.append({
                    "question_id": q['question_id'],
                    "question_text": q['question_text'],
                    "question_image_url": q['question_image_url'],
                    "question_type": q['question_type'],
                    "difficulty": q['difficulty'],
                    "options": q['options'],
                    "answer": q['answer'],
                    "analysis": q['analysis'],
                    "skill_focus": q['skill_focus']
                })
        
        if not question_ids:
            return {
                "mission_id": f"mission_wpc_{int(time.time())}",
                "mission_type": "WEAK_POINT_CONSOLIDATION",
                "metadata": {
                    "title": f"专项巩固：{target_node_name}",
                    "objective": f"尝试解决在{target_node_name}的学习中遇到的困难。",
                    "reason": f"未找到与知识点'{target_node_name}'匹配的题目。"
                },
                "payload": {
                    "target_node": {
                        "id": target_node_id,
                        "name": target_node_name
                    },
                    "steps": []
                }
            }
        
        # 查询用户之前做错的题目，并获取题目的完整内容
        wrong_question_sql = """
            SELECT 
                wq.question_id,
                q.question_text,
                q.question_image_url,
                q.question_type,
                q.difficulty,
                q.options,
                q.answer,
                q.analysis,
                q.skill_focus
            FROM wrong_questions as wq
            JOIN questions q ON wq.question_id = q.question_id
            WHERE wq.user_id = ? 
            AND wq.question_id IN (
                SELECT qnm.question_id 
                FROM question_to_node_mapping qnm
                WHERE qnm.node_id = ?
            )
            AND wq.status = '未掌握'
            ORDER BY wq.last_wrong_time DESC 
            LIMIT 1;
        """
        wrong_question = conn.execute(wrong_question_sql, (user_id, target_node_id)).fetchone()
        wrong_question_detail = None
        wrong_question_id = None
        
        if wrong_question:
            wrong_question_id = wrong_question['question_id']
            wrong_question_detail = {
                "question_id": wrong_question['question_id'],
                "question_text": wrong_question['question_text'],
                "question_image_url": wrong_question['question_image_url'],
                "question_type": wrong_question['question_type'],
                "difficulty": wrong_question['difficulty'],
                "options": wrong_question['options'],
                "answer": wrong_question['answer'],
                "analysis": wrong_question['analysis'],
                "skill_focus": wrong_question['skill_focus']
            }
        
        # 4. 包装任务
        mission_id = f"mission_wpc_{int(time.time())}"
        
        # 根据难度和任务焦点生成任务描述
        difficulty_desc = "基础" if difficulty_range[0] < 0.4 else ("中等" if difficulty_range[0] < 0.7 else "高级")
        objective = f"彻底解决在{target_node_name}的学习中遇到的困难。"
        reason = decision_reasoning if decision_reasoning else f"注意到你在之前的练习中，对'{target_node_name}'掌握不牢固。我们一起来攻克它！"
        
        # 构建步骤
        steps = []
        
        # 如果有错题，添加错题回顾步骤
        if wrong_question_id and wrong_question_detail:
            steps.append({
                "step": 1,
                "type": "WRONG_QUESTION_REVIEW",
                "content": {
                    "question_id": wrong_question_id, 
                    "prompt": "我们先回顾一下你上次做错的这道题。",
                    "question_text": wrong_question_detail["question_text"],
                    "question_image_url": wrong_question_detail["question_image_url"],
                    "question_type": wrong_question_detail["question_type"],
                    "difficulty": wrong_question_detail["difficulty"],
                    "options": wrong_question_detail["options"],
                    "answer": wrong_question_detail["answer"],
                    "analysis": wrong_question_detail["analysis"],
                    "skill_focus": wrong_question_detail["skill_focus"]
                }
            })
        
        # 添加练习题步骤
        practice_step = 2 if wrong_question_id else 1
        for i, q_id in enumerate(question_ids[:2]):  # 最多取前两道题
            # 找到对应题目的详细信息
            q_detail = next((q for q in question_details if q["question_id"] == q_id), None)
            if q_detail:
                steps.append({
                    "step": practice_step + i,
                    "type": "QUESTION_PRACTICE",
                    "content": {
                        "question_id": q_id, 
                        "difficulty": q_detail["difficulty"], 
                        "prompt": "现在来做一道类似的题目。" if i == 0 else "再来一道题巩固一下。",
                        "question_text": q_detail["question_text"],
                        "question_image_url": q_detail["question_image_url"],
                        "question_type": q_detail["question_type"],
                        "options": q_detail["options"],
                        "answer": q_detail["answer"],
                        "analysis": q_detail["analysis"],
                        "skill_focus": q_detail["skill_focus"]
                    }
                })
        
        return {
            "mission_id": mission_id,
            "mission_type": "WEAK_POINT_CONSOLIDATION",
            "metadata": {
                "title": f"专项巩固：{target_node_name}",
                "objective": objective,
                "reason": reason
            },
            "payload": {
                "target_node": {
                    "id": target_node_id,
                    "name": target_node_name
                },
                "steps": steps,
                # "all_questions": question_details  # 添加所有题目的详细信息
            }
        }

    finally:
        conn.close()