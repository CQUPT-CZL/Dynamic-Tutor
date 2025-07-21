import sqlite3
import os
import random
import json
import time
from tqdm import tqdm
from datetime import datetime
from collections import defaultdict

# --- 配置区 ---
DB_FILE = "my_database.db"
NUM_INTERACTIONS_PER_USER = 100

# --- 虚拟学生画像定义 ---
PERSONAS = {
    "小崔": {"name": "基础薄弱的小崔", "base_accuracy": 0.4, "weakness": "knowledge"},
    "小陈": {"name": "聪明的马虎蛋小陈", "base_accuracy": 0.8, "weakness": "calculation"},
    "小李": {"name": "稳步前进的小李", "base_accuracy": 0.7, "weakness": None},
    "小张": {"name": "学霸小张", "base_accuracy": 0.95, "weakness": None}
}

# --- 模块顺序定义 ---
MODULE_ORDER = [
    "第一模块：概率论的基本概念",
    "第二模块：概率运算进阶", 
    "第三模块：随机变量及其分布",
    "第四模块：数字特征与关系",
    "第五模块：极限定理",
    "第六模块：数理统计"
]

def get_db_connection():
    """获取数据库连接"""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def generate_mock_diagnosis(is_correct, persona):
    """根据答题结果和用户画像，生成一份模拟的诊断JSON"""
    scores = {"knowledge": 0.7, "logic": 0.7, "calculation": 0.7, "behavior": 0.7}
    if is_correct:
        summary = "表现出色，完全掌握！"
        scores = {k: round(random.uniform(0.8, 1.0), 2) for k in scores}
    else:
        weakness = persona.get("weakness")
        if weakness == "knowledge":
            scores["knowledge"] = round(random.uniform(0.1, 0.4), 2)
            summary = "对核心概念的理解似乎还不够深入哦。"
        elif weakness == "calculation":
            scores["calculation"] = round(random.uniform(0.1, 0.4), 2)
            scores["logic"] = round(random.uniform(0.8, 1.0), 2)
            summary = "思路完全正确，但在计算上出了点小差错。"
        else:
            scores["logic"] = round(random.uniform(0.3, 0.6), 2)
            summary = "解题的大方向上可能需要再思考一下。"
    
    diagnosis_report = {
        "is_correct": is_correct,
        "assessment_dimensions": [
            {"dimension": "知识掌握", "score": scores["knowledge"]},
            {"dimension": "解题逻辑", "score": scores["logic"]},
            {"dimension": "计算准确性", "score": scores["calculation"]},
            {"dimension": "行为表现", "score": scores["behavior"]}
        ],
        "overall_summary": summary
    }
    return json.dumps(diagnosis_report, ensure_ascii=False)

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

def get_next_learnable_node_in_module(cursor, user_id, module_name, all_nodes, prereq_map):
    """在指定模块内获取下一个可学习的节点"""
    # 获取用户当前的掌握度
    cursor.execute("SELECT node_id, mastery_score FROM user_node_mastery WHERE user_id = ?", (user_id,))
    mastery_rows = cursor.fetchall()
    user_mastery = {row['node_id']: row['mastery_score'] for row in mastery_rows}
    
    # 获取模块内的所有节点
    module_nodes = get_module_nodes(cursor, module_name)
    if not module_nodes:
        return None
    
    # 找出已掌握的节点
    mastered_nodes = {node_id for node_id, score in user_mastery.items() if score >= 0.8}
    
    # 在模块内寻找可学习的节点
    learnable_candidates = []
    for node_id in module_nodes:
        node_id_str = str(node_id)
        # 如果节点未掌握，并且它的所有前置知识都已掌握
        prerequisites = prereq_map.get(node_id_str, set())
        if user_mastery.get(node_id_str, 0.0) < 0.8 and prerequisites.issubset(mastered_nodes):
            if node_id_str in all_nodes:
                learnable_candidates.append(all_nodes[node_id_str])
    
    # 如果没有找到可学习的节点，选择模块内第一个未掌握的节点（可能是循环依赖的情况）
    if not learnable_candidates:
        for node_id in module_nodes:
            node_id_str = str(node_id)
            if user_mastery.get(node_id_str, 0.0) < 0.8 and node_id_str in all_nodes:
                learnable_candidates.append(all_nodes[node_id_str])
                break
    
    if not learnable_candidates:
        return None
    
    # 选择难度最低的节点
    learnable_candidates.sort(key=lambda x: x['node_difficulty'])
    return learnable_candidates[0]

def get_next_learnable_node(cursor, user_id, all_nodes, prereq_map):
    """
    根据模块化学习策略，推荐下一个最该学习的知识点
    策略：按模块顺序学习，只有当前模块完成后才能进入下一模块
    """
    # 获取用户当前的全景知识画像
    cursor.execute("SELECT node_id, mastery_score FROM user_node_mastery WHERE user_id = ?", (user_id,))
    mastery_rows = cursor.fetchall()
    user_mastery = {row['node_id']: row['mastery_score'] for row in mastery_rows}
    
    # 调试信息：显示用户掌握度情况
    if not user_mastery:
        print(f"  📝 用户{user_id}还没有任何学习记录，从第一模块开始学习")
    else:
        mastered_count = len([score for score in user_mastery.values() if score >= 0.8])
        # print(f"  📊 用户{user_id}已掌握节点数: {mastered_count}/{len(user_mastery)}")
    
    # 获取当前应该学习的模块
    current_module = get_current_module(cursor, user_id)
    if not current_module:
        print(f"  🎓 用户{user_id}已完成所有模块的学习！")
        return None
    
    print(f"  📚 用户{user_id}当前学习模块: {current_module}")
    
    # 在当前模块内寻找下一个可学习的节点
    next_node = get_next_learnable_node_in_module(cursor, user_id, current_module, all_nodes, prereq_map)
    
    # if next_node:
    #     print(f"  🎯 推荐学习节点: {next_node['node_name']} (难度: {next_node['node_difficulty']})")
    # else:
    #     print(f"  ⚠️ 在模块 {current_module} 中未找到可学习的节点")
    
    return next_node

def simulate_user_learning():
    """主函数，模拟所有用户的学习过程，并填充动态数据表。"""
    if not os.path.exists(DB_FILE):
        print(f"❌ 错误: 数据库文件 '{DB_FILE}' 不存在。")
        return

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        print("🚀 开始模块化智能学习轨迹模拟...")

        # --- 1. 预加载所有需要的静态数据到内存 ---
        print("\n--- 正在预加载知识图谱和题库 ---")
        all_nodes = {str(row['node_id']): dict(row) for row in cursor.execute("SELECT * FROM knowledge_nodes").fetchall()}
        
        # 构建节点间的依赖关系图（仅针对模块内的节点）
        prereq_map = defaultdict(set)
        all_edges = cursor.execute("SELECT source_node_id, target_node_id, relation_type FROM knowledge_edges").fetchall()
        
        for edge in all_edges:
            source_id, target_id, rel_type = str(edge['source_node_id']), str(edge['target_node_id']), edge['relation_type']
            
            # 只处理节点间的指向关系（不包括模块的包含关系）
            if rel_type == '指向':
                prereq_map[target_id].add(source_id)
        
        print("✅ 模块化依赖关系图构建完成！")
        
        # 构建节点到题目的映射
        node_to_questions_map = defaultdict(list)
        for row in cursor.execute("SELECT q.question_id, q.difficulty, qnm.node_id FROM questions q JOIN question_to_node_mapping qnm ON q.question_id = qnm.question_id").fetchall():
            node_to_questions_map[str(row['node_id'])].append(dict(row))
        
        users = cursor.execute("SELECT user_id, username FROM users WHERE role = 'student'").fetchall()

        # --- 2. 为每个用户进行模块化学习模拟 ---
        for user in users:
            user_id = user['user_id']
            username = user['username']
            if username not in PERSONAS: 
                continue
            persona = PERSONAS[username]
            
            print(f"\n--- 正在模拟 '{persona['name']}' 的模块化学习轨迹 ---")

            current_learning_node = None
            node_switch_count = 0
            current_module = None
            
            for interaction_num in tqdm(range(NUM_INTERACTIONS_PER_USER), desc=f"  模拟'{username}'学习中", leave=False):
                # 每次循环睡眠0.1秒
                time.sleep(0.1)
                target_node = get_next_learnable_node(cursor, user_id, all_nodes, prereq_map)
                
                # 检测节点切换
                if current_learning_node != (target_node['node_id'] if target_node else None):
                    if current_learning_node is not None:
                        node_switch_count += 1
                        print(f"\n  📚 {username} 切换学习节点: {current_learning_node} -> {target_node['node_id'] if target_node else 'None'}")
                    current_learning_node = target_node['node_id'] if target_node else None
                
                # 检测模块切换
                new_module = get_current_module(cursor, user_id)
                if current_module != new_module:
                    if current_module is not None:
                        print(f"\n  🎉 {username} 完成模块: {current_module}")
                        print(f"  🚀 {username} 开始新模块: {new_module}")
                    current_module = new_module
                
                if not target_node:
                    print(f"\n  🎓 {username} 已完成所有模块的学习！模拟结束。(共切换了{node_switch_count}个节点)")
                    break
                
                available_questions = node_to_questions_map.get(str(target_node['node_id']))
                if not available_questions:
                    print(f"  ⚠️ 节点 {target_node['node_id']} 没有关联的题目，跳过")
                    continue
                    
                question = random.choice(available_questions)
                question_id = question['question_id']
                question_difficulty = question['difficulty']

                # 计算答题准确率（基于用户画像和题目难度）
                accuracy_chance = persona['base_accuracy'] + (0.5 - question_difficulty) * 0.3
                is_correct = random.random() < accuracy_chance
                diagnosis_json_str = generate_mock_diagnosis(is_correct, persona)

                # 记录答题记录
                cursor.execute(
                    "INSERT INTO user_answers (user_id, question_id, user_answer, is_correct, time_spent, confidence, diagnosis_json) VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (user_id, question_id, "模拟答案", is_correct, random.randint(30, 300), random.uniform(0.3, 1.0), diagnosis_json_str)
                )

                # 更新掌握度
                node_id_str = str(target_node['node_id'])
                cursor.execute("SELECT mastery_score FROM user_node_mastery WHERE user_id = ? AND node_id = ?", (user_id, node_id_str))
                current_mastery_row = cursor.fetchone()
                current_mastery = current_mastery_row['mastery_score'] if current_mastery_row else 0.0
                
                # 掌握度更新算法
                if is_correct:
                    # 答对时，根据题目难度动态调整增长幅度
                    growth = 0.1 + question_difficulty * 0.1  # 难题答对增长更多
                    new_mastery = min(1.0, current_mastery + growth)
                else:
                    # 答错时，掌握度下降
                    new_mastery = max(0.0, current_mastery - 0.05)
                
                # 保留两位小数
                new_mastery = round(new_mastery, 2)
                
                # 更新或插入掌握度记录
                if current_mastery_row:
                    cursor.execute("UPDATE user_node_mastery SET mastery_score = ? WHERE user_id = ? AND node_id = ?", (new_mastery, user_id, node_id_str))
                else:
                    cursor.execute("INSERT INTO user_node_mastery (user_id, node_id, mastery_score) VALUES (?, ?, ?)", (user_id, node_id_str, new_mastery))
                
                # # 详细的掌握度变化日志
                # if interaction_num % 10 == 0 or new_mastery >= 0.8:
                #     result_emoji = "✅" if is_correct else "❌"
                #     print(f"  {result_emoji} 节点{node_id_str}: {current_mastery:.3f} -> {new_mastery:.3f} (题目难度: {question_difficulty:.2f})")
                
                # 记录错题
                if not is_correct:
                    cursor.execute(
                        "INSERT OR REPLACE INTO wrong_questions (user_id, question_id, wrong_count, last_wrong_time) VALUES (?, ?, COALESCE((SELECT wrong_count FROM wrong_questions WHERE user_id = ? AND question_id = ?), 0) + 1, ?)",
                        (user_id, question_id, user_id, question_id, datetime.now())
                    )

                conn.commit()

        print("\n🎉 模块化学习轨迹模拟完成！")
        print("📊 数据已成功写入数据库，可以开始体验智能推荐系统了。")

    except Exception as e:
        print(f"❌ 模拟过程中发生错误: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    simulate_user_learning()
