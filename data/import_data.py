import sqlite3
import os
import json
from tqdm import tqdm
import random

# --- 配置区 ---
DB_FILE = "my_database.db"
JSON_FILE = "./raw/KG_data_v2.json"  # 你的JSON数据文件名
TEACHER_USER_ID = 3            # 假设“胡老师”的user_id是3

def format_node_learning_text(node_obj):
    """将JSON中节点的描述、属性、公式格式化为一段学习文本"""
    learning_text = ""
    if node_obj.get("description"):
        learning_text += f"【描述】\n{node_obj['description']}\n\n"
    
    if node_obj.get("properties"):
        learning_text += "【核心属性】\n"
        for prop in node_obj["properties"]:
            learning_text += f"- {prop}\n"
        learning_text += "\n"
        
    if node_obj.get("formulas"):
        learning_text += "【相关公式】\n"
        for formula in node_obj["formulas"]:
            learning_text += f"`{formula}`\n" # 使用反引号标记为代码，方便前端渲染
            
    return learning_text.strip()

def initialize_database_from_json(db_path, json_path):
    """从JSON文件初始化所有数据：节点、边，并生成题目。"""
    if not os.path.exists(db_path):
        print(f"❌ 错误: 数据库文件 '{db_path}' 不存在。请先运行你的schema.sql脚本创建数据库和表。")
        return
    if not os.path.exists(json_path):
        print(f"❌ 错误: JSON数据文件 '{json_path}' 不存在。")
        return

    # 1. 读取JSON文件
    with open(json_path, 'r', encoding='utf-8') as f:
        kg_data = json.load(f)
    
    nodes_from_json = kg_data.get("nodes", [])
    edges_from_json = kg_data.get("triplets", [])

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    node_name_to_id_map = {}

    try:
        # --- 阶段一：填充知识图谱节点 (Nodes) from JSON ---
        print("\n--- 阶段一：从JSON填充知识图谱节点 ---")
        for node_data in tqdm(nodes_from_json, desc="插入知识点"):
            node_name = node_data['name']
            
            # 检查节点是否已存在
            cursor.execute("SELECT node_id FROM knowledge_nodes WHERE node_name = ?", (node_name,))
            existing_node = cursor.fetchone()
            
            if existing_node:
                node_id = existing_node[0]
            else:
                # 格式化学习文本
                learning_text = format_node_learning_text(node_data)
                
                cursor.execute(
                    "INSERT INTO knowledge_nodes (node_name, node_difficulty, level, node_learning, node_type) VALUES (?, ?, ?, ?, ?)",
                    (
                        node_name, 
                        round(random.random(), 2), # 随机生成一个难度
                        '大学', # 假设都属于大学
                        learning_text,
                        node_data.get('node_type')
                    )
                )
                node_id = cursor.lastrowid
            
            node_name_to_id_map[node_name] = node_id

        # --- 阶段二：填充知识图谱关系 (Edges) from JSON ---
        print("\n--- 阶段二：从JSON填充知识图谱关系 ---")
        for edge_data in tqdm(edges_from_json, desc="创建关系"):
            source_name = edge_data['subject']
            target_name = edge_data['object']
            relation_type = edge_data['predicate']

            
            
            source_id = node_name_to_id_map.get(source_name)
            target_id = node_name_to_id_map.get(target_name)

            if source_id and target_id:
                cursor.execute(
                    "INSERT OR IGNORE INTO knowledge_edges (source_node_id, target_node_id, relation_type, created_by) VALUES (?, ?, ?, ?)",
                    (source_id, target_id, relation_type, TEACHER_USER_ID)
                )

        # --- 阶段三：为每个知识点生成并插入题目 ---
        print("\n--- 阶段三：为每个知识点生成题目并关联 ---")
        skill_focus_options = ['concept', 'calculation', 'logic', 'application']

        for node_name, node_id in tqdm(node_name_to_id_map.items(), desc="生成题目"):
            for i in range(1, 10):
                question_type = random.choice(['选择题', '填空题', '解答题'])
                difficulty = round(random.uniform(0.1, 0.9), 2)
                skill_focus = random.choice(skill_focus_options)
                
                question_text = f"这是一道关于“{node_name}”的[{skill_focus}]型{question_type}，难度为{difficulty}。(题目{i})"
                answer = f"“{node_name}”题目{i}的标准答案。"
                analysis = f"“{node_name}”题目{i}的详细解析。"

                cursor.execute(
                    "INSERT INTO questions (question_text, question_type, difficulty, skill_focus, answer, analysis, created_by) VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (question_text, question_type, difficulty, skill_focus, answer, analysis, TEACHER_USER_ID)
                )
                new_question_id = cursor.lastrowid
                
                cursor.execute(
                    "INSERT INTO question_to_node_mapping (question_id, node_id) VALUES (?, ?)",
                    (new_question_id, node_id)
                )
        
        # 提交所有更改
        conn.commit()
        print("\n🎉🎉🎉 恭喜！JSON中的知识图谱及生成的题目已成功装载到数据库！")

    except Exception as e:
        print(f"\n❌ 发生严重错误: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == '__main__':
    initialize_database_from_json(DB_FILE, JSON_FILE)
