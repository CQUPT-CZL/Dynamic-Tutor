#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据信息查看脚本
用于查看当前数据库中的所有数据信息
"""

import sys
import os

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database import DatabaseManager
import json

def main():
    print("📊 数据库信息查看工具")
    print("=" * 50)
    
    try:
        # 初始化数据库管理器
        db = DatabaseManager()
        print("✅ 数据库连接成功")
        
        # 查看用户信息
        print("\n👥 用户信息:")
        print("-" * 30)
        users = db.get_all_users() if hasattr(db, 'get_all_users') else []
        if not users:
            # 如果没有get_all_users方法，尝试直接查询数据库
            import sqlite3
            with sqlite3.connect(db.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                users = cursor.execute("SELECT * FROM users").fetchall()
                users = [dict(user) for user in users]
        
        if users:
            for user in users:
                print(f"  📝 用户ID: {user.get('id', 'N/A')}")
                print(f"     用户名: {user.get('username', 'N/A')}")
                print(f"     年级: {user.get('grade', 'N/A')}")
                print(f"     创建时间: {user.get('created_at', 'N/A')}")
                print()
        else:
            print("  ❌ 暂无用户数据")
        
        # 查看题目信息
        print("\n📚 题目信息:")
        print("-" * 30)
        try:
            import sqlite3
            with sqlite3.connect(db.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                questions = cursor.execute("SELECT * FROM questions LIMIT 5").fetchall()
                questions = [dict(q) for q in questions]
                
                if questions:
                    for i, question in enumerate(questions, 1):
                        print(f"  📝 题目 {i}:")
                        print(f"     ID: {question.get('id', 'N/A')}")
                        print(f"     标题: {question.get('title', 'N/A')}")
                        print(f"     学科: {question.get('subject', 'N/A')}")
                        print(f"     分类: {question.get('category', 'N/A')}")
                        print(f"     难度: {question.get('difficulty', 'N/A')}")
                        print()
                    
                    # 统计题目总数
                    total_count = cursor.execute("SELECT COUNT(*) FROM questions").fetchone()[0]
                    print(f"  📊 题目总数: {total_count}")
                else:
                    print("  ❌ 暂无题目数据")
        except Exception as e:
            print(f"  ❌ 查询题目失败: {e}")
        
        # 查看答题记录
        print("\n📈 答题记录:")
        print("-" * 30)
        try:
            import sqlite3
            with sqlite3.connect(db.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                records = cursor.execute("""
                    SELECT ah.*, u.username 
                    FROM answer_history ah 
                    JOIN users u ON ah.user_id = u.id 
                    ORDER BY ah.answer_time DESC 
                    LIMIT 5
                """).fetchall()
                records = [dict(r) for r in records]
                
                if records:
                    for i, record in enumerate(records, 1):
                        print(f"  📝 记录 {i}:")
                        print(f"     用户: {record.get('username', 'N/A')}")
                        print(f"     题目ID: {record.get('question_id', 'N/A')}")
                        print(f"     答案: {record.get('user_answer', 'N/A')[:50]}...")
                        print(f"     正确性: {'✅ 正确' if record.get('is_correct') else '❌ 错误'}")
                        print(f"     答题时间: {record.get('answer_time', 'N/A')}")
                        print()
                    
                    # 统计答题记录总数
                    total_records = cursor.execute("SELECT COUNT(*) FROM answer_history").fetchone()[0]
                    print(f"  📊 答题记录总数: {total_records}")
                else:
                    print("  ❌ 暂无答题记录")
        except Exception as e:
            print(f"  ❌ 查询答题记录失败: {e}")
        
        # 查看错题记录
        print("\n❌ 错题记录:")
        print("-" * 30)
        try:
            import sqlite3
            with sqlite3.connect(db.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                wrong_questions = cursor.execute("""
                    SELECT wq.*, u.username, q.title 
                    FROM wrong_questions wq 
                    JOIN users u ON wq.user_id = u.id 
                    LEFT JOIN questions q ON wq.question_id = q.id 
                    ORDER BY wq.last_wrong_time DESC 
                    LIMIT 5
                """).fetchall()
                wrong_questions = [dict(wq) for wq in wrong_questions]
                
                if wrong_questions:
                    for i, wrong in enumerate(wrong_questions, 1):
                        print(f"  📝 错题 {i}:")
                        print(f"     用户: {wrong.get('username', 'N/A')}")
                        print(f"     题目: {wrong.get('title', 'N/A')}")
                        print(f"     错误次数: {wrong.get('wrong_count', 'N/A')}")
                        print(f"     状态: {wrong.get('status', 'N/A')}")
                        print(f"     最后错误时间: {wrong.get('last_wrong_time', 'N/A')}")
                        print()
                    
                    # 统计错题总数
                    total_wrong = cursor.execute("SELECT COUNT(*) FROM wrong_questions").fetchone()[0]
                    print(f"  📊 错题总数: {total_wrong}")
                else:
                    print("  ❌ 暂无错题记录")
        except Exception as e:
            print(f"  ❌ 查询错题记录失败: {e}")
        
        # 查看数据库表结构
        print("\n🗄️ 数据库表结构:")
        print("-" * 30)
        try:
            import sqlite3
            with sqlite3.connect(db.db_path) as conn:
                cursor = conn.cursor()
                tables = cursor.execute("""
                    SELECT name FROM sqlite_master 
                    WHERE type='table' AND name NOT LIKE 'sqlite_%'
                """).fetchall()
                
                for table in tables:
                    table_name = table[0]
                    print(f"  📋 表名: {table_name}")
                    
                    # 获取表的列信息
                    columns = cursor.execute(f"PRAGMA table_info({table_name})").fetchall()
                    for col in columns:
                        print(f"     - {col[1]} ({col[2]})")
                    
                    # 获取记录数
                    count = cursor.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
                    print(f"     记录数: {count}")
                    print()
        except Exception as e:
            print(f"  ❌ 查询表结构失败: {e}")
        
    except Exception as e:
        print(f"❌ 数据库连接失败: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n🎉 数据查看完成！")

if __name__ == "__main__":
    main()