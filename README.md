<div align="center">

# 🎓 AI智慧学习平台

<img src="static/登录界面.png" alt="AI智慧学习平台" width="800" style="border-radius: 15px; box-shadow: 0 10px 30px rgba(0,0,0,0.3); margin: 20px 0;">

[![Python](https://img.shields.io/badge/Python-3.13+-3776ab?style=for-the-badge&logo=python&logoColor=white)](https://python.org) [![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com) [![Streamlit](https://img.shields.io/badge/Streamlit-1.46+-ff4b4b?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io) [![SQLite](https://img.shields.io/badge/SQLite-3.0+-003b57?style=for-the-badge&logo=sqlite&logoColor=white)](https://sqlite.org)

### 🚀 基于AI驱动的个性化学习平台，助力教育数字化转型

**✨ 智能诊断 • 📊 数据驱动 • 🎯 个性化推荐 • 🗺️ 知识图谱可视化**

---

[🎯 核心特性](#-核心特性) • [🚀 快速开始](#-快速开始) • [📖 API文档](#-api文档) • [🤝 贡献指南](#-贡献指南)

</div>

---

## 📖 项目简介

**AI智慧学习平台** 是一个现代化的教育科技解决方案，采用前后端分离架构，为学生提供个性化学习体验，为教师提供智能教学管理工具。平台集成了AI答案诊断、知识图谱可视化、个性化推荐等前沿技术，致力于提升学习效率和教学质量。

### 🎯 设计理念

- **🤖 AI驱动**: 智能诊断、个性化推荐、自适应学习路径
- **📊 数据驱动**: 基于学习数据的精准分析和决策支持
- **🎨 用户体验**: 直观友好的界面设计，流畅的交互体验
- **🔧 技术先进**: 现代化技术栈，高性能、高可扩展性
- **📱 响应式**: 支持多设备访问，随时随地学习

---

## ✨ 核心特性

### 🎓 学生端功能

<table>
<tr>
<td width="50%">

#### 📋 智能任务推荐
- 🎯 **个性化推荐**: AI分析学习历史，智能推荐学习内容
- 📈 **学习路径**: 自动规划最优学习顺序和进度
- ⏰ **进度跟踪**: 实时显示学习进度和完成情况
- 🔔 **智能提醒**: 错题复习和学习计划提醒

#### 🎯 自由练习模式
- 🗺️ **可视化图谱**: 可收起的知识图谱，直观展示掌握度
- 🎮 **点击练习**: 点击知识点即可开始对应题目练习
- 🤖 **实时诊断**: AI实时诊断答案，提供详细反馈
- 📊 **动态更新**: 根据答题情况实时更新掌握度

</td>
<td width="50%">

#### 🗺️ 知识图谱分析
- 🌐 **可视化展示**: D3.js驱动的交互式知识图谱
- 📊 **掌握度分析**: 详细的掌握度统计和分布分析
- 💡 **学习建议**: 基于掌握度的个性化学习建议
- 🎨 **进度可视化**: 每个知识点的掌握进度动态展示

#### 📊 智能测评系统
- 🎯 **能力评估**: 全面评估各知识点掌握情况
- 📈 **成绩分析**: 详细的答题统计和趋势分析
- 🔍 **弱项识别**: 自动识别薄弱知识点
- 💪 **提升建议**: 针对性的学习改进建议

</td>
</tr>
</table>

### 👨‍🏫 教师端功能

<table>
<tr>
<td width="50%">

#### 📚 知识点管理
- ✏️ **CRUD操作**: 创建、编辑、删除知识点
- 🎚️ **难度设置**: 设置知识点难度等级和学习目标
- 📦 **批量管理**: 支持批量导入和编辑操作
- 📊 **使用统计**: 知识点使用情况和效果分析

#### 📝 题目管理系统
- 📋 **多类型支持**: 选择题、填空题、解答题等
- 🖼️ **图片上传**: 支持题目图片上传和管理
- 🏷️ **智能标注**: 设置题目难度和知识点关联
- 🔄 **状态管理**: 草稿、发布状态智能管理

</td>
<td width="50%">

#### 🕸️ 知识图谱构建
- 🎨 **可视化编辑**: 拖拽式知识点关系构建
- 🔗 **关系类型**: 支持多种知识点关系定义
- 👁️ **实时预览**: 实时预览知识图谱结构
- ⚡ **批量操作**: 批量添加和修改关系

#### 📈 学生数据分析（暂未开发）
- 📊 **学习数据**: 学生学习行为和成绩深度分析
- 🎯 **掌握度统计**: 班级知识点掌握度分布
- 🛤️ **学习轨迹**: 学生学习路径和时间分析
- 📋 **报告生成**: 自动生成详细学习报告

</td>
</tr>
</table>

---

## 🏗️ 技术架构

### 系统架构图

![系统架构图](static/架构图.png)


### 🛠️ 技术栈

<table>
<tr>
<td width="50%">

**🎨 前端技术栈**
- **Streamlit 1.46+** - 快速构建交互式Web应用
- **Python 3.13+** - 主要编程语言
- **D3.js** - 知识图谱可视化
- **Pandas** - 数据处理与分析
- **Plotly** - 数据可视化图表
- **CSS3** - 自定义样式与响应式设计

</td>
<td width="50%">

**⚙️ 后端技术栈**
- **FastAPI 0.115+** - 高性能异步API框架
- **SQLite** - 轻量级关系型数据库
- **Pydantic** - 数据验证与序列化
- **Uvicorn** - ASGI高性能服务器
- **Python-multipart** - 文件上传支持
- **Neo4j** - 图数据库支持（可选）

</td>
</tr>
</table>

### 🏛️ 架构优势

- **🔄 前后端分离**: 独立开发、部署、扩展，技术栈灵活
- **🛠️ 服务层设计**: 统一接口封装，错误处理，模拟服务支持
- **📦 模块化设计**: 角色分离，页面模块化，API模块化
- **🗄️ 数据库设计**: 关系型设计，支持复杂查询和事务
- **🤖 AI集成**: 智能诊断，个性化推荐，易于扩展

---

## 📁 项目结构

```
unveiling-the-list/
├── 📁 frontend/                    # 🎨 前端应用
│   ├── 🚀 app.py                  # 主应用入口
│   ├── ⚙️ config.py               # 配置和样式
│   ├── 📁 components/             # 🧩 组件模块
│   │   ├── login.py              # 登录组件
│   │   └── question_practice.py  # 练习组件
│   ├── 📁 services/               # 🔧 服务层
│   │   ├── api_service.py        # API服务封装
│   │   └── mock_api_service.py   # 模拟API服务
│   └── 📁 pages/                  # 📄 页面模块
│       ├── 📁 student/            # 🎓 学生端页面
│       │   ├── daily_tasks.py    # 今日任务
│       │   ├── free_practice.py  # 自由练习
│       │   ├── knowledge_map.py  # 知识图谱
│       │   ├── self_assessment.py # 自我测评
│       │   └── wrong_questions.py # 错题集
│       └── 📁 teacher/            # 👨‍🏫 教师端页面
│           ├── knowledge_management.py      # 知识点管理
│           ├── question_management.py       # 题目管理
│           └── knowledge_graph_builder.py   # 知识图谱构建
├── 📁 backend/                     # ⚙️ 后端API服务器
│   ├── 🚀 api_server_restructured.py # FastAPI服务器
│   ├── 🔧 init_database.py        # 数据库初始化
│   ├── 📄 requirements.txt        # 后端依赖
│   ├── 📁 uploads/                # 📁 文件上传目录
│   └── 📁 api/                    # 🔌 API模块
│       ├── 📁 common/             # 🔧 通用模块
│       ├── 📁 student/            # 🎓 学生端API
│       └── 📁 teacher/            # 👨‍🏫 教师端API
├── 📁 data/                       # 🗄️ 数据文件
│   ├── my_database.db            # SQLite数据库
│   ├── create_tables.sql         # 数据库表结构
│   └── import_data.py            # 数据导入脚本
├── 📁 test/                       # 🧪 测试文件
├── 🚀 start_system.py             # 系统启动脚本（静默模式）
├── 🚀 start_system_verbose.py     # 系统启动脚本（详细输出）
├── 📄 pyproject.toml              # 项目配置文件
└── 📖 README.md                   # 项目说明
```

---

## 🚀 快速开始

### 📋 环境要求

- **Python**: 3.13+ 🐍
- **操作系统**: Windows / macOS / Linux 💻
- **内存**: 建议 4GB+ 🧠
- **磁盘空间**: 500MB+ 💾

### ⚡ 一键启动（推荐）

```bash
# 克隆项目
git clone https://github.com/CQUPT-CZL/Dynamic-Tutor.git
cd Dynamic-Tutor

# 安装依赖（推荐使用 uv）
pip install uv
uv sync

# 一键启动系统
python start_system.py
```

### 🔧 手动启动（开发模式）

<details>
<summary>点击展开详细步骤</summary>

#### 1️⃣ 安装依赖

```bash
# 方式一：使用 uv（推荐）
pip install uv
uv sync

# 方式二：使用 pip
pip install -r backend/requirements.txt
```

#### 2️⃣ 启动后端

```bash
cd backend
python init_database.py          # 初始化数据库
python api_server_restructured.py # 启动API服务器
```

#### 3️⃣ 启动前端（新终端）

```bash
cd frontend
streamlit run app.py --server.port 8501
```

</details>

### 🌐 访问地址

启动成功后，您可以通过以下地址访问系统：

| 🎯 服务 | 🔗 地址 | 📝 说明 |
|---------|---------|----------|
| 🎨 **前端应用** | http://localhost:8501 | 学生和教师界面 |
| ⚙️ **后端API** | http://localhost:8000 | RESTful API服务 |
| 📚 **API文档** | http://localhost:8000/docs | 交互式API文档 |
| 🔍 **健康检查** | http://localhost:8000/health | 系统状态检查 |

### 👥 默认用户账号

| 👤 用户名 | 🎭 角色 | 📝 说明 |
|-----------|---------|----------|
| 小崔 | 🎓 学生 | 学生端功能演示 |
| 小陈 | 🎓 学生 | 学生端功能演示 |
| 舵老师 | 👨‍🏫 教师 | 教师端功能演示 |

---

## 📖 API文档

本平台提供完整的RESTful API接口，支持学生端和教师端的所有功能。API采用角色分离设计，提供高性能的服务支持。

### 📚 文档资源

<div align="center">

| 📋 文档类型 | 🔗 访问地址 | 📝 说明 |
|-------------|-------------|----------|
| **🔗 交互式API文档** | [http://localhost:8000/docs](http://localhost:8000/docs) | Swagger UI，支持在线测试 |
| **📄 完整API文档** | [API_DOCUMENTATION.md](API_DOCUMENTATION.md) | 详细的API接口说明文档 |
| **🔍 API信息接口** | [http://localhost:8000/api-info](http://localhost:8000/api-info) | 获取API结构信息 |
| **💚 健康检查** | [http://localhost:8000/health](http://localhost:8000/health) | 系统状态检查 |

</div>

### 🎯 API特性

- **🔄 角色分离**: 学生端(`/student/`)和教师端(`/teacher/`)接口完全分离
- **📊 功能完整**: 涵盖学习推荐、答案诊断、知识图谱、数据分析等核心功能
- **🖼️ 多模态支持**: 支持文本和图片答案诊断
- **⚡ 高性能**: 基于FastAPI的异步处理，支持高并发访问
- **📝 标准化**: 统一的请求响应格式和错误处理机制

> 💡 **提示**: 建议开发者优先查看交互式API文档进行接口测试，详细的接口说明请参考完整API文档。

---

## 🐛 故障排除

<details>
<summary>🔧 常见问题及解决方案</summary>

### 🔌 后端连接问题

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

### 🌐 前端访问问题

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

### 🗄️ 数据库问题

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

### 📦 依赖问题

**问题**: 模块导入错误

```bash
# 重新安装依赖
pip install -r backend/requirements.txt

# 或使用 uv
uv sync

# 检查Python版本
python --version  # 需要 3.13+
```

</details>

---

## 🧪 测试

### 🔬 运行测试

```bash
# 运行所有测试
python -m pytest test/

# 运行特定测试
python test/test_api.py
python test/test_database.py
python test/check_data_info.py
```

### 📊 测试覆盖

- ✅ **API测试**: 覆盖所有API接口
- ✅ **数据库测试**: 测试数据库操作和约束
- ✅ **集成测试**: 测试前后端集成功能
- ✅ **性能测试**: 关键功能的性能测试

---

## 🤝 贡献指南

### 🚀 参与贡献

1. **🍴 Fork项目**: 点击右上角Fork按钮
2. **📥 克隆仓库**: `git clone https://github.com/your-username/unveiling-the-list.git`
3. **🌿 创建分支**: `git checkout -b feature/new-feature`
4. **💻 开发功能**: 按照开发规范进行开发
5. **🧪 测试验证**: 确保所有测试通过
6. **📝 提交代码**: `git commit -m "Add new feature"`
7. **🚀 推送分支**: `git push origin feature/new-feature`
8. **🔄 创建PR**: 在GitHub上创建Pull Request

### 📝 提交规范

```bash
# 提交信息格式
type(scope): description

# 示例
feat(student): add knowledge map interaction
fix(api): resolve database connection issue
docs(readme): update installation guide
```

### 🔍 代码审查

- ✅ 所有PR需要经过代码审查
- ✅ 确保代码符合项目规范
- ✅ 添加必要的测试用例
- ✅ 更新相关文档

---

## 📊 项目统计

<div align="center">

| 📈 指标 | 📊 数值 |
|---------|----------|
| **开发语言** | Python 3.13+ |
| **代码行数** | 约 5000+ 行 |
| **API接口** | 30+ 个 |
| **功能模块** | 学生端5个，教师端4个 |
| **数据表** | 8个核心表 |
| **测试覆盖** | 80%+ |

</div>



---

## 📞 联系方式

<div align="center">

### 🛠️ 技术支持

📧 **邮箱**: 1522518cui@gmail.com
🐛 **问题反馈**: [GitHub Issues](https://github.com/CQUPT-CZL/Dynamic-Tutor/issues)  
💬 **讨论交流**: [GitHub Discussions](https://github.com/CQUPT-CZL/Dynamic-Tutor/discussions)

### 👨‍💻 开发团队

**项目负责人**: czl 
**项目开始**: 2025年

---

### 🎓 AI智慧学习平台 v2.0

**🚀 让学习更智能，让教育更高效！**

[![GitHub stars](https://img.shields.io/github/stars/CQUPT-CZL/Dynamic-Tutor?style=social)](https://github.com/CQUPT-CZL/Dynamic-Tutor)
[![GitHub forks](https://img.shields.io/github/forks/CQUPT-CZL/Dynamic-Tutor?style=social)](https://github.com/CQUPT-CZL/Dynamic-Tutor)
[![GitHub issues](https://img.shields.io/github/issues/CQUPT-CZL/Dynamic-Tutor)](https://github.com/CQUPT-CZL/Dynamic-Tutor/issues)

**如果这个项目对您有帮助，请给我们一个 ⭐ Star！**

</div>
