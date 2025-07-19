#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
学生画像分析接口 (Profile Analyst Data API)
负责从数据库收集和预处理学生的近期学习数据，
为下游的AI智能体提供决策依据。
"""

from turtle import st
from fastapi import APIRouter, HTTPException
from numpy.ma import fix_invalid
from ..common.database import get_db_connection
import requests
import json
import time
from collections import defaultdict


# --- 核心数据处理函数 ---
def get_user_profile_data(user_id: int, last_n: int = 30):
    """
    为指定用户提取并处理近期学习数据，生成分析摘要。
    """
    conn = get_db_connection()
    
    try:
        # 1. 查询近期答题记录，并JOIN上题目和知识点信息，最重要的是获取其高阶“领域”
        # 这个查询非常关键，它一次性获取了我们需要的所有原始信息
        sql = """
            -- 这是最终版的、能精确查找"章节"的查询
            -- 这个查询的目的是为了按“具体知识点”进行分组统计
            SELECT
                ua.is_correct,
                ua.diagnosis_json,
                kn.node_id,
                kn.node_name
            FROM
                user_answers AS ua
            JOIN
                question_to_node_mapping AS qnm ON ua.question_id = qnm.question_id
            JOIN
                knowledge_nodes AS kn ON qnm.node_id = kn.node_id
            WHERE
                ua.user_id = ? -- 筛选指定用户
            ORDER BY
                ua.timestamp DESC
            LIMIT ?; -- 限制分析最近的N条记录
        """
        recent_answers = conn.execute(sql, (user_id, last_n)).fetchall()
        # print(recent_answers)

        if not recent_answers:
            return {"message": "该用户尚无足够的学习记录进行分析。"}

        # 2. 在Python中进行分组和统计
        # defaultdict可以让我们方便地处理分组
        domain_stats = defaultdict(lambda: {
            "interaction_count": 0, 
            "correct_count": 0, 
            "scores": defaultdict(list)
        })

        for answer in recent_answers:
            node_id = answer['node_id']
            node_name = answer['node_name']
            # 使用知识点名称作为分组键
            if node_name not in domain_stats:
                domain_stats[node_name]["node_id"] = node_id
            domain_stats[node_name]["interaction_count"] += 1
            if answer['is_correct']:
                domain_stats[node_name]["correct_count"] += 1
            
            # 解析diagnosis_json来累加四个维度的分数
            if answer['diagnosis_json']:
                try:
                    diagnosis = json.loads(answer['diagnosis_json'])
                    # print(f"诊断数据: {diagnosis}")  # 打印诊断数据
                    for dim in diagnosis.get('assessment_dimensions', []):
                        dimension_name = dim['dimension'].split(' ')[0] # '知识掌握' -> '知识掌握'
                        domain_stats[node_name]["scores"][dimension_name].append(dim['score'])
                        # print(f"维度: {dimension_name}, 分数: {dim['score']}")  # 打印维度和分数
                except (json.JSONDecodeError, KeyError):
                    # print(f"JSON解析错误或缺少键: {answer['diagnosis_json']}")  # 打印错误信息
                    continue

        # 3. 格式化输出，计算平均分
        analysis_by_domain = []
        total_interactions = len(recent_answers)
        total_correct = sum(1 for ans in recent_answers if ans['is_correct'])

        for domain, stats in domain_stats.items():
            avg_scores = {}
            for dim_name, score_list in stats["scores"].items():
                print(f"维度: {dim_name}, 所有分数: {score_list}")
                avg_scores[dim_name] = round(sum(score_list) / len(score_list), 2) if score_list else 0.0

            analysis_by_domain.append({
                "node_id": stats["node_id"],  # 添加node_id
                "node_name": domain,  # 更改字段名以反映这是知识点名称而非领域名称
                "interaction_count": stats["interaction_count"],
                "accuracy": round(stats["correct_count"] / stats["interaction_count"], 2),
                "average_scores": avg_scores
            })

        # 4. 组装成最终的、将要发送给画像分析师Agent的JSON
        # print(final_payload)
        final_payload = {
            "user_id": user_id,
            "analysis_window": total_interactions,
            "overall_recent_accuracy": round(total_correct / total_interactions, 2),
            "analysis_by_node": analysis_by_domain  # 更新字段名以反映这是按知识点分析而非领域
        }
        print(final_payload)
        
        return final_payload

    except Exception as e:
        print(f"处理用户{user_id}的数据时出错: {e}")
        raise
    finally:
        conn.close()


# --- AI API调用函数 ---
def call_ai_diagnosis_api(profile_data):
    """
    调用AI诊断API，处理用户学习数据并返回诊断结果。
    
    Args:
        profile_data (dict): 用户学习数据分析结果
        
    Returns:
        tuple: (decision_reasoning, strategic_decision) 诊断理由和策略决策
        
    Raises:
        HTTPException: 当API调用失败时抛出异常
    """
    print(f"🤖 开始调用AI诊断API")
    
    url = "https://xingchen-api.xf-yun.com/workflow/v1/chat/completions"
    
    payload = json.dumps({
    "flow_id": "7352207588747141122",
    "parameters": {
        "AGENT_USER_INPUT": json.dumps(profile_data),
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
    print("📨 AI API响应成功")
    
    # 检查响应是否成功
    if 'choices' not in response or not response['choices'] or 'delta' not in response['choices'][0]:
        print("❌ AI API响应格式错误")
        raise HTTPException(status_code=500, detail="AI生成学习目标失败：响应格式错误")
        
    content = response['choices'][0]['delta'].get('content')
    if not content:
        print("❌ AI API返回内容为空")
        raise HTTPException(status_code=500, detail="AI诊断失败")

    decision_reasoning = content.split('##')[0]
    strategic_decision = json.loads(content.split('##')[1])
    
    # print(f"✅ AI诊断内容: {content}")
    
    return decision_reasoning, strategic_decision


def handle_weak_point_consolidation(user_id: int, decision: dict):
    """
    处理"弱点巩固"任务 - 实现"靶向治疗"逻辑
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
        objective = f"彻底解决在{target_node_name}的{task_focus}时遇到的困难。"
        reason = f"AI注意到你({user_id})在之前的练习中，对'{target_node_name}'掌握不牢固。我们一起来攻克它！"
        
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
                "all_questions": question_details  # 添加所有题目的详细信息
            }
        }

    finally:
        conn.close()



def handle_new_knowledge(user_id: int, strategic_decision: dict):
    """
    处理新知识学习类型的学习任务
    
    Args:
        user_id (int): 用户ID
        strategic_decision (dict): AI生成的战略决策
        
    Returns:
        dict: 包含学习任务详情的数据包
    """
    print(f"📚 为用户{user_id}生成新知识学习任务")
    
    # 从strategic_decision中获取目标领域和难度范围
    target = strategic_decision.get('target', {})
    constraints = strategic_decision.get('constraints', {})
    
    domain_name = target.get('domain_name')
    difficulty_range = constraints.get('difficulty_range', [0.3, 0.8])  # 默认难度范围
    
    if not domain_name:
        print(f"⚠️ 未找到目标领域名称，使用默认推荐")
        return {
            "mission_id": f"new-{user_id}-{hash(str(strategic_decision))%1000}",
            "mission_type": "NEW_KNOWLEDGE",
            "title": "探索新知识领域",
            "description": "这个学习任务将引导你学习新的知识点，拓展你的知识面。",
            "target_knowledge_points": [],
            "learning_resources": [],
            "estimated_time": "60分钟",
            "reward_points": 200
        }
    
    # 连接数据库
    conn = get_db_connection()
    target_knowledge_points = []
    learning_resources = []
    
    try:
        # 1. 查找指定领域的节点ID
        domain_query = "SELECT node_id FROM knowledge_nodes WHERE node_name = ? LIMIT 1"
        domain_result = conn.execute(domain_query, (domain_name,)).fetchone()
        
        if not domain_result:
            print(f"⚠️ 未找到领域: {domain_name}")
            return {
                "mission_id": f"new-{user_id}-{hash(str(strategic_decision))%1000}",
                "mission_type": "NEW_KNOWLEDGE",
                "title": "探索新知识领域",
                "description": "这个学习任务将引导你学习新的知识点，拓展你的知识面。",
                "target_knowledge_points": [],
                "learning_resources": [],
                "estimated_time": "60分钟",
                "reward_points": 200
            }
        
        domain_id = domain_result['node_id']
        
        # 2. 查找该领域下的所有知识点，按难度排序
        knowledge_query = """
            SELECT 
                kn.node_id, 
                kn.node_name, 
                kn.node_difficulty as difficulty,
                kn.node_learning
            FROM 
                knowledge_nodes kn
            JOIN 
                knowledge_edges ke ON kn.node_id = ke.target_node_id
            WHERE 
                ke.source_node_id = ? 
                AND ke.relation_type = 'CONTAINS'
                AND kn.node_difficulty BETWEEN ? AND ?
            ORDER BY 
                kn.node_difficulty ASC
            LIMIT 5
        """
        
        knowledge_results = conn.execute(
            knowledge_query, 
            (domain_id, difficulty_range[0], difficulty_range[1])
        ).fetchall()
        
        # 3. 为每个知识点查找推荐题目和学习资源
        for knowledge in knowledge_results:
            # 查找与该知识点相关的题目
            question_query = """
                SELECT 
                    q.question_id
                FROM 
                    questions q
                JOIN 
                    question_to_node_mapping qnm ON q.question_id = qnm.question_id
                WHERE 
                    qnm.node_id = ?
                    AND q.difficulty BETWEEN ? AND ?
                ORDER BY 
                    q.difficulty ASC
                LIMIT 3
            """
            
            question_results = conn.execute(
                question_query, 
                (knowledge['node_id'], difficulty_range[0], difficulty_range[1])
            ).fetchall()
            
            recommended_questions = [q['question_id'] for q in question_results]
            
            # 添加到目标知识点列表
            target_knowledge_points.append({
                "node_id": knowledge['node_id'],
                "node_name": knowledge['node_name'],
                "difficulty": knowledge['difficulty'],
                "recommended_questions": recommended_questions
            })
            
            # 如果有学习内容，添加到学习资源
            if knowledge['node_learning']:
                learning_resources.append({
                    "type": "text",
                    "title": f"{knowledge['node_name']}基础知识",
                    "content": knowledge['node_learning']
                })
        
        # 添加一些通用学习资源
        learning_resources.append({
            "type": "video",
            "title": f"{domain_name}视频讲解",
            "url": f"https://example.com/videos/{domain_id}"
        })
        
        learning_resources.append({
            "type": "article",
            "title": f"{domain_name}详细教程",
            "url": f"https://example.com/articles/{domain_id}"
        })
        
        # 4. 构建并返回学习任务包
        return {
            "mission_id": f"new-{user_id}-{hash(str(strategic_decision))%1000}",
            "mission_type": "NEW_KNOWLEDGE",
            "title": f"探索{domain_name}知识领域",
            "description": f"这个学习任务将引导你学习{domain_name}中的新知识点，难度范围在{difficulty_range[0]}-{difficulty_range[1]}之间。",
            "target_knowledge_points": target_knowledge_points,
            "learning_resources": learning_resources,
            "estimated_time": f"{45 + len(target_knowledge_points) * 15}分钟",
            "reward_points": 150 + len(target_knowledge_points) * 25
        }
        
    except Exception as e:
        print(f"处理新知识学习任务时出错: {e}")
        raise
    finally:
        conn.close()

def handle_skill_enhancement(user_id: int, strategic_decision: dict):
    """
    处理技能提升类型的学习任务
    
    Args:
        user_id (int): 用户ID
        strategic_decision (dict): AI生成的战略决策
        
    Returns:
        dict: 包含学习任务详情的数据包
    """
    print(f"🚀 为用户{user_id}生成技能提升学习任务")
    
    # 从strategic_decision中获取目标领域和难度范围
    target = strategic_decision.get('target', {})
    constraints = strategic_decision.get('constraints', {})
    
    domain_name = target.get('domain_name')
    difficulty_range = constraints.get('difficulty_range', [0.4, 0.9])  # 默认难度范围
    task_focus = constraints.get('task_focus', [])
    
    if not domain_name:
        print(f"⚠️ 未找到目标领域名称，使用默认推荐")
        return {
            "mission_id": f"skill-{user_id}-{hash(str(strategic_decision))%1000}",
            "mission_type": "SKILL_ENHANCEMENT",
            "title": "提升解题技能",
            "description": "这个学习任务专注于提升你的解题技巧和应用能力。",
            "target_skills": [],
            "practice_strategy": "先完成基础题，再挑战进阶题，最后尝试综合应用题",
            "estimated_time": "90分钟",
            "reward_points": 250
        }
    
    # 连接数据库
    conn = get_db_connection()
    target_skills = []
    
    try:
        # 1. 查找指定领域的节点ID
        domain_query = "SELECT node_id FROM knowledge_nodes WHERE node_name = ? LIMIT 1"
        domain_result = conn.execute(domain_query, (domain_name,)).fetchone()
        
        if not domain_result:
            print(f"⚠️ 未找到领域: {domain_name}")
            return {
                "mission_id": f"skill-{user_id}-{hash(str(strategic_decision))%1000}",
                "mission_type": "SKILL_ENHANCEMENT",
                "title": "提升解题技能",
                "description": "这个学习任务专注于提升你的解题技巧和应用能力。",
                "target_skills": [],
                "practice_strategy": "先完成基础题，再挑战进阶题，最后尝试综合应用题",
                "estimated_time": "90分钟",
                "reward_points": 250
            }
        
        domain_id = domain_result['node_id']
        
        # 2. 查找用户在该领域的掌握度
        mastery_query = """
            SELECT 
                kn.node_id, 
                kn.node_name,
                unm.mastery_score as current_level
            FROM 
                knowledge_nodes kn
            JOIN 
                knowledge_edges ke ON kn.node_id = ke.target_node_id
            LEFT JOIN
                user_node_mastery unm ON kn.node_id = unm.node_id AND unm.user_id = ?
            WHERE 
                ke.source_node_id = ? 
                AND ke.relation_type = 'CONTAINS'
            ORDER BY 
                unm.mastery_score ASC
            LIMIT 5
        """
        
        mastery_results = conn.execute(mastery_query, (user_id, domain_id)).fetchall()
        
        # 3. 查找题目的技能重点
        skill_query = """
            SELECT DISTINCT
                q.skill_focus,
                q.difficulty
            FROM 
                questions q
            JOIN 
                question_to_node_mapping qnm ON q.question_id = qnm.question_id
            JOIN
                knowledge_edges ke ON qnm.node_id = ke.target_node_id
            WHERE 
                ke.source_node_id = ?
                AND q.skill_focus IS NOT NULL
                AND q.difficulty BETWEEN ? AND ?
            LIMIT 5
        """
        
        skill_results = conn.execute(
            skill_query, 
            (domain_id, difficulty_range[0], difficulty_range[1])
        ).fetchall()
        
        # 合并技能和掌握度数据
        skills_map = {}
        
        # 先处理掌握度数据
        for mastery in mastery_results:
            node_name = mastery['node_name']
            current_level = mastery['current_level'] or 0.5  # 默认值
            
            if node_name not in skills_map:
                skills_map[node_name] = {
                    "node_id": mastery['node_id'],
                    "skill_name": node_name,
                    "current_level": current_level,
                    "target_level": min(current_level + 0.2, 1.0),
                    "recommended_questions": []
                }
        
        # 再处理技能重点数据
        for skill in skill_results:
            skill_name = skill['skill_focus']
            if skill_name and skill_name not in skills_map:
                skills_map[skill_name] = {
                    "skill_name": skill_name,
                    "current_level": 0.6,  # 默认值
                    "target_level": 0.8,
                    "recommended_questions": []
                }
        
        # 4. 为每个技能查找推荐题目
        for skill_name, skill_data in skills_map.items():
            # 查找与该技能相关的题目
            if "node_id" in skill_data:
                # 基于知识点的题目
                question_query = """
                    SELECT 
                        q.question_id
                    FROM 
                        questions q
                    JOIN 
                        question_to_node_mapping qnm ON q.question_id = qnm.question_id
                    WHERE 
                        qnm.node_id = ?
                        AND q.difficulty BETWEEN ? AND ?
                    ORDER BY 
                        q.difficulty ASC
                    LIMIT 3
                """
                
                question_results = conn.execute(
                    question_query, 
                    (skill_data["node_id"], difficulty_range[0], difficulty_range[1])
                ).fetchall()
            else:
                # 基于技能重点的题目
                question_query = """
                    SELECT 
                        q.question_id
                    FROM 
                        questions q
                    WHERE 
                        q.skill_focus = ?
                        AND q.difficulty BETWEEN ? AND ?
                    ORDER BY 
                        q.difficulty ASC
                    LIMIT 3
                """
                
                question_results = conn.execute(
                    question_query, 
                    (skill_name, difficulty_range[0], difficulty_range[1])
                ).fetchall()
            
            skill_data["recommended_questions"] = [q['question_id'] for q in question_results]
            target_skills.append(skill_data)
        
        # 如果没有找到技能，添加一些默认技能
        if not target_skills:
            target_skills = [
                {
                    "skill_name": "概率计算",
                    "current_level": 0.65,
                    "target_level": 0.8,
                    "recommended_questions": []
                },
                {
                    "skill_name": "公式应用",
                    "current_level": 0.7,
                    "target_level": 0.85,
                    "recommended_questions": []
                }
            ]
        
        # 5. 构建并返回学习任务包
        return {
            "mission_id": f"skill-{user_id}-{hash(str(strategic_decision))%1000}",
            "mission_type": "SKILL_ENHANCEMENT",
            "title": f"提升{domain_name}解题技能",
            "description": f"这个学习任务专注于提升你在{domain_name}领域的解题技巧和应用能力，难度范围在{difficulty_range[0]}-{difficulty_range[1]}之间。",
            "target_skills": target_skills,
            "practice_strategy": "先完成基础题，再挑战进阶题，最后尝试综合应用题",
            "estimated_time": f"{60 + len(target_skills) * 15}分钟",
            "reward_points": 200 + len(target_skills) * 25
        }
        
    except Exception as e:
        print(f"处理技能提升任务时出错: {e}")
        raise
    finally:
        conn.close()

# --- API 路由 ---
router = APIRouter(prefix="/recommendation", tags=["学生推荐"])

@router.get("/{user_id}")
async def get_user_recommendation(user_id: int):
    """
    获取指定用户的学习画像分析数据。
    这个接口是"学习规划师Agent"和"总指挥Agent"决策的数据来源。
    """
    try:
        profile_data = get_user_profile_data(user_id)
        if "message" in profile_data:
            raise HTTPException(status_code=404, detail=profile_data["message"])

        # 调用AI诊断API
        decision_reasoning, strategic_decision = call_ai_diagnosis_api(profile_data)

        print(decision_reasoning, strategic_decision)

        mission_type = strategic_decision.get('mission_type')

        # --- 步骤3: 根据总指挥的战略，调用相应的战术执行函数 ---
        final_mission_package = None
        if mission_type == "WEAK_POINT_CONSOLIDATION":
            final_mission_package = handle_weak_point_consolidation(user_id, strategic_decision)
        elif mission_type == "NEW_KNOWLEDGE":
            final_mission_package = handle_new_knowledge(user_id, strategic_decision)
        elif mission_type == "SKILL_ENHANCEMENT":
            final_mission_package = handle_skill_enhancement(user_id, strategic_decision)
        else:
            print(f"⚠️ 未知的任务类型 '{mission_type}'，执行默认推荐。")
            final_mission_package = handle_new_knowledge(user_id, strategic_decision)

    
        return final_mission_package
        
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"生成用户画像数据失败: {str(e)}")
