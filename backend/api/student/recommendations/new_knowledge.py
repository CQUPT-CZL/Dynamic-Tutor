#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
新知识学习类型的学习任务处理模块
"""

import json
from ...common.database import get_db_connection

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