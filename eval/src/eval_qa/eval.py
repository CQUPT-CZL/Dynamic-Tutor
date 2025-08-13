from calendar import c
import json
import random
import requests
from datetime import datetime
import os
import time
from tqdm import tqdm
from fastapi import APIRouter, HTTPException, UploadFile, File

def load_test_data(file_path, num_samples=1, seed=42):
    """
    从JSON文件中随机选取指定数量的测试数据
    """
    random.seed(seed)
    
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 随机选取数据
    # 如果num_samples为负数,则按顺序选择前n条数据
    if num_samples < 0:
        selected_data = data[:abs(num_samples)]
    # 否则随机抽样
    else:
        selected_data = random.sample(data, min(num_samples, len(data)))
    return selected_data

def call_ai_diagnosis_api(question_text, user_answer):
    """
    调用AI诊断API
    """
    try:
        url = "https://xingchen-api.xf-yun.com/workflow/v1/chat/completions"
        
        input_text = question_text + "##" + user_answer + "##" + str(180)
        payload = json.dumps({
            "flow_id": "7347650620700119042",
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
            
        # print(f"✅ AI诊断内容: {content}")
        
        # 解析AI响应
        parts = content.split("##")
        if len(parts) < 3:
            print(f"❌ AI响应格式不正确，无法解析: {content}")
            raise HTTPException(status_code=500, detail="AI响应格式错误")
            
        is_correct = parts[0].strip().lower() == 'yes'
        reason = parts[1].strip()

        # 检查是否有评分部分
        if len(parts) >= 3 and parts[2].strip():
            try:
                # 尝试解析JSON评分数组
                scores_json = parts[2].strip()
                scores = json.loads(scores_json)
                # print(f"📊 解析评分数据: {scores}")
            except json.JSONDecodeError as e:
                print(f"⚠️ 评分数据解析失败: {e}")
                # 评分解析失败不影响主要结果
                pass
        
        result = {
            "is_correct": is_correct,
            "assessment_dimensions": scores,
            "overall_summary": reason,
        }
        return result
    except Exception as e:
        return {"error": str(e)}

def evaluate_diagnosis():
    """
    主评估函数
    """
    start_time = time.time()
    
    # 数据文件路径
    data_file = "../../eval_data/题目诊断/黄金测试集-题目诊断.json"
    
    # 检查文件是否存在
    if not os.path.exists(data_file):
        print(f"❌ 数据文件不存在: {data_file}")
        return
    
    print("📊 开始评估AI诊断功能")
    print(f"📁 数据文件: {data_file}")
    
    # 加载测试数据
    test_data = load_test_data(data_file, num_samples=-110, seed=42)
    print(f"✅ 成功加载 {len(test_data)} 条测试数据")
    print("\n🚀 开始处理数据...")
    
    # 存储结果
    results = []
    success_count = 0
    skip_count = 0
    
    # 使用进度条
    for item in tqdm(test_data, desc="📊 处理进度", unit="题"):
        question_text = item.get('题目', '')
        user_answer = item.get('解题过程', '')
        
        # 调用API
        api_result = call_ai_diagnosis_api(question_text, user_answer)
        
        # 如果调用失败，跳过这条数据
        if isinstance(api_result, dict) and "error" in api_result:
            skip_count += 1
            continue
        
        # 构建结果记录
        result_item = {
            "题号": item.get('题号'),
            "题目": question_text,
            "用户答案": user_answer,
            "标准答案": item.get('标准答案'),
            "用户提交答案": item.get('答案'),
            "原始正确性": item.get('is_correct_by_llm'),
            "api_调用结果": api_result,
            "调用时间": datetime.now().isoformat()
        }
        
        results.append(result_item)
        success_count += 1
    
    # 保存结果
    output_file = f"/Users/cuiziliang/Projects/unveiling-the-list/eval/eval_data/题目诊断/eval_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    # 计算运行时间
    end_time = time.time()
    runtime = end_time - start_time
    
    print(f"\n📄 评估结果已保存到: {output_file}")
    print(f"📈 总共处理了 {len(test_data)} 条数据")
    print(f"✅ 成功处理: {success_count} 条")
    print(f"⏭️ 跳过失败: {skip_count} 条")
    success_rate = success_count / len(test_data) * 100 if test_data else 0
    print(f"📊 成功率: {success_rate:.1f}%")
    print(f"⏱️ 总运行时间: {runtime:.2f} 秒")

if __name__ == "__main__":
    evaluate_diagnosis()