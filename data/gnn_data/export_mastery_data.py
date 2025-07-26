#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
📊 用户知识点掌握度数据导出工具

功能:
1. 从数据库中提取用户知识点掌握度数据
2. 导出为CSV格式文件
3. 打印详细的统计信息

输出格式:
user_id,node_id,mastery_score,username,node_name,node_difficulty,level
"""

import sqlite3
import csv
import os
from datetime import datetime
import pandas as pd

# 配置
DB_FILE = "../my_database.db"
OUTPUT_CSV = "user_mastery_data.csv"

def get_db_connection():
    """获取数据库连接"""
    if not os.path.exists(DB_FILE):
        raise FileNotFoundError(f"❌ 数据库文件 {DB_FILE} 不存在")
    
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def extract_mastery_data():
    """提取用户知识点掌握度数据 📈"""
    print("🚀 开始提取用户知识点掌握度数据...")
    print("=" * 60)
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # 查询掌握度数据，关联用户和知识点信息
        query = """
        SELECT
            unm.mastery_id,
            unm.user_id,
            unm.node_id,
            unm.mastery_score,
            u.username,
            kn.node_name,
            kn.node_difficulty,
            kn.level,
            kn.node_type
        FROM user_node_mastery unm
        JOIN users u ON unm.user_id = u.user_id
        JOIN knowledge_nodes kn ON unm.node_id = kn.node_id
        WHERE u.role = 'student'
        ORDER BY unm.user_id, unm.node_id
        """
        
        print("📊 执行数据查询...")
        cursor.execute(query)
        mastery_data = cursor.fetchall()
        
        if not mastery_data:
            print("⚠️ 没有找到掌握度数据")
            return []
        
        # 转换为字典列表
        data_list = [dict(row) for row in mastery_data]
        
        print(f"✅ 成功提取 {len(data_list)} 条掌握度记录")
        
        return data_list
        
    except Exception as e:
        print(f"❌ 数据提取失败: {str(e)}")
        raise
    finally:
        conn.close()

def print_statistics(data_list):
    """打印详细统计信息 📈"""
    if not data_list:
        return
    
    print("\n📊 数据统计信息:")
    print("=" * 60)
    
    # 转换为DataFrame便于分析
    df = pd.DataFrame(data_list)
    
    # 基本统计
    total_records = len(df)
    unique_users = df['user_id'].nunique()
    unique_nodes = df['node_id'].nunique()
    
    print(f"📋 基本信息:")
    print(f"   总记录数: {total_records:,}")
    print(f"   用户数量: {unique_users}")
    print(f"   知识点数量: {unique_nodes}")
    print(f"   平均每用户掌握度记录: {total_records/unique_users:.1f}")
    
    # 掌握度分布统计
    print(f"\n📈 掌握度分布:")
    mastery_stats = df['mastery_score'].describe()
    print(f"   最小值: {mastery_stats['min']:.3f}")
    print(f"   最大值: {mastery_stats['max']:.3f}")
    print(f"   平均值: {mastery_stats['mean']:.3f}")
    print(f"   中位数: {mastery_stats['50%']:.3f}")
    print(f"   标准差: {mastery_stats['std']:.3f}")
    
    # 掌握度等级分布
    print(f"\n🎯 掌握度等级分布:")
    excellent = len(df[df['mastery_score'] >= 0.8])
    good = len(df[(df['mastery_score'] >= 0.6) & (df['mastery_score'] < 0.8)])
    fair = len(df[(df['mastery_score'] >= 0.4) & (df['mastery_score'] < 0.6)])
    poor = len(df[df['mastery_score'] < 0.4])
    
    print(f"   🌟 优秀 (≥0.8): {excellent:,} ({excellent/total_records*100:.1f}%)")
    print(f"   👍 良好 (0.6-0.8): {good:,} ({good/total_records*100:.1f}%)")
    print(f"   📚 一般 (0.4-0.6): {fair:,} ({fair/total_records*100:.1f}%)")
    print(f"   📖 待提高 (<0.4): {poor:,} ({poor/total_records*100:.1f}%)")
    
    # 按用户统计
    print(f"\n👥 用户掌握度统计:")
    user_stats = df.groupby(['user_id', 'username']).agg({
        'mastery_score': ['count', 'mean', 'std'],
        'node_id': 'count'
    }).round(3)
    
    for (user_id, username), stats in user_stats.iterrows():
        count = int(stats[('mastery_score', 'count')])
        mean_score = stats[('mastery_score', 'mean')]
        std_score = stats[('mastery_score', 'std')]
        
        print(f"   👤 {username} (ID:{user_id}): {count}个知识点, 平均掌握度:{mean_score:.3f}, 标准差:{std_score:.3f}")
    
    # 按知识点类型统计
    if 'node_type' in df.columns:
        print(f"\n📚 知识点类型分布:")
        type_stats = df.groupby('node_type').agg({
            'mastery_score': ['count', 'mean'],
            'node_id': 'nunique'
        }).round(3)
        
        for node_type, stats in type_stats.iterrows():
            count = int(stats[('mastery_score', 'count')])
            mean_score = stats[('mastery_score', 'mean')]
            unique_nodes = int(stats[('node_id', 'nunique')])
            
            print(f"   📖 {node_type}: {unique_nodes}个知识点, {count}条记录, 平均掌握度:{mean_score:.3f}")
    
    # 按难度统计
    print(f"\n⭐ 知识点难度与掌握度关系:")
    # 将难度分组
    df['difficulty_group'] = pd.cut(df['node_difficulty'], 
                                   bins=[0, 0.3, 0.6, 1.0], 
                                   labels=['简单', '中等', '困难'])
    
    difficulty_stats = df.groupby('difficulty_group').agg({
        'mastery_score': ['count', 'mean'],
        'node_id': 'nunique'
    }).round(3)
    
    for difficulty, stats in difficulty_stats.iterrows():
        count = int(stats[('mastery_score', 'count')])
        mean_score = stats[('mastery_score', 'mean')]
        unique_nodes = int(stats[('node_id', 'nunique')])
        
        print(f"   {difficulty}: {unique_nodes}个知识点, {count}条记录, 平均掌握度:{mean_score:.3f}")

def export_to_csv(data_list, output_file):
    """导出数据到CSV文件 💾"""
    if not data_list:
        print("⚠️ 没有数据可导出")
        return False
    
    print(f"\n💾 导出数据到CSV文件: {output_file}")
    
    try:
        # 定义CSV字段
        fieldnames = [
            'mastery_id',
            'user_id', 'node_id', 'mastery_score', 
            'username', 'node_name', 'node_difficulty', 
            'level', 'node_type'
        ]
        
        with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            # 写入表头
            writer.writeheader()
            
            # 写入数据
            for row in data_list:
                writer.writerow(row)
        
        # 检查文件大小
        file_size = os.path.getsize(output_file)
        file_size_mb = file_size / (1024 * 1024)
        
        print(f"✅ CSV文件导出成功!")
        print(f"   文件路径: {os.path.abspath(output_file)}")
        print(f"   文件大小: {file_size_mb:.2f} MB")
        print(f"   记录数量: {len(data_list):,}")
        
        return True
        
    except Exception as e:
        print(f"❌ CSV导出失败: {str(e)}")
        return False

def validate_data_quality(data_list):
    """验证数据质量 🔍"""
    if not data_list:
        return
    
    print(f"\n🔍 数据质量检查:")
    print("-" * 40)
    
    df = pd.DataFrame(data_list)
    
    # 检查缺失值
    missing_data = df.isnull().sum()
    if missing_data.sum() > 0:
        print(f"⚠️ 发现缺失值:")
        for col, count in missing_data.items():
            if count > 0:
                print(f"   {col}: {count} 个缺失值")
    else:
        print(f"✅ 无缺失值")
    
    # 检查掌握度范围
    invalid_mastery = df[(df['mastery_score'] < 0) | (df['mastery_score'] > 1)]
    if len(invalid_mastery) > 0:
        print(f"⚠️ 发现 {len(invalid_mastery)} 个无效掌握度值 (不在0-1范围内)")
    else:
        print(f"✅ 掌握度值范围正常 (0-1)")
    
    # 检查重复记录
    duplicates = df.duplicated(subset=['user_id', 'node_id'])
    duplicate_count = duplicates.sum()
    if duplicate_count > 0:
        print(f"⚠️ 发现 {duplicate_count} 个重复的用户-知识点组合")
    else:
        print(f"✅ 无重复的用户-知识点组合")
    
    # 数据完整性检查
    print(f"\n📋 数据完整性:")
    print(f"   用户ID范围: {df['user_id'].min()} - {df['user_id'].max()}")
    print(f"   知识点ID范围: {df['node_id'].min()} - {df['node_id'].max()}")
    print(f"   掌握度范围: {df['mastery_score'].min():.3f} - {df['mastery_score'].max():.3f}")

def main():
    """主函数 🚀"""
    print("📊 用户知识点掌握度数据导出工具")
    print("=" * 60)
    print(f"⏰ 开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📁 数据库文件: {DB_FILE}")
    print(f"📄 输出文件: {OUTPUT_CSV}")
    
    try:
        # 1. 提取数据
        data_list = extract_mastery_data()
        
        if not data_list:
            print("\n❌ 没有数据可处理，程序退出")
            return
        
        # 2. 数据质量检查
        validate_data_quality(data_list)
        
        # 3. 打印统计信息
        print_statistics(data_list)
        
        # 4. 导出CSV
        success = export_to_csv(data_list, OUTPUT_CSV)
        
        if success:
            print(f"\n🎉 数据导出完成!")
            print(f"\n💡 使用建议:")
            print(f"   - 可以用Excel或其他工具打开CSV文件进行进一步分析")
            print(f"   - 数据可用于机器学习模型训练")
            print(f"   - 建议定期导出数据进行备份")
        else:
            print(f"\n❌ 数据导出失败")
        
    except Exception as e:
        print(f"\n❌ 程序执行失败: {str(e)}")
        import traceback
        traceback.print_exc()
    
    finally:
        print(f"\n⏰ 结束时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)

if __name__ == "__main__":
    main()