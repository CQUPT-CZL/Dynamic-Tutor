#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
学生推荐模块 - 主文件
负责从数据库收集和预处理学生的近期学习数据，
为下游的AI智能体提供决策依据。
"""

from fastapi import APIRouter, HTTPException
from ...common.database import get_db_connection
import requests
import json
import time
from collections import defaultdict

# 导入各类型推荐处理函数
from .weak_point import handle_weak_point_consolidation
from .new_knowledge import handle_new_knowledge
from .skill_enhancement import handle_skill_enhancement

# --- 核心数据处理函数 ---
def get_user_profile_data(user_id: int, last_n: int = 30):
    """
    为指定用户提取并处理近期学习数据，生成分析摘要。
    """
    conn = get_db_connection()
    
    try:
        # 1. 查询近期答题记录，并JOIN上题目和知识点信息，最重要的是获取其高阶"领域"
        # 这个查询非常关键，它一次性获取了我们需要的所有原始信息
        sql = """
            -- 这是最终版的、能精确查找"章节"的查询
            -- 这个查询的目的是为了按"具体知识点"进行分组统计
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
                # print(f"维度: {dim_name}, 所有分数: {score_list}")
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

        # mission_type = "NEW_KNOWLEDGE"
        # strategic_decision = None

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