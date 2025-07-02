#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试数据库功能
"""

import os
import sys

# 添加backend路径
backend_path = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.append(backend_path)

from database import DatabaseManager

def test_database():
    """测试数据库基本功能"""
    print("🧪 测试数据库功能...")
    print("=" * 40)
    
    try:
        # 初始化数据库管理器
        db_manager = DatabaseManager()
        print("✅ 数据库管理器初始化成功")
        
        # 测试获取用户信息
        user_info = db_manager.get_user_by_username("小明")
        if user_info:
            print(f"✅ 获取用户信息成功：{user_info['name']}")
        else:
            print("⚠️ 未找到用户'小明'")
        
        # 测试获取题目
        questions = db_manager.get_questions_by_category("高中函数", "函数性质")
        print(f"✅ 获取题目成功，共 {len(questions)} 道题")
        
        # 测试获取错题
        wrong_questions = db_manager.get_user_wrong_questions("小明")
        print(f"✅ 获取错题成功，用户'小明'有 {len(wrong_questions)} 道错题")
        
        print("\n🎉 数据库功能测试完成！")
        return True
        
    except Exception as e:
        print(f"❌ 测试失败：{e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_database()
    sys.exit(0 if success else 1)