# initialize_data.py

import sqlite3
import random
import csv
import os
# from tqdm import tqdm

DB_FILE = "my_database.db"
CSV_FILE = "./raw/filtered_high_school_bracket_image.csv" # 你的原始数据CSV

def get_or_create_node(cursor, node_name, level):
    # ... 这个函数和之前一样，无需改动 ...
    node_id = ''.join(filter(str.isalnum, node_name.strip()))
    if not node_id: return None
    cursor.execute("SELECT node_id FROM knowledge_nodes WHERE node_id = ?", (node_id,))
    if cursor.fetchone() is None:
        cursor.execute(
            "INSERT INTO knowledge_nodes (node_id, node_name, level) VALUES (?, ?, ?)", 
            (node_id, node_name, level)
        )
    return node_id

def import_questions_from_csv(cursor):
    print("\n--- 阶段一：从CSV导入题库 ---")
    with open(CSV_FILE, mode='r', encoding='utf-8-sig') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            try:
                # --- 关键改动：不再从CSV读取ID ---
                # 我们从INSERT语句中移除了 question_id
                cursor.execute(
                    """
                    INSERT INTO questions 
                    (question_text, question_type, difficulty, answer, analysis) 
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        row.get('question'),
                        '选择题' if row.get('answer', '').strip().upper() in ['A', 'B', 'C', 'D'] else '非选择题',
                        round(float(row.get('difficulty', random.random())), 2),
                        row.get('answer'),
                        row.get('analysis')
                    )
                )
                
                # --- 关键改动：获取刚刚插入的自增ID ---
                new_question_id = cursor.lastrowid

                # --- 关联知识点 (逻辑不变) ---
                tags_string = row.get('knowledge_points') or row.get('subject') or f"{row.get('level')}综合"
                level_for_node = row.get('level') 
                knowledge_point_names = [tag.strip() for tag in tags_string.split(';')]
                
                for node_name in knowledge_point_names:
                    if node_name:
                        node_id = get_or_create_node(cursor, node_name, level_for_node)
                        if node_id:
                            cursor.execute(
                                "INSERT OR IGNORE INTO question_to_node_mapping (question_id, node_id) VALUES (?, ?)",
                                (new_question_id, node_id)
                            )
            except Exception as e:
                print(f"处理行 {row.get('id', '未知ID')} 时发生错误: {e}")

def generate_user_mastery_data(cursor):
    print("\n--- 阶段二：为所有用户生成模拟知识点掌握度 ---")
    cursor.execute("SELECT user_id FROM users")
    user_ids = [row[0] for row in cursor.fetchall()]
    
    cursor.execute("SELECT node_id FROM knowledge_nodes")
    node_ids = [row[0] for row in cursor.fetchall()]

    for user_id in user_ids:
        for node_id in node_ids:
            # 为每个用户对每个知识点生成一个0.1到1.0的随机掌握度
            score = round(random.uniform(0.1, 1.0), 2)
            cursor.execute(
                "INSERT INTO user_node_mastery (user_id, node_id, mastery_score) VALUES (?, ?, ?)",
                (user_id, node_id, score)
            )

def generate_wrong_questions_data(cursor):
    print("\n--- 阶段三：为所有用户生成模拟错题本 ---")
    cursor.execute("SELECT user_id FROM users")
    user_ids = [row[0] for row in cursor.fetchall()]

    cursor.execute("SELECT question_id FROM questions")
    question_ids = [row[0] for row in cursor.fetchall()]

    if not question_ids:
        print("题库为空，无法生成错题记录。")
        return

    for user_id in user_ids:
        # 为每个用户随机挑选3道题作为错题
        wrong_sample_questions = random.sample(question_ids, min(len(question_ids), 3))
        for question_id in wrong_sample_questions:
            wrong_count = random.randint(1, 5)
            cursor.execute(
                "INSERT OR IGNORE INTO wrong_questions (user_id, question_id, wrong_count) VALUES (?, ?, ?)",
                (user_id, question_id, wrong_count)
            )

def main():
    # 确保我们操作的是一个由schema.sql创建好的数据库
    if not os.path.exists(DB_FILE):
        print(f"错误: 数据库文件 {DB_FILE} 不存在。请先使用 schema.sql 创建。")
        return
        
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    try:
        import_questions_from_csv(cursor)
        generate_user_mastery_data(cursor)
        generate_wrong_questions_data(cursor)
        conn.commit()
        print("\n🎉🎉🎉 所有数据导入和生成操作成功完成！")
    except Exception as e:
        print(f"\n发生严重错误，操作已回滚: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == '__main__':
    main()