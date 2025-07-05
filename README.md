# 🎓 AI智慧学习平台

一个基于前后端分离架构的智能学习平台，提供个性化学习推荐、智能答案诊断、知识图谱可视化等功能。

## 🏗️ 架构设计

### 前后端分离架构

```
┌─────────────────┐    HTTP API    ┌─────────────────┐
│   前端 (Streamlit) │ ◄──────────► │   后端 (FastAPI) │
│                 │               │                 │
│  - 用户界面      │               │  - 业务逻辑      │
│  - 交互逻辑      │               │  - 数据处理      │
│  - 状态管理      │               │  - AI诊断        │
└─────────────────┘               └─────────────────┘
```

### 技术栈

**前端技术栈：**
- Streamlit - 快速构建Web应用
- Python - 主要编程语言
- CSS - 自定义样式

**后端技术栈：**
- FastAPI - 高性能API框架
- SQLite - 轻量级数据库
- Pydantic - 数据验证
- Uvicorn - ASGI服务器

## 📁 项目结构

```
unveiling-the-list/
├── frontend/                 # 前端应用
│   ├── app.py               # 主应用入口
│   ├── config.py            # 配置和样式
│   ├── services/            # 服务层
│   │   ├── __init__.py
│   │   └── api_service.py   # API服务封装
│   └── pages/               # 页面模块
│       ├── __init__.py
│       ├── home.py          # 首页
│       ├── daily_tasks.py   # 今日任务
│       ├── free_practice.py # 自由练习
│       ├── knowledge_map.py # 知识图谱
│       ├── self_assessment.py # 自我测评
│       └── wrong_questions.py # 错题集
├── backend/                  # 后端API服务器
│   ├── api_server.py        # FastAPI服务器
│   └── requirements.txt     # 后端依赖
├── data/                    # 数据文件
│   └── my_database.db       # SQLite数据库
├── start_system.py          # 系统启动脚本
├── API_DOCUMENTATION.md     # API文档
└── README.md               # 项目说明
```

## 🚀 快速开始

### 方法一：一键启动（推荐）

```bash
# 1. 安装依赖
pip install -r backend/requirements.txt

# 2. 一键启动前后端
python start_system.py
```

### 方法二：分别启动

```bash
# 1. 安装依赖
pip install -r backend/requirements.txt

# 2. 启动后端API服务器
cd backend
python api_server.py

# 3. 新开终端，启动前端应用
cd frontend
streamlit run app.py
```

## 🌐 访问地址

- **前端应用**: http://localhost:8501
- **后端API**: http://localhost:8000
- **API文档**: http://localhost:8000/docs

## 📋 功能模块

### 1. 今日任务 📋
- 个性化学习推荐
- 学习进度统计
- 错题提醒

### 2. 自由练习 🎯
- 知识点选择
- 题目练习
- 掌握度跟踪

### 3. 知识图谱 🗺️
- 知识点可视化
- 掌握度分析
- 学习建议

### 4. 自我测评 📊
- 能力评估
- 成绩分析
- 学习建议

### 5. 错题集 ❌
- 错题回顾
- 统计分析
- 专项练习

## 🔧 API接口

### 核心接口

| 接口 | 方法 | 描述 |
|------|------|------|
| `/health` | GET | 健康检查 |
| `/users` | GET | 获取用户列表 |
| `/recommendation/{user_id}` | GET | 获取学习推荐 |
| `/diagnose` | POST | 答案诊断 |
| `/knowledge-map/{user_id}` | GET | 获取知识图谱 |
| `/wrong-questions/{user_id}` | GET | 获取错题集 |
| `/stats/{user_id}` | GET | 获取用户统计 |

详细API文档请访问：http://localhost:8000/docs

## 🏗️ 架构优势

### 1. 前后端分离
- **解耦合**: 前端和后端独立开发、部署
- **可扩展**: 可以轻松替换前端或后端技术栈
- **团队协作**: 前后端团队可以并行开发

### 2. 服务层设计
- **统一接口**: 所有API调用通过服务层封装
- **错误处理**: 统一的错误处理和重试机制
- **缓存策略**: 可以轻松添加缓存层

### 3. 模块化设计
- **页面模块**: 每个功能页面独立模块
- **服务模块**: API调用逻辑独立封装
- **配置模块**: 样式和配置集中管理

## 🔄 开发流程

### 添加新功能

1. **后端开发**:
   ```python
   # 在 backend/api_server.py 中添加新接口
   @app.get("/new-endpoint")
   async def new_endpoint():
       return {"message": "新功能"}
   ```

2. **前端服务层**:
   ```python
   # 在 frontend/services/api_service.py 中添加方法
   def new_feature(self):
       return self._make_request("GET", "/new-endpoint")
   ```

3. **前端页面**:
   ```python
   # 在 frontend/pages/ 中创建新页面
   def render_new_page(api_service, current_user):
       data = api_service.new_feature()
       # 渲染页面
   ```

## 🐛 故障排除

### 常见问题

1. **后端连接失败**
   - 检查后端服务器是否启动
   - 确认端口8000未被占用
   - 查看后端日志

2. **前端无法访问**
   - 检查Streamlit是否正常启动
   - 确认端口8501未被占用
   - 查看前端日志

3. **数据库错误**
   - 确认 `data/my_database.db` 文件存在
   - 检查数据库权限
   - 查看数据库连接配置

### 日志查看

```bash
# 后端日志
cd backend
python api_server.py

# 前端日志
cd frontend
streamlit run app.py --logger.level debug
```

## 📝 开发规范

### 代码规范
- 使用Python类型注解
- 遵循PEP 8代码风格
- 添加适当的注释和文档字符串

### API设计规范
- 使用RESTful API设计原则
- 统一的响应格式
- 适当的HTTP状态码

### 前端规范
- 模块化组件设计
- 统一的错误处理
- 响应式布局

## 🤝 贡献指南

1. Fork 项目
2. 创建功能分支
3. 提交更改
4. 推送到分支
5. 创建 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 📞 联系方式

如有问题或建议，请通过以下方式联系：

- 提交 Issue
- 发送邮件
- 项目讨论区

---

🎓 **AI智慧学习平台** - 让学习更智能，让进步更高效！
