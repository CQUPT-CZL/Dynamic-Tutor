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
    """在指定模块内获取候选学习节点（包括一跳和二跳节点）"""
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
    
    # 候选节点列表，包含权重信息
    all_candidates = []
    
    # 1. 寻找一跳节点（直接可学习的节点）- 权重 0.8
    print("🎯 寻找一跳节点（直接可学习）...")
    for node_id in module_nodes:
        node_id_str = str(node_id)
        if user_mastery.get(node_id_str, 0.0) < 0.8:  # 未掌握的节点
            prerequisites = prereq_map.get(node_id_str, set())
            prereq_names = [node_name_map.get(prereq_id, f'未知({prereq_id})') for prereq_id in prerequisites]
            print(f"  检查节点 {node_id_str}({node_name_map.get(node_id_str, '未知')}) 的前置条件: {prereq_names}")
            
            if prerequisites.issubset(mastered_nodes):  # 所有前置条件都已掌握
                # 获取节点详细信息
                cursor.execute("""
                    SELECT node_id, node_name, node_difficulty, node_learning
                    FROM knowledge_nodes 
                    WHERE node_id = ?
                """, (node_id,))
                node_info = cursor.fetchone()
                if node_info:
                    candidate = dict(node_info)
                    candidate['hop_weight'] = 0.8  # 一跳权重
                    candidate['hop_type'] = '一跳'
                    all_candidates.append(candidate)
                    print(f"    ✅ 添加一跳候选节点: {candidate['node_name']} (权重: 0.8)")
    
    # 2. 寻找二跳节点（需要先学一个一跳候选节点的）- 权重 0.5
    print("🎯 寻找二跳节点（需要一个一跳候选节点作为前置）...")
    
    # 获取一跳候选节点的ID集合
    one_hop_node_ids = {str(c['node_id']) for c in all_candidates if c['hop_type'] == '一跳'}
    
    for node_id in module_nodes:
        node_id_str = str(node_id)
        if user_mastery.get(node_id_str, 0.0) < 0.8:  # 未掌握的节点
            prerequisites = prereq_map.get(node_id_str, set())
            
            # 检查是否恰好缺少一个前置节点，且这个前置节点是一跳候选节点
            unmastered_prereqs = prerequisites - mastered_nodes
            if len(unmastered_prereqs) == 1:  # 恰好缺少一个前置节点
                missing_prereq = list(unmastered_prereqs)[0]
                
                # 检查这个缺少的前置节点是否是一跳候选节点
                if missing_prereq in one_hop_node_ids:
                    missing_prereq_name = node_name_map.get(missing_prereq, f'未知({missing_prereq})')
                    
                    # 获取节点详细信息
                    cursor.execute("""
                        SELECT node_id, node_name, node_difficulty, node_learning
                        FROM knowledge_nodes 
                        WHERE node_id = ?
                    """, (node_id,))
                    node_info = cursor.fetchone()
                    if node_info:
                        candidate = dict(node_info)
                        candidate['hop_weight'] = 0.5  # 二跳权重
                        candidate['hop_type'] = '二跳'
                        candidate['missing_prereq'] = missing_prereq_name
                        all_candidates.append(candidate)
                        print(f"    ✅ 添加二跳候选节点: {candidate['node_name']} (权重: 0.5, 需要先学一跳节点: {missing_prereq_name})")
    
    print(f"📊 总共找到 {len(all_candidates)} 个候选节点 (一跳: {len([c for c in all_candidates if c['hop_type'] == '一跳'])}, 二跳: {len([c for c in all_candidates if c['hop_type'] == '二跳'])})")
    
    # 如果有候选节点，使用GNN预测选择最佳节点
    if all_candidates:
        print(f"🤖 开始为 {len(all_candidates)} 个候选节点调用GNN预测...")
        
        # 为每个候选节点调用GNN预测
        candidates_with_prediction = []
        for candidate in all_candidates:
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
                    print(f"  🎯 {candidate['hop_type']}节点 {candidate['node_name']} (ID: {candidate['node_id']}) 预测概率: {prediction_probability:.3f}")
                    
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
        
        # 调用AI API评估候选节点适合度
        if candidates_with_prediction:
            # 准备AI评估所需的数据
            mastered_node_names = [node_name_map.get(node_id, f'未知({node_id})') for node_id in mastered_nodes]
            candidate_node_names = [c['node_name'] for c in candidates_with_prediction]
            
            # 调用AI适合度评估
            ai_suitability_scores = call_ai_suitability_api(module_name, mastered_node_names, candidate_node_names)
            
            # 将AI评分添加到候选节点中
            for candidate in candidates_with_prediction:
                candidate['ai_suitability'] = 0.5  # 默认值
                if ai_suitability_scores:
                    for ai_score in ai_suitability_scores:
                        if ai_score.get('node_name') == candidate['node_name']:
                            candidate['ai_suitability'] = ai_score.get('suitability_score', 0.5)
                            break
            
            # 计算三维综合评分（删除难度评分）
            for candidate in candidates_with_prediction:
                # 综合评分：33% GNN预测 + 33% 跳数权重 + 33% AI适合度
                candidate['combined_score'] = (
                    0.33 * candidate['gnn_prediction'] + 
                    0.33 * candidate['hop_weight'] +
                    0.33 * candidate['ai_suitability']
                )
                hop_info = f", 需要先学: {candidate['missing_prereq']}" if candidate['hop_type'] == '二跳' else ""
                print(f"  📊 {candidate['hop_type']}节点 {candidate['node_name']}: GNN={candidate['gnn_prediction']:.3f} | 跳数权重={candidate['hop_weight']:.1f} | AI适合度={candidate['ai_suitability']:.3f} | 综合评分={candidate['combined_score']:.3f}{hop_info}")
            
            best_candidate = max(candidates_with_prediction, key=lambda x: x['combined_score'])
            print(f"🏆 基于三维综合评分选择最佳节点: {best_candidate['node_name']} (综合评分: {best_candidate['combined_score']:.3f})")
            return best_candidate

    # 如果没有找到可学习的节点，选择模块内第一个未掌握的节点（可能是循环依赖的情况）
    if not all_candidates:
        print(f"  ⚠️ 未找到满足前置条件的节点，寻找备选节点...")
        backup_candidates = []
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
                    backup_candidate = dict(node_info)
                    backup_candidate['hop_type'] = '备选'
                    backup_candidate['hop_weight'] = 0.3  # 备选节点权重较低
                    backup_candidate['missing_prereq'] = '存在循环依赖'
                    backup_candidates.append(backup_candidate)
                    break
        
        # 对备选节点也进行GNN预测
        if backup_candidates:
            print(f"  🔮 对备选节点进行GNN预测...")
            candidates_with_prediction = []
            
            for candidate in backup_candidates:
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
                        print(f"    🎯 {candidate['hop_type']}节点 {candidate['node_name']} (ID: {candidate['node_id']}) 预测概率: {prediction_probability:.3f}")
                        
                        candidate['gnn_prediction'] = prediction_probability
                        candidates_with_prediction.append(candidate)
                    else:
                        print(f"    ⚠️ {candidate['hop_type']}节点 {candidate['node_name']} GNN预测失败，状态码: {response.status_code}")
                        candidate['gnn_prediction'] = 0.0
                        candidates_with_prediction.append(candidate)
                        
                except Exception as e:
                    print(f"    ❌ {candidate['hop_type']}节点 {candidate['node_name']} GNN预测出错: {e}")
                    candidate['gnn_prediction'] = 0.0
                    candidates_with_prediction.append(candidate)
            
            if candidates_with_prediction:
                # 为备选节点也调用AI适合度评估
                mastered_node_names = [node_name_map.get(node_id, f'未知({node_id})') for node_id in mastered_nodes]
                candidate_node_names = [c['node_name'] for c in candidates_with_prediction]
                
                ai_suitability_scores = call_ai_suitability_api(module_name, mastered_node_names, candidate_node_names)
                
                # 将AI评分添加到备选候选节点中
                for candidate in candidates_with_prediction:
                    candidate['ai_suitability'] = 0.3  # 备选节点AI适合度默认较低
                    if ai_suitability_scores:
                        for ai_score in ai_suitability_scores:
                            if ai_score.get('node_name') == candidate['node_name']:
                                candidate['ai_suitability'] = ai_score.get('suitability_score', 0.3)
                                break
                
                # 计算备选节点的三维综合评分（删除难度评分）
                for candidate in candidates_with_prediction:
                    # 综合评分：33% GNN预测 + 33% 跳数权重 + 33% AI适合度
                    candidate['combined_score'] = (
                        0.33 * candidate['gnn_prediction'] + 
                        0.33 * candidate['hop_weight'] +
                        0.33 * candidate['ai_suitability']
                    )
                    print(f"    📊 {candidate['hop_type']}节点 {candidate['node_name']}: GNN={candidate['gnn_prediction']:.3f} | 跳数权重={candidate['hop_weight']:.1f} | AI适合度={candidate['ai_suitability']:.3f} | 综合评分={candidate['combined_score']:.3f} ({candidate['missing_prereq']})")
                
                best_candidate = max(candidates_with_prediction, key=lambda x: x['combined_score'])
                print(f"  🏆 基于三维综合评分选择最佳备选节点: {best_candidate['node_name']} (综合评分: {best_candidate['combined_score']:.3f})")
                return best_candidate
    
    if not all_candidates:
        return None
    
    # 如果没有进行GNN预测，按难度排序选择
    all_candidates.sort(key=lambda x: x['node_difficulty'])
    return all_candidates[0]


# --- AI API调用函数 ---
def call_ai_suitability_api(module_name, mastered_nodes, candidate_nodes):
    """调用AI API评估候选节点的适合度"""
    print(f"🤖 调用AI API评估候选节点适合度...")
    
    # 组装输入数据
    profile_data = {
        "current_module": module_name,
        "mastered_knowledge": [node for node in mastered_nodes],
        "candidate_knowledge": [node for node in candidate_nodes]
    }
    print(profile_data)
    
    url = "https://xingchen-api.xf-yun.com/workflow/v1/chat/completions"
    
    payload = json.dumps({
        "flow_id": "7358414739635269632",
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
    
    try:
        print(f"🌐 发送AI适合度评估请求...")
        response = requests.request("POST", url, headers=headers, data=payload).json()
        print("📨 AI API响应成功")
        
        # 检查响应是否成功
        if 'choices' not in response or not response['choices'] or 'delta' not in response['choices'][0]:
            print("❌ AI API响应格式错误")
            return None
            
        content = response['choices'][0]['delta'].get('content')
        if not content:
            print("❌ AI API返回内容为空")
            return None
        
        # 解析AI返回的适合度评分
        try:
            suitability_scores = json.loads(content)
            print(f"✅ AI适合度评估完成，获得 {len(suitability_scores)} 个节点评分")
            return suitability_scores
        except json.JSONDecodeError:
            print("❌ AI返回内容不是有效的JSON格式")
            return None
            
    except Exception as e:
        print(f"❌ AI API调用失败: {e}")
        return None


def handle_new_knowledge(user_id: int, strategic_decision: dict = None, decision_reasoning: str = None):
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
                "title": f"{primary_node['node_name']}",
                "objective": f"在{current_module}中掌握{primary_node['node_name']}知识点",
                "reason": decision_reasoning if decision_reasoning else f"根据模块化学习策略，你当前正在学习{current_module}，推荐掌握{primary_node['node_name']}知识点，这是当前模块中最适合学习的内容"
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



from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/recommendation", tags=["新知识推荐"])

@router.get("/new_knowledge/{user_id}")
async def get_user_profile(user_id: int):
    return handle_new_knowledge(user_id)