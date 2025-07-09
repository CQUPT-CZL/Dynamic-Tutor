# API模块说明

本目录包含AI智慧学习平台的后端API接口，按角色分离，便于维护和扩展。

## 目录结构

```
api/
├── __init__.py          # 包初始化文件
├── README.md            # 本文档
├── common/              # 通用API模块
│   ├── __init__.py      # 包初始化文件
│   ├── database.py      # 数据库连接模块
│   ├── models.py        # 数据模型定义
│   ├── system.py        # 系统相关接口（健康检查等）
│   └── users.py         # 用户管理接口
├── student/             # 学生端API模块
│   ├── __init__.py      # 包初始化文件
│   ├── recommendation.py # 学习推荐接口
│   ├── diagnosis.py     # 答案诊断接口
│   ├── knowledge_map.py # 知识图谱接口
│   ├── questions.py     # 练习题目接口
│   ├── wrong_questions.py # 错题集接口
│   └── stats.py         # 用户统计接口
└── teacher/             # 教师端API模块
    ├── __init__.py      # 包初始化文件
    ├── class_management.py # 班级管理接口
    ├── student_analytics.py # 学生学习分析接口
    └── assignment_management.py # 作业管理接口
```

## 模块说明

### database.py
- 提供统一的数据库连接函数 `get_db_connection()`
- 自动处理数据库路径和连接配置

### models.py
- 定义API请求和响应的数据模型
- 使用Pydantic进行数据验证
## 模块说明

### 通用模块 (common/)
#### system.py
- `/` - API根路径
- `/health` - 健康检查接口

#### users.py
- `/users` - 获取用户列表

#### database.py
- 提供数据库连接功能

#### models.py
- 定义API数据模型

### 学生端模块 (student/)
#### recommendation.py
- `/student/recommendation/{user_id}` - 获取学习推荐

#### diagnosis.py
- `/student/diagnose` - 文本答案诊断
- `/student/diagnose/image` - 图片答案诊断

#### knowledge_map.py
- `/student/knowledge-map/{user_id}` - 获取知识图谱
- `/student/knowledge-map/get-nodes` - 获取知识节点
- `/student/knowledge-map/mastery/{user_id}/{node_name}` - 获取/更新掌握度

#### questions.py
- `/student/questions/{node_name}` - 获取练习题目

#### wrong_questions.py
- `/student/wrong-questions/{user_id}` - 获取错题集

#### stats.py
- `/student/stats/{user_id}` - 获取用户统计

### 教师端模块 (teacher/)
#### class_management.py
- `/teacher/class/list/{teacher_id}` - 获取教师班级列表
- `/teacher/class/students/{class_id}` - 获取班级学生
- `/teacher/class/create` - 创建班级

#### student_analytics.py
- `/teacher/analytics/class/{class_id}/overview` - 班级概览
- `/teacher/analytics/student/{student_id}/progress` - 学生进度
- `/teacher/analytics/class/{class_id}/weak-points` - 班级薄弱点

#### assignment_management.py
- `/teacher/assignment/create` - 创建作业
- `/teacher/assignment/list/{teacher_id}` - 获取作业列表
- `/teacher/assignment/submissions/{assignment_id}` - 获取作业提交
- `/teacher/assignment/update/{assignment_id}` - 更新作业

#### knowledge_management.py
- `/teacher/knowledge/create` - 创建知识点
- `/teacher/knowledge/list` - 获取知识点列表
- `/teacher/knowledge/update/{node_id}` - 更新知识点
- `/teacher/knowledge/delete/{node_id}` - 删除知识点
- `/teacher/knowledge/prerequisites/{node_id}` - 获取知识点前置条件
- `/teacher/knowledge/detail/{node_id}` - 获取知识点详细信息



## 使用方法

1. 所有模块都使用FastAPI的APIRouter进行路由管理
2. 每个模块都有独立的错误处理
3. 统一的数据库连接和模型定义
4. 在主服务器文件中导入并注册所有路由

## 扩展新接口

1. 在api目录下创建新的模块文件
2. 定义路由和接口函数
3. 在api_server_new.py中导入并注册新路由
4. 更新本文档

## 注意事项

- 所有数据库操作都通过database.py模块进行
- 错误处理使用HTTPException
- 数据模型使用Pydantic进行验证
- 接口文档会自动生成在/docs路径