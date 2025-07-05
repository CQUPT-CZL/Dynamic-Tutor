#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库初始化脚本
创建所有必要的表结构和初始数据
"""

import sqlite3
import os
from pathlib import Path

def init_database():
    """初始化数据库"""
    # 确保data目录存在
    data_dir = Path("../data")
    data_dir.mkdir(exist_ok=True)
    
    db_path = data_dir / "my_database.db"
    
    # 连接数据库
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    
    print(f"🔧 初始化数据库: {db_path}")
    
    # 读取SQL文件
    sql_file = Path("../data/create_tables.sql")
    if sql_file.exists():
        with open(sql_file, 'r', encoding='utf-8') as f:
            sql_content = f.read()
        
        # 执行SQL语句
        try:
            conn.executescript(sql_content)
            conn.commit()
            print("✅ 数据库表结构创建成功")
        except Exception as e:
            print(f"❌ 创建表结构失败: {e}")
            return False
    else:
        print("❌ SQL文件不存在")
        return False
    
    # 验证表是否创建成功
    tables = [
        'users', 'knowledge_nodes', 'knowledge_edges', 
        'questions', 'question_to_node_mapping', 
        'user_node_mastery', 'user_answers', 'wrong_questions'
    ]
    
    for table in tables:
        try:
            cursor = conn.execute(f"SELECT COUNT(*) as count FROM {table}")
            count = cursor.fetchone()["count"]
            print(f"✅ 表 {table}: {count} 条记录")
        except Exception as e:
            print(f"❌ 表 {table} 验证失败: {e}")
    
    conn.close()
    print("🎉 数据库初始化完成")
    return True

if __name__ == "__main__":
    init_database() 