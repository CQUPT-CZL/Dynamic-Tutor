#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API测试脚本
测试后端API的各项功能
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_health():
    """测试健康检查"""
    print("🔍 测试健康检查...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 健康检查通过: {data}")
            return True
        else:
            print(f"❌ 健康检查失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 健康检查异常: {e}")
        return False

def test_users():
    """测试用户列表"""
    print("\n🔍 测试用户列表...")
    try:
        response = requests.get(f"{BASE_URL}/users")
        if response.status_code == 200:
            users = response.json()
            print(f"✅ 获取用户列表成功: {len(users)} 个用户")
            for user in users:
                print(f"   - {user['username']} (ID: {user['user_id']})")
            return True
        else:
            print(f"❌ 获取用户列表失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 获取用户列表异常: {e}")
        return False

def test_knowledge_map():
    """测试知识图谱"""
    print("\n🔍 测试知识图谱...")
    try:
        response = requests.get(f"{BASE_URL}/knowledge-map/1")
        if response.status_code == 200:
            knowledge_map = response.json()
            print(f"✅ 获取知识图谱成功: {len(knowledge_map)} 个知识点")
            for node in knowledge_map[:3]:  # 只显示前3个
                print(f"   - {node['node_name']} (掌握度: {node['mastery']:.1%})")
            return True
        else:
            print(f"❌ 获取知识图谱失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 获取知识图谱异常: {e}")
        return False

def test_questions():
    """测试练习题"""
    print("\n🔍 测试练习题...")
    try:
        response = requests.get(f"{BASE_URL}/questions/二次函数")
        if response.status_code == 200:
            data = response.json()
            questions = data.get("questions", [])
            print(f"✅ 获取练习题成功: {len(questions)} 道题")
            if questions:
                print(f"   示例题目: {questions[0][:50]}...")
            return True
        else:
            print(f"❌ 获取练习题失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 获取练习题异常: {e}")
        return False

def test_diagnosis():
    """测试答案诊断"""
    print("\n🔍 测试答案诊断...")
    try:
        data = {
            "user_id": "1",
            "question_id": "1",
            "answer": "最小值为-4，当x=-1时取得",
            "answer_type": "text",
            "time_spent": 120,
            "confidence": 0.8
        }
        response = requests.post(f"{BASE_URL}/diagnose", json=data)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 答案诊断成功: {result['diagnosis']}")
            return True
        else:
            print(f"❌ 答案诊断失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 答案诊断异常: {e}")
        return False

def test_stats():
    """测试用户统计"""
    print("\n🔍 测试用户统计...")
    try:
        response = requests.get(f"{BASE_URL}/stats/1")
        if response.status_code == 200:
            stats = response.json()
            print(f"✅ 获取用户统计成功:")
            print(f"   - 今日答题: {stats.get('total_questions_answered', 0)} 题")
            print(f"   - 正确率: {stats.get('correct_rate', 0):.1%}")
            print(f"   - 学习时长: {stats.get('study_time_today', 0)} 分钟")
            return True
        else:
            print(f"❌ 获取用户统计失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 获取用户统计异常: {e}")
        return False

def test_wrong_questions():
    """测试错题集"""
    print("\n🔍 测试错题集...")
    try:
        response = requests.get(f"{BASE_URL}/wrong-questions/1")
        if response.status_code == 200:
            data = response.json()
            wrong_questions = data.get("wrong_questions", [])
            print(f"✅ 获取错题集成功: {len(wrong_questions)} 道错题")
            return True
        else:
            print(f"❌ 获取错题集失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 获取错题集异常: {e}")
        return False

def main():
    """主测试函数"""
    print("🧪 API功能测试")
    print("=" * 50)
    
    # 等待后端启动
    print("⏳ 等待后端服务器启动...")
    for i in range(30):
        if test_health():
            break
        time.sleep(1)
        print(f"  等待中... ({i+1}/30)")
    else:
        print("❌ 后端服务器启动超时")
        return False
    
    # 运行测试
    tests = [
        ("健康检查", test_health),
        ("用户列表", test_users),
        ("知识图谱", test_knowledge_map),
        ("练习题", test_questions),
        ("答案诊断", test_diagnosis),
        ("用户统计", test_stats),
        ("错题集", test_wrong_questions),
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
        print("🎉 所有API测试通过！")
        return True
    else:
        print("⚠️ 部分API测试失败，请检查后端服务")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1) 