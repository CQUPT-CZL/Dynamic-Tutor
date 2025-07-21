#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
新知识学习类型的学习任务处理模块
"""

import json
from collections import defaultdict
from re import U
from ...common.database import get_db_connection

# --- 模块顺序定义 ---
MODULE_ORDER = [
    "第一模块：概率论的基本概念",
    "第二模块：概率运算进阶", 
    "第三模块：随机变量及其分布",
    "第四模块：数字特征与关系",
    "第五模块：极限定理",
    "第六模块：数理统计"
]

def get_module_nodes(cursor, module_name):
    """获取指定模块包含的所有节点"""
    cursor.execute("""
        SELECT target_node_id as node_id
        FROM knowledge_edges ke
        JOIN knowledge_nodes kn ON ke.source_node_id = kn.node_id
        WHERE kn.node_name = ? AND ke.relation_type = '包含'
    """, (module_name,))
    return [row['node_id'] for row in cursor.fetchall()]

def is_module_completed(cursor, user_id, module_name, mastery_threshold=0.8):
    """检查用户是否完成了指定模块的学习"""
    module_nodes = get_module_nodes(cursor, module_name)
    if not module_nodes:
        return True  # 空模块视为已完成
    
    cursor.execute("""
        SELECT COUNT(*) as mastered_count
        FROM user_node_mastery
        WHERE user_id = ? AND node_id IN ({}) AND mastery_score >= ?
    """.format(','.join('?' * len(module_nodes))), [user_id] + module_nodes + [mastery_threshold])
    
    mastered_count = cursor.fetchone()['mastered_count']
    return mastered_count == len(module_nodes)

def get_current_module(cursor, user_id):
    """获取用户当前应该学习的模块"""
    for module_name in MODULE_ORDER:
        if not is_module_completed(cursor, user_id, module_name):
            return module_name
    return None  # 所有模块都已完成

def get_next_learnable_node_in_module(cursor, user_id, module_name):
    """在指定模块内获取下一个可学习的节点"""
    # 创建 node_id 到名字的映射
    cursor.execute("SELECT node_id, node_name FROM knowledge_nodes")
    node_name_map = {str(row['node_id']): row['node_name'] for row in cursor.fetchall()}
    
    # 获取用户当前的掌握度
    cursor.execute("SELECT node_id, mastery_score FROM user_node_mastery WHERE user_id = ?", (user_id,))
    mastery_rows = cursor.fetchall()
    user_mastery = {str(row['node_id']): row['mastery_score'] for row in mastery_rows}
    print(f"用户掌握度: {[(node_id, score, node_name_map.get(node_id, '未知')) for node_id, score in user_mastery.items()]}")
    # 获取模块内的所有节点
    module_nodes = get_module_nodes(cursor, module_name)
    print(f"模块节点: {[(node_id, node_name_map.get(str(node_id), '未知')) for node_id in module_nodes]}")
    if not module_nodes:
        return None
    
    # 找出已掌握的节点
    mastered_nodes = {str(node_id) for node_id, score in user_mastery.items() if score >= 0.8}
    
    # 构建节点间的依赖关系图（仅针对模块内的节点）
    prereq_map = defaultdict(set)
    cursor.execute("SELECT source_node_id, target_node_id, relation_type FROM knowledge_edges WHERE relation_type = '指向'")
    all_edges = cursor.fetchall()
    
    for edge in all_edges:
        source_id, target_id = str(edge['source_node_id']), str(edge['target_node_id'])
        prereq_map[target_id].add(source_id)
    
    # 在模块内寻找可学习的节点
    learnable_candidates = []
    for node_id in module_nodes:
        node_id_str = str(node_id)
        # 如果节点未掌握，并且它的所有前置知识都已掌握
        prerequisites = prereq_map.get(node_id_str, set())
        prereq_names = [node_name_map.get(prereq_id, f'未知({prereq_id})') for prereq_id in prerequisites]
        print(f"节点 {node_id_str}({node_name_map.get(node_id_str, '未知')}) 的前置条件: {prereq_names}")
        if user_mastery.get(node_id_str, 0.0) < 0.8 and prerequisites.issubset(mastered_nodes):
            # 获取节点详细信息
            cursor.execute("""
                SELECT node_id, node_name, node_difficulty, node_learning
                FROM knowledge_nodes 
                WHERE node_id = ?
            """, (node_id,))
            node_info = cursor.fetchone()
            if node_info:
                learnable_candidates.append(dict(node_info))
    
    print(f"可学习候选节点: {[(candidate['node_id'], candidate['node_name']) for candidate in learnable_candidates]}")
    
    # 如果没有找到可学习的节点，选择模块内第一个未掌握的节点（可能是循环依赖的情况）
    if not learnable_candidates:
        for node_id in module_nodes:
            node_id_str = str(node_id)
            if user_mastery.get(node_id_str, 0.0) < 0.8:
                cursor.execute("""
                    SELECT node_id, node_name, node_difficulty, node_learning
                    FROM knowledge_nodes 
                    WHERE node_id = ?
                """, (node_id,))
                node_info = cursor.fetchone()
                if node_info:
                    learnable_candidates.append(dict(node_info))
                    break
    
    if not learnable_candidates:
        return None
    
    # 选择难度最低的节点
    learnable_candidates.sort(key=lambda x: x['node_difficulty'])
    return learnable_candidates[0]

def handle_new_knowledge(user_id: int, strategic_decision: dict = None):
    """
    处理新知识学习类型的学习任务
    
    Args:
        user_id (int): 用户ID
        strategic_decision (dict, optional): AI生成的战略决策（已弃用，保留兼容性）
        
    Returns:
        dict: 包含学习任务详情的数据包
    """
    print(f"📚 为用户{user_id}生成新知识学习任务")
    
    # 连接数据库
    conn = get_db_connection()
    target_knowledge_points = []
    
    try:
        print(f"🔍 开始基于模块化策略查询用户{user_id}的候选学习节点...")
        
        # 获取用户当前应该学习的模块
        cursor = conn.cursor()
        current_module = get_current_module(cursor, user_id)
        if not current_module:
            print(f"🎓 用户{user_id}已完成所有模块的学习！")
            return {
                "mission_type": "NEW_KNOWLEDGE",
                "metadata": {
                    "title": "恭喜完成所有学习模块",
                    "objective": "你已经掌握了所有知识模块",
                    "reason": "恭喜！你已经完成了所有模块的学习，可以进行综合复习或挑战更高难度的内容"
                },
                "payload": {
                    "target_node": {
                        "name": "学习完成"
                    },
                    "steps": []
                }
            }
        
        print(f"📚 用户{user_id}当前学习模块: {current_module}")
        
        # 在当前模块内寻找下一个可学习的节点
        target_node = get_next_learnable_node_in_module(cursor, user_id, current_module)
        
        if not target_node:
            print(f"⚠️ 在模块 {current_module} 中未找到可学习的节点")
            return {
                "mission_type": "NEW_KNOWLEDGE",
                "metadata": {
                    "title": "模块学习暂停",
                    "objective": "当前模块暂无可学习内容",
                    "reason": f"在{current_module}中暂时没有找到适合的新知识点，建议先巩固已有知识或联系老师获取更多学习建议"
                },
                "payload": {
                    "target_node": {
                        "name": "暂无推荐"
                    },
                    "steps": []
                }
            }
        
        print(f"🎯 推荐学习节点: {target_node['node_name']} (难度: {target_node['node_difficulty']})")
        
        # 获取用户当前掌握度
        cursor.execute("SELECT mastery_score FROM user_node_mastery WHERE user_id = ? AND node_id = ?", (user_id, target_node['node_id']))
        mastery_row = cursor.fetchone()
        current_mastery = mastery_row['mastery_score'] if mastery_row else 0.0
        
        knowledge = {
            'node_id': target_node['node_id'],
            'node_name': target_node['node_name'],
            'difficulty': target_node['node_difficulty'],
            'node_learning': target_node['node_learning'],
            'current_mastery': current_mastery
        }
        
        print(f"📝 处理推荐知识点: {knowledge['node_name']} (掌握度: {knowledge['current_mastery']:.2f})")
        
        # 查找与该知识点相关的题目
        question_query = """
            SELECT 
                q.question_id,
                q.question_text,
                q.difficulty
            FROM 
                questions q
            JOIN 
                question_to_node_mapping qnm ON q.question_id = qnm.question_id
            WHERE 
                qnm.node_id = ?
            ORDER BY 
                q.difficulty ASC
            LIMIT 3
        """
        
        question_results = conn.execute(
            question_query, 
            (knowledge['node_id'],)
        ).fetchall()
        
        recommended_questions = [{
            'question_id': q['question_id'],
            'question_text': q['question_text'],
            'difficulty': q['difficulty']
        } for q in question_results]
        print(f"  ✅ 为 {knowledge['node_name']} 找到 {len(recommended_questions)} 道练习题")
        
        # 添加到目标知识点列表（只有一个）
        target_knowledge_points.append({
            "node_id": knowledge['node_id'],
            "node_name": knowledge['node_name'],
            "difficulty": knowledge['difficulty'],
            "node_learning": knowledge['node_learning'],
            "recommended_questions": recommended_questions,
            "current_mastery": knowledge['current_mastery']
        })
        
        # 检查是否成功获取到学习节点
        if not target_knowledge_points:
            print(f"⚠️ 未找到适合的新知识学习节点")
            print(f"💡 建议检查用户{user_id}的学习进度或知识图谱配置")
            return {
                "mission_type": "NEW_KNOWLEDGE",
                "metadata": {
                    "title": "探索新知识领域",
                    "objective": "学习新的知识点，拓展知识面",
                    "reason": "暂时没有找到适合的新知识点，建议先巩固已有知识或联系老师获取更多学习建议"
                },
                "payload": {
                    "target_node": {
                        "name": "暂无推荐"
                    },
                    "steps": []
                }
            }
        
        # 选择掌握度最低的节点作为主要学习目标
        primary_node = target_knowledge_points[0]
        print(f"🎯 选择主要学习目标: {primary_node['node_name']} (掌握度: {primary_node['current_mastery']:.2f})")
        
        # 4. 构建学习步骤
        steps = []
        print(f"🔨 开始构建学习步骤，专注于单个知识点: {primary_node['node_name']}")
        
        # 为选中的知识点创建学习步骤（只有一个）
        knowledge_point = target_knowledge_points[0]
        print(f"  📚 为知识点: {knowledge_point['node_name']} 创建学习步骤")
        
        # 添加概念学习步骤
        if knowledge_point.get('node_learning'):
            steps.append({
                "type": "CONCEPT_LEARNING",
                "content": {
                    "title": f"{knowledge_point['node_name']}基础概念",
                    "text": knowledge_point.get('node_learning', f"{knowledge_point['node_name']}的相关知识内容")
                }
            })
            print(f"    ✅ 添加概念学习步骤: {knowledge_point['node_name']}基础概念")
        
        # 添加题目练习步骤
        for question in knowledge_point.get('recommended_questions', []):
            steps.append({
                "type": "QUESTION_PRACTICE",
                "content": {
                    "question_id": question['question_id'],
                    "prompt": f"让我们来练习一下{knowledge_point['node_name']}相关的题目",
                    "question_text": question['question_text'],
                    "question": question['question_text'],
                    "difficulty": question['difficulty'],
                    "question_type": "text_input"
                }
            })
            print(f"    ✅ 添加题目练习步骤: 题目ID {question['question_id']}")
        
        print(f"🎉 学习任务构建完成，共生成 {len(steps)} 个学习步骤")
        
        # 5. 构建并返回符合API格式的学习任务包
        return {
            "mission_type": "NEW_KNOWLEDGE",
            "metadata": {
                "title": f"模块化学习：{primary_node['node_name']}",
                "objective": f"在{current_module}中掌握{primary_node['node_name']}知识点",
                "reason": f"根据模块化学习策略，你当前正在学习{current_module}，推荐掌握{primary_node['node_name']}知识点，这是当前模块中最适合学习的内容"
            },
            "payload": {
                "target_node": {
                    "name": primary_node['node_name']
                },
                "steps": steps
            }
        }
        
    except Exception as e:
        print(f"❌ 处理新知识学习任务时出错: {e}")
        print(f"🔧 错误详情: {type(e).__name__}")
        return {
            "mission_type": "NEW_KNOWLEDGE",
            "metadata": {
                "title": "探索新知识领域",
                "objective": "学习新的知识点，拓展知识面",
                "reason": "系统暂时无法生成学习任务，请稍后重试"
            },
            "payload": {
                "target_node": {
                    "name": "系统错误"
                },
                "steps": []
            }
        }
    finally:
        conn.close()