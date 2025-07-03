# AI智慧学习平台 API 接口文档

## 概述

本文档描述了AI智慧学习平台的RESTful API接口，实现前后端分离架构。后端使用FastAPI框架，提供高性能的API服务。

## 基础信息

- **基础URL**: `http://localhost:8000/api`
- **API版本**: v1.0.0
- **数据格式**: JSON
- **字符编码**: UTF-8

## 通用响应格式

### 成功响应
```json
{
  "status": "success",
  "data": {...},
  "message": "操作成功"
}
```

### 错误响应
```json
{
  "status": "error",
  "error": "错误描述",
  "detail": "详细错误信息"
}
```

## API 接口列表

### 1. 系统相关接口

#### 1.1 健康检查
- **接口**: `GET /health`
- **描述**: 检查API服务状态
- **响应**:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z",
  "database": "connected"
}
```

#### 1.2 API根路径
- **接口**: `GET /`
- **描述**: 获取API基本信息
- **响应**:
```json
{
  "message": "🎓 AI智慧学习平台API",
  "version": "1.0.0",
  "docs": "/docs",
  "status": "running"
}
```

### 2. 用户管理接口

#### 2.1 获取用户列表
- **接口**: `GET /users`
- **描述**: 获取所有用户信息
- **响应**:
```json
[
  {
    "username": "小明",
    "name": "张小明",
    "grade": "高一"
  },
  {
    "username": "小红",
    "name": "李小红",
    "grade": "高一"
  }
]
```

### 3. 学习推荐接口

#### 3.1 获取用户学习推荐
- **接口**: `GET /recommendation/{user_id}`
- **描述**: 获取指定用户的个性化学习推荐
- **参数**:
  - `user_id` (string): 用户ID
- **响应**:
```json
{
  "mission_id": "mission_001",
  "type": "知识点练习",
  "reason": "根据你的学习情况，建议加强二次函数的练习",
  "content": {
    "knowledge_point": "二次函数",
    "difficulty": "中等",
    "question_count": 5,
    "question_id": "q_001",
    "question_text": "求函数 f(x) = x² + 2x - 3 的最小值"
  }
}
```

### 4. 答案诊断接口

#### 4.1 诊断文本答案
- **接口**: `POST /diagnose`
- **描述**: 诊断用户提交的文本答案
- **请求体**:
```json
{
  "user_id": "小明",
  "question_id": "q_001",
  "answer": "最小值为-4，当x=-1时取得",
  "answer_type": "text",
  "time_spent": 300,
  "confidence": 0.8
}
```
- **响应**:
```json
{
  "status": "success",
  "diagnosis": "答案正确！解题思路清晰",
  "hint": null,
  "correct_answer": "最小值为-4，当x=-1时取得",
  "next_recommendation": "可以尝试更复杂的二次函数问题"
}
```

#### 4.2 诊断图片答案
- **接口**: `POST /diagnose/image`
- **描述**: 诊断用户提交的图片答案
- **参数**:
  - `user_id` (string): 用户ID
  - `question_id` (string): 题目ID
  - `image` (file): 答案图片文件
  - `time_spent` (integer, 可选): 答题用时（秒）
  - `confidence` (float, 可选): 答题信心度（0-1）
- **响应**: 同文本答案诊断

### 5. 知识图谱接口

#### 5.1 获取用户知识图谱
- **接口**: `GET /knowledge-map/{user_id}`
- **描述**: 获取用户的个人知识图谱
- **参数**:
  - `user_id` (string): 用户ID
- **响应**:
```json
[
  {
    "知识点名称": "二次函数定义",
    "难度": "简单",
    "我的掌握度": 0.85,
    "正确题数": 17,
    "总题数": 20
  },
  {
    "知识点名称": "二次函数图像与性质",
    "难度": "中等",
    "我的掌握度": 0.72,
    "正确题数": 13,
    "总题数": 18
  }
]
```

#### 5.2 获取所有知识节点
- **接口**: `GET /knowledge-nodes`
- **描述**: 获取系统中所有知识节点
- **响应**:
```json
{
  "nodes": {
    "二次函数定义": "简单",
    "二次函数图像与性质": "中等",
    "二次函数三种解析式": "困难"
  }
}
```

#### 5.3 获取用户掌握度
- **接口**: `GET /mastery/{user_id}/{node_name}`
- **描述**: 获取用户对特定知识点的掌握度
- **参数**:
  - `user_id` (string): 用户ID
  - `node_name` (string): 知识点名称
- **响应**:
```json
{
  "mastery": 0.85
}
```

### 6. 练习题目接口

#### 6.1 获取知识点练习题
- **接口**: `GET /questions/{node_name}`
- **描述**: 获取指定知识点的练习题目
- **参数**:
  - `node_name` (string): 知识点名称
- **响应**:
```json
{
  "questions": [
    "求函数 f(x) = x² + 2x - 3 的最小值",
    "已知二次函数 f(x) = ax² + bx + c，求其对称轴",
    "判断二次函数 y = -2x² + 4x + 1 的开口方向"
  ]
}
```

### 7. 错题集接口

#### 7.1 获取用户错题集
- **接口**: `GET /wrong-questions/{user_id}`
- **描述**: 获取用户的错题记录
- **参数**:
  - `user_id` (string): 用户ID
- **响应**:
```json
{
  "wrong_questions": [
    {
      "question_id": "q_001",
      "question_text": "求函数 f(x) = x² + 2x - 3 的最小值",
      "subject": "数学",
      "knowledge_point": "二次函数",
      "user_answer": "最小值为-2",
      "correct_answer": "最小值为-4",
      "date": "2024-01-15",
      "attempts": 2
    }
  ]
}
```

### 8. 统计信息接口

#### 8.1 获取用户学习统计
- **接口**: `GET /stats/{user_id}`
- **描述**: 获取用户的学习统计信息
- **参数**:
  - `user_id` (string): 用户ID
- **响应**:
```json
{
  "total_questions_answered": 156,
  "correct_rate": 0.85,
  "study_time_today": 45,
  "streak_days": 7,
  "mastery_progress": 0.72,
  "weekly_progress": {
    "monday": 12,
    "tuesday": 8,
    "wednesday": 15,
    "thursday": 10,
    "friday": 18,
    "saturday": 6,
    "sunday": 9
  }
}
```

## 错误代码说明

| 状态码 | 说明 |
|--------|------|
| 200 | 请求成功 |
| 400 | 请求参数错误 |
| 404 | 资源不存在 |
| 500 | 服务器内部错误 |

## 使用示例

### Python 请求示例

```python
import requests

# 基础URL
base_url = "http://localhost:8000/api"

# 获取用户列表
response = requests.get(f"{base_url}/users")
users = response.json()
print(users)

# 获取用户推荐
user_id = "小明"
response = requests.get(f"{base_url}/recommendation/{user_id}")
recommendation = response.json()
print(recommendation)

# 提交答案诊断
data = {
    "user_id": "小明",
    "question_id": "q_001",
    "answer": "最小值为-4",
    "answer_type": "text"
}
response = requests.post(f"{base_url}/diagnose", json=data)
diagnosis = response.json()
print(diagnosis)
```

### JavaScript 请求示例

```javascript
// 基础URL
const baseUrl = "http://localhost:8000/api";

// 获取用户列表
fetch(`${baseUrl}/users`)
  .then(response => response.json())
  .then(users => console.log(users));

// 获取用户推荐
const userId = "小明";
fetch(`${baseUrl}/recommendation/${userId}`)
  .then(response => response.json())
  .then(recommendation => console.log(recommendation));

// 提交答案诊断
const data = {
  user_id: "小明",
  question_id: "q_001",
  answer: "最小值为-4",
  answer_type: "text"
};

fetch(`${baseUrl}/diagnose`, {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify(data)
})
.then(response => response.json())
.then(diagnosis => console.log(diagnosis));
```

## 部署说明

### 后端部署

1. 安装依赖：
```bash
cd backend
pip install -r requirements.txt
```

2. 启动服务器：
```bash
python api_server.py
```

3. 访问API文档：
   - Swagger UI: `http://localhost:8000/docs`
   - ReDoc: `http://localhost:8000/redoc`

### 前端部署

1. 安装依赖：
```bash
cd frontend
pip install -r requirements.txt
```

2. 启动前端应用：
```bash
streamlit run app.py
```

3. 访问前端应用：
   - 前端界面: `http://localhost:8501`

## 注意事项

1. **CORS配置**: 当前配置允许所有域名访问，生产环境中应该限制为特定域名
2. **数据验证**: 所有输入数据都会进行验证，确保数据安全性
3. **错误处理**: API会返回详细的错误信息，便于调试
4. **性能优化**: 使用了异步处理，支持高并发访问
5. **数据库连接**: 确保数据库文件存在且可访问

## 更新日志

### v1.0.0 (2024-01-15)
- 初始版本发布
- 实现基础的用户管理、学习推荐、答案诊断等功能
- 支持文本和图片答案诊断
- 提供完整的知识图谱和统计功能