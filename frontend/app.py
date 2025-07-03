#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI智慧学习平台 - 前端应用
使用Streamlit构建，通过API与后端交互
"""

import streamlit as st
import requests
import json
from typing import Dict, List, Any
import time
from datetime import datetime

# 导入页面模块
from pages import daily_tasks, free_practice, knowledge_map, self_assessment, wrong_questions
from config import init_session_state, render_user_selector, load_css

# API配置
API_BASE_URL = "http://localhost:8000/api"

class APIClient:
    """API客户端类，处理与后端的HTTP通信"""
    
    def __init__(self, base_url: str = API_BASE_URL):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json",
            "Accept": "application/json"
        })
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """发送HTTP请求的通用方法"""
        url = f"{self.base_url}{endpoint}"
        try:
            response = self.session.request(method, url, **kwargs)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            st.error(f"API请求失败: {e}")
            return {"error": str(e)}
    
    def get_users(self) -> List[Dict[str, str]]:
        """获取用户列表"""
        result = self._make_request("GET", "/users")
        return result if isinstance(result, list) else []
    
    def get_recommendation(self, user_id: str) -> Dict[str, Any]:
        """获取用户推荐"""
        return self._make_request("GET", f"/recommendation/{user_id}")
    
    def diagnose_answer(self, user_id: str, question_id: str, answer: str, 
                       answer_type: str = "text", time_spent: int = None, 
                       confidence: float = None) -> Dict[str, Any]:
        """诊断答案"""
        data = {
            "user_id": user_id,
            "question_id": question_id,
            "answer": answer,
            "answer_type": answer_type
        }
        if time_spent is not None:
            data["time_spent"] = time_spent
        if confidence is not None:
            data["confidence"] = confidence
        
        return self._make_request("POST", "/diagnose", json=data)
    
    def get_knowledge_map(self, user_id: str) -> List[Dict[str, Any]]:
        """获取知识图谱"""
        result = self._make_request("GET", f"/knowledge-map/{user_id}")
        return result if isinstance(result, list) else []
    
    def get_knowledge_nodes(self) -> Dict[str, str]:
        """获取知识节点"""
        result = self._make_request("GET", "/knowledge-nodes")
        return result.get("nodes", {}) if isinstance(result, dict) else {}
    
    def get_user_mastery(self, user_id: str, node_name: str) -> float:
        """获取用户掌握度"""
        result = self._make_request("GET", f"/mastery/{user_id}/{node_name}")
        return result.get("mastery", 0.0) if isinstance(result, dict) else 0.0
    
    def get_questions_for_node(self, node_name: str) -> List[str]:
        """获取知识点练习题"""
        result = self._make_request("GET", f"/questions/{node_name}")
        return result.get("questions", []) if isinstance(result, dict) else []
    
    def get_wrong_questions(self, user_id: str) -> List[Dict[str, Any]]:
        """获取错题集"""
        result = self._make_request("GET", f"/wrong-questions/{user_id}")
        return result.get("wrong_questions", []) if isinstance(result, dict) else []
    
    def get_user_stats(self, user_id: str) -> Dict[str, Any]:
        """获取用户统计"""
        return self._make_request("GET", f"/stats/{user_id}")
    
    def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        return self._make_request("GET", "/health")

def check_api_connection(api_client: APIClient) -> bool:
    """检查API连接状态"""
    try:
        health = api_client.health_check()
        return health.get("status") == "healthy"
    except:
        return False



def main():
    """主应用函数"""
    # 初始化API客户端
    if "api_client" not in st.session_state:
        st.session_state.api_client = APIClient()
    
    api_client = st.session_state.api_client
    
    # 检查API连接
    if "api_connected" not in st.session_state:
        st.session_state.api_connected = check_api_connection(api_client)
    
    # 初始化页面配置
    init_session_state()
    
    # 加载CSS样式
    load_css()
    
    # 渲染顶部标题栏
    st.markdown("""
    <div class="main-header">
        <h1>🎓 AI智慧学习平台</h1>
        <p>个性化学习，智能推荐，助力学习进步</p>
    </div>
    """, unsafe_allow_html=True)
    
    # API连接状态显示
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.session_state.api_connected:
            st.success("🟢 后端API连接正常")
        else:
            st.error("🔴 后端API连接失败，请确保后端服务器正在运行")
            if st.button("🔄 重新连接"):
                st.session_state.api_connected = check_api_connection(api_client)
                st.rerun()
    
    # 如果API未连接，显示启动说明
    if not st.session_state.api_connected:
        st.markdown("""
        ### 📋 启动说明
        
        请按以下步骤启动后端服务器：
        
        1. **打开终端**，进入项目的 `backend` 目录
        2. **安装依赖**：
           ```bash
           pip install -r requirements.txt
           ```
        3. **启动后端服务器**：
           ```bash
           python api_server.py
           ```
        4. **等待服务器启动**，看到 "🚀 启动AI智慧学习平台API服务器..." 后点击上方的重新连接按钮
        
        后端服务器将在 `http://localhost:8000` 运行
        """)
        return
    
    # 渲染用户选择区域
    render_user_selector(api_client)
    
    # 如果没有选择用户，显示用户选择提示
    if not st.session_state.current_user:
        st.info("👆 请先选择一个用户开始学习")
        return
    
    # 主要功能区域
    st.markdown("---")
    
    # 创建标签页
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📋 今日任务", 
        "🎯 自由练习", 
        "🗺️ 知识图谱", 
        "📊 自我测评", 
        "❌ 错题集"
    ])
    
    # 今日任务页面
    with tab1:
        daily_tasks.render_daily_tasks_page(api_client, st.session_state.current_user)
    
    # 自由练习页面
    with tab2:
        free_practice.render_free_practice_page(api_client, st.session_state.current_user)
    
    # 知识图谱页面
    with tab3:
        knowledge_map.render_knowledge_map_page(api_client, st.session_state.current_user)
    
    # 自我测评页面
    with tab4:
        self_assessment.render_self_assessment_page(api_client, st.session_state.current_user)
    
    # 错题集页面
    with tab5:
        wrong_questions.render_wrong_questions_page(api_client, st.session_state.current_user)
    
    # 页面底部信息
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; padding: 20px;">
        <p>🎓 AI智慧学习平台 v2.0 | 前后端分离版本</p>
        <p>API文档: <a href="http://localhost:8000/docs" target="_blank">http://localhost:8000/docs</a></p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()