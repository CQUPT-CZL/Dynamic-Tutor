-- 确保每次执行都是全新的开始 (可选，开发时方便)
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS knowledge_nodes;
DROP TABLE IF EXISTS knowledge_edges;
DROP TABLE IF EXISTS questions;
DROP TABLE IF EXISTS question_to_node_mapping;
DROP TABLE IF EXISTS user_node_mastery;
DROP TABLE IF EXISTS user_answers;
DROP TABLE IF EXISTS wrong_questions;

-- 1. 用户表
CREATE TABLE users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE
);

-- 2. 知识点表 (图的"点")
CREATE TABLE knowledge_nodes (
    node_id TEXT PRIMARY KEY NOT NULL,
    node_name TEXT NOT NULL,
    node_difficulty REAL, -- 知识点本身的抽象难度 (0.0 - 1.0)
    level TEXT,           -- 知识点所属年级，如 "高一"
    node_learning TEXT    -- 知识点的讲解、定义等核心文本
);

-- 3. 知识点关系表 (图的"边")
CREATE TABLE knowledge_edges (
    edge_id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_node_id TEXT NOT NULL,
    target_node_id TEXT NOT NULL,
    relation_type TEXT NOT NULL, -- 例如 'is_prerequisite_for' (是...的前置知识)
    FOREIGN KEY (source_node_id) REFERENCES knowledge_nodes (node_id),
    FOREIGN KEY (target_node_id) REFERENCES knowledge_nodes (node_id)
);

-- 4. 题库表
CREATE TABLE questions (
    question_id INTEGER PRIMARY KEY,
    question_text TEXT NOT NULL,
    question_type TEXT,       -- '选择题', '填空题', '解答题'
    difficulty REAL,         -- 题目的具体难度 (0.0 - 1.0)
    analysis TEXT,             -- 题目的解析
    answer TEXT                -- 题目的答案
);

-- 5. 题目与知识点关联表
CREATE TABLE question_to_node_mapping (
    mapping_id INTEGER PRIMARY KEY AUTOINCREMENT,
    question_id INTEGER NOT NULL,
    node_id TEXT NOT NULL,
    FOREIGN KEY (question_id) REFERENCES questions (question_id),
    FOREIGN KEY (node_id) REFERENCES knowledge_nodes (node_id)
);

-- 6. 用户掌握度表
CREATE TABLE user_node_mastery (
    mastery_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    node_id TEXT NOT NULL,
    mastery_score REAL NOT NULL DEFAULT 0.0,
    FOREIGN KEY (user_id) REFERENCES users (user_id),
    FOREIGN KEY (node_id) REFERENCES knowledge_nodes (node_id)
);

-- 7. 用户答题记录表
CREATE TABLE user_answers (
    answer_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    question_id INTEGER NOT NULL,
    user_answer TEXT,
    is_correct BOOLEAN NOT NULL,
    time_spent INTEGER, -- 答题用时（秒）
    confidence REAL,    -- 答题信心度（0-1）
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (user_id),
    FOREIGN KEY (question_id) REFERENCES questions (question_id)
);

-- 8. 错题表
CREATE TABLE wrong_questions (
    wrong_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    question_id INTEGER NOT NULL,
    wrong_count INTEGER DEFAULT 1,
    first_wrong_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_wrong_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    status TEXT DEFAULT '未掌握', -- '未掌握', '已攻克'
    FOREIGN KEY (user_id) REFERENCES users (user_id),
    FOREIGN KEY (question_id) REFERENCES questions (question_id),
    UNIQUE(user_id, question_id) -- 确保每个用户对同一道错题只有一条记录
);

-- 为初始用户数据做准备
INSERT INTO users (username) VALUES ('小崔');
INSERT INTO users (username) VALUES ('小陈');
INSERT INTO users (username) VALUES ('小胡');

PRAGMA foreign_keys = ON;