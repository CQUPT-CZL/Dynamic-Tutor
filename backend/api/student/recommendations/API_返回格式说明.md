# 📋 学生端每日任务 API 返回格式说明

基于前端 `daily_tasks.py` 文件的分析，本文档详细说明了学生端每日任务相关的后端 API 返回格式。

## 🎯 1. 获取用户推荐任务 API

**接口**: `api_service.get_recommendation(user_id)`

### 📊 返回数据结构

```json
{
  "mission_type": "string",  // 任务类型
  "metadata": {
    "title": "string",      // 任务标题
    "objective": "string",  // 学习目标
    "reason": "string"      // 推荐理由
  },
  "payload": {             // 任务具体内容，根据任务类型不同而不同
    // 详见下方各任务类型的具体格式
  }
}
```

### 🚀 任务类型 (mission_type)

支持以下四种任务类型：

- `NEW_KNOWLEDGE` - 新知探索 🚀
- `WEAK_POINT_CONSOLIDATION` - 弱点巩固 💪
- `SKILL_ENHANCEMENT` - 技能提升 ⚡
- `EXPLORATORY` - 兴趣探索 🎨

---

## 📚 2. 新知探索 & 弱点巩固任务格式

**适用于**: `NEW_KNOWLEDGE` 和 `WEAK_POINT_CONSOLIDATION`

### payload 结构

```json
{
  "target_node": {
    "name": "string"        // 目标知识点名称
  },
  "steps": [
    {
      "type": "string",     // 步骤类型
      "content": {          // 步骤内容，根据类型不同而不同
        // 详见下方各步骤类型的具体格式
      }
    }
  ]
}
```

### 📋 学习步骤类型 (step.type)

#### 1. 概念学习 (CONCEPT_LEARNING)

```json
{
  "type": "CONCEPT_LEARNING",
  "content": {
    "title": "string",      // 概念标题
    "text": "string"       // 概念内容文本
  }
}
```

#### 2. 题目练习 (QUESTION_PRACTICE)

```json
{
  "type": "QUESTION_PRACTICE",
  "content": {
    "question_id": "string",     // 题目ID（必需）
    "prompt": "string",          // 提示信息
    "question_text": "string",   // 题目文本
    "question": "string",        // 题目内容
    "difficulty": 0.5,           // 难度系数 (0.0-1.0)
    "question_type": "string"     // 题目类型，如 "text_input"
  }
}
```

#### 3. 错题回顾 (WRONG_QUESTION_REVIEW)

```json
{
  "type": "WRONG_QUESTION_REVIEW",
  "content": {
    "question_id": "string",     // 题目ID（必需）
    "prompt": "string",          // 回顾提示
    "question_text": "string",   // 题目文本
    "question": "string",        // 题目内容
    "difficulty": 0.5,           // 难度系数 (0.0-1.0)
    "question_type": "string"     // 题目类型
  }
}
```

---

## ⚡ 3. 技能提升任务格式

**适用于**: `SKILL_ENHANCEMENT`

### payload 结构

```json
{
  "target_skill": "string",    // 目标技能名称
  "questions": [
    {
      "question_id": "string",     // 题目ID（必需）
      "prompt": "string",          // 提示信息
      "question_text": "string",   // 题目文本
      "question": "string",        // 题目内容
      "difficulty": 0.5,           // 难度系数 (0.0-1.0)
      "question_type": "string"     // 题目类型
    }
  ]
}
```

---

## 🎨 4. 兴趣探索任务格式

**适用于**: `EXPLORATORY`

### payload 结构

```json
{
  "content_type": "string",     // 内容类型
  "title": "string",           // 标题
  "body": "string",            // 内容正文
  "image_url": "string"        // 相关图片URL（可选）
}
```

---

## 📊 5. 获取用户统计数据 API

**接口**: `api_service.get_user_stats(user_id)`

### 返回数据结构

```json
{
  "total_questions_answered": 0,    // 今日完成题目数
  "correct_rate": 0.0,             // 正确率 (0.0-1.0)
  "study_time_today": 0,           // 今日学习时长（分钟）
  "streak_days": 0                 // 连续学习天数
}
```

---

## ❌ 6. 获取错题数据 API

**接口**: `api_service.get_wrong_questions(user_id)`

### 返回数据结构

```json
[
  {
    "question_text": "string",    // 题目文本
    "subject": "string",          // 科目
    "date": "string"              // 错误日期
  }
]
```

---

## 🚨 7. 错误处理

### 推荐任务获取失败

当 `get_recommendation` 返回错误时，应包含 `error` 字段：

```json
{
  "error": "string"    // 错误信息
}
```

### 空数据处理

- 当没有推荐任务时，返回 `null` 或空对象 `{}`
- 当没有错题时，返回空数组 `[]`
- 当统计数据不可用时，各字段应有默认值（如 0）

---

## 💡 8. 实现建议

### 🔧 后端实现要点

1. **数据完整性**: 确保所有必需字段都有值，特别是 `question_id`
2. **类型一致性**: 保持数据类型的一致性，如难度系数始终为浮点数
3. **错误处理**: 提供清晰的错误信息和状态码
4. **性能优化**: 考虑缓存机制，避免重复计算推荐结果

### 📱 前端适配要点

1. **容错处理**: 对缺失字段提供默认值
2. **用户体验**: 在数据加载时显示适当的加载状态
3. **错误反馈**: 向用户展示友好的错误信息

### 🎯 扩展性考虑

1. **新任务类型**: 可以轻松添加新的 `mission_type`
2. **新步骤类型**: 可以扩展新的学习步骤类型
3. **个性化**: 支持根据用户偏好调整推荐策略

---

## 📝 示例完整返回数据

### 新知探索任务示例

```json
{
  "mission_type": "NEW_KNOWLEDGE",
  "metadata": {
    "title": "探索二次函数的奥秘",
    "objective": "掌握二次函数的基本概念和图像特征",
    "reason": "根据你的学习进度，现在是学习二次函数的最佳时机"
  },
  "payload": {
    "target_node": {
      "name": "二次函数"
    },
    "steps": [
      {
        "type": "CONCEPT_LEARNING",
        "content": {
          "title": "二次函数的定义",
          "text": "二次函数是形如 f(x) = ax² + bx + c 的函数..."
        }
      },
      {
        "type": "QUESTION_PRACTICE",
        "content": {
          "question_id": "q_001",
          "prompt": "让我们来练习一下二次函数的基本形式",
          "question_text": "请写出一般二次函数的标准形式",
          "question": "请写出一般二次函数的标准形式",
          "difficulty": 0.3,
          "question_type": "text_input"
        }
      }
    ]
  }
}
```

这份文档为后端开发者提供了完整的 API 返回格式规范，确保前后端数据交互的一致性和可靠性。 🎉