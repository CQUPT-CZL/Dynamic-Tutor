import sqlite3
import os
from tqdm import tqdm
import random

# --- 配置区 ---
DB_FILE = "my_database.db"  # 你的数据库文件名
TEACHER_USER_ID = 3           # 假设“胡老师”的user_id是3，用于标记创建者

# --- 知识图谱数据定义 (点和边都定义在这里) ---

# 1. 定义所有知识点 (Nodes)
KNOWLEDGE_NODES_DATA = [
    # 模块一
    {'name': '1.1 随机试验与样本空间', 'difficulty': 0.1, 'level': '大一', 'learning': '定义了概率论的基本研究对象和环境。'},
    {'name': '1.2 随机事件及其关系与运算', 'difficulty': 0.2, 'level': '大一', 'learning': '学习事件的包含、互斥、对立关系，以及并、交、差运算。'},
    {'name': '1.3 概率的定义与性质', 'difficulty': 0.3, 'level': '大一', 'learning': '掌握古典、几何、统计三种概率定义，以及概率的公理化定义和核心性质。'},
    {'name': '1.4 条件概率与事件的独立性', 'difficulty': 0.5, 'level': '大一', 'learning': '核心概念，包括条件概率、乘法公式、全概率公式和贝叶斯公式。'},
    # 模块二
    {'name': '2.1 随机变量的概念', 'difficulty': 0.2, 'level': '大一', 'learning': '将随机试验的结果映射为数字，是概率论的一次重要抽象。'},
    {'name': '2.2 离散型随机变量', 'difficulty': 0.4, 'level': '大一', 'learning': '研究变量取值为有限或可数个的情况，重点学习二项分布和泊松分布。'},
    {'name': '2.3 连续型随机变量', 'difficulty': 0.4, 'level': '大一', 'learning': '研究变量取值充满一个区间的情况，重点学习均匀、指数和正态分布。'},
    {'name': '2.4 分布函数(CDF)', 'difficulty': 0.5, 'level': '大一', 'learning': '描述随机变量落在某个区间内的概率，是连接离散和连续的桥梁。'},
    # 你可以在这里继续添加所有模块的知识点...
]

# 2. 定义知识点之间的关系 (Edges)
# 使用知识点的名字，脚本会自动查询它们的ID
KNOWLEDGE_EDGES_DATA = [
    # (起点名称, 终点名称, 关系类型)
    ('1.1 随机试验与样本空间', '1.2 随机事件及其关系与运算', 'is_prerequisite_for'),
    ('1.2 随机事件及其关系与运算', '1.3 概率的定义与性质', 'is_prerequisite_for'),
    ('1.3 概率的定义与性质', '1.4 条件概率与事件的独立性', 'is_prerequisite_for'),
    ('1.4 条件概率与事件的独立性', '2.1 随机变量的概念', 'is_prerequisite_for'),
    ('2.1 随机变量的概念', '2.2 离散型随机变量', 'is_prerequisite_for'),
    ('2.1 随机变量的概念', '2.3 连续型随机变量', 'is_prerequisite_for'),
    ('2.2 离散型随机变量', '2.4 分布函数(CDF)', 'is_prerequisite_for'),
    ('2.3 连续型随机变量', '2.4 分布函数(CDF)', 'is_prerequisite_for'),
]

def initialize_database(db_path):
    """
    一个函数搞定所有事情：填充节点、边，并生成题目。
    """
    if not os.path.exists(db_path):
        print(f"❌ 错误: 数据库文件 '{db_path}' 不存在。请先运行你的schema.sql脚本创建数据库和表。")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    node_name_to_id_map = {}

    try:
        # --- 阶段一：填充知识图谱节点 (Nodes) ---
        print("\n--- 阶段一：填充知识图谱节点 ---")
        for node_data in tqdm(KNOWLEDGE_NODES_DATA, desc="插入知识点"):
            node_name = node_data['name']
            cursor.execute("SELECT node_id FROM knowledge_nodes WHERE node_name = ?", (node_name,))
            existing_node = cursor.fetchone()
            if existing_node:
                node_id = existing_node[0]
            else:
                cursor.execute(
                    "INSERT INTO knowledge_nodes (node_name, node_difficulty, level, node_learning) VALUES (?, ?, ?, ?)",
                    (node_name, node_data['difficulty'], node_data['level'], node_data['learning'])
                )
                node_id = cursor.lastrowid
            node_name_to_id_map[node_name] = node_id

        # --- 阶段二：填充知识图谱关系 (Edges) ---
        print("\n--- 阶段二：填充知识图谱关系 ---")
        for edge_data in tqdm(KNOWLEDGE_EDGES_DATA, desc="创建关系"):
            source_name, target_name, relation_type = edge_data
            source_id = node_name_to_id_map.get(source_name)
            target_id = node_name_to_id_map.get(target_name)

            if source_id and target_id:
                cursor.execute(
                    "INSERT OR IGNORE INTO knowledge_edges (source_node_id, target_node_id, relation_type, created_by) VALUES (?, ?, ?, ?)",
                    (source_id, target_id, relation_type, TEACHER_USER_ID)
                )

        # --- 阶段三：为每个知识点生成并插入题目 ---
        print("\n--- 阶段三：为每个知识点生成题目并关联 ---")
        for node_name, node_id in tqdm(node_name_to_id_map.items(), desc="生成题目"):
            for i in range(1, 4):
                question_type = random.choice(['选择题', '填空题', '解答题'])
                difficulty = round(random.uniform(0.1, 0.9), 2)
                question_text = f"这是一道关于“{node_name}”的{question_type}，难度为{difficulty}。(题目{i})"
                answer = f"“{node_name}”题目{i}的标准答案。"
                analysis = f"“{node_name}”题目{i}的详细解析。"

                cursor.execute(
                    "INSERT INTO questions (question_text, question_type, difficulty, answer, analysis, created_by) VALUES (?, ?, ?, ?, ?, ?)",
                    (question_text, question_type, difficulty, answer, analysis, TEACHER_USER_ID)
                )
                new_question_id = cursor.lastrowid
                
                cursor.execute(
                    "INSERT INTO question_to_node_mapping (question_id, node_id) VALUES (?, ?)",
                    (new_question_id, node_id)
                )
        
        # 提交所有更改
        conn.commit()
        print("\n🎉🎉🎉 恭喜！所有数据已成功装载到数据库！")

    except Exception as e:
        print(f"\n❌ 发生严重错误: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == '__main__':
    initialize_database(DB_FILE)
