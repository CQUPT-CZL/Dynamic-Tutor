import sqlite3
import os
import random
import json # <<< 核心新增：导入json库用于转换字典为字符串
from tqdm import tqdm
from datetime import datetime

# --- 配置区 ---
DB_FILE = "my_database.db"
NUM_INTERACTIONS_PER_USER = 50

# --- 虚拟学生画像定义 ---
PERSONAS = {
    "小崔": {"name": "新手小崔", "base_accuracy": 0.5, "weakness": "knowledge"},
    "小陈": {"name": "聪明的马虎蛋小陈", "base_accuracy": 0.8, "weakness": "calculation"},
}

def get_db_connection():
    """获取数据库连接"""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def generate_mock_diagnosis(is_correct, persona, question_difficulty):
    """
    <<< 核心新增：根据答题结果和用户画像，生成一份模拟的诊断JSON >>>
    """
    if is_correct:
        # 如果回答正确，所有维度得分都很高
        scores = {
            "knowledge": round(random.uniform(0.8, 1.0), 2),
            "logic": round(random.uniform(0.8, 1.0), 2),
            "calculation": round(random.uniform(0.8, 1.0), 2),
            "behavior": round(random.uniform(0.7, 1.0), 2)
        }
        summary = "表现出色，完全掌握！"
    else:
        # 如果回答错误，根据学生的“弱点”来决定哪个维度分低
        scores = {
            "knowledge": round(random.uniform(0.5, 0.9), 2),
            "logic": round(random.uniform(0.6, 1.0), 2),
            "calculation": round(random.uniform(0.7, 1.0), 2),
            "behavior": round(random.uniform(0.3, 0.6), 2)
        }
        weakness = persona.get("weakness", "knowledge")
        if weakness == "knowledge":
            scores["knowledge"] = round(random.uniform(0.1, 0.4), 2)
            summary = "对核心概念的理解似乎还不够深入哦。"
        elif weakness == "calculation":
            scores["calculation"] = round(random.uniform(0.1, 0.4), 2)
            scores["logic"] = round(random.uniform(0.8, 1.0), 2) # 马虎蛋的逻辑通常很好
            summary = "思路完全正确，但在计算上出了点小差错。"
        else: # 默认情况
            scores["logic"] = round(random.uniform(0.2, 0.5), 2)
            summary = "解题的大方向上可能需要再思考一下。"

    # 组装成我们设计的JSON格式
    diagnosis_report = {
        "diagnosis_id": f"diag_mock_{int(datetime.now().timestamp())}_{random.randint(100,999)}",
        "is_correct": is_correct,
        "assessment_dimensions": [
            {"dimension": "知识掌握 (Knowledge Mastery)", "score": scores["knowledge"], "feedback": "模拟反馈..."},
            {"dimension": "解题逻辑 (Logical Reasoning)", "score": scores["logic"], "feedback": "模拟反馈..."},
            {"dimension": "计算准确性 (Calculation Accuracy)", "score": scores["calculation"], "feedback": "模拟反馈..."},
            {"dimension": "行为表现 (Behavioral Performance)", "score": scores["behavior"], "feedback": "模拟反馈..."}
        ],
        "overall_summary": summary
    }
    # 将Python字典转换为JSON字符串，以便存入数据库
    return json.dumps(diagnosis_report, ensure_ascii=False)


def simulate_user_learning():
    """主函数，模拟所有用户的学习过程，并填充动态数据表。"""
    if not os.path.exists(DB_FILE):
        print(f"❌ 错误: 数据库文件 '{DB_FILE}' 不存在。")
        return

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        print("🚀 开始模拟用户学习行为 (含多维度诊断)...")

        users = cursor.execute("SELECT user_id, username FROM users WHERE role = 'student'").fetchall()
        questions = cursor.execute("SELECT question_id, difficulty FROM questions").fetchall()
        
        if not questions:
            print("❌ 题库为空，无法进行模拟。")
            return

        q_to_n_map = {row['question_id']: [] for row in cursor.execute("SELECT DISTINCT question_id FROM question_to_node_mapping").fetchall()}
        for row in cursor.execute("SELECT question_id, node_id FROM question_to_node_mapping").fetchall():
            q_to_n_map[row['question_id']].append(row['node_id'])

        for user in tqdm(users, desc="模拟用户学习"):
            user_id = user['user_id']
            username = user['username']
            persona = PERSONAS.get(username, {"base_accuracy": 0.6, "weakness": "knowledge"})
            
            for _ in tqdm(range(NUM_INTERACTIONS_PER_USER), desc=f"  模拟'{username}'答题中", leave=False):
                question = random.choice(questions)
                question_id = question['question_id']
                question_difficulty = question['difficulty']

                accuracy_chance = persona['base_accuracy'] + (0.5 - question_difficulty) * 0.2
                is_correct = random.random() < accuracy_chance

                # <<< 核心修改 1：生成模拟的诊断JSON >>>
                diagnosis_json_str = generate_mock_diagnosis(is_correct, persona, question_difficulty)

                # <<< 核心修改 2：在INSERT语句中加入 diagnosis_json 字段 >>>
                cursor.execute(
                    """
                    INSERT INTO user_answers 
                    (user_id, question_id, is_correct, time_spent, confidence, diagnosis_json)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (
                        user_id, question_id, is_correct,
                        random.randint(30, 300), 
                        round(random.uniform(0.3, 1.0), 2),
                        diagnosis_json_str # 传入JSON字符串
                    )
                )

                if not is_correct:
                    cursor.execute(
                        """
                        INSERT INTO wrong_questions (user_id, question_id, last_wrong_time)
                        VALUES (?, ?, ?)
                        ON CONFLICT(user_id, question_id) DO UPDATE SET
                        wrong_count = wrong_count + 1,
                        last_wrong_time = excluded.last_wrong_time;
                        """,
                        (user_id, question_id, datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                    )

                related_nodes = q_to_n_map.get(question_id, [])
                for node_id in related_nodes:
                    cursor.execute("SELECT mastery_score FROM user_node_mastery WHERE user_id = ? AND node_id = ?", (user_id, node_id))
                    current_mastery_row = cursor.fetchone()
                    current_score = current_mastery_row['mastery_score'] if current_mastery_row else 0.0

                    if is_correct:
                        new_score = current_score + (1.0 - current_score) * 0.1
                    else:
                        new_score = current_score * 0.8
                    
                    new_score = round(new_score, 4)

                    cursor.execute(
                        "INSERT OR REPLACE INTO user_node_mastery (user_id, node_id, mastery_score) VALUES (?, ?, ?)",
                        (user_id, node_id, new_score)
                    )
        
        conn.commit()
        print("\n🎉🎉🎉 所有用户的学习行为模拟完成！")

    except Exception as e:
        print(f"\n❌ 发生严重错误: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == '__main__':
    simulate_user_learning()
