import pandas as pd
import time

def get_recommendation_for_user(user_id):
    """模拟为用户生成一个推荐任务"""
    if user_id == "小明":
        return {
            "mission_id": "M001",
            "reason": "根据你上次的练习，我们发现你对 **二次函数零点** 的概念有些混淆。",
            "type": "概念重学与练习",
            "content": {
                "concept_text": "函数零点的定义：对于函数y=f(x)，我们把使f(x)=0的实数x叫做这个函数的零点。",
                "question_text": "求函数 f(x) = x² - 5x + 6 的零点。",
                "question_id": "Q102"
            }
        }
    elif user_id == "小红":
        return {
            "mission_id": "M002",
            "reason": "你已经掌握了二次函数的基础性质，非常棒！我们来挑战一个新知识点吧！",
            "type": "新知探索",
            "content": {
                "concept_text": "函数最值的定义：函数在某个区间内的最大值或最小值。",
                "question_text": "求函数 f(x) = x² - 2x + 3 在区间 [0, 3] 上的最大值和最小值。",
                "question_id": "Q201"
            }
        }
    else:
        return {
            "mission_id": "M003",
            "reason": "让我们从一个基础题开始今天的学习吧！",
            "type": "基础练习",
            "content": {
                 "question_text": "判断函数 f(x) = x³ 的奇偶性。",
                 "question_id": "Q301"
            }
        }

def diagnose_answer(user_id, question_id, answer):
    """模拟诊断用户的答案"""
    if not answer:
        return {"status": "error", "message": "答案不能为空哦！"}
    # 模拟AI思考过程
    time.sleep(2) 
    if "x=2" in answer and "x=3" in answer:
        return {
            "status": "success",
            "diagnosis": "回答正确！你对因式分解法求解二次方程掌握得很扎实。",
            "next_recommendation": "建议你继续学习二次函数的图像性质。"
        }
    else:
        return {
            "status": "partial",
            "diagnosis": "答案不够完整。提示：可以尝试因式分解 x² - 5x + 6 = (x-2)(x-3)。",
            "hint": "当 (x-2)(x-3) = 0 时，x = 2 或 x = 3"
        }

def get_user_knowledge_map(user_id):
    """模拟获取用户的知识图谱掌握情况"""
    base_map = {
        "ECH_DY": {"name": "二次函数定义", "difficulty": 1},
        "ECH_TXXZ": {"name": "图像与性质", "difficulty": 3},
        "ECH_JXS": {"name": "三种解析式", "difficulty": 2},
        "ECH_ZZWT": {"name": "最值问题", "difficulty": 4},
        "ECH_GX": {"name": "与方程/不等式关系", "difficulty": 3}
    }
    
    user_progress = {
        "小明": {"ECH_GX": 0.4, "ECH_DY": 0.9},
        "小红": {"ECH_DY": 1.0, "ECH_TXXZ": 0.8, "ECH_JXS": 0.6},
        "小刚": {"ECH_DY": 0.3}
    }
    
    user_map = []
    for node_id, details in base_map.items():
        mastery = user_progress.get(user_id, {}).get(node_id, 0.0)
        user_map.append({
            "知识点ID": node_id,
            "知识点名称": details["name"],
            "难度": "⭐" * details["difficulty"],
            "我的掌握度": mastery
        })
    return pd.DataFrame(user_map)

def get_all_knowledge_nodes():
    """获取所有可用的知识节点"""
    return {
        "ECH_DY": "二次函数定义",
        "ECH_TXXZ": "图像与性质",
        "ECH_JXS": "三种解析式",
        "ECH_ZZWT": "最值问题",
        "ECH_GX": "与方程/不等式关系"
    }

def get_node_difficulty(node_id):
    """获取知识点难度"""
    difficulty_map = {
        "ECH_DY": 1,
        "ECH_TXXZ": 3,
        "ECH_JXS": 2,
        "ECH_ZZWT": 4,
        "ECH_GX": 3
    }
    return difficulty_map.get(node_id, 1)

def get_questions_for_node(node_id):
    """获取指定知识点的多个练习题"""
    questions = {
        "ECH_DY": [
            "请写出二次函数的一般式、顶点式和零点式。",
            "什么是二次函数？请举例说明。",
            "二次函数的定义域和值域分别是什么？"
        ],
        "ECH_TXXZ": [
            "函数 f(x) = -2(x-1)² + 5 的开口方向、对称轴和顶点坐标分别是什么？",
            "如何根据二次函数的解析式判断其图像的开口方向？",
            "二次函数 y = ax² + bx + c 的对称轴公式是什么？"
        ],
        "ECH_JXS": [
            "将二次函数 y = x² - 4x + 3 转换为顶点式。",
            "已知二次函数的顶点为(2, -1)，且过点(0, 3)，求其解析式。",
            "二次函数的三种解析式之间如何相互转换？"
        ],
        "ECH_ZZWT": [
            "求函数 f(x) = x² - 6x + 8 的最小值。",
            "在区间 [-1, 3] 上，函数 f(x) = x² - 2x + 5 的最值是多少？",
            "如何利用配方法求二次函数的最值？"
        ],
        "ECH_GX": [
            "二次函数 y = x² - 5x + 6 与 x 轴的交点坐标是什么？",
            "如何利用判别式判断二次函数与 x 轴的交点个数？",
            "解不等式 x² - 3x - 4 > 0。"
        ]
    }
    return questions.get(node_id, ["抱歉，暂未收录该知识点的题目。"])

def get_user_mastery(user_id, node_id):
    """获取用户对特定知识点的掌握度"""
    user_progress = {
        "小明": {"ECH_GX": 0.4, "ECH_DY": 0.9},
        "小红": {"ECH_DY": 1.0, "ECH_TXXZ": 0.8, "ECH_JXS": 0.6},
        "小刚": {"ECH_DY": 0.3}
    }
    return user_progress.get(user_id, {}).get(node_id, 0.0)