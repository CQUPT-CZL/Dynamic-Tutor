-- schema.sql

-- 1. 用户表
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE
);

-- 2. 知识点表 (图的“点”)
CREATE TABLE IF NOT EXISTS knowledge_nodes (
    node_id TEXT PRIMARY KEY NOT NULL,
    node_name TEXT NOT NULL,
    node_difficulty TEXT, -- 知识点本身的难度，如 "入门", "进阶"
    level TEXT,           -- 知识点所属年级，如 "高二"
    node_learning TEXT    -- 知识点的讲解、定义等核心文本
);

-- 3. 知识点关系表 (图的“边”)
CREATE TABLE IF NOT EXISTS knowledge_edges (
    edge_id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_node_id TEXT NOT NULL,
    target_node_id TEXT NOT NULL,
    relation_type TEXT NOT NULL, -- 例如 'is_prerequisite_for' (是...的前置知识)
    FOREIGN KEY (source_node_id) REFERENCES knowledge_nodes (node_id),
    FOREIGN KEY (target_node_id) REFERENCES knowledge_nodes (node_id)
);

-- 4. 题库表
CREATE TABLE IF NOT EXISTS questions (
    question_id INTEGER PRIMARY KEY,
    question_text TEXT NOT NULL,
    question_type TEXT,       -- '选择题', '填空题', '解答题'
    difficulty REAL,         -- 题目的具体难度，0.0到1.0之间的小数
    analysis TEXT,             -- 题目的解析
    answer TEXT                -- 题目的答案
);

-- 5. 题目与知识点关联表
CREATE TABLE IF NOT EXISTS question_to_node_mapping (
    mapping_id INTEGER PRIMARY KEY AUTOINCREMENT,
    question_id INTEGER NOT NULL,
    node_id TEXT NOT NULL,
    FOREIGN KEY (question_id) REFERENCES questions (question_id),
    FOREIGN KEY (node_id) REFERENCES knowledge_nodes (node_id)
);

-- 6. 用户掌握度表
CREATE TABLE IF NOT EXISTS user_node_mastery (
    mastery_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    node_id TEXT NOT NULL,
    mastery_score REAL NOT NULL DEFAULT 0.0,
    FOREIGN KEY (user_id) REFERENCES users (user_id),
    FOREIGN KEY (node_id) REFERENCES knowledge_nodes (node_id)
);

-- 为初始用户数据做准备
INSERT OR IGNORE INTO users (user_id, username) VALUES (1, '小崔');
INSERT OR IGNORE INTO users (user_id, username) VALUES (2, '小陈');
INSERT OR IGNORE INTO users (user_id, username) VALUES (3, '小胡');