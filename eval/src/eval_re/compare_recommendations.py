#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
推荐结果比较分析脚本
比较分离后的AI推荐和规则推荐文件中每个用户的不同推荐算法结果
"""

import json
import os
from collections import defaultdict
import glob

def extract_target_content(recommendation_data):
    """
    从推荐数据中提取target内容
    """
    try:
        strategic_decision = recommendation_data.get('strategic_decision', {})
        target = strategic_decision.get('target')
        
        if isinstance(target, dict):
            return {
                'node_name': target.get('node_name', ''),
                'type': target.get('type', '')
            }
        elif isinstance(target, str):
            # 如果target是字符串，直接返回
            return {'node_name': target, 'type': ''}
        else:
            return None
    except Exception as e:
        print(f"提取target内容时出错: {e}")
        return None

def compare_target_consistency(rule_target, ai_target):
    """比较两个算法推荐的目标内容是否一致"""
    if rule_target is None or ai_target is None:
        return False, "缺少目标信息"
    
    if rule_target == ai_target:
        return True, f"完全一致: {rule_target}"
    else:
        return False, f"不一致: 规则推荐={rule_target}, AI推荐={ai_target}"

def compare_recommendations(ai_file_path, rule_file_path):
    """比较分离后的AI推荐和规则推荐文件中每个用户的不同推荐算法结果"""
    # 读取AI推荐文件
    with open(ai_file_path, 'r', encoding='utf-8') as f:
        ai_data = json.load(f)
    
    # 读取规则推荐文件
    with open(rule_file_path, 'r', encoding='utf-8') as f:
        rule_data = json.load(f)
    
    # 获取共同用户ID
    common_users = set(ai_data.keys()) & set(rule_data.keys())
    
    # 统计完全正确的用户数量
    fully_correct_count = 0
    correct_users = []
    incorrect_users = []
    
    for user_id in common_users:
        # 提取每个算法的mission_type
        mission_types = []
        rule_mission_type = 'N/A'
        ai_mission_type = 'N/A'
        
        # 处理规则推荐
        if (user_id in rule_data and 'rule_based_recommendation' in rule_data[user_id] and
            'strategic_decision' in rule_data[user_id]['rule_based_recommendation']):
            rule_mission_type = rule_data[user_id]['rule_based_recommendation']['strategic_decision'].get('mission_type', 'N/A')
            if rule_mission_type != 'N/A':
                mission_types.append(rule_mission_type)
        
        # 处理AI推荐
        if (user_id in ai_data and 'ai_recommendation' in ai_data[user_id] and
            'strategic_decision' in ai_data[user_id]['ai_recommendation']):
            ai_mission_type = ai_data[user_id]['ai_recommendation']['strategic_decision'].get('mission_type', 'N/A')
            if ai_mission_type != 'N/A':
                mission_types.append(ai_mission_type)
        
        # 获取target信息
        rule_target = None
        ai_target = None
        if user_id in rule_data and 'rule_based_recommendation' in rule_data[user_id]:
            rule_target = extract_target_content(rule_data[user_id]['rule_based_recommendation'])
        if user_id in ai_data and 'ai_recommendation' in ai_data[user_id]:
            ai_target = extract_target_content(ai_data[user_id]['ai_recommendation'])
        
        # 检查mission_type一致性
        if len(mission_types) == 2 and len(set(mission_types)) == 1:
            # mission_type一致，进一步比较target内容
            is_consistent, _ = compare_target_consistency(rule_target, ai_target)
            
            user_info = {
                'user_id': user_id,
                'mission_type': rule_mission_type,
                'rule_target': rule_target,
                'ai_target': ai_target
            }
            
            if is_consistent:
                fully_correct_count += 1
                correct_users.append(user_info)
            else:
                incorrect_users.append(user_info)
        else:
            # mission_type不一致
            user_info = {
                'user_id': user_id,
                'rule_mission_type': rule_mission_type,
                'ai_mission_type': ai_mission_type,
                'rule_target': rule_target,
                'ai_target': ai_target
            }
            incorrect_users.append(user_info)
    
    # 打印所有正确用户的信息
    print("✅ 完全正确的用户信息:")
    print("=" * 80)
    for user in sorted(correct_users, key=lambda x: int(x['user_id'])):
        print(f"用户 {user['user_id']}: {user['mission_type']} | 规则目标: {user['rule_target']} | AI目标: {user['ai_target']}")
    
    print(f"\n✅ 正确用户总数: {len(correct_users)} 个")
    
    # 打印所有错误用户的信息
    print("\n❌ 错误的用户信息:")
    print("=" * 80)
    for user in sorted(incorrect_users, key=lambda x: int(x['user_id'])):
        if 'mission_type' in user:
            # mission_type一致但target不一致
            print(f"用户 {user['user_id']}: {user['mission_type']} | 规则目标: {user['rule_target']} | AI目标: {user['ai_target']} [目标不一致]")
        else:
            # mission_type不一致
            print(f"用户 {user['user_id']}: 规则类型: {user['rule_mission_type']} | AI类型: {user['ai_mission_type']} | 规则目标: {user['rule_target']} | AI目标: {user['ai_target']} [类型不一致]")
    
    print(f"\n❌ 错误用户总数: {len(incorrect_users)} 个")
    
    # 计算完全正确的比例
    total_users = len(common_users)
    correct_percentage = (fully_correct_count / total_users * 100) if total_users > 0 else 0
    
    print(f"\n📊 完全正确比例: {fully_correct_count}/{total_users} = {correct_percentage:.1f}%")

def main():
    # 分离结果目录
    separated_dir = "/Users/cuiziliang/Projects/unveiling-the-list/eval/eval_data/推荐/分离结果"
    
    # 找到最新的AI推荐和规则推荐文件
    ai_files = glob.glob(os.path.join(separated_dir, "我们的系统推荐结果.json"))
    rule_files = glob.glob(os.path.join(separated_dir, "黄金测试集-推荐.json"))
    
    if not ai_files or not rule_files:
        print("❌ 未找到分离的推荐结果文件")
        return
    
    # 获取最新的文件
    latest_ai_file = max(ai_files, key=os.path.getctime)
    latest_rule_file = max(rule_files, key=os.path.getctime)
    
    # 比较推荐结果并直接打印
    compare_recommendations(latest_ai_file, latest_rule_file)

if __name__ == "__main__":
    main()