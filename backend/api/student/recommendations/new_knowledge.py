#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
新知识学习类型的学习任务处理模块
"""

import json
import requests
from collections import defaultdict
from re import U
from ...common.database import get_db_connection

# --- 模块顺序定义 ---
MODULE_ORDER = [
    "概率论的基本概念",
    "概率运算进阶", 
    "随机变量及其分布",
    "数字特征与关系",
    "极限定理",
    "数理统计"
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
    # print(f"模块节点: {module_nodes}")
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
    
    # 如果有候选节点，使用GNN预测选择最佳节点
    if learnable_candidates:
        print(f"🤖 开始为 {len(learnable_candidates)} 个候选节点调用GNN预测...")
        
        # 为每个候选节点调用GNN预测
        candidates_with_prediction = []
        for candidate in learnable_candidates:
            try:
                # 调用GNN预测API
                prediction_data = {
                    "user_id": user_id,
                    "knowledge_id": candidate['node_id']
                }
                
                response = requests.post(
                    "http://0.0.0.0:8008/predict",
                    json=prediction_data,
                    timeout=5
                )
                
                if response.status_code == 200:
                    prediction_result = response.json()
                    prediction_probability = prediction_result.get('probability', 0.0)
                    print(f"  🎯 节点 {candidate['node_name']} (ID: {candidate['node_id']}) 预测概率: {prediction_probability:.3f}")
                    
                    candidate['gnn_prediction'] = prediction_probability
                    candidates_with_prediction.append(candidate)
                else:
                    print(f"  ⚠️ 节点 {candidate['node_name']} GNN预测失败，状态码: {response.status_code}")
                    # 如果预测失败，设置默认概率
                    candidate['gnn_prediction'] = 0.0
                    candidates_with_prediction.append(candidate)
                    
            except Exception as e:
                print(f"  ❌ 节点 {candidate['node_name']} GNN预测出错: {e}")
                # 如果预测出错，设置默认概率
                candidate['gnn_prediction'] = 0.0
                candidates_with_prediction.append(candidate)
        
        # 根据GNN预测概率和难度的综合评分选择最佳节点（1:1权重）
        if candidates_with_prediction:
            # 计算难度的归一化分数（难度越低分数越高）
            max_difficulty = max(c['node_difficulty'] for c in candidates_with_prediction)
            min_difficulty = min(c['node_difficulty'] for c in candidates_with_prediction)
            difficulty_range = max_difficulty - min_difficulty if max_difficulty > min_difficulty else 1
            
            for candidate in candidates_with_prediction:
                # 归一化难度分数（0-1，难度越低分数越高）
                normalized_difficulty_score = 1 - (candidate['node_difficulty'] - min_difficulty) / difficulty_range
                # 综合评分：50% GNN预测 + 50% 难度评分
                candidate['combined_score'] = 0.5 * candidate['gnn_prediction'] + 0.5 * normalized_difficulty_score
                print(f"  📊 节点 {candidate['node_name']}: GNN={candidate['gnn_prediction']:.3f}, 难度评分={normalized_difficulty_score:.3f}, 综合评分={candidate['combined_score']:.3f}")
            
            best_candidate = max(candidates_with_prediction, key=lambda x: x['combined_score'])
            print(f"🏆 基于综合评分选择最佳节点: {best_candidate['node_name']} (综合评分: {best_candidate['combined_score']:.3f})")
            return best_candidate

    # 如果没有找到可学习的节点，选择模块内第一个未掌握的节点（可能是循环依赖的情况）
    if not learnable_candidates:
        print(f"  ⚠️ 未找到满足前置条件的节点，寻找备选节点...")
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
        
        # 对备选节点也进行GNN预测
        if learnable_candidates:
            print(f"  🔮 对备选节点进行GNN预测...")
            candidates_with_prediction = []
            
            for candidate in learnable_candidates:
                try:
                    prediction_data = {
                        "user_id": user_id,
                        "knowledge_id": candidate['node_id']
                    }
                    
                    response = requests.post(
                        "http://0.0.0.0:8008/predict",
                        json=prediction_data,
                        timeout=5
                    )
                    
                    if response.status_code == 200:
                        prediction_result = response.json()
                        prediction_probability = prediction_result.get('probability', 0.0)
                        print(f"    🎯 备选节点 {candidate['node_name']} (ID: {candidate['node_id']}) 预测概率: {prediction_probability:.3f}")
                        
                        candidate['gnn_prediction'] = prediction_probability
                        candidates_with_prediction.append(candidate)
                    else:
                        print(f"    ⚠️ 备选节点 {candidate['node_name']} GNN预测失败，状态码: {response.status_code}")
                        candidate['gnn_prediction'] = 0.0
                        candidates_with_prediction.append(candidate)
                        
                except Exception as e:
                    print(f"    ❌ 备选节点 {candidate['node_name']} GNN预测出错: {e}")
                    candidate['gnn_prediction'] = 0.0
                    candidates_with_prediction.append(candidate)
            
            if candidates_with_prediction:
                 # 计算备选节点的难度归一化分数
                 max_difficulty = max(c['node_difficulty'] for c in candidates_with_prediction)
                 min_difficulty = min(c['node_difficulty'] for c in candidates_with_prediction)
                 difficulty_range = max_difficulty - min_difficulty if max_difficulty > min_difficulty else 1
                 
                 for candidate in candidates_with_prediction:
                     # 归一化难度分数（0-1，难度越低分数越高）
                     normalized_difficulty_score = 1 - (candidate['node_difficulty'] - min_difficulty) / difficulty_range
                     # 综合评分：50% GNN预测 + 50% 难度评分
                     candidate['combined_score'] = 0.5 * candidate['gnn_prediction'] + 0.5 * normalized_difficulty_score
                     print(f"    📊 备选节点 {candidate['node_name']}: GNN={candidate['gnn_prediction']:.3f}, 难度评分={normalized_difficulty_score:.3f}, 综合评分={candidate['combined_score']:.3f}")
                 
                 best_candidate = max(candidates_with_prediction, key=lambda x: x['combined_score'])
                 print(f"  🏆 基于综合评分选择最佳备选节点: {best_candidate['node_name']} (综合评分: {best_candidate['combined_score']:.3f})")
                 return best_candidate
    
    if not learnable_candidates:
        return None
    
    # 如果没有进行GNN预测，按难度排序选择
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