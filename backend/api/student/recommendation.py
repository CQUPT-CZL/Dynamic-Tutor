#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
学生画像分析接口 (Profile Analyst Data API)
负责从数据库收集和预处理学生的近期学习数据，
为下游的AI智能体提供决策依据。
"""

from fastapi import APIRouter, HTTPException
from ..common.database import get_db_connection
import requests
import json
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
            SELECT
                ua.is_correct,                -- 答题是否正确
                ua.diagnosis_json,            -- 答题诊断数据(JSON格式)
                domain_node.node_name as domain_name -- 章节名称
            FROM
                user_answers AS ua            -- 用户答题记录表
            JOIN
                question_to_node_mapping AS qnm ON ua.question_id = qnm.question_id  -- 关联题目和知识点映射表
            JOIN
                knowledge_edges AS ke ON qnm.node_id = ke.target_node_id            -- 关联知识点关系边表
            JOIN
                knowledge_nodes AS domain_node ON ke.source_node_id = domain_node.node_id  -- 关联知识点节点表
            WHERE
                ua.user_id = ?                -- 筛选指定用户
                AND ke.relation_type = 'CONTAINS'  -- 筛选包含关系
                AND domain_node.node_type = '章节' -- 筛选章节级别的知识点
            ORDER BY
                ua.timestamp DESC             -- 按时间倒序排序
            LIMIT ?;                          -- 限制返回记录数
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
            domain = answer['domain_name']
            domain_stats[domain]["interaction_count"] += 1
            if answer['is_correct']:
                domain_stats[domain]["correct_count"] += 1
            
            # 解析diagnosis_json来累加四个维度的分数
            if answer['diagnosis_json']:
                try:
                    diagnosis = json.loads(answer['diagnosis_json'])
                    for dim in diagnosis.get('assessment_dimensions', []):
                        dimension_name = dim['dimension'].split(' ')[0] # '知识掌握' -> '知识掌握'
                        domain_stats[domain]["scores"][dimension_name].append(dim['score'])
                except (json.JSONDecodeError, KeyError):
                    # 如果JSON格式错误或缺少键，就跳过
                    continue

        # 3. 格式化输出，计算平均分
        analysis_by_domain = []
        total_interactions = len(recent_answers)
        total_correct = sum(1 for ans in recent_answers if ans['is_correct'])

        for domain, stats in domain_stats.items():
            avg_scores = {}
            for dim_name, score_list in stats["scores"].items():
                avg_scores[dim_name] = round(sum(score_list) / len(score_list), 2) if score_list else 0.0

            analysis_by_domain.append({
                "domain_name": domain,
                "interaction_count": stats["interaction_count"],
                "accuracy": round(stats["correct_count"] / stats["interaction_count"], 2),
                "average_scores": avg_scores
            })

        # 4. 组装成最终的、将要发送给画像分析师Agent的JSON
        final_payload = {
            "user_id": user_id,
            "analysis_window": total_interactions,
            "overall_recent_accuracy": round(total_correct / total_interactions, 2),
            "analysis_by_domain": analysis_by_domain
        }
        
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


# --- 学习任务处理函数 ---
def handle_weak_point_consolidation(user_id: int, strategic_decision: dict):
    """
    处理薄弱点巩固类型的学习任务
    
    Args:
        user_id (int): 用户ID
        strategic_decision (dict): AI生成的战略决策
        
    Returns:
        dict: 包含学习任务详情的数据包
    """
    print(f"🔍 为用户{user_id}生成薄弱点巩固学习任务")
    
    # 模拟数据 - 薄弱点巩固任务
    return {
        "mission_id": f"weak-{user_id}-{hash(str(strategic_decision))%1000}",
        "mission_type": "WEAK_POINT_CONSOLIDATION",
        "title": "巩固薄弱知识点",
        "description": "这个学习任务旨在帮助你巩固最近学习中表现较弱的知识点。",
        "target_knowledge_points": [
            {
                "node_id": 15,
                "node_name": "条件概率",
                "difficulty": 0.6,
                "recommended_questions": [101, 102, 103]
            },
            {
                "node_id": 22,
                "node_name": "贝叶斯公式",
                "difficulty": 0.7,
                "recommended_questions": [201, 202, 203]
            }
        ],
        "estimated_time": "45分钟",
        "reward_points": 150
    }

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
    
    # 模拟数据 - 新知识学习任务
    return {
        "mission_id": f"new-{user_id}-{hash(str(strategic_decision))%1000}",
        "mission_type": "NEW_KNOWLEDGE",
        "title": "探索新知识领域",
        "description": "这个学习任务将引导你学习新的知识点，拓展你的知识面。",
        "target_knowledge_points": [
            {
                "node_id": 30,
                "node_name": "多维随机变量",
                "difficulty": 0.8,
                "recommended_questions": [301, 302, 303]
            },
            {
                "node_id": 35,
                "node_name": "边缘分布",
                "difficulty": 0.75,
                "recommended_questions": [401, 402, 403]
            }
        ],
        "learning_resources": [
            {
                "type": "video",
                "title": "多维随机变量入门",
                "url": "https://example.com/videos/multivariate"
            },
            {
                "type": "article",
                "title": "边缘分布详解",
                "url": "https://example.com/articles/marginal-distribution"
            }
        ],
        "estimated_time": "60分钟",
        "reward_points": 200
    }

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
    
    # 模拟数据 - 技能提升任务
    return {
        "mission_id": f"skill-{user_id}-{hash(str(strategic_decision))%1000}",
        "mission_type": "SKILL_ENHANCEMENT",
        "title": "提升解题技能",
        "description": "这个学习任务专注于提升你的解题技巧和应用能力。",
        "target_skills": [
            {
                "skill_name": "概率计算",
                "current_level": 0.65,
                "target_level": 0.8,
                "recommended_questions": [501, 502, 503]
            },
            {
                "skill_name": "公式应用",
                "current_level": 0.7,
                "target_level": 0.85,
                "recommended_questions": [601, 602, 603]
            }
        ],
        "practice_strategy": "先完成基础题，再挑战进阶题，最后尝试综合应用题",
        "estimated_time": "90分钟",
        "reward_points": 250
    }

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

    
        return {
            "user_id": user_id,
            "decision_reasoning": decision_reasoning,
            "strategic_decision": strategic_decision,
            "mission_package": final_mission_package
        }
        
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"生成用户画像数据失败: {str(e)}")
