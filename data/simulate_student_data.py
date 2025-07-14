import sqlite3
import os
import random
from tqdm import tqdm
from datetime import datetime

# --- 配置区 ---
DB_FILE = "my_database.db"
NUM_INTERACTIONS_PER_USER = 50  # 为每个用户模拟50次答题行为

# --- 虚拟学生画像定义 ---
# 我们可以定义不同类型的学生，让生成的数据更逼真
PERSONAS = {
    "小崔": {"name": "新手小崔", "base_accuracy": 0.5, "type": "cautious"},
    "小陈": {"name": "学霸小陈", "base_accuracy": 0.8, "type": "confident"},
    "小胡": {"name": "教师胡老师", "base_accuracy": 0.95, "type": "expert"} # 也可以模拟老师答题
}

def get_db_connection():
    """获取数据库连接"""
    conn = sqlite3.connect(DB_FILE)
    # 使用Row工厂可以让查询结果像字典一样访问
    conn.row_factory = sqlite3.Row
    return conn

def simulate_user_learning():
    """
    主函数，模拟所有用户的学习过程，并填充动态数据表。
    """
    if not os.path.exists(DB_FILE):
        print(f"❌ 错误: 数据库文件 '{DB_FILE}' 不存在。请先运行初始化脚本。")
        return

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        print("🚀 开始模拟用户学习行为，生成动态数据...")

        # 1. 获取所有需要的基础数据
        users = cursor.execute("SELECT user_id, username FROM users WHERE role = 'student'").fetchall()
        questions = cursor.execute("SELECT question_id, difficulty FROM questions").fetchall()
        
        if not questions:
            print("❌ 题库为空，无法进行模拟。请先填充题目。")
            return

        # 创建一个 question_id -> [node_id, ...] 的映射，方便查询
        q_to_n_map = {}
        for row in cursor.execute("SELECT question_id, node_id FROM question_to_node_mapping").fetchall():
            if row['question_id'] not in q_to_n_map:
                q_to_n_map[row['question_id']] = []
            q_to_n_map[row['question_id']].append(row['node_id'])

        # 2. 为每个用户进行学习模拟
        for user in tqdm(users, desc="模拟用户学习"):
            user_id = user['user_id']
            username = user['username']
            persona = PERSONAS.get(username, {"base_accuracy": 0.6, "type": "normal"}) # 如果用户不在画像中，给个默认值
            
            print(f"\n--- 正在模拟 '{persona['name']}' 的学习过程 ---")

            for _ in tqdm(range(NUM_INTERACTIONS_PER_USER), desc=f"  答题中...", leave=False):
                # a. 随机选择一道题
                question = random.choice(questions)
                question_id = question['question_id']
                question_difficulty = question['difficulty']

                # b. 根据用户画像和题目难度，决定本次答题是否正确
                # 基础正确率 + (0.5 - 题目难度)的微调，难度越高越容易错
                accuracy_chance = persona['base_accuracy'] + (0.5 - question_difficulty) * 0.2
                is_correct = random.random() < accuracy_chance

                # c. 插入到 user_answers 表
                cursor.execute(
                    """
                    INSERT INTO user_answers (user_id, question_id, is_correct, time_spent, confidence)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        user_id, 
                        question_id, 
                        is_correct,
                        random.randint(30, 300), # 随机用时30-300秒
                        round(random.uniform(0.3, 1.0), 2) # 随机信心度
                    )
                )

                # d. 如果答错了，更新错题本
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

                # e. 更新相关知识点的掌握度 (user_node_mastery)
                related_nodes = q_to_n_map.get(question_id, [])
                for node_id in related_nodes:
                    # 获取当前掌握度
                    cursor.execute("SELECT mastery_score FROM user_node_mastery WHERE user_id = ? AND node_id = ?", (user_id, node_id))
                    current_mastery_row = cursor.fetchone()
                    current_score = current_mastery_row['mastery_score'] if current_mastery_row else 0.0

                    # 根据对错更新分数 (一个简单的模型)
                    if is_correct:
                        # 做对了，掌握度增加，越接近1增加越慢
                        new_score = current_score + (1.0 - current_score) * 0.1
                    else:
                        # 做错了，掌握度降低
                        new_score = current_score * 0.8
                    
                    new_score = round(new_score, 4) # 保留4位小数

                    # 使用 INSERT OR REPLACE 插入或更新掌握度记录
                    cursor.execute(
                        """
                        INSERT OR REPLACE INTO user_node_mastery (user_id, node_id, mastery_score)
                        VALUES (?, ?, ?)
                        """,
                        (user_id, node_id, new_score)
                    )
        
        # 提交所有更改
        conn.commit()
        print("\n🎉🎉🎉 所有用户的学习行为模拟完成！数据库已填充动态数据。")

    except Exception as e:
        print(f"\n❌ 发生严重错误: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == '__main__':
    simulate_user_learning()
