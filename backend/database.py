import sqlite3
import json
import os
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional

# 获取日志记录器
logger = logging.getLogger('database')

class DatabaseManager:
    """SQLite数据库管理类"""
    
    def __init__(self, db_path: str = "data/learning_platform.db"):
        self.db_path = db_path
        logger.info(f"🗄️ 初始化数据库管理器，数据库路径: {db_path}")
        self.init_database()
    
    def init_database(self):
        """初始化数据库，创建所有必要的表"""
        logger.info("📋 开始初始化数据库表结构")
        # 确保数据目录存在
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        logger.info(f"📁 数据目录已确保存在: {os.path.dirname(self.db_path)}")
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # 创建用户表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    name TEXT NOT NULL,
                    grade TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_login TIMESTAMP
                )
            """)
            
            # 创建学科表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS subjects (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    description TEXT
                )
            """)
            
            # 创建知识点分类表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS knowledge_categories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    subject_id INTEGER NOT NULL,
                    name TEXT NOT NULL,
                    description TEXT,
                    FOREIGN KEY (subject_id) REFERENCES subjects (id),
                    UNIQUE(subject_id, name)
                )
            """)
            
            # 创建题目表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS questions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    question_id TEXT UNIQUE NOT NULL,
                    category_id INTEGER NOT NULL,
                    question_text TEXT NOT NULL,
                    question_type TEXT NOT NULL,
                    options TEXT,  -- JSON格式存储选项
                    correct_answer TEXT NOT NULL,
                    difficulty TEXT NOT NULL,
                    knowledge_points TEXT,  -- JSON格式存储知识点列表
                    explanation TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (category_id) REFERENCES knowledge_categories (id)
                )
            """)
            
            # 创建用户学习进度表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_progress (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    category_id INTEGER NOT NULL,
                    mastery_level REAL DEFAULT 0.0,
                    correct_count INTEGER DEFAULT 0,
                    total_attempts INTEGER DEFAULT 0,
                    last_study_time TIMESTAMP,
                    weak_points TEXT,  -- JSON格式存储薄弱点
                    FOREIGN KEY (user_id) REFERENCES users (id),
                    FOREIGN KEY (category_id) REFERENCES knowledge_categories (id),
                    UNIQUE(user_id, category_id)
                )
            """)
            
            # 创建答题历史表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS answer_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    question_id TEXT NOT NULL,
                    user_answer TEXT NOT NULL,
                    correct_answer TEXT NOT NULL,
                    is_correct BOOLEAN NOT NULL,
                    answer_time TIMESTAMP NOT NULL,
                    time_spent INTEGER,  -- 答题用时（秒）
                    answer_type TEXT DEFAULT 'text',  -- 'text' 或 'image'
                    confidence REAL,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            """)
            
            # 创建错题集表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS wrong_questions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    question_id TEXT NOT NULL,
                    wrong_count INTEGER DEFAULT 1,
                    first_wrong_time TIMESTAMP NOT NULL,
                    last_wrong_time TIMESTAMP NOT NULL,
                    status TEXT DEFAULT '未掌握',  -- '未掌握', '已掌握', '需复习'
                    FOREIGN KEY (user_id) REFERENCES users (id),
                    UNIQUE(user_id, question_id)
                )
            """)
            
            # 创建学习统计表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS learning_stats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    total_study_time INTEGER DEFAULT 0,  -- 总学习时间（秒）
                    total_questions_attempted INTEGER DEFAULT 0,
                    total_correct INTEGER DEFAULT 0,
                    accuracy_rate REAL DEFAULT 0.0,
                    current_streak INTEGER DEFAULT 0,  -- 当前连续正确数
                    best_streak INTEGER DEFAULT 0,  -- 最佳连续正确数
                    favorite_topics TEXT,  -- JSON格式存储喜欢的主题
                    study_days INTEGER DEFAULT 0,  -- 学习天数
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id),
                    UNIQUE(user_id)
                )
            """)
            
            conn.commit()
    
    def migrate_from_json(self, questions_file: str, user_progress_file: str):
        """从JSON文件迁移数据到SQLite数据库"""
        print("🔄 开始数据迁移...")
        
        # 读取JSON数据
        with open(questions_file, 'r', encoding='utf-8') as f:
            questions_data = json.load(f)
        
        with open(user_progress_file, 'r', encoding='utf-8') as f:
            user_data = json.load(f)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # 迁移学科和知识点分类数据
            print("📚 迁移学科和知识点数据...")
            for subject_name, categories in questions_data.items():
                # 插入学科
                cursor.execute(
                    "INSERT OR IGNORE INTO subjects (name) VALUES (?)",
                    (subject_name,)
                )
                subject_id = cursor.execute(
                    "SELECT id FROM subjects WHERE name = ?", (subject_name,)
                ).fetchone()[0]
                
                # 插入知识点分类
                for category_name in categories.keys():
                    cursor.execute(
                        "INSERT OR IGNORE INTO knowledge_categories (subject_id, name) VALUES (?, ?)",
                        (subject_id, category_name)
                    )
            
            # 迁移题目数据
            print("📝 迁移题目数据...")
            for subject_name, categories in questions_data.items():
                for category_name, questions in categories.items():
                    # 获取分类ID
                    category_id = cursor.execute(
                        """SELECT kc.id FROM knowledge_categories kc 
                           JOIN subjects s ON kc.subject_id = s.id 
                           WHERE s.name = ? AND kc.name = ?""",
                        (subject_name, category_name)
                    ).fetchone()[0]
                    
                    # 插入题目
                    for question in questions:
                        cursor.execute(
                            """INSERT OR IGNORE INTO questions 
                               (question_id, category_id, question_text, question_type, 
                                options, correct_answer, difficulty, knowledge_points, explanation)
                               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                            (
                                question['id'],
                                category_id,
                                question['question'],
                                question['type'],
                                json.dumps(question.get('options', []), ensure_ascii=False),
                                question['correct_answer'],
                                question['difficulty'],
                                json.dumps(question['knowledge_points'], ensure_ascii=False),
                                question.get('explanation', '')
                            )
                        )
            
            # 迁移用户数据
            print("👤 迁移用户数据...")
            for username, user_info in user_data.items():
                # 插入用户基本信息
                user_basic = user_info['user_info']
                cursor.execute(
                    """INSERT OR IGNORE INTO users (username, name, grade, created_at, last_login)
                       VALUES (?, ?, ?, ?, ?)""",
                    (
                        username,
                        user_basic['name'],
                        user_basic.get('grade', ''),
                        user_basic.get('created_at', ''),
                        user_basic.get('last_login', '')
                    )
                )
                
                user_id = cursor.execute(
                    "SELECT id FROM users WHERE username = ?", (username,)
                ).fetchone()[0]
                
                # 迁移学习进度数据
                knowledge_graph = user_info.get('knowledge_graph', {})
                for subject_name, categories in knowledge_graph.items():
                    for category_name, progress in categories.items():
                        # 获取分类ID
                        category_result = cursor.execute(
                            """SELECT kc.id FROM knowledge_categories kc 
                               JOIN subjects s ON kc.subject_id = s.id 
                               WHERE s.name = ? AND kc.name = ?""",
                            (subject_name, category_name)
                        ).fetchone()
                        
                        if category_result:
                            category_id = category_result[0]
                            cursor.execute(
                                """INSERT OR REPLACE INTO user_progress 
                                   (user_id, category_id, mastery_level, correct_count, 
                                    total_attempts, last_study_time, weak_points)
                                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                                (
                                    user_id,
                                    category_id,
                                    progress.get('mastery_level', 0.0),
                                    progress.get('correct_count', 0),
                                    progress.get('total_attempts', 0),
                                    progress.get('last_study_time', ''),
                                    json.dumps(progress.get('weak_points', []), ensure_ascii=False)
                                )
                            )
                
                # 迁移答题历史
                answer_history = user_info.get('answer_history', [])
                for answer in answer_history:
                    cursor.execute(
                        """INSERT OR IGNORE INTO answer_history 
                           (user_id, question_id, user_answer, correct_answer, 
                            is_correct, answer_time, time_spent, answer_type, confidence)
                           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                        (
                            user_id,
                            answer['question_id'],
                            answer['user_answer'],
                            answer['correct_answer'],
                            answer['is_correct'],
                            answer['answer_time'],
                            answer.get('time_spent', 0),
                            answer.get('answer_type', 'text'),
                            answer.get('confidence', 0.0)
                        )
                    )
                
                # 迁移错题数据
                wrong_questions = user_info.get('wrong_questions', [])
                for wrong_q in wrong_questions:
                    cursor.execute(
                        """INSERT OR REPLACE INTO wrong_questions 
                           (user_id, question_id, wrong_count, first_wrong_time, 
                            last_wrong_time, status)
                           VALUES (?, ?, ?, ?, ?, ?)""",
                        (
                            user_id,
                            wrong_q['question_id'],
                            wrong_q['wrong_count'],
                            wrong_q['first_wrong_time'],
                            wrong_q['last_wrong_time'],
                            wrong_q['status']
                        )
                    )
                
                # 迁移学习统计数据
                learning_stats = user_info.get('learning_stats', {})
                if learning_stats:
                    cursor.execute(
                        """INSERT OR REPLACE INTO learning_stats 
                           (user_id, total_study_time, total_questions_attempted, 
                            total_correct, accuracy_rate, current_streak, best_streak, 
                            favorite_topics, study_days)
                           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                        (
                            user_id,
                            learning_stats.get('total_study_time', 0),
                            learning_stats.get('total_questions_attempted', 0),
                            learning_stats.get('total_correct', 0),
                            learning_stats.get('accuracy_rate', 0.0),
                            learning_stats.get('current_streak', 0),
                            learning_stats.get('best_streak', 0),
                            json.dumps(learning_stats.get('favorite_topics', []), ensure_ascii=False),
                            learning_stats.get('study_days', 0)
                        )
                    )
            
            conn.commit()
        
        print("✅ 数据迁移完成！")
    
    def get_user_by_username(self, username: str) -> Optional[Dict]:
        """根据用户名获取用户信息"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            result = cursor.execute(
                "SELECT * FROM users WHERE username = ?", (username,)
            ).fetchone()
            
            return dict(result) if result else None
    
    def get_questions_by_category(self, subject: str, category: str) -> List[Dict]:
        """获取指定分类的题目"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            results = cursor.execute(
                """SELECT q.* FROM questions q
                   JOIN knowledge_categories kc ON q.category_id = kc.id
                   JOIN subjects s ON kc.subject_id = s.id
                   WHERE s.name = ? AND kc.name = ?""",
                (subject, category)
            ).fetchall()
            
            questions = []
            for row in results:
                question = dict(row)
                question['options'] = json.loads(question['options']) if question['options'] else []
                question['knowledge_points'] = json.loads(question['knowledge_points'])
                questions.append(question)
            
            return questions
    
    def get_user_wrong_questions(self, username: str) -> List[Dict]:
        """获取用户的错题列表"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            results = cursor.execute(
                """SELECT wq.*, q.question_text, q.difficulty, q.knowledge_points
                   FROM wrong_questions wq
                   JOIN users u ON wq.user_id = u.id
                   JOIN questions q ON wq.question_id = q.question_id
                   WHERE u.username = ?
                   ORDER BY wq.last_wrong_time DESC""",
                (username,)
            ).fetchall()
            
            wrong_questions = []
            for row in results:
                question = dict(row)
                question['knowledge_points'] = json.loads(question['knowledge_points'])
                wrong_questions.append(question)
            
            return wrong_questions
    
    def add_answer_record(self, username: str, question_id: str, user_answer: str, 
                         correct_answer: str, is_correct: bool, time_spent: int = 0, 
                         answer_type: str = 'text', confidence: float = 0.0):
        """添加答题记录"""
        logger.info(f"💾 开始保存答题记录 - 用户: {username}, 题目ID: {question_id}, 答案类型: {answer_type}")
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # 获取用户ID
                user_result = cursor.execute(
                    "SELECT id FROM users WHERE username = ?", (username,)
                ).fetchone()
                
                if not user_result:
                    logger.error(f"❌ 用户不存在: {username}")
                    return False
                    
                user_id = user_result[0]
                logger.info(f"👤 找到用户ID: {user_id}")
                
                # 添加答题记录
                cursor.execute(
                    """INSERT INTO answer_history 
                       (user_id, question_id, user_answer, correct_answer, 
                        is_correct, answer_time, time_spent, answer_type, confidence)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (
                        user_id, question_id, user_answer, correct_answer,
                        is_correct, datetime.now().isoformat(), time_spent, answer_type, confidence
                    )
                )
                logger.info(f"📝 答题记录已保存 - 结果: {'正确' if is_correct else '错误'}")
                
                # 如果答错，更新错题集
                if not is_correct:
                    cursor.execute(
                        """INSERT OR REPLACE INTO wrong_questions 
                           (user_id, question_id, wrong_count, first_wrong_time, last_wrong_time, status)
                           VALUES (?, ?, 
                                   COALESCE((SELECT wrong_count FROM wrong_questions 
                                            WHERE user_id = ? AND question_id = ?), 0) + 1,
                                   COALESCE((SELECT first_wrong_time FROM wrong_questions 
                                            WHERE user_id = ? AND question_id = ?), ?),
                                   ?, '未掌握')""",
                        (user_id, question_id, user_id, question_id, user_id, question_id, 
                         datetime.now().isoformat(), datetime.now().isoformat())
                    )
                    logger.info(f"📚 错题记录已更新 - 用户: {username}, 题目: {question_id}")
                
                conn.commit()
                logger.info(f"✅ 数据库操作完成 - 用户: {username}")
                return True
                
        except Exception as e:
            logger.error(f"❌ 保存答题记录失败 - 用户: {username}, 错误: {str(e)}")
            return False

if __name__ == "__main__":
    # 测试数据库迁移
    db = DatabaseManager()
    
    # 检查JSON文件是否存在
    questions_file = "data/questions.json"
    user_progress_file = "data/user_progress.json"
    
    if os.path.exists(questions_file) and os.path.exists(user_progress_file):
        db.migrate_from_json(questions_file, user_progress_file)
        print("🎉 数据库初始化和迁移完成！")
    else:
        print("⚠️ JSON数据文件不存在，仅创建数据库结构")