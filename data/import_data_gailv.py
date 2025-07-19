import sqlite3
import os
from tqdm import tqdm
import random

# --- 配置区 ---
DB_FILE = "my_database.db"  # 你的数据库文件名
TEACHER_USER_ID = 3           # 假设“胡老师”的user_id是3

# --- 知识图谱数据定义 (全新、详细的概率论数据) ---

# 1. 定义所有知识点 (Nodes)，包括大的章节和具体的小概念
KNOWLEDGE_NODES_DATA = [
    # 领域
    {'name': '概率论', 'difficulty': 1.0, 'level': '大学', 'learning': '研究随机现象统计规律性的数学分支。', 'node_type': '领域'},
    
    # 章节
    {'name': '随机事件与概率', 'difficulty': 0.8, 'level': '大学', 'learning': '概率论的公理化基础和基本概念。', 'node_type': '章节'},
    {'name': '随机变量及其分布', 'difficulty': 0.9, 'level': '大学', 'learning': '将随机事件的结果数字化，是概率论的核心抽象。', 'node_type': '章节'},
    {'name': '多维随机变量及其分布', 'difficulty': 0.9, 'level': '大学', 'learning': '研究多个随机变量之间的相互关系。', 'node_type': '章节'},

    # --- 第一章详细知识点 ---
    {'name': '随机试验与样本空间', 'difficulty': 0.1, 'level': '大学', 'learning': '定义了概率论的基本研究对象和环境。', 'node_type': '主题'},
    {'name': '随机事件及其关系与运算', 'difficulty': 0.2, 'level': '大学', 'learning': '学习事件的包含、互斥、对立关系，以及并、交、差运算。', 'node_type': '主题'},
    {'name': '概率的定义与性质', 'difficulty': 0.3, 'level': '大学', 'learning': '掌握古典、几何、统计三种概率定义，以及概率的公理化定义和核心性质。', 'node_type': '主题'},
    {'name': '条件概率与事件的独立性', 'difficulty': 0.5, 'level': '大学', 'learning': '核心概念，包括条件概率、乘法公式、全概率公式和贝叶斯公式。', 'node_type': '主题'},
    {'name': '古典概型', 'difficulty': 0.2, 'level': '大学', 'learning': '要求试验结果有限且等可能。', 'node_type': '概念'},
    {'name': '贝叶斯公式', 'difficulty': 0.6, 'level': '大学', 'learning': '由因果推断执果索因的核心公式。', 'node_type': '概念'},

    # --- 第二章详细知识点 ---
    {'name': '随机变量的概念', 'difficulty': 0.2, 'level': '大学', 'learning': '将随机试验的结果映射为数字。', 'node_type': '主题'},
    {'name': '离散型随机变量', 'difficulty': 0.4, 'level': '大学', 'learning': '变量取值为有限或可数个的情况。', 'node_type': '主题'},
    {'name': '连续型随机变量', 'difficulty': 0.4, 'level': '大学', 'learning': '变量取值充满一个区间的情况。', 'node_type': '主题'},
    {'name': '分布函数(CDF)', 'difficulty': 0.5, 'level': '大学', 'learning': '描述随机变量P{X ≤ x}的函数。', 'node_type': '主题'},
    {'name': '二项分布', 'difficulty': 0.3, 'level': '大学', 'learning': 'n重伯努利试验中成功次数的分布。', 'node_type': '概念'},
    {'name': '正态分布', 'difficulty': 0.5, 'level': '大学', 'learning': '自然界中最常见、最重要的连续分布。', 'node_type': '概念'},

    # --- 第三章详细知识点 ---
    {'name': '二维随机变量联合分布', 'difficulty': 0.5, 'level': '大学', 'learning': '描述两个随机变量同时取值的概率规律。', 'node_type': '主题'},
    {'name': '边缘分布', 'difficulty': 0.4, 'level': '大学', 'learning': '在联合分布中，只考虑其中一个变量的分布。', 'node_type': '主题'},
    {'name': '条件分布', 'difficulty': 0.6, 'level': '大学', 'learning': '在给定一个变量的条件下，另一个变量的分布。', 'node_type': '主题'},
    {'name': '随机变量的独立性', 'difficulty': 0.5, 'level': '大学', 'learning': '判断两个随机变量是否相互独立。', 'node_type': '主题'},
]

# 2. 定义知识点之间的关系 (Edges)
KNOWLEDGE_EDGES_DATA = [
    # 领域 -> 章节 (从属关系)
    ('概率论', '随机事件与概率', 'CONTAINS'),
    ('概率论', '随机变量及其分布', 'CONTAINS'),
    ('概率论', '多维随机变量及其分布', 'CONTAINS'),

    # 章节 -> 主题 (从属关系)
    ('随机事件与概率', '随机试验与样本空间', 'CONTAINS'),
    ('随机事件与概率', '随机事件及其关系与运算', 'CONTAINS'),
    ('随机事件与概率', '概率的定义与性质', 'CONTAINS'),
    ('随机事件与概率', '条件概率与事件的独立性', 'CONTAINS'),
    
    # 主题 -> 具体概念 (从属关系)
    ('概率的定义与性质', '古典概型', 'CONTAINS'),
    ('条件概率与事件的独立性', '贝叶斯公式', 'CONTAINS'),
    
    # 章节内依赖关系 (is_prerequisite_for)
    ('随机试验与样本空间', '随机事件及其关系与运算', 'is_prerequisite_for'),
    ('随机事件及其关系与运算', '概率的定义与性质', 'is_prerequisite_for'),
    ('概率的定义与性质', '条件概率与事件的独立性', 'is_prerequisite_for'),
    
    # 跨章节依赖关系
    ('随机事件与概率', '随机变量的概念', 'is_prerequisite_for'),
    ('随机变量的概念', '离散型随机变量', 'is_prerequisite_for'),
    ('随机变量的概念', '连续型随机变量', 'is_prerequisite_for'),
    ('离散型随机变量', '分布函数(CDF)', 'is_prerequisite_for'),
    ('连续型随机变量', '分布函数(CDF)', 'is_prerequisite_for'),
    ('随机变量及其分布', '二维随机变量联合分布', 'is_prerequisite_for'),
    ('二维随机变量联合分布', '边缘分布', 'is_prerequisite_for'),
    ('边缘分布', '条件分布', 'is_prerequisite_for'),
    ('条件分布', '随机变量的独立性', 'is_prerequisite_for'),
]

def initialize_database(db_path):
    """一个函数搞定所有事情：填充节点、边，并生成题目。"""
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
                    "INSERT INTO knowledge_nodes (node_name, node_difficulty, level, node_learning, node_type) VALUES (?, ?, ?, ?, ?)",
                    (node_name, node_data['difficulty'], node_data['level'], node_data['learning'], node_data['node_type'])
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
        
        # <<< 核心修改 1：定义能力偏向类型 >>>
        skill_focus_options = ['concept', 'calculation', 'logic', 'application']

        for node_name, node_id in tqdm(node_name_to_id_map.items(), desc="生成题目"):
            # 只为最底层的具体知识点生成题目，不为章节或领域生成
            if not any(edge[0] == node_name for edge in KNOWLEDGE_EDGES_DATA if edge[2] == 'CONTAINS'):
                for i in range(1, 10):
                    question_type = random.choice(['选择题', '填空题', '解答题'])
                    difficulty = round(random.uniform(0.1, 0.9), 2)
                    
                    # <<< 核心修改 2：为题目随机分配一个能力偏向 >>>
                    skill_focus = random.choice(skill_focus_options)
                    
                    question_text = f"这是一道关于“{node_name}”的[{skill_focus}]型{question_type}，难度为{difficulty}。(题目{i})"
                    answer = f"“{node_name}”题目{i}的标准答案。"
                    analysis = f"“{node_name}”题目{i}的详细解析。"

                    # <<< 核心修改 3：在INSERT语句中加入skill_focus字段 >>>
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
        print("\n🎉🎉🎉 恭喜！所有数据已成功装载到数据库！")

    except Exception as e:
        print(f"\n❌ 发生严重错误: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == '__main__':
    initialize_database(DB_FILE)
