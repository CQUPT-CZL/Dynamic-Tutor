#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI智慧学习平台 - 前端应用
使用Streamlit构建，通过API与后端交互
"""

import streamlit as st
from datetime import datetime

# 导入页面模块
from pages import daily_tasks, free_practice, knowledge_map, self_assessment, wrong_questions
from config import init_session_state, render_user_selector, load_custom_css
from services import get_api_service

def check_api_connection(api_service) -> bool:
    """检查API连接状态"""
    try:
        health = api_service.health_check()
        print(health)
        return health.get("status") == "healthy"
    except:
        return False



def main():
    """主应用函数"""
    # 初始化API服务
    api_service = get_api_service()
    
    # 检查API连接
    if "api_connected" not in st.session_state:
        st.session_state.api_connected = check_api_connection(api_service)
    
    # 初始化页面配置
    init_session_state()
    
    # 加载CSS样式
    load_custom_css()
    
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
                st.session_state.api_connected = check_api_connection(api_service)
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
    current_user = render_user_selector(api_service)
    st.session_state.current_user = current_user

    USER_MAP = {
        "小崔": 1,
        "小陈": 2,
        "小胡": 3
    }
    if current_user:
        st.session_state.user_id = USER_MAP[current_user]

    print(current_user)
    
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
        daily_tasks.render_daily_tasks_page(api_service, st.session_state.current_user, st.session_state.user_id)
    
    # 自由练习页面
    with tab2:
        free_practice.render_free_practice_page(api_service, st.session_state.current_user, st.session_state.user_id)
    
    # 知识图谱页面
    with tab3:
        knowledge_map.render_knowledge_map_page(api_service, st.session_state.current_user, st.session_state.user_id)
    
    # 自我测评页面
    with tab4:
        self_assessment.render_self_assessment_page(api_service, st.session_state.current_user, st.session_state.user_id)
    
    # 错题集页面
    with tab5:
        wrong_questions.render_wrong_questions_page(api_service, st.session_state.current_user, st.session_state.user_id)
    
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