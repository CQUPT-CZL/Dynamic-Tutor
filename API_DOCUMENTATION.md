# 🎓 AI智慧学习平台 API 文档

## 📖 概述

本文档描述了AI智慧学习平台的RESTful API接口，采用前后端分离架构。后端使用FastAPI框架，按角色分离设计，提供高性能的API服务。

## 🔗 基础信息

- **基础URL**: `http://localhost:8000`
- **API版本**: v2.0.0
- **数据格式**: JSON
- **字符编码**: UTF-8
- **交互式文档**: http://localhost:8000/docs

## 🏗️ API架构

### 角色分离设计

```
/                    # 通用接口
├── /student/        # 🎓 学生端接口
└── /teacher/        # 👨‍🏫 教师端接口
```

## 📋 通用接口

### 系统状态

| 接口 | 方法 | 描述 |
|------|------|------|
| `/` | GET | API根路径信息 |
| `/health` | GET | 健康检查 |
| `/users` | GET | 获取用户列表 |
| `/api-info` | GET | 获取API结构信息 |

#### 健康检查示例
```bash
GET /health
```

**响应**:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z",
  "database": "connected"
}
```

---

## 🎓 学生端接口

### 1. 学习推荐

**接口**: `GET /student/recommendation/{user_id}`

**功能**: 获取个性化学习推荐，支持四种任务类型：
- 🆕 新知探索 (NEW_KNOWLEDGE)
- 💪 弱点巩固 (WEAK_POINT_CONSOLIDATION) 
- 🚀 技能提升 (SKILL_ENHANCEMENT)
- 🔍 兴趣探索 (EXPLORATORY)

**响应示例**:
```json
{
  "mission_id": "mission_nk_1642234567",
  "mission_type": "NEW_KNOWLEDGE",
  "metadata": {
    "title": "新知识解锁：条件概率！",
    "objective": "通过本次任务，你将掌握条件概率的定义和基本计算方法。",
    "reason": "AI发现你已经完全掌握了'概率的定义与性质'，现在是深入学习的最佳时机！"
  },
  "payload": {
    "target_node": {
      "id": "conditional_probability",
      "name": "条件概率"
    },
    "steps": [...]
  }
}
```

### 2. 答案诊断

#### 文本答案诊断
**接口**: `POST /student/diagnose`

**请求体**:
```json
{
  "user_id": "小明",
  "question_id": "q_001",
  "answer": "最小值为-4，当x=-1时取得",
  "time_spent": 300,
  "confidence": 0.8
}
```

#### 图片答案诊断
**接口**: `POST /student/diagnose/image`

**参数**: 
- `user_id` (string): 用户ID
- `question_id` (string): 题目ID
- `image` (file): 答案图片文件
- `time_spent` (int, 可选): 答题用时
- `confidence` (float, 可选): 答题信心度

### 3. 知识图谱

| 接口 | 方法 | 描述 |
|------|------|------|
| `/student/knowledge-map/{user_id}` | GET | 获取用户知识图谱 |
| `/student/knowledge-map/get-nodes` | GET | 获取所有知识节点 |
| `/student/knowledge-map/mastery/{user_id}/{node_name}` | GET | 获取知识点掌握度 |

### 4. 练习与错题

| 接口 | 方法 | 描述 |
|------|------|------|
| `/student/questions/{node_name}` | GET | 获取知识点练习题 |
| `/student/wrong-questions/{user_id}` | GET | 获取用户错题集 |
| `/student/stats/{user_id}` | GET | 获取用户学习统计 |

---

## 👨‍🏫 教师端接口

### 1. 知识点管理

**基础路径**: `/teacher/knowledge`

| 接口 | 方法 | 描述 |
|------|------|------|
| `/nodes` | GET | 获取知识点列表 |
| `/nodes` | POST | 创建知识点 |
| `/nodes/{node_id}` | PUT | 更新知识点 |
| `/nodes/{node_id}` | DELETE | 删除知识点 |
| `/nodes/stats` | GET | 获取知识点统计 |
| `/graph-data` | GET | 获取知识图谱数据 |
| `/generate-learning-objective` | POST | AI生成学习目标 |

#### 创建知识点示例
```bash
POST /teacher/knowledge/nodes
```

**请求体**:
```json
{
  "node_name": "二次函数",
  "difficulty_level": "中等",
  "subject": "数学",
  "grade": "高一",
  "description": "二次函数的定义、性质和应用"
}
```

### 2. 题目管理

**基础路径**: `/teacher/question`

| 接口 | 方法 | 描述 |
|------|------|------|
| `/questions` | GET | 获取题目列表 |
| `/questions` | POST | 创建题目 |
| `/questions/{question_id}` | PUT | 更新题目 |
| `/questions/{question_id}` | DELETE | 删除题目 |
| `/upload-image` | POST | 上传题目图片 |
| `/map-to-node` | POST | 关联题目到知识点 |

#### 创建题目示例
```bash
POST /teacher/question/questions
```

**请求体**:
```json
{
  "question_text": "求函数 f(x) = x² + 2x - 3 的最小值",
  "question_type": "解答题",
  "answer": "最小值为-4，当x=-1时取得",
  "analysis": "使用配方法或求导法求解",
  "difficulty": "中等",
  "subject": "数学",
  "grade": "高一"
}
```

### 3. 学生数据分析

**基础路径**: `/teacher/analytics`

| 接口 | 方法 | 描述 |
|------|------|------|
| `/class/{class_id}/overview` | GET | 班级学习概览 |
| `/student/{student_id}/progress` | GET | 学生学习进度 |
| `/class/{class_id}/weak-points` | GET | 班级薄弱知识点 |

---

## 🔧 使用示例

### Python 示例

```python
import requests

base_url = "http://localhost:8000"

# 获取学习推荐
response = requests.get(f"{base_url}/student/recommendation/小明")
recommendation = response.json()
print(recommendation)

# 提交答案诊断
data = {
    "user_id": "小明",
    "question_id": "q_001",
    "answer": "最小值为-4",
    "time_spent": 300
}
response = requests.post(f"{base_url}/student/diagnose", json=data)
result = response.json()
print(result)

# 创建知识点（教师端）
knowledge_data = {
    "node_name": "二次函数",
    "difficulty_level": "中等",
    "subject": "数学",
    "grade": "高一"
}
response = requests.post(f"{base_url}/teacher/knowledge/nodes", json=knowledge_data)
print(response.json())
```

### JavaScript 示例

```javascript
const baseUrl = "http://localhost:8000";

// 获取用户知识图谱
fetch(`${baseUrl}/student/knowledge-map/小明`)
  .then(response => response.json())
  .then(data => console.log(data));

// 上传图片答案
const formData = new FormData();
formData.append('user_id', '小明');
formData.append('question_id', 'q_001');
formData.append('image', imageFile);

fetch(`${baseUrl}/student/diagnose/image`, {
  method: 'POST',
  body: formData
})
.then(response => response.json())
.then(result => console.log(result));
```

---

## 🚀 快速启动

### 启动后端服务

```bash
cd backend
python api_server_restructured.py
```

### 访问地址

- **API服务**: http://localhost:8000
- **交互式文档**: http://localhost:8000/docs
- **API信息**: http://localhost:8000/api-info

---

## 📝 注意事项

1. **CORS配置**: 当前允许 `http://localhost:8501` 访问
2. **文件上传**: 支持图片答案上传，文件保存在 `/uploads` 目录
3. **数据库**: 使用SQLite数据库，确保数据库文件存在
4. **错误处理**: 统一的异常处理和错误响应格式
5. **角色分离**: 学生端和教师端接口完全分离，便于权限管理

---

## 🔄 更新日志

### v2.0.0 (2024-01-15)
- ✨ 重构API架构，按角色分离
- 🎯 优化学习推荐算法，支持四种任务类型
- 📊 增强答案诊断功能，支持图片识别
- 🗺️ 完善知识图谱管理
- 👨‍🏫 新增教师端完整功能模块
- 📈 添加学生数据分析功能

---

*📚 更多详细信息请访问交互式API文档: http://localhost:8000/docs*