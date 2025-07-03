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

    print(f"🚀 开始从 {CSV_FILE} 导入数据 (使用占位符策略)...")
    
    with open(CSV_FILE, mode='r', encoding='utf-8-sig') as csvfile: # 使用 utf-8-sig 来处理可能的BOM头
        reader = csv.DictReader(csvfile)
        
        for row in tqdm.tqdm(reader, desc="导入数据"):
            try:
                question_id = int(row['id'])
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
                        round(float(row.get('difficulty', random.random())), 1),
                        row.get('answer'),
                        row.get('analysis')
                    )
                )

                # --- 核心修改在这里：智能生成知识点标签 ---
                
                # 1. 优先尝试获取 'knowledge_points' 列
                tags_string = row.get('knowledge_points')
                
                # 2. 如果没有，再尝试获取 'subject' 列 (根据你最初的截图)
                if not tags_string:
                    tags_string = row.get('subject')

                # 3. 如果连 subject 都没有，我们就用 'level' 列来创造一个
                if not tags_string:
                    level = row.get('level')
                    if level:
                        tags_string = f"{level}综合" # 例如，生成 "高二综合" 这样的知识点
                    else:
                        tags_string = "未分类知识点" # 最后的备用方案

                # --- 后续的关联逻辑保持不变 ---
                level_for_node = row.get('level') 
                knowledge_point_names = [tag.strip() for tag in tags_string.split(';')]
                
                for node_name in knowledge_point_names:
                    if node_name:
                        node_id = get_or_create_node(cursor, node_name, level_for_node)
                        if node_id:
                            cursor.execute(
                                "INSERT OR IGNORE INTO question_to_node_mapping (question_id, node_id) VALUES (?, ?)",
                                (question_id, node_id)
                            )
                
            except Exception as e:
                print(f"处理行 {row.get('id', '未知ID')} 时发生错误: {e}")

    # ... (提交和关闭连接的代码不变) ...
    conn.commit()
    conn.close()

    print("\n🎉 数据导入全部完成！")

if __name__ == '__main__':
    main()