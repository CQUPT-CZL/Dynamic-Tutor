import sqlite3
import random
import tqdm
import csv

# 使用绝对路径确保能找到数据库文件
DB_FILE = "my_database.db"
CSV_FILE = "./raw/filtered_high_school_bracket_image.csv"

def get_or_create_node(cursor, node_name, level):
    """
    检查知识点是否存在，如果不存在则创建。
    第一次创建时，会把这行数据里的'level'作为知识点的默认年级。
    """
    node_id = ''.join(filter(str.isalnum, node_name.strip()))
    if not node_id: 
        return None

    cursor.execute("SELECT node_id FROM knowledge_nodes WHERE node_id = ?", (node_id,))
    data = cursor.fetchone()
    
    if data is None:
        print(f"  - 新知识点 '{node_name}'，正在创建...")
        # 对于CSV中没有的node_difficulty和node_learning，我们传入None，数据库会自动存为NULL (空)
        cursor.execute(
            "INSERT INTO knowledge_nodes (node_id, node_name, level) VALUES (?, ?, ?)", 
            (node_id, node_name, level)
        )
    return node_id

def main():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    print(f"🚀 开始从 {CSV_FILE} 导入数据...")
    
    # 添加计数器统计成功导入的行数
    success_count = 0

    with open(CSV_FILE, mode='r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        
        for row in tqdm.tqdm(reader, desc="导入数据"):
            try:
                # --- 1. 插入或替换题目信息到 `questions` 表 ---
                # row.get(key, None) 可以在CSV缺少该列时安全地返回None
                question_id = int(row['\ufeffid'])
                # 判断答案是否为ABCD中的一个字母来确定题目类型
                answer = row.get('answer', '').strip().upper()
                question_type = '选择题' if answer in ['A', 'B', 'C', 'D'] else '非选择题'
                
                cursor.execute(
                    """
                    INSERT OR REPLACE INTO questions 
                    (question_id, question_text, question_type, difficulty, answer, analysis) 
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (
                        question_id,
                        row.get('question'),
                        question_type,
                        round(float(row.get('difficulty', random.random())), 1), # 如果没有难度，随机选
                        row.get('answer'),
                        row.get('analysis')
                    )
                )
                print(f"\n处理题目ID: {question_id}...")

                # --- 2. 处理并关联知识点 ---
                tags_string = row.get('knowledge_points', '')
                level = row.get('level') # 获取该题的年级信息

                if tags_string:
                    knowledge_point_names = [tag.strip() for tag in tags_string.split(';')]
                    
                    for node_name in knowledge_point_names:
                        if node_name:
                            # a. 获取或创建知识点节点
                            node_id = get_or_create_node(cursor, node_name, level)
                            
                            # b. 在映射表中创建关联
                            if node_id:
                                cursor.execute(
                                    "INSERT OR IGNORE INTO question_to_node_mapping (question_id, node_id) VALUES (?, ?)",
                                    (question_id, node_id)
                                )
                                print(f"  - 已关联到知识点: '{node_name}'")
                
                # 成功处理完一行数据，计数器加1
                success_count += 1

            except Exception as e:
                print(f"处理行 {row['\ufeffid']} 时发生严重错误: {e}")

    conn.commit()
    conn.close()

    print(f"\n🎉 数据导入全部完成！成功导入 {success_count} 行数据。请使用DB Browser for SQLite检查结果。")

if __name__ == '__main__':
    main()