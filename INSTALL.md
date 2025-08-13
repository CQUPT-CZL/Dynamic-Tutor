# 📦 安装与运行指南

## 🔧 环境要求

- **Python**: 3.13+ 🐍
- **操作系统**: macOS / Linux / Windows 💻
- **包管理器**: uv (推荐) 或 pip 📦

## 🚀 快速安装

### 2️⃣ 安装依赖

#### 使用 uv (推荐) ⚡

```bash
# 安装 uv (如果还没有安装)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 安装项目依赖
uv sync
```

#### 使用 pip 📦

```bash
# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # macOS/Linux
# 或 venv\Scripts\activate  # Windows

# 安装依赖
pip install -r backend/requirements.txt
pip install streamlit pandas plotly pyvis streamlit-agraph streamlit-mermaid
```

### 3️⃣ 初始化数据库

```bash
cd data
make all
```

## 🏃‍♂️ 运行服务

### 启动后端API服务 🔧

```bash
cd backend
uv run api_server_restructured.py
```

后端服务将在 `http://localhost:8000` 启动
- 📖 API文档: http://localhost:8000/docs
- 📊 API信息: http://localhost:8000/api-info

### 启动前端界面 🎨

**新开一个终端窗口**，然后运行：

```bash
# 在项目根目录下
streamlit run frontend/pages/student/home.py --server.port 8501
```

前端界面将在 `http://localhost:8501` 启动

## 🎯 访问地址

- **前端界面**: http://localhost:8501 🌐
- **后端API**: http://localhost:8000 ⚙️
- **API文档**: http://localhost:8000/docs 📚

## 🔍 验证安装

1. 访问 http://localhost:8501 查看前端界面 ✅
2. 访问 http://localhost:8000/docs 查看API文档 ✅
3. 检查数据库文件是否生成在 `data/my_database.db` ✅

## ⚠️ 常见问题

### 端口被占用
如果端口被占用，可以修改端口：

```bash
# 修改后端端口
uvicorn api_server_restructured:app --host 0.0.0.0 --port 8001

# 修改前端端口
streamlit run frontend/pages/student/home.py --server.port 8502
```

### 依赖安装失败
确保Python版本为3.13+，并尝试升级pip：

```bash
pip install --upgrade pip
```
---


## 验证指标
验证比赛两大指标结结果
```
cd eval\src
uv run eval_qa\compare_diagnosis.py
(上面是题目诊断)

uv run eval_qa\compare_recommendations.py
(上面是路径推荐)
```

🎉 **安装完成！现在可以开始使用AI智慧学习平台了！**