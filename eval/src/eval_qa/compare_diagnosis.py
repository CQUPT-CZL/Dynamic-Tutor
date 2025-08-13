import json
import os

def load_json_file(file_path):
    """加载JSON文件"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def compare_diagnosis_results():
    """比较两个诊断结果文件"""
    # 文件路径
    file1 = "/Users/cuiziliang/Projects/unveiling-the-list/eval/eval_data/题目诊断/解题进度_llm_langchain批改_过滤后v1.json"
    file2 = "/Users/cuiziliang/Projects/unveiling-the-list/eval/eval_data/题目诊断/eval_results_20250804_170903.json"
    
    # 检查文件是否存在
    if not os.path.exists(file1):
        print(f"❌ 文件不存在: {file1}")
        return
    if not os.path.exists(file2):
        print(f"❌ 文件不存在: {file2}")
        return
    
    # 加载数据
    data1 = load_json_file(file1)
    data2 = load_json_file(file2)
    
    # 获取数据列表
    if 'processed_data' in data1:
        items1 = data1['processed_data']
    else:
        items1 = data1
    
    items2 = data2
    
    print("📊 开始比较诊断结果")
    print(f"文件1数据量: {len(items1)}")
    print(f"文件2数据量: {len(items2)}")
    print("="*80)
    
    # 创建题号映射
    items1_dict = {item.get('题号'): item for item in items1}
    items2_dict = {item.get('题号'): item for item in items2}
    
    # 找到共同的题号
    common_ids = set(items1_dict.keys()) & set(items2_dict.keys())
    print(f"共同题号数量: {len(common_ids)}")
    print("="*80)
    

    num_true = 0
    false_questions = []
    for question_id in sorted(common_ids):
        item1 = items1_dict[question_id]
        item2 = items2_dict[question_id]
        
        # print(f"\n📝 题号: {question_id}")
        # print(f"题目: {item1.get('题目', '')[:50]}...")
        
        # 比较正确性判断
        correct1 = item1.get('is_correct_by_llm')
        if 'api_调用结果' in item2 and 'is_correct' in item2['api_调用结果']:
            correct2 = item2['api_调用结果']['is_correct']
        else:
            correct2 = None
        
        if correct1 != correct2:
            false_questions.append(question_id)
            continue
            
        # print(f"\n🎯 正确性判断比较:")
        # print(f"  文件1 (langchain): {correct1}")
        # print(f"  文件2 (api调用):   {correct2}")
        # print(f"  判断一致性: {'✅ 一致' if correct1 == correct2 else '❌ 不一致'}")
        
        # 比较四个维度评分
        # print(f"\n📊 四个维度评分比较:")
        
        # 获取文件1的评分
        scores1 = item1.get('detailed_scores_by_llm', [])
        scores1_dict = []
        for score in scores1:
            scores1_dict.append(score.get('score', 0))
            
        
        # 获取文件2的评分
        scores2_dict = []
        if 'api_调用结果' in item2 and 'assessment_dimensions' in item2['api_调用结果']:
            scores2 = item2['api_调用结果']['assessment_dimensions']
            for score in scores2:
                scores2_dict.append(score.get('score', 0))
        
        # 打印维度对比
        # print(f"  文件1 (langchain): {scores1_dict}")
        # print(f"  文件2 (api调用):   {scores2_dict}")
        # print("-" * 60)

        if abs(sum(scores1_dict) - sum(scores2_dict)) <= 0.8:
            num_true += 1
    
    print(f"做对百分比: {num_true / len(common_ids):.2%}")
    print(f"错误题号: {false_questions}")

if __name__ == "__main__":
    compare_diagnosis_results()