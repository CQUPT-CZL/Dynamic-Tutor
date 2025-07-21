-- ====================================================================
--            AI自适应学习平台 - 最终版SQLite数据库 Schema
-- ====================================================================

-- 删除旧表，确保每次执行都是一个全新的、干净的开始
PRAGMA foreign_keys = OFF;
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS knowledge_nodes;
DROP TABLE IF EXISTS knowledge_edges;
DROP TABLE IF EXISTS questions;
DROP TABLE IF EXISTS question_to_node_mapping;
DROP TABLE IF EXISTS user_node_mastery;
DROP TABLE IF EXISTS user_answers;
DROP TABLE IF EXISTS wrong_questions;
PRAGMA foreign_keys = ON;


-- 表1: 用户表 (增加了role字段)
CREATE TABLE users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    role TEXT NOT NULL DEFAULT 'student' -- 'student' 或 'teacher'
);

-- 表2: 知识点表 (图的“点”)
CREATE TABLE knowledge_nodes (
    node_id INTEGER PRIMARY KEY AUTOINCREMENT,
    node_name TEXT NOT NULL,
    node_difficulty REAL, -- 知识点本身的抽象难度 (0.0 - 1.0)
    level TEXT,           -- 知识点所属年级
    node_type TEXT,        -- 知识点类型：概念、章节等
    node_learning TEXT    -- 知识点的讲解、定义等核心文本
);

-- 表3: 知识点关系表 (图的“边”) (增加了status和created_by)
CREATE TABLE knowledge_edges (
    edge_id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_node_id TEXT NOT NULL,
    target_node_id TEXT NOT NULL,
    relation_type TEXT NOT NULL, -- 例如 'is_prerequisite_for'
    status TEXT NOT NULL DEFAULT 'published', -- 'draft' (AI建议), 'published' (教师确认)
    created_by INTEGER NOT NULL, -- 关联到users表，记录创建者
    FOREIGN KEY (source_node_id) REFERENCES knowledge_nodes (node_id),
    FOREIGN KEY (target_node_id) REFERENCES knowledge_nodes (node_id),
    FOREIGN KEY (created_by) REFERENCES users (user_id)
);

-- 表4: 题库表 (增加了图片、状态和创建者)
CREATE TABLE questions (
    question_id INTEGER PRIMARY KEY AUTOINCREMENT,
    question_text TEXT NOT NULL,
    question_image_url TEXT, -- 存储图片路径
    question_type TEXT,      -- '选择题', '填空题', '解答题'
    difficulty REAL,         -- 题目的具体难度 (0.0 - 1.0)
    options TEXT,            -- 对于选择题，存储JSON格式的选项
    answer TEXT,
    analysis TEXT,
    skill_focus TEXT,        -- 题目的技能重点
    status TEXT NOT NULL DEFAULT 'published', -- 'draft' (AI生成), 'published' (教师发布)
    created_by INTEGER NOT NULL, -- 关联到users表，记录创建者
    FOREIGN KEY (created_by) REFERENCES users (user_id)
);

-- 表5: 题目与知识点关联表
CREATE TABLE question_to_node_mapping (
    mapping_id INTEGER PRIMARY KEY AUTOINCREMENT,
    question_id INTEGER NOT NULL,
    node_id TEXT NOT NULL,
    FOREIGN KEY (question_id) REFERENCES questions (question_id),
    FOREIGN KEY (node_id) REFERENCES knowledge_nodes (node_id)
);

-- 表6: 用户掌握度表
CREATE TABLE user_node_mastery (
    mastery_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    node_id TEXT NOT NULL,
    mastery_score REAL NOT NULL DEFAULT 0.0,
    FOREIGN KEY (user_id) REFERENCES users (user_id),
    FOREIGN KEY (node_id) REFERENCES knowledge_nodes (node_id),
    UNIQUE(user_id, node_id)
);

-- 表7: 用户答题记录表
CREATE TABLE user_answers (
    answer_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    question_id INTEGER NOT NULL,
    user_answer TEXT,
    is_correct BOOLEAN NOT NULL,
    time_spent INTEGER, -- 答题用时（秒）
    confidence REAL,    -- 答题信心度（0-1）
    diagnosis_json TEXT, -- 答题诊断agent返回的多维得分数组（JSON格式）
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (user_id),
    FOREIGN KEY (question_id) REFERENCES questions (question_id)
);

-- 表8: 错题表
CREATE TABLE wrong_questions (
    wrong_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    question_id INTEGER NOT NULL,
    wrong_count INTEGER DEFAULT 1,
    last_wrong_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    status TEXT DEFAULT '未掌握', -- '未掌握', '已攻克'
    FOREIGN KEY (user_id) REFERENCES users (user_id),
    FOREIGN KEY (question_id) REFERENCES questions (question_id),
    UNIQUE(user_id, question_id)
);

-- 插入一些初始用户，用于测试
INSERT INTO users (username, role) VALUES ('小崔', 'student');
INSERT INTO users (username, role) VALUES ('小陈', 'student');
INSERT INTO users (username, role) VALUES ('小李', 'student');
INSERT INTO users (username, role) VALUES ('小张', 'student');
INSERT INTO users (username, role) VALUES ('舵老师', 'teacher');