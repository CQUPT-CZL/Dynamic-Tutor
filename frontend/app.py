#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI智慧学习平台 - 前端应用
使用Streamlit构建，通过API与后端交互
支持教师和学生两种角色
"""

import streamlit as st
from datetime import datetime

# 导入页面模块
from pages.student import daily_tasks, free_practice, knowledge_map, self_assessment, wrong_questions
from pages.teacher import knowledge_management, question_management, knowledge_graph_builder
from components.login import render_login_page, render_logout_button, is_logged_in, get_current_user
from config import init_session_state, load_custom_css
from services import get_api_service

def check_api_connection(api_service) -> bool:
    """检查API连接状态"""
    try:
        health = api_service.health_check()
        print(health)
        return health.get("status") == "healthy"
    except:
        return False



def render_student_interface(api_service):
    """渲染学生界面"""
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

def render_teacher_interface(api_service):
    """渲染教师界面"""
    # 创建标签页
    tab1, tab2, tab3 = st.tabs([
        "📚 知识点管理", 
        "📝 题目管理", 
        "🕸️ 知识图谱构建"
    ])
    
    # 知识点管理页面
    with tab1:
        knowledge_management.render_knowledge_management_page(api_service, st.session_state.current_user, st.session_state.user_id)
    
    # 题目管理页面
    with tab2:
        question_management.render_question_management_page(api_service, st.session_state.current_user, st.session_state.user_id)
    
    # 知识图谱构建页面
    with tab3:
        knowledge_graph_builder.render_knowledge_graph_builder_page(api_service, st.session_state.current_user, st.session_state.user_id)

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
    
    # 检查用户是否已登录
    if not is_logged_in():
        # 显示登录页面
        render_login_page(api_service)
        return
    
    # 用户已登录，显示主界面
    current_user_info = get_current_user()
    current_user = current_user_info['username']
    user_role = current_user_info['role']
    
    # 渲染顶部标题栏和用户信息
    col1, col2 = st.columns([2.5, 1.5])
    
    with col1:
        st.markdown("""
        <div class="main-header" style="padding: 1.5rem 0 0.5rem 0; background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); border-radius: 16px 16px 0 0; box-shadow: 0 4px 16px rgba(102,126,234,0.08);">
            <h1 style="color: #fff; font-size: 2.6rem; margin-bottom: 0.2em; letter-spacing: 2px;">🎓 AI智慧学习平台</h1>
            <p style="color: #f3f3f3; font-size: 1.15rem; margin: 0;">个性化学习，智能推荐，助力学习进步 🚀</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        role_emoji = "🎓" if user_role == "student" else "👨‍🏫"
        role_text = "学生" if user_role == "student" else "教师"
        st.markdown(f"""
        <div style="text-align: center; padding: 1.5rem 0.5rem; background: linear-gradient(135deg, #43cea2 0%, #185a9d 100%); color: white; border-radius: 16px; margin-top: 1rem; box-shadow: 0 2px 8px rgba(67,206,162,0.10);">
            <h4 style='font-size: 1.3rem; margin-bottom: 0.3em;'>{role_emoji} {current_user}</h4>
            <p style="margin: 0; font-size: 1.05rem; letter-spacing: 1px;">{role_text}模式</p>
        </div>
        """, unsafe_allow_html=True)
    
    # with col3:
    #     st.markdown("<div style='margin-top: 2.5rem;'></div>", unsafe_allow_html=True)
    #     render_logout_button()
    
    # API连接状态显示
    if st.session_state.api_connected:
        st.success("🟢 后端API连接正常")
    else:
        st.error("🔴 后端API连接失败")
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            if st.button("🔄 重新连接API", use_container_width=True):
                st.session_state.api_connected = check_api_connection(api_service)
                st.rerun()
    
    # 主要功能区域
    st.markdown("---")
    
    # 根据角色渲染不同界面
    if user_role == "student":
        render_student_interface(api_service)
    elif user_role == "teacher":
        render_teacher_interface(api_service)
    
    # 页面底部信息
    # st.markdown("---")
    st.markdown("""
        <div style='
            height: 4px;
            background: linear-gradient(90deg, 
                #FF6B6B 0%, 
                #4ECDC4 33%, 
                #45B7D1 66%, 
                #96E6A1 100%
            );
            margin: 1.5rem 0;
            border-radius: 2px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        '></div>
    """, unsafe_allow_html=True)
    st.markdown(f"""
    <div style="text-align: center; color: #666; padding: 22px 0 10px 0; background: linear-gradient(90deg, #f8fafc 60%, #e0e7ff 100%); border-radius: 0 0 18px 18px; margin-top: 2rem; box-shadow: 0 -2px 12px rgba(118,75,162,0.06);">
        <p style="font-size: 1.1rem; margin-bottom: 0.5em;">🎓 <b>AI智慧学习平台 v2.0</b> | 登录版本</p>
        <p style="margin: 0.2em 0;">登录时间: {current_user_info['login_time'].strftime('%Y-%m-%d %H:%M:%S')}</p>
        <p style="margin: 0.2em 0; font-size: 0.95rem; color: #aaa;">© 2025 刘立团队</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()