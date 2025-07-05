# API模块说明

本目录包含AI智慧学习平台的后端API接口，按功能模块分离，便于维护和扩展。

## 目录结构

```
api/
├── __init__.py          # 包初始化文件
├── database.py          # 数据库连接模块
├── models.py            # 数据模型定义
├── system.py            # 系统相关接口（健康检查等）
├── users.py             # 用户管理接口
├── recommendation.py    # 学习推荐接口
├── diagnosis.py         # 答案诊断接口
├── knowledge_map.py     # 知识图谱接口
├── questions.py         # 练习题目接口
├── wrong_questions.py   # 错题集接口
└── stats.py             # 用户统计接口
```

## 模块说明

### database.py
- 提供统一的数据库连接函数 `get_db_connection()`
- 自动处理数据库路径和连接配置

### models.py
- 定义API请求和响应的数据模型
- 使用Pydantic进行数据验证

### system.py
- `/` - API根路径
- `/health` - 健康检查接口

### users.py
- `/users` - 获取用户列表

### recommendation.py
- `/recommendation/{user_id}` - 获取用户学习推荐

### diagnosis.py
- `/diagnose/` - 诊断文本答案
- `/diagnose/image` - 诊断图片答案

### knowledge_map.py
- `/knowledge-map/{user_id}` - 获取用户知识图谱
- `/knowledge-map/nodes/all` - 获取所有知识节点
- `/knowledge-map/mastery/{user_id}/{node_name}` - 获取/更新用户掌握度

### questions.py
- `/questions/{node_name}` - 获取知识点练习题

### wrong_questions.py
- `/wrong-questions/{user_id}` - 获取错题集

### stats.py
- `/stats/{user_id}` - 获取用户统计信息

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