import sys
import os
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading



# 添加项目根目录到Python路径
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
sys.path.insert(0, project_root)

from backend.api.common.database import get_db_connection
from backend.api.student.recommendations.new_knowledge import get_current_module, get_next_learnable_node_in_module
import requests
import json
import time
from collections import defaultdict
from fastapi import HTTPException
from datetime import datetime

# --- 核心数据处理函数 ---
def get_user_profile_data(user_id: int, last_n: int = 30):
    """
    为指定用户提取并处理近期学习数据，生成分析摘要。
    """
    conn = get_db_connection()
    
    try:
        # 1. 查询近期答题记录，并JOIN上题目和知识点信息，最重要的是获取其高阶"领域"
        # 这个查询非常关键，它一次性获取了我们需要的所有原始信息
        sql = """
            -- 这是最终版的、能精确查找"章节"的查询
            -- 这个查询的目的是为了按"具体知识点"进行分组统计
            SELECT
                ua.is_correct,
                ua.diagnosis_json,
                kn.node_id,
                kn.node_name
            FROM
                user_answers AS ua
            JOIN
                question_to_node_mapping AS qnm ON ua.question_id = qnm.question_id
            JOIN
                knowledge_nodes AS kn ON qnm.node_id = kn.node_id
            WHERE
                ua.user_id = ? -- 筛选指定用户
            ORDER BY
                ua.timestamp DESC
            LIMIT ?; -- 限制分析最近的N条记录
        """
        recent_answers = conn.execute(sql, (user_id, last_n)).fetchall()
        # print(recent_answers)

        if not recent_answers:
            return {"message": "该用户尚无足够的学习记录进行分析。"}

        # 2. 在Python中进行分组和统计
        # defaultdict可以让我们方便地处理分组
        domain_stats = defaultdict(lambda: {
            "interaction_count": 0, 
            "correct_count": 0, 
            "scores": defaultdict(list)
        })

        for answer in recent_answers:
            node_id = answer['node_id']
            node_name = answer['node_name']
            # 使用知识点名称作为分组键
            if node_name not in domain_stats:
                domain_stats[node_name]["node_id"] = node_id
            domain_stats[node_name]["interaction_count"] += 1
            if answer['is_correct']:
                domain_stats[node_name]["correct_count"] += 1
            
            # 解析diagnosis_json来累加四个维度的分数
            if answer['diagnosis_json']:
                try:
                    diagnosis = json.loads(answer['diagnosis_json'])
                    # print(f"诊断数据: {diagnosis}")  # 打印诊断数据
                    for dim in diagnosis.get('assessment_dimensions', []):
                        dimension_name = dim['dimension'].split(' ')[0] # '知识掌握' -> '知识掌握'
                        domain_stats[node_name]["scores"][dimension_name].append(dim['score'])
                        # print(f"维度: {dimension_name}, 分数: {dim['score']}")  # 打印维度和分数
                except (json.JSONDecodeError, KeyError):
                    # print(f"JSON解析错误或缺少键: {answer['diagnosis_json']}")  # 打印错误信息
                    continue

        # 3. 格式化输出，计算平均分
        analysis_by_domain = []
        total_interactions = len(recent_answers)
        total_correct = sum(1 for ans in recent_answers if ans['is_correct'])

        for domain, stats in domain_stats.items():
            avg_scores = {}
            for dim_name, score_list in stats["scores"].items():
                # print(f"维度: {dim_name}, 所有分数: {score_list}")
                avg_scores[dim_name] = round(sum(score_list) / len(score_list), 2) if score_list else 0.0

            analysis_by_domain.append({
                "node_id": stats["node_id"],  # 添加node_id
                "node_name": domain,  # 更改字段名以反映这是知识点名称而非领域名称
                "interaction_count": stats["interaction_count"],
                "accuracy": round(stats["correct_count"] / stats["interaction_count"], 2),
                "average_scores": avg_scores
            })

        # 4. 组装成最终的、将要发送给画像分析师Agent的JSON
        # print(final_payload)
        final_payload = {
            "user_id": user_id,
            "analysis_window": total_interactions,
            "overall_recent_accuracy": round(total_correct / total_interactions, 2),
            "analysis_by_node": analysis_by_domain  # 更新字段名以反映这是按知识点分析而非领域
        }
        # print(final_payload)
        
        return final_payload

    except Exception as e:
        print(f"处理用户{user_id}的数据时出错: {e}")
        raise
    finally:
        conn.close()


def get_knowledge_nodes():
    """获取所有知识节点"""
    try:
        conn = get_db_connection()
        cursor = conn.execute("SELECT node_id, node_name, node_difficulty, node_type FROM knowledge_nodes")
        
        nodes = {}
        for row in cursor.fetchall():
            if row['node_type'] != '模块':
                nodes[row["node_id"]] = row["node_name"]
        # print(nodes.values())
        conn.close()
        return nodes.values()
    except Exception as e:
        print(e)


def get_knowledge_map(user_id: str):
    """获取用户知识图谱和模块学习进度"""
    try:
        # 模块顺序定义
        MODULE_ORDER = [
            "概率论的基本概念",
            "概率运算进阶", 
            "随机变量及其分布",
            "数字特征与关系",
            "极限定理",
            "数理统计"
        ]
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 获取用户掌握度数据
        cursor.execute("""
            SELECT 
                kn.node_id,
                kn.node_name,
                kn.node_difficulty,
                kn.level,
                COALESCE(unm.mastery_score, 0.0) as mastery_score
            FROM knowledge_nodes kn
            LEFT JOIN user_node_mastery unm ON kn.node_id = unm.node_id AND unm.user_id = ?
            WHERE kn.node_type != '模块'
            ORDER BY kn.node_id
        """, (user_id,))
        
        all_nodes = cursor.fetchall()
        user_mastery = {str(row['node_id']): row['mastery_score'] for row in all_nodes}
        
        # 构建模块信息字典
        modules_info = {}
        completed_modules = []
        current_module = None
        current_module_info = None
        
        for module_name in MODULE_ORDER:
            # 获取模块包含的所有节点
            cursor.execute("""
                SELECT target_node_id as node_id, target_kn.node_name
                FROM knowledge_edges ke
                JOIN knowledge_nodes kn ON ke.source_node_id = kn.node_id
                JOIN knowledge_nodes target_kn ON ke.target_node_id = target_kn.node_id
                WHERE kn.node_name = ? AND ke.relation_type = '包含'
            """, (module_name,))
            
            module_nodes = cursor.fetchall()
            if not module_nodes:
                continue
                
            # 统计模块内节点的掌握情况
            mastered_nodes = []
            unmastered_nodes = []
            
            for node in module_nodes:
                node_id_str = str(node['node_id'])
                mastery_score = user_mastery.get(node_id_str, 0.0)
                
                if mastery_score >= 0.8:
                    mastered_nodes.append(node['node_name'])
                else:
                    unmastered_nodes.append(node['node_name'])
            
            # 判断模块是否完成
            is_completed = len(unmastered_nodes) == 0
            
            modules_info[module_name] = {
                'mastered_nodes': mastered_nodes,
                'unmastered_nodes': unmastered_nodes,
                'is_completed': is_completed,
                'total_nodes': len(module_nodes),
                'mastered_count': len(mastered_nodes)
            }
            
            if is_completed:
                completed_modules.append(module_name)
            elif current_module is None:  # 第一个未完成的模块就是当前学习模块
                current_module = module_name
                current_module_info = modules_info[module_name]
        
        # 构建自然语言描述
        description_parts = []
        
        # 已完成的模块
        if completed_modules:
            description_parts.append(f"用户已经完成了{len(completed_modules)}个模块的学习：{', '.join(completed_modules)}")
        else:
            description_parts.append("用户尚未完成任何模块的学习")
        
        # 当前学习模块
        if current_module and current_module_info:
            mastered_str = f"已掌握{len(current_module_info['mastered_nodes'])}个知识点" if current_module_info['mastered_nodes'] else "尚未掌握任何知识点"
            unmastered_str = f"还需学习{len(current_module_info['unmastered_nodes'])}个知识点" if current_module_info['unmastered_nodes'] else "已完成所有知识点"
            
            description_parts.append(f"目前正在学习'{current_module}'模块，{mastered_str}，{unmastered_str}")
            
            if current_module_info['mastered_nodes']:
                description_parts.append(f"已掌握的知识点包括：{', '.join(current_module_info['mastered_nodes'])}")
            
            if current_module_info['unmastered_nodes']:
                description_parts.append(f"待学习的知识点包括：{', '.join(current_module_info['unmastered_nodes'])}")
        else:
            description_parts.append("恭喜！用户已完成所有模块的学习")
        
        natural_language_description = "。".join(description_parts) + "。"
        # print(natural_language_description)
        
        # 返回原有的已掌握知识点列表（保持兼容性）和新增的模块信息
        mastered_knowledge_list = [row['node_name'] for row in all_nodes if row['mastery_score'] > 0.8]
        
        conn.close()
        
        # 返回包含模块信息的字典
        return {
            'mastered_knowledge_list': mastered_knowledge_list,  # 原有格式，保持兼容性
            'modules_info': modules_info,
            'natural_language_description': natural_language_description,
            'completed_modules': completed_modules,
            'current_module': current_module
        }
        
    except Exception as e:
        print(f"获取知识图谱时出错: {e}")
        return []

def get_users():
    """获取用户列表"""
    try:
        conn = get_db_connection()
        cursor = conn.execute("SELECT user_id, username, role FROM users")
        # 只返回角色为学生的用户
        users = [{"user_id": row["user_id"], "username": row["username"], "role": row["role"]} 
                for row in cursor.fetchall() 
                if row["role"] == "student"]
        conn.close()
        return users
    except Exception as e:
        print(e)


# --- AI API调用函数 ---
def call_ai_re_api(profile_data):
    """
    这是我们系统的推荐算法
    
    Args:
        profile_data (dict): 用户学习数据分析结果
        
    Returns:
        tuple: (decision_reasoning, strategic_decision) 诊断理由和策略决策
        
    Raises:
        HTTPException: 当API调用失败时抛出异常
    """
    # print(f"🤖 开始调用AI推荐API")      
    
    url = "https://xingchen-api.xf-yun.com/workflow/v1/chat/completions"
    
    payload = json.dumps({
    "flow_id": "7352207588747141122",
    "parameters": {
        "AGENT_USER_INPUT": json.dumps(profile_data),
    },
    "ext": {
        "bot_id": "workflow",
        "caller": "workflow"
    },
    "stream": False,
    })
    headers = {
    'Authorization': 'Bearer 4cec7267c3353726a2f1656cb7c0ec37:NDk0MDk0N2JiYzg0ZTgxMzVlNmRkM2Fh',
    'Content-Type': 'application/json',
    'Accept': '*/*',
    'Host': 'xingchen-api.xf-yun.com',
    'Connection': 'keep-alive'
    }
    
    # print(f"🌐 发送API请求到: {url}")
    response = requests.request("POST", url, headers=headers, data=payload).json()
    # print("📨 AI API响应成功")
    
    # 检查响应是否成功
    if 'choices' not in response or not response['choices'] or 'delta' not in response['choices'][0]:
        print("❌ AI API响应格式错误")
        raise HTTPException(status_code=500, detail="AI生成学习目标失败：响应格式错误")
        
    content = response['choices'][0]['delta'].get('content')
    if not content:
        print("❌ AI API返回内容为空")
        raise HTTPException(status_code=500, detail="AI诊断失败")

    decision_reasoning = content.split('##')[0]
    strategic_decision = json.loads(content.split('##')[1])

    mission_type = strategic_decision.get('mission_type')

    if mission_type == "NEW_KNOWLEDGE":
        conn = get_db_connection()
        cursor = conn.cursor()
        module_name = get_current_module(cursor, profile_data['user_id'])
        strategic_decision['target']['type'] = get_next_learnable_node_in_module(cursor, profile_data['user_id'], module_name)
        conn.close()
    
    # print(f"✅ AI推荐内容: {content}")
    
    return {
        "decision_reasoning": decision_reasoning,
        "strategic_decision": strategic_decision
    }


def call_re_api(input_text):
    """
    调用AI推荐API
    """
    try:
        url = "https://xingchen-api.xf-yun.com/workflow/v1/chat/completions"
        
        payload = json.dumps({
            "flow_id": "7357270047910617090",
            "parameters": {
                "AGENT_USER_INPUT": input_text,
            },
            "ext": {
                "bot_id": "workflow",
                "caller": "workflow"
            },
            "stream": False,
        })
        headers = {
            'Authorization': 'Bearer 4cec7267c3353726a2f1656cb7c0ec37:NDk0MDk0N2JiYzg0ZTgxMzVlNmRkM2Fh',
            'Content-Type': 'application/json',
            'Accept': '*/*',
            'Host': 'xingchen-api.xf-yun.com',
            'Connection': 'keep-alive'
        }
        
        response = requests.request("POST", url, headers=headers, data=payload).json()
        
        # 检查响应是否成功
        if 'choices' not in response or not response['choices'] or 'delta' not in response['choices'][0]:
            return {"error": "AI API响应格式错误"}
            
        content = response['choices'][0]['delta'].get('content')
        # print(content)

        if not content:
            print("❌ AI API返回内容为空")
            raise HTTPException(status_code=500, detail="AI诊断失败")
        decision_reasoning = content.split('##')[0]
        strategic_decision = json.loads(content.split('##')[1])
            
        return {
            "decision_reasoning": decision_reasoning,
            "strategic_decision": strategic_decision
        }
    except Exception as e:
        return {"error": str(e)}


def process_user(user, nodes):
    """处理单个用户的评估任务"""
    try:
        user_id = user["user_id"]

        if user_id < 50:
            return None

        knowledge_map_data = get_knowledge_map(user_id)
        
        user_profile = get_user_profile_data(user_id, last_n=20)
        
        # 使用自然语言描述和已掌握知识点列表构建输入文本
        if isinstance(knowledge_map_data, dict):
            natural_description = knowledge_map_data.get('natural_language_description', '')
            mastered_list = knowledge_map_data.get('mastered_knowledge_list', [])
            
            # 构建更丰富的输入文本
            # knowledge_info = f"学习进度描述：{natural_description}\n已掌握知识点：{mastered_list}"
            input_text = str(user_profile) + "##" + natural_description
            
            if len(mastered_list) == 0:
                input_text = str(user_profile) + "##" + "用户未学习任何知识点"
        else:
            # 兼容旧格式（如果返回的是列表）
            input_text = str(user_profile) + "##" + natural_description
            if len(knowledge_map_data) == 0:
                input_text = str(user_profile) + "##" + "用户未学习任何知识点" + "##" + str(nodes)

        # 获取两个API的结果
        result_re = call_re_api(input_text)
        # result_multi_re = call_multi_re_api(input_text)
        result_ai_re = call_ai_re_api(user_profile)
        
        # 返回用户结果
        return user_id, {
            'prompt': input_text,
            "rule_based_recommendation": result_re,
            # "multi_expert_recommendation": result_multi_re,
            "ai_recommendation": result_ai_re
        }
    except Exception as e:
        print(f"❌ 处理用户 {user['user_id']} 时出错: {e}")
        return user['user_id'], {"error": str(e)}


def main():
    users = get_users()
    nodes = get_knowledge_nodes()
    
    print(f"🚀 开始并行处理 {len(users)} 个用户的评估任务...")
    
    # 创建输出文件路径
    output_file = f"/Users/cuiziliang/Projects/unveiling-the-list/eval/eval_data/推荐/eval_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    # 初始化JSON文件
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("{\n")
    
    # 创建文件写入锁
    file_lock = threading.Lock()
    
    # 统计变量
    success_count = 0
    error_count = 0
    processed_count = 0
    
    # 使用线程池进行并行处理
    max_workers = min(2, len(users))  # 最多2个并发线程，避免过多请求
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # 提交所有任务
        future_to_user = {executor.submit(process_user, user, nodes): user for user in users}
        
        # 使用tqdm显示进度
        with tqdm(total=len(users), desc="🔄 处理用户评估") as pbar:
            for future in as_completed(future_to_user):
                user = future_to_user[future]
                result = future.result()
                if result is None:
                    continue
                try:
                    user_id, result = future.result()
                    
                    # 立即写入文件（线程安全）
                    with file_lock:
                        with open(output_file, "a", encoding="utf-8") as f:
                            # 如果不是第一个用户，添加逗号
                            if processed_count > 0:
                                f.write(",\n")
                            # 写入用户结果
                            f.write(f'  "{user_id}": {json.dumps(result, ensure_ascii=False, indent=2).replace(chr(10), chr(10) + "  ")}')
                        
                        processed_count += 1
                        if 'error' not in result:
                            success_count += 1
                        else:
                            error_count += 1
                    
                    pbar.set_postfix({"当前用户": user['username'], "已完成": processed_count})
                    
                except Exception as e:
                    print(f"❌ 用户 {user['username']} 处理失败: {e}")
                    error_result = {"error": str(e)}
                    
                    # 立即写入错误结果（线程安全）
                    with file_lock:
                        with open(output_file, "a", encoding="utf-8") as f:
                            # 如果不是第一个用户，添加逗号
                            if processed_count > 0:
                                f.write(",\n")
                            # 写入错误结果
                            f.write(f'  "{user["user_id"]}": {json.dumps(error_result, ensure_ascii=False, indent=2).replace(chr(10), chr(10) + "  ")}')
                        
                        processed_count += 1
                        error_count += 1
                    
                finally:
                    pbar.update(1)
    
    # 完成JSON文件
    with open(output_file, "a", encoding="utf-8") as f:
        f.write("\n}")
        
    print(f"✅ 并行处理完成！结果已保存到 {output_file}")
    print(f"📊 成功处理: {success_count} 个用户")
    print(f"❌ 处理失败: {error_count} 个用户")
    print(f"📁 总计处理: {processed_count} 个用户")


if __name__ == "__main__":
    main()
