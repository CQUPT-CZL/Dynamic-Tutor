#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试前后端分离架构
验证API通信是否正常
"""

import requests
import json
import time
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from frontend.services.api_service import APIService

def test_backend_health():
    """测试后端健康检查"""
    print("🔍 测试后端健康检查...")
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 后端健康检查通过: {data}")
            return True
        else:
            print(f"❌ 后端健康检查失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 后端连接失败: {e}")
        return False

def test_api_service():
    """测试前端API服务"""
    print("\n🔍 测试前端API服务...")
    try:
        api_service = APIService()
        
        # 测试健康检查
        health = api_service.health_check()
        if health.get("status") == "healthy":
            print("✅ API服务健康检查通过")
        else:
            print(f"❌ API服务健康检查失败: {health}")
            return False
        
        # 测试获取用户列表
        users = api_service.get_users()
        if isinstance(users, list):
            print(f"✅ 获取用户列表成功: {len(users)} 个用户")
        else:
            print(f"❌ 获取用户列表失败: {users}")
            return False
        
        # 测试获取推荐
        if users:
            user_id = users[0]['username']
            recommendation = api_service.get_recommendation(user_id)
            if not recommendation.get("error"):
                print(f"✅ 获取用户推荐成功: {recommendation.get('type', '未知')}")
            else:
                print(f"❌ 获取用户推荐失败: {recommendation}")
                return False
        
        return True
    except Exception as e:
        print(f"❌ API服务测试失败: {e}")
        return False

def test_frontend_imports():
    """测试前端模块导入"""
    print("\n🔍 测试前端模块导入...")
    try:
        # 测试服务层导入
        from frontend.services import APIService, get_api_service
        print("✅ 服务层模块导入成功")
        
        # 测试页面模块导入
        from frontend.pages import (
            daily_tasks, free_practice, knowledge_map, 
            self_assessment, wrong_questions
        )
        print("✅ 页面模块导入成功")
        
        # 测试配置模块导入
        from frontend.config import init_session_state, render_user_selector
        print("✅ 配置模块导入成功")
        
        return True
    except Exception as e:
        print(f"❌ 前端模块导入失败: {e}")
        return False

def test_api_endpoints():
    """测试API端点"""
    print("\n🔍 测试API端点...")
    endpoints = [
        ("/", "GET", "API根路径"),
        ("/health", "GET", "健康检查"),
        ("/users", "GET", "用户列表"),
    ]
    
    success_count = 0
    for endpoint, method, description in endpoints:
        try:
            response = requests.request(method, f"http://localhost:8000{endpoint}", timeout=5)
            if response.status_code == 200:
                print(f"✅ {description} 测试通过")
                success_count += 1
            else:
                print(f"❌ {description} 测试失败: {response.status_code}")
        except Exception as e:
            print(f"❌ {description} 测试失败: {e}")
    
    return success_count == len(endpoints)

def main():
    """主测试函数"""
    print("🧪 前后端分离架构测试")
    print("=" * 50)
    
    # 等待后端启动
    print("⏳ 等待后端服务器启动...")
    for i in range(30):
        if test_backend_health():
            break
        time.sleep(1)
        print(f"  等待中... ({i+1}/30)")
    else:
        print("❌ 后端服务器启动超时")
        return False
    
    # 运行测试
    tests = [
        ("后端健康检查", test_backend_health),
        ("前端模块导入", test_frontend_imports),
        ("API端点测试", test_api_endpoints),
        ("前端API服务", test_api_service),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 运行测试: {test_name}")
        if test_func():
            passed += 1
            print(f"✅ {test_name} 通过")
        else:
            print(f"❌ {test_name} 失败")
    
    print("\n" + "=" * 50)
    print(f"📊 测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试通过！前后端分离架构工作正常")
        return True
    else:
        print("⚠️ 部分测试失败，请检查配置")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 