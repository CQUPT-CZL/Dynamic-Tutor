# 教师端API接口文档

本文档定义了教师端功能所需的所有API接口。

## 基础信息

- **基础URL**: `http://localhost:8000`
- **认证方式**: 暂无（后续可添加JWT认证）
- **数据格式**: JSON

## 1. 知识点管理API

### 1.1 获取知识点列表

```http
GET /api/teacher/knowledge-nodes
```

**查询参数:**
- `search` (可选): 搜索关键词
- `level` (可选): 难度等级 (初级/中级/高级)
- `page` (可选): 页码，默认1
- `limit` (可选): 每页数量，默认20

**响应示例:**
```json
{
  "status": "success",
  "data": {
    "nodes": [
      {
        "node_id": "math_001",
        "node_name": "一元二次方程",
        "node_difficulty": 0.7,
        "level": "中级",
        "node_learning": "掌握一元二次方程的解法和应用"
      }
    ],
    "total": 25,
    "page": 1,
    "limit": 20
  }
}
```

### 1.2 创建知识点

```http
POST /api/teacher/knowledge-nodes
```

**请求体:**
```json
{
  "node_id": "math_004",
  "node_name": "三角函数",
  "node_difficulty": 0.6,
  "level": "中级",
  "node_learning": "理解三角函数的定义和基本性质"
}
```

**响应示例:**
```json
{
  "status": "success",
  "message": "知识点创建成功",
  "data": {
    "node_id": "math_004"
  }
}
```

### 1.3 更新知识点

```http
PUT /api/teacher/knowledge-nodes/{node_id}
```

**请求体:**
```json
{
  "node_name": "三角函数基础",
  "node_difficulty": 0.65,
  "level": "中级",
  "node_learning": "理解三角函数的定义、性质和基本应用"
}
```

### 1.4 删除知识点

```http
DELETE /api/teacher/knowledge-nodes/{node_id}
```

### 1.5 获取知识点统计

```http
GET /api/teacher/knowledge-nodes/stats
```

**响应示例:**
```json
{
  "status": "success",
  "data": {
    "total_nodes": 25,
    "level_distribution": {
      "初级": 10,
      "中级": 10,
      "高级": 5
    },
    "avg_difficulty": 0.65,
    "recent_added": 3
  }
}
```

## 2. 题目管理API

### 2.1 获取题目列表

```http
GET /api/teacher/questions
```

**查询参数:**
- `search` (可选): 搜索关键词
- `type` (可选): 题目类型 (选择题/填空题/解答题)
- `status` (可选): 状态 (draft/published)
- `page` (可选): 页码，默认1
- `limit` (可选): 每页数量，默认20

**响应示例:**
```json
{
  "status": "success",
  "data": {
    "questions": [
      {
        "question_id": 1,
        "question_text": "解方程 x² - 5x + 6 = 0",
        "question_type": "解答题",
        "difficulty": 0.6,
        "answer": "x = 2 或 x = 3",
        "analysis": "使用因式分解法：(x-2)(x-3)=0",
        "status": "published",
        "created_by": 3,
        "question_image_url": null
      }
    ],
    "total": 156,
    "page": 1,
    "limit": 20
  }
}
```

### 2.2 创建题目

```http
POST /api/teacher/questions
```

**请求体:**
```json
{
  "question_text": "计算函数 f(x) = x² + 2x + 1 在 x = 1 处的值",
  "question_type": "填空题",
  "difficulty": 0.4,
  "answer": "4",
  "analysis": "将x=1代入函数：f(1) = 1² + 2×1 + 1 = 4",
  "status": "draft",
  "question_image_url": null
}
```

### 2.3 更新题目

```http
PUT /api/teacher/questions/{question_id}
```

### 2.4 删除题目

```http
DELETE /api/teacher/questions/{question_id}
```

### 2.5 发布题目

```http
POST /api/teacher/questions/{question_id}/publish
```

### 2.6 上传题目图片

```http
POST /api/teacher/questions/upload-image
```

**请求体:** multipart/form-data
- `file`: 图片文件

**响应示例:**
```json
{
  "status": "success",
  "data": {
    "image_url": "/images/questions/20231201_123456_image.jpg"
  }
}
```

### 2.7 获取题目统计

```http
GET /api/teacher/questions/stats
```

**响应示例:**
```json
{
  "status": "success",
  "data": {
    "total_questions": 156,
    "published_questions": 120,
    "draft_questions": 36,
    "type_distribution": {
      "选择题": 60,
      "填空题": 45,
      "解答题": 51
    },
    "avg_difficulty": 0.58,
    "recent_added": 8
  }
}
```

## 3. 题目与知识点关联API

### 3.1 创建题目知识点关联

```http
POST /api/teacher/question-node-mapping
```

**请求体:**
```json
{
  "question_id": 1,
  "node_id": "math_001"
}
```

### 3.2 获取题目知识点关联列表

```http
GET /api/teacher/question-node-mapping
```

**查询参数:**
- `question_id` (可选): 题目ID
- `node_id` (可选): 知识点ID

**响应示例:**
```json
{
  "status": "success",
  "data": {
    "mappings": [
      {
        "mapping_id": 1,
        "question_id": 1,
        "question_text": "解方程 x² - 5x + 6 = 0",
        "node_id": "math_001",
        "node_name": "一元二次方程"
      }
    ]
  }
}
```

### 3.3 删除题目知识点关联

```http
DELETE /api/teacher/question-node-mapping/{mapping_id}
```

## 4. 知识图谱管理API

### 4.1 获取知识图谱数据

```http
GET /api/teacher/knowledge-graph
```

**响应示例:**
```json
{
  "status": "success",
  "data": {
    "nodes": [
      {
        "id": "math_001",
        "name": "一元二次方程",
        "level": "中级",
        "difficulty": 0.7
      }
    ],
    "edges": [
      {
        "source": "math_002",
        "target": "math_001",
        "relation_type": "prerequisite",
        "status": "published"
      }
    ]
  }
}
```

### 4.2 获取知识点关系列表

```http
GET /api/teacher/knowledge-edges
```

**查询参数:**
- `status` (可选): 状态 (draft/published)
- `relation_type` (可选): 关系类型

**响应示例:**
```json
{
  "status": "success",
  "data": {
    "edges": [
      {
        "edge_id": 1,
        "source_node_id": "math_002",
        "target_node_id": "math_004",
        "relation_type": "prerequisite",
        "status": "published",
        "created_by": 3,
        "source_name": "函数的概念",
        "target_name": "二次函数"
      }
    ]
  }
}
```

### 4.3 创建知识点关系

```http
POST /api/teacher/knowledge-edges
```

**请求体:**
```json
{
  "source_node_id": "math_002",
  "target_node_id": "math_004",
  "relation_type": "prerequisite",
  "status": "draft"
}
```

### 4.4 更新知识点关系

```http
PUT /api/teacher/knowledge-edges/{edge_id}
```

### 4.5 删除知识点关系

```http
DELETE /api/teacher/knowledge-edges/{edge_id}
```

### 4.6 发布知识点关系

```http
POST /api/teacher/knowledge-edges/{edge_id}/publish
```

### 4.7 获取AI关系建议

```http
GET /api/teacher/knowledge-edges/ai-suggestions
```

**响应示例:**
```json
{
  "status": "success",
  "data": {
    "suggestions": [
      {
        "source_node_id": "math_001",
        "target_node_id": "math_004",
        "relation_type": "related",
        "confidence": 0.85,
        "reason": "一元二次方程与二次函数在数学概念上密切相关",
        "source_name": "一元二次方程",
        "target_name": "二次函数"
      }
    ]
  }
}
```

### 4.8 获取知识图谱分析

```http
GET /api/teacher/knowledge-graph/analysis
```

**响应示例:**
```json
{
  "status": "success",
  "data": {
    "basic_stats": {
      "total_nodes": 25,
      "total_edges": 18,
      "avg_degree": 1.44,
      "connected_components": 2,
      "diameter": 4,
      "clustering_coefficient": 0.35
    },
    "node_importance": [
      {
        "node_id": "math_002",
        "node_name": "函数的概念",
        "degree": 4,
        "betweenness": 0.25,
        "pagerank": 0.18
      }
    ],
    "health_metrics": {
      "connectivity": 85,
      "completeness": 72,
      "balance": 68,
      "hierarchy": 78
    }
  }
}
```

## 5. 用户管理API

### 5.1 获取用户列表（按角色过滤）

```http
GET /api/users
```

**查询参数:**
- `role` (可选): 用户角色 (student/teacher)

**响应示例:**
```json
{
  "status": "success",
  "data": {
    "users": [
      {
        "user_id": 1,
        "username": "小崔",
        "role": "student"
      },
      {
        "user_id": 3,
        "username": "胡老师",
        "role": "teacher"
      }
    ]
  }
}
```

## 6. 错误响应格式

所有API在出错时返回统一格式：

```json
{
  "status": "error",
  "message": "错误描述",
  "code": "ERROR_CODE",
  "details": {
    "field": "具体错误信息"
  }
}
```

## 7. 状态码说明

- `200`: 成功
- `201`: 创建成功
- `400`: 请求参数错误
- `401`: 未授权
- `403`: 权限不足
- `404`: 资源不存在
- `409`: 资源冲突（如ID重复）
- `500`: 服务器内部错误

## 8. 数据验证规则

### 知识点
- `node_id`: 必填，唯一，格式：字母+下划线+数字
- `node_name`: 必填，长度1-100字符
- `node_difficulty`: 必填，范围0.0-1.0
- `level`: 必填，枚举值：初级/中级/高级
- `node_learning`: 必填，长度1-500字符

### 题目
- `question_text`: 必填，长度1-2000字符
- `question_type`: 必填，枚举值：选择题/填空题/解答题
- `difficulty`: 必填，范围0.0-1.0
- `answer`: 必填，长度1-500字符
- `analysis`: 可选，长度0-1000字符
- `status`: 必填，枚举值：draft/published

### 知识点关系
- `source_node_id`: 必填，必须存在的知识点ID
- `target_node_id`: 必填，必须存在的知识点ID，且不能与source_node_id相同
- `relation_type`: 必填，枚举值：prerequisite/related/contains/similar
- `status`: 必填，枚举值：draft/published

## 9. 实现优先级

### 高优先级（核心功能）
1. 知识点CRUD操作
2. 题目CRUD操作
3. 用户列表获取（按角色过滤）
4. 基础统计信息

### 中优先级（重要功能）
1. 题目与知识点关联
2. 知识点关系管理
3. 知识图谱数据获取
4. 图片上传功能

### 低优先级（高级功能）
1. AI关系建议
2. 知识图谱分析
3. 复杂统计和报表
4. 批量操作功能

## 10. 注意事项

1. 所有API都需要验证用户权限，确保只有教师角色可以访问教师端API
2. 删除操作需要检查关联关系，避免数据不一致
3. 图片上传需要验证文件类型和大小限制
4. AI功能可以先返回模拟数据，后续接入真实AI服务
5. 分页查询需要合理设置默认值和最大值限制
6. 所有输入数据都需要进行安全验证，防止SQL注入等攻击