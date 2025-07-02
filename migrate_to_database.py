#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据迁移脚本：将JSON数据迁移到SQLite数据库

使用方法：
    python migrate_to_database.py
"""

import os
import sys
from pathlib import Path
import asyncio

# 添加backend路径
backend_path = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.append(backend_path)

# 设置事件循环策略，避免事件循环关闭错误
if sys.platform.startswith('win'):
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
else:
    try:
        import uvloop
        asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    except ImportError:
        pass

from backend.database import DatabaseManager

def main():
    """主函数：执行数据迁移"""
    print("🚀 开始数据迁移到SQLite数据库...")
    print("=" * 50)
    
    # 检查JSON文件是否存在
    questions_file = "data/questions.json"
    user_progress_file = "data/user_progress.json"
    
    if not os.path.exists(questions_file):
        print(f"❌ 错误：找不到题目数据文件 {questions_file}")
        return False
    
    if not os.path.exists(user_progress_file):
        print(f"❌ 错误：找不到用户进度文件 {user_progress_file}")
        return False
    
    print(f"✅ 找到数据文件：")
    print(f"   📚 题目数据：{questions_file}")
    print(f"   👤 用户数据：{user_progress_file}")
    print()
    
    try:
        # 初始化数据库管理器
        print("🔧 初始化数据库...")
        db_manager = DatabaseManager()
        
        # 执行数据迁移
        print("📦 开始迁移数据...")
        db_manager.migrate_from_json(questions_file, user_progress_file)
        
        print()
        print("🎉 数据迁移完成！")
        print("=" * 50)
        print("📊 数据库信息：")
        print(f"   📁 数据库文件：{db_manager.db_path}")
        print(f"   📈 数据库大小：{get_file_size(db_manager.db_path)}")
        
        # 显示迁移统计
        show_migration_stats(db_manager)
        
        print()
        print("💡 提示：")
        print("   - 原JSON文件已保留，可以作为备份")
        print("   - 应用现在将使用SQLite数据库")
        print("   - 可以删除JSON文件以节省空间（建议先备份）")
        
        return True
        
    except Exception as e:
        print(f"❌ 迁移过程中出错：{e}")
        import traceback
        traceback.print_exc()
        return False

def get_file_size(file_path):
    """获取文件大小的友好显示"""
    try:
        size = os.path.getsize(file_path)
        if size < 1024:
            return f"{size} B"
        elif size < 1024 * 1024:
            return f"{size / 1024:.1f} KB"
        else:
            return f"{size / (1024 * 1024):.1f} MB"
    except:
        return "未知"

def show_migration_stats(db_manager):
    """显示迁移统计信息"""
    try:
        import sqlite3
        
        with sqlite3.connect(db_manager.db_path) as conn:
            cursor = conn.cursor()
            
            # 统计各表的记录数
            tables = [
                ('用户', 'users'),
                ('学科', 'subjects'),
                ('知识点分类', 'knowledge_categories'),
                ('题目', 'questions'),
                ('用户进度', 'user_progress'),
                ('答题历史', 'answer_history'),
                ('错题集', 'wrong_questions'),
                ('学习统计', 'learning_stats')
            ]
            
            print("   📋 数据统计：")
            for name, table in tables:
                count = cursor.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
                print(f"      {name}：{count} 条记录")
                
    except Exception as e:
        print(f"   ⚠️ 无法获取统计信息：{e}")

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)