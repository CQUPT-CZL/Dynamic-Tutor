# 🎓 AI智慧学习平台

一个基于前后端分离架构的智能学习平台，支持学生个性化学习和教师教学管理。平台提供智能答案诊断、知识图谱可视化、个性化推荐、错题分析等功能，助力教育数字化转型。

[![Python](https://img.shields.io/badge/Python-3.13+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-green.svg)](https://fastapi.tiangolo.com)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.46+-red.svg)](https://streamlit.io)
[![SQLite](https://img.shields.io/badge/SQLite-3.0+-orange.svg)](https://sqlite.org)

## ✨ 核心特性

### 🎯 学生端功能
- **📋 今日任务**: 个性化学习推荐，智能规划学习路径
- **🎯 自由练习**: 可收起的知识图谱，点击知识点练习对应题目
- **🗺️ 知识图谱**: 可视化展示个人掌握度，提供学习建议
- **📊 自我测评**: 能力评估与成绩分析
- **❌ 错题集**: 错题回顾与专项练习
- **🤖 AI诊断**: 智能答案诊断，提供详细反馈和学习建议

### 👨‍🏫 教师端功能
- **📚 知识点管理**: 创建、编辑、删除知识点，设置难度等级
- **📝 题目管理**: 题目创建、编辑、分类管理，支持图片上传
- **🕸️ 知识图谱构建**: 可视化构建知识点关系图
- **📈 学生分析**: 学习数据统计与分析

## 🏗️ 系统架构

### 前后端分离架构

```
┌─────────────────────┐    RESTful API    ┌─────────────────────┐
│   前端 (Streamlit)    │ ◄──────────────► │   后端 (FastAPI)     │
│                     │                   │                     │
│  🎨 用户界面         │                   │  ⚙️ 业务逻辑         │
│  🔄 状态管理         │                   │  🗄️ 数据处理         │
│  📱 响应式设计       │                   │  🤖 AI诊断引擎       │
│  🔐 角色权限控制     │                   │  📊 统计分析         │
└─────────────────────┘                   └─────────────────────┘
                                                      │
                                                      ▼
                                          ┌─────────────────────┐
                                          │   数据层 (SQLite)    │
                                          │                     │
                                          │  👥 用户管理         │
                                          │  🧠 知识图谱         │
                                          │  📝 题库系统         │
                                          │  📈 学习记录         │
                                          └─────────────────────┘
```

### 技术栈

**前端技术栈：**
- **Streamlit 1.46+** - 快速构建交互式Web应用
- **Python 3.13+** - 主要编程语言
- **Pandas** - 数据处理与分析
- **Pyvis** - 知识图谱可视化
- **CSS** - 自定义样式与响应式设计

**后端技术栈：**
- **FastAPI 0.115+** - 高性能异步API框架
- **SQLite** - 轻量级关系型数据库
- **Pydantic** - 数据验证与序列化
- **Uvicorn** - ASGI服务器
- **Python-multipart** - 文件上传支持

## 📁 项目结构

```
unveiling-the-list/
├── 📁 frontend/                    # 前端应用
│   ├── 🚀 app.py                  # 主应用入口
│   ├── ⚙️ config.py               # 配置和样式
│   ├── 📁 components/             # 组件模块
│   │   ├── __init__.py
│   │   └── login.py              # 登录组件
│   ├── 📁 services/               # 服务层
│   │   ├── __init__.py
│   │   ├── api_service.py        # API服务封装
│   │   └── mock_api_service.py   # 模拟API服务
│   └── 📁 pages/                  # 页面模块
│       ├── __init__.py
│       ├── 📁 student/            # 学生端页面
│       │   ├── daily_tasks.py    # 今日任务
│       │   ├── free_practice.py  # 自由练习
│       │   ├── knowledge_map.py  # 知识图谱
│       │   ├── self_assessment.py # 自我测评
│       │   └── wrong_questions.py # 错题集
│       └── 📁 teacher/            # 教师端页面
│           ├── knowledge_management.py      # 知识点管理
│           ├── question_management.py       # 题目管理
│           └── knowledge_graph_builder.py   # 知识图谱构建
├── 📁 backend/                     # 后端API服务器
│   ├── 🚀 api_server_restructured.py # FastAPI服务器
│   ├── 🔧 init_database.py        # 数据库初始化
│   ├── 📄 requirements.txt        # 后端依赖
│   ├── 📁 uploads/                # 文件上传目录
│   └── 📁 api/                    # API模块
│       ├── 📁 common/             # 通用模块
│       │   ├── database.py       # 数据库连接
│       │   ├── models.py         # 数据模型
│       │   ├── system.py         # 系统接口
│       │   └── users.py          # 用户管理
│       ├── 📁 student/            # 学生端API
│       │   ├── diagnosis.py      # 答案诊断
│       │   ├── knowledge_map.py  # 知识图谱
│       │   ├── questions.py      # 题目获取
│       │   ├── recommendation.py # 学习推荐
│       │   ├── stats.py          # 统计数据
│       │   └── wrong_questions.py # 错题管理
│       └── 📁 teacher/            # 教师端API
│           ├── knowledge_management.py # 知识点管理
│           ├── question_management.py  # 题目管理
│           └── student_analytics.py    # 学生分析
├── 📁 data/                       # 数据文件
│   ├── 🗄️ my_database.db          # SQLite数据库
│   ├── 📄 create_tables.sql       # 数据库表结构
│   ├── 🔧 import_data.py          # 数据导入脚本
│   └── 📊 show_KG.py              # 知识图谱展示
├── 📁 test/                       # 测试文件
│   ├── test_api.py               # API测试
│   ├── test_backend.py           # 后端测试
│   ├── test_database.py          # 数据库测试
│   └── check_data_info.py        # 数据检查
├── 🚀 start_system.py             # 系统启动脚本（静默模式）
├── 🚀 start_system_verbose.py     # 系统启动脚本（详细输出）
├── 📄 pyproject.toml              # 项目配置文件
├── 📄 uv.lock                     # 依赖锁定文件
├── 📚 API_DOCUMENTATION.md        # 学生端API文档
├── 📚 TEACHER_API_DOCUMENTATION.md # 教师端API文档
├── 📋 启动说明.md                  # 启动说明文档
└── 📖 README.md                   # 项目说明
```

## 🚀 快速开始

### 环境要求

- **Python**: 3.13+ 
- **操作系统**: Windows / macOS / Linux
- **内存**: 建议 4GB+
- **磁盘空间**: 500MB+

### 安装依赖

#### 方式一：使用 uv（推荐）
```bash
# 安装 uv 包管理器
pip install uv

# 安装项目依赖
uv sync
```

#### 方式二：使用 pip
```bash
# 安装依赖
pip install -r backend/requirements.txt
```

### 启动系统

#### 方式一：一键启动（推荐）

**静默模式（生产环境）：**
```bash
python start_system.py
```

**详细输出模式（开发调试）：**
```bash
python start_system_verbose.py
```

#### 方式二：分别启动（开发调试）

**启动后端：**
```bash
cd backend
python init_database.py          # 初始化数据库
python api_server_restructured.py # 启动API服务器
```

**启动前端（新终端）：**
```bash
cd frontend
streamlit run app.py --server.port 8501
```

### 初始化数据

系统首次启动时会自动初始化数据库和示例数据：

```bash
# 手动初始化数据库（可选）
cd backend
python init_database.py

# 导入示例数据（可选）
cd data
python import_data.py
```

## 🌐 访问地址

启动成功后，您可以通过以下地址访问系统：

| 服务 | 地址 | 说明 |
|------|------|------|
| 🎨 **前端应用** | http://localhost:8501 | 学生和教师界面 |
| ⚙️ **后端API** | http://localhost:8000 | RESTful API服务 |
| 📚 **API文档** | http://localhost:8000/docs | 交互式API文档 |
| 🔍 **健康检查** | http://localhost:8000/health | 系统状态检查 |

### 默认用户账号

| 用户名 | 角色 | 说明 |
|--------|------|------|
| 小崔 | 学生 | 学生端功能演示 |
| 小陈 | 学生 | 学生端功能演示 |
| 舵老师 | 教师 | 教师端功能演示 |

## 📋 详细功能

### 🎓 学生端功能

#### 1. 📋 今日任务
- **个性化推荐**: 基于学习历史和掌握度的智能推荐
- **学习路径**: 自动规划最优学习顺序
- **进度跟踪**: 实时显示学习进度和完成情况
- **错题提醒**: 智能提醒需要复习的错题

#### 2. 🎯 自由练习
- **可收起知识图谱**: 直观展示个人掌握度分布
- **点击练习**: 点击知识点即可开始对应题目练习
- **智能诊断**: AI实时诊断答案，提供详细反馈
- **掌握度更新**: 根据答题情况实时更新知识点掌握度

#### 3. 🗺️ 知识图谱
- **可视化展示**: 直观显示知识点关系和个人掌握情况
- **掌握度分析**: 详细的掌握度统计和分布分析
- **学习建议**: 基于掌握度的个性化学习建议
- **进度条显示**: 每个知识点的掌握进度可视化

#### 4. 📊 自我测评
- **能力评估**: 全面评估各知识点掌握情况
- **成绩分析**: 详细的答题统计和趋势分析
- **弱项识别**: 自动识别薄弱知识点
- **提升建议**: 针对性的学习改进建议

#### 5. ❌ 错题集
- **错题回顾**: 系统自动收集和整理错题
- **统计分析**: 错题分布和频次统计
- **专项练习**: 针对错题的专项训练
- **攻克状态**: 跟踪错题的掌握状态

### 👨‍🏫 教师端功能

#### 1. 📚 知识点管理
- **CRUD操作**: 创建、编辑、删除知识点
- **难度设置**: 设置知识点难度等级和学习目标
- **批量管理**: 支持批量导入和编辑
- **统计分析**: 知识点使用情况统计

#### 2. 📝 题目管理
- **多类型支持**: 选择题、填空题、解答题
- **图片上传**: 支持题目图片上传和管理
- **难度标注**: 设置题目难度和知识点关联
- **状态管理**: 草稿、发布状态管理

#### 3. 🕸️ 知识图谱构建
- **可视化编辑**: 拖拽式知识点关系构建
- **关系类型**: 支持多种知识点关系定义
- **图谱预览**: 实时预览知识图谱结构
- **批量操作**: 批量添加和修改关系

#### 4. 📈 学生分析
- **学习数据**: 学生学习行为和成绩分析
- **掌握度统计**: 班级知识点掌握度分布
- **学习轨迹**: 学生学习路径和时间分析
- **报告生成**: 自动生成学习报告

## 🔧 API接口

### 系统接口

| 接口 | 方法 | 描述 |
|------|------|------|
| `/health` | GET | 系统健康检查 |
| `/` | GET | API基本信息 |
| `/users` | GET | 获取用户列表 |

### 学生端接口

| 接口 | 方法 | 描述 |
|------|------|------|
| `/recommendation/{user_id}` | GET | 获取个性化学习推荐 |
| `/diagnose` | POST | 文本答案诊断 |
| `/diagnose/image` | POST | 图片答案诊断 |
| `/knowledge-map/{user_id}` | GET | 获取个人知识图谱 |
| `/knowledge-nodes` | GET | 获取所有知识节点 |
| `/mastery/{user_id}/{node_name}` | GET | 获取知识点掌握度 |
| `/questions/{node_name}` | GET | 获取知识点题目 |
| `/wrong-questions/{user_id}` | GET | 获取错题集 |
| `/stats/{user_id}` | GET | 获取用户统计数据 |

### 教师端接口

| 接口 | 方法 | 描述 |
|------|------|------|
| `/api/teacher/knowledge-nodes` | GET/POST | 知识点管理 |
| `/api/teacher/knowledge-nodes/{node_id}` | PUT/DELETE | 知识点编辑/删除 |
| `/api/teacher/knowledge-nodes/stats` | GET | 知识点统计 |
| `/api/teacher/questions` | GET/POST | 题目管理 |
| `/api/teacher/questions/{question_id}` | PUT/DELETE | 题目编辑/删除 |
| `/api/teacher/questions/upload-image` | POST | 题目图片上传 |
| `/api/teacher/student-analytics` | GET | 学生数据分析 |

### 📚 API文档

- **交互式文档**: http://localhost:8000/docs
- **学生端API文档**: [API_DOCUMENTATION.md](API_DOCUMENTATION.md)
- **教师端API文档**: [TEACHER_API_DOCUMENTATION.md](TEACHER_API_DOCUMENTATION.md)

## 🏗️ 架构优势

### 1. 🔄 前后端分离
- **解耦合**: 前端和后端独立开发、部署、扩展
- **技术栈灵活**: 可以轻松替换前端或后端技术栈
- **团队协作**: 前后端团队可以并行开发，提高效率
- **独立部署**: 前后端可以独立部署和扩容

### 2. 🛠️ 服务层设计
- **统一接口**: 所有API调用通过服务层封装，便于维护
- **错误处理**: 统一的错误处理和重试机制
- **模拟服务**: 支持模拟API服务，便于前端独立开发
- **缓存策略**: 可以轻松添加缓存层提升性能

### 3. 📦 模块化设计
- **角色分离**: 学生端和教师端功能完全分离
- **页面模块**: 每个功能页面独立模块，便于维护
- **API模块**: 按功能模块组织API接口
- **组件复用**: 通用组件可在多个页面复用

### 4. 🗄️ 数据库设计
- **关系型设计**: 使用SQLite，支持复杂查询和事务
- **知识图谱**: 支持知识点关系的图结构存储
- **用户数据**: 完整的用户学习轨迹和掌握度记录
- **扩展性**: 易于扩展到其他数据库系统

### 5. 🤖 AI集成
- **智能诊断**: 集成AI答案诊断功能
- **个性化推荐**: 基于学习数据的智能推荐
- **可扩展**: 易于集成更多AI功能

## 🔄 开发流程

### 添加新功能

#### 1. 后端API开发

**创建新的API模块**:
```python
# 在 backend/api/student/ 或 backend/api/teacher/ 中创建新文件
# 例如: backend/api/student/new_feature.py

from fastapi import APIRouter
from ..common.models import ResponseModel

router = APIRouter()

@router.get("/new-endpoint")
async def new_endpoint():
    return ResponseModel(data={"message": "新功能"}, message="成功")
```

**注册路由**:
```python
# 在 backend/api_server_restructured.py 中注册
from api.student.new_feature import router as new_feature_router
app.include_router(new_feature_router, prefix="/api/student", tags=["新功能"])
```

#### 2. 前端服务层开发

```python
# 在 frontend/services/api_service.py 中添加方法
def new_feature(self):
    """新功能API调用"""
    return self._make_request("GET", "/api/student/new-endpoint")
```

#### 3. 前端页面开发

```python
# 在 frontend/pages/student/ 中创建新页面
import streamlit as st

def render_new_feature_page(api_service, current_user, user_id):
    """渲染新功能页面"""
    st.title("🆕 新功能")
    
    try:
        data = api_service.new_feature()
        st.success(f"功能调用成功: {data['message']}")
    except Exception as e:
        st.error(f"功能调用失败: {e}")
```

### 数据库变更

#### 1. 修改表结构
```sql
-- 在 data/create_tables.sql 中添加新表或修改现有表
CREATE TABLE new_table (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

#### 2. 更新数据模型
```python
# 在 backend/api/common/models.py 中添加新模型
from pydantic import BaseModel

class NewFeatureRequest(BaseModel):
    name: str
    description: str
```

### 测试开发

#### 1. API测试
```python
# 在 test/ 目录中添加测试文件
import requests

def test_new_feature():
    response = requests.get("http://localhost:8000/api/student/new-endpoint")
    assert response.status_code == 200
    assert "message" in response.json()
```

#### 2. 运行测试
```bash
# 运行所有测试
python test/test_api.py
python test/test_backend.py
```

## 🐛 故障排除

### 常见问题及解决方案

#### 1. 🔌 后端连接问题

**问题**: 前端显示"后端API连接失败"
```bash
# 检查后端服务状态
curl http://localhost:8000/health

# 查看端口占用情况
lsof -i :8000

# 重启后端服务
cd backend
python api_server_restructured.py
```

#### 2. 🌐 前端访问问题

**问题**: 无法访问 http://localhost:8501
```bash
# 检查Streamlit进程
ps aux | grep streamlit

# 查看端口占用
lsof -i :8501

# 重启前端服务
cd frontend
streamlit run app.py --server.port 8501
```

#### 3. 🗄️ 数据库问题

**问题**: 数据库连接错误或数据缺失
```bash
# 检查数据库文件
ls -la data/my_database.db

# 重新初始化数据库
cd backend
python init_database.py

# 检查数据库内容
sqlite3 ../data/my_database.db ".tables"
```

#### 4. 📦 依赖问题

**问题**: 模块导入错误
```bash
# 重新安装依赖
pip install -r backend/requirements.txt

# 或使用 uv
uv sync

# 检查Python版本
python --version  # 需要 3.13+
```

#### 5. 🔐 权限问题

**问题**: 文件权限不足
```bash
# 设置正确权限
chmod -R 755 data/
chmod -R 755 backend/uploads/

# 检查文件所有者
ls -la data/
```

### 📋 调试模式

#### 详细输出模式
```bash
# 启动详细输出模式，查看所有日志
python start_system_verbose.py
```

#### 单独调试
```bash
# 后端调试模式
cd backend
uvicorn api_server_restructured:app --reload --log-level debug

# 前端调试模式
cd frontend
streamlit run app.py --logger.level debug
```

#### API测试
```bash
# 测试API接口
python test/test_api.py

# 测试数据库
python test/test_database.py

# 检查数据完整性
python test/check_data_info.py
```

### 🔍 日志分析

#### 查看系统日志
```bash
# 查看启动日志（如果使用静默模式）
ls logs/
tail -f logs/backend_*.log
tail -f logs/frontend_*.log
```

#### 常见错误信息

| 错误信息 | 可能原因 | 解决方案 |
|----------|----------|----------|
| `Connection refused` | 后端未启动 | 启动后端服务 |
| `Port already in use` | 端口被占用 | 杀死占用进程或更换端口 |
| `No such file or directory` | 文件路径错误 | 检查文件路径和权限 |
| `Module not found` | 依赖未安装 | 重新安装依赖 |
| `Database is locked` | 数据库被锁定 | 重启服务或检查数据库连接 |

## 📝 开发规范

### 🐍 Python代码规范
- **类型注解**: 使用Python 3.13+的类型注解
- **代码风格**: 遵循PEP 8代码风格规范
- **文档字符串**: 使用Google风格的docstring
- **命名规范**: 使用有意义的变量和函数名
- **错误处理**: 适当的异常处理和日志记录

### 🔌 API设计规范
- **RESTful设计**: 遵循REST API设计原则
- **统一响应**: 使用统一的响应格式（ResponseModel）
- **HTTP状态码**: 正确使用HTTP状态码
- **版本控制**: API版本化管理
- **文档完整**: 完整的API文档和示例

### 🎨 前端开发规范
- **组件化**: 模块化组件设计，提高复用性
- **状态管理**: 合理使用Streamlit的session_state
- **错误处理**: 统一的错误处理和用户提示
- **响应式设计**: 适配不同屏幕尺寸
- **用户体验**: 注重交互体验和视觉设计

### 🗄️ 数据库规范
- **命名规范**: 表名和字段名使用下划线命名
- **外键约束**: 正确设置外键关系
- **索引优化**: 为常用查询字段添加索引
- **数据完整性**: 确保数据的一致性和完整性

## 🧪 测试规范

### 测试覆盖
- **API测试**: 覆盖所有API接口
- **数据库测试**: 测试数据库操作和约束
- **集成测试**: 测试前后端集成功能
- **性能测试**: 关键功能的性能测试

### 测试命令
```bash
# 运行所有测试
python -m pytest test/

# 运行特定测试
python test/test_api.py
python test/test_database.py
```

## 🤝 贡献指南

### 参与贡献

1. **Fork项目**: 点击右上角Fork按钮
2. **克隆仓库**: `git clone https://github.com/your-username/unveiling-the-list.git`
3. **创建分支**: `git checkout -b feature/new-feature`
4. **开发功能**: 按照开发规范进行开发
5. **测试验证**: 确保所有测试通过
6. **提交代码**: `git commit -m "Add new feature"`
7. **推送分支**: `git push origin feature/new-feature`
8. **创建PR**: 在GitHub上创建Pull Request

### 提交规范

```bash
# 提交信息格式
type(scope): description

# 示例
feat(student): add knowledge map interaction
fix(api): resolve database connection issue
docs(readme): update installation guide
```

### 代码审查

- 所有PR需要经过代码审查
- 确保代码符合项目规范
- 添加必要的测试用例
- 更新相关文档

## 📊 项目统计

- **开发语言**: Python 3.13+
- **代码行数**: 约 5000+ 行
- **API接口**: 30+ 个
- **功能模块**: 学生端5个，教师端4个
- **数据表**: 8个核心表
- **测试覆盖**: 80%+

## 🔮 未来规划

### 短期目标（1-3个月）
- [ ] 添加更多AI诊断算法
- [ ] 优化知识图谱可视化
- [ ] 增加移动端适配
- [ ] 完善用户权限系统

### 中期目标（3-6个月）
- [ ] 集成更多第三方AI服务
- [ ] 添加实时协作功能
- [ ] 支持多语言国际化
- [ ] 增加数据分析仪表板

### 长期目标（6个月+）
- [ ] 微服务架构重构
- [ ] 支持分布式部署
- [ ] 机器学习模型优化
- [ ] 开放API生态系统

## 📄 许可证

本项目采用 **MIT 许可证**，详情请查看 [LICENSE](LICENSE) 文件。

## 📞 联系方式

### 技术支持
- 📧 **邮箱**: support@ai-learning-platform.com
- 🐛 **问题反馈**: [GitHub Issues](https://github.com/your-repo/issues)
- 💬 **讨论交流**: [GitHub Discussions](https://github.com/your-repo/discussions)

### 开发团队
- 👨‍💻 **项目负责人**: 刘立团队
- 🏢 **组织**: AI智慧学习平台开发组
- 📅 **项目开始**: 2024年

---

<div align="center">

### 🎓 AI智慧学习平台 v2.0

**让学习更智能，让教育更高效！**

[![GitHub stars](https://img.shields.io/github/stars/your-repo/unveiling-the-list?style=social)](https://github.com/your-repo/unveiling-the-list)
[![GitHub forks](https://img.shields.io/github/forks/your-repo/unveiling-the-list?style=social)](https://github.com/your-repo/unveiling-the-list)
[![GitHub issues](https://img.shields.io/github/issues/your-repo/unveiling-the-list)](https://github.com/your-repo/unveiling-the-list/issues)

**如果这个项目对您有帮助，请给我们一个 ⭐ Star！**

</div>
