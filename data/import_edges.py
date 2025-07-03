import sqlite3
import csv

DB_FILE = "my_database.db"  # 你的数据库文件名
CSV_FILE = "./raw/knowledge_edges.csv" # 我们刚刚创建的边表CSV

def get_node_id(cursor, node_name):
    """根据知识点名称查询其ID。"""
    cursor.execute("SELECT node_id FROM knowledge_nodes WHERE node_name = ?", (node_name,))
    result = cursor.fetchone()
    if result:
        return result[0]
    else:
        print(f"⚠️ 警告: 在 knowledge_nodes 表中未找到知识点 '{node_name}'，将跳过此条关系。")
        return None

def main():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    print(f"🚀 开始从 {CSV_FILE} 导入知识点依赖关系...")
    
    edge_count = 0
    with open(CSV_FILE, mode='r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        
        for row in reader:
            source_name = row['source_node_name']
            target_name = row['target_node_name']
            relation = row['relation_type']

            # 1. 查询起点和终点节点的ID
            source_id = get_node_id(cursor, source_name)
            target_id = get_node_id(cursor, target_name)

            # 2. 只有当起点和终点都存在时，才插入关系
            if source_id and target_id:
                try:
                    cursor.execute(
                        """
                        INSERT INTO knowledge_edges (source_node_id, target_node_id, relation_type)
                        VALUES (?, ?, ?)
                        """,
                        (source_id, target_id, relation)
                    )
                    edge_count += 1
                    print(f"  - 成功创建关系: {source_name} -> {target_name}")
                except sqlite3.IntegrityError:
                    # 如果关系已存在，可能会有唯一性约束，这里简单忽略
                    print(f"  - 关系: {source_name} -> {target_name} 已存在，跳过。")
                except Exception as e:
                    print(f"插入关系 {source_name} -> {target_name} 时发生错误: {e}")

    conn.commit()
    conn.close()

    print(f"\n🎉 关系导入完成！共计成功创建 {edge_count} 条边。")

if __name__ == '__main__':
    main()