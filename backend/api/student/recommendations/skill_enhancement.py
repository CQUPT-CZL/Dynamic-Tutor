#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
技能提升类型的学习任务处理模块
"""

import json
from ...common.database import get_db_connection

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
                user_node_mastery unm ON kn.node_id = unm.node_id
            WHERE 
                unm.user_id = ? 
                AND kn.node_id IN (
                    SELECT target_node_id 
                    FROM knowledge_edges 
                    WHERE source_node_id = ? AND relation_type = 'CONTAINS'
                )
            ORDER BY 
                unm.mastery_score ASC
            LIMIT 3;
        """
        
        mastery_results = conn.execute(mastery_query, (user_id, domain_id)).fetchall()
        
        # 3. 如果找到了掌握度数据，为每个知识点生成技能提升目标
        if mastery_results:
            for mastery in mastery_results:
                # 计算目标掌握度（当前掌握度+0.15，但不超过0.95）
                current_level = mastery['current_level']
                target_level = min(current_level + 0.15, 0.95)
                
                # 添加到目标技能列表
                target_skills.append({
                    "node_id": mastery['node_id'],
                    "node_name": mastery['node_name'],
                    "skill_name": mastery['node_name'],  # 使用知识点名称作为技能名称
                    "current_level": current_level,
                    "target_level": target_level,
                    "recommended_questions": []
                })
        
        # 4. 如果没有掌握度数据，查找该领域下的技能类型知识点
        if not target_skills:
            skills_query = """
                SELECT 
                    kn.node_id, 
                    kn.node_name,
                    kn.node_difficulty
                FROM 
                    knowledge_nodes kn
                JOIN 
                    knowledge_edges ke ON kn.node_id = ke.target_node_id
                WHERE 
                    ke.source_node_id = ? 
                    AND ke.relation_type = 'CONTAINS'
                    AND kn.node_type = 'SKILL'
                ORDER BY 
                    kn.node_difficulty ASC
                LIMIT 3;
            """
            
            skills_results = conn.execute(skills_query, (domain_id,)).fetchall()
            
            for skill in skills_results:
                # 设置默认的当前掌握度和目标掌握度
                current_level = 0.6  # 默认当前掌握度
                target_level = 0.8   # 默认目标掌握度
                
                # 添加到目标技能列表
                target_skills.append({
                    "node_id": skill['node_id'],
                    "node_name": skill['node_name'],
                    "skill_name": skill['node_name'],  # 使用知识点名称作为技能名称
                    "current_level": current_level,
                    "target_level": target_level,
                    "recommended_questions": []
                })
        
        # 5. 为每个技能查找推荐题目
        for skill_data in target_skills:
            skill_name = skill_data["skill_name"]
            
            # 查找与该技能相关的题目
            if "node_id" in skill_data:
                # 如果有节点ID，使用节点ID查询
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
                # 否则使用技能名称查询
                question_query = """
                    SELECT 
                        q.question_id
                    FROM 
                        questions q
                    WHERE 
                        q.skill_focus LIKE ?
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