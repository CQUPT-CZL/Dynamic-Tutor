#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据导入脚本
从JSON文件导入知识图谱数据和数学题目数据到SQLite数据库
"""

import sqlite3
import os
import json
from tqdm import tqdm
import random
from typing import Dict, List, Any

# --- 配置区 ---
DB_FILE = "my_database.db"
KG_JSON_FILE = "./raw/KG_data_v2.json"  # 知识图谱数据文件
MATH_QUESTIONS_JSON_FILE = "./raw/final_math_questions_1754188486.json"  # 数学题目数据文件


def connect_database(db_path: str = DB_FILE) -> sqlite3.Connection:
    """
    连接到SQLite数据库
    
    Args:
        db_path: 数据库文件路径
        
    Returns:
        数据库连接对象
    """
    if not os.path.exists(db_path):
        raise FileNotFoundError(f"数据库文件不存在: {db_path}")
    
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON")  # 启用外键约束
    return conn


def get_teacher_user_id(conn: sqlite3.Connection) -> int:
    """
    获取教师用户ID（用于设置created_by字段）
    
    Args:
        conn: 数据库连接
        
    Returns:
        教师用户ID
    """
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM users WHERE role = 'teacher' LIMIT 1")
    result = cursor.fetchone()
    
    if result is None:
        raise ValueError("数据库中没有找到教师用户")
    
    return result[0]


def load_json_data(json_path: str) -> Dict[str, Any]:
    """
    加载JSON数据
    
    Args:
        json_path: JSON文件路径
        
    Returns:
        JSON数据
    """
    if not os.path.exists(json_path):
        raise FileNotFoundError(f"JSON文件不存在: {json_path}")
    
    with open(json_path, 'r', encoding='utf-8') as f:
        return json.load(f)

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


def insert_knowledge_node(conn: sqlite3.Connection, node_name: str) -> str:
    """
    插入知识点节点，如果已存在则返回现有ID
    
    Args:
        conn: 数据库连接
        node_name: 知识点名称
        
    Returns:
        知识点节点ID
    """
    cursor = conn.cursor()
    
    # 检查是否已存在
    cursor.execute("SELECT node_id FROM knowledge_nodes WHERE node_name = ?", (node_name,))
    result = cursor.fetchone()
    
    if result:
        return str(result[0])
    
    # 插入新的知识点节点
    cursor.execute("""
        INSERT INTO knowledge_nodes (node_name, node_difficulty, level, node_type, node_learning)
        VALUES (?, ?, ?, ?, ?)
    """, (
        node_name,
        0.5,  # 默认难度
        "高中",  # 默认年级
        "概念",  # 默认类型
        f"{node_name}相关的数学概念和方法"  # 默认学习内容
    ))
    
    return str(cursor.lastrowid)


def insert_question(conn: sqlite3.Connection, question_data: Dict[str, Any], 
                   teacher_id: int) -> int:
    """
    插入题目数据
    
    Args:
        conn: 数据库连接
        question_data: 题目数据
        teacher_id: 教师用户ID
        
    Returns:
        题目ID
    """
    cursor = conn.cursor()
    
    # 处理options字段 - 如果是字典则转换为JSON字符串
    options = question_data.get('options', "")
    if isinstance(options, dict):
        import json
        options = json.dumps(options, ensure_ascii=False)
    elif options is None:
        options = ""
    
    cursor.execute("""
        INSERT INTO questions (
            question_text, question_type, difficulty, options, answer, 
            analysis, skill_focus, status, created_by
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        question_data.get('question_text', ''),
        question_data.get('question_type', '解答题'),
        question_data.get('difficulty', 0.5),
        options,
        question_data.get('answer', ''),
        question_data.get('analysis', ''),
        question_data.get('skill_focus', ''),
        'published',  # 状态设为已发布
        teacher_id
    ))
    
    return cursor.lastrowid


def insert_question_node_mapping(conn: sqlite3.Connection, question_id: int, node_id: str):
    """
    插入题目与知识点的关联关系
    
    Args:
        conn: 数据库连接
        question_id: 题目ID
        node_id: 知识点节点ID
    """
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO question_to_node_mapping (question_id, node_id)
        VALUES (?, ?)
    """, (question_id, node_id))


def import_math_questions(conn: sqlite3.Connection, teacher_id: int):
    """
    导入数学题目数据
    
    Args:
        conn: 数据库连接
        teacher_id: 教师用户ID
    """
    print("\n--- 导入数学题目数据 ---")
    
    # 加载数学题目数据
    questions_data = load_json_data(MATH_QUESTIONS_JSON_FILE)
    print(f"成功加载数学题目数据，包含 {len(questions_data)} 个知识点分类")
    
    # 统计信息
    total_questions = 0
    knowledge_nodes_created = set()
    
    # 遍历每个知识点分类
    for knowledge_point, question_types in tqdm(questions_data.items(), desc="导入数学题目"):
        # 创建或获取知识点节点
        node_id = insert_knowledge_node(conn, knowledge_point)
        knowledge_nodes_created.add(knowledge_point)
        
        # 处理该知识点下的不同题型
        for question_type, questions in question_types.items():
            # 处理该题型下的所有题目
            for question in questions:
                # 确保question是字典类型
                if isinstance(question, dict):
                    # 插入题目
                    question_id = insert_question(conn, question, teacher_id)
                    
                    # 创建题目与知识点的关联
                    insert_question_node_mapping(conn, question_id, node_id)
                    
                    total_questions += 1
                else:
                    print(f"警告：跳过非字典类型的题目数据: {question}")
    
    print(f"导入了 {len(knowledge_nodes_created)} 个数学知识点")
    print(f"导入了 {total_questions} 道数学题目")

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
                    (source_id, target_id, relation_type, 1)
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
    # 连接数据库
    conn = connect_database()
    
    try:
        # 获取教师用户ID
        teacher_id = get_teacher_user_id(conn)
        if teacher_id is None:
            print("错误：找不到用户名为 'teacher' 的教师用户")
            conn.close()
            exit(1)
        
        print(f"找到教师用户 (ID: {teacher_id})")
        
        # 导入知识图谱数据
        initialize_database_from_json(DB_FILE, KG_JSON_FILE)
        
        # 导入数学题目数据
        import_math_questions(conn, teacher_id)
        
        print("\n🎉 所有数据导入完成！")
        
    except Exception as e:
        print(f"\n❌ 导入过程中发生错误: {e}")
    finally:
        conn.commit()
        conn.close()
