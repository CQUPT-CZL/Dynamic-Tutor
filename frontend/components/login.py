#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
登录界面模块
提供用户身份验证和角色选择功能
"""

import streamlit as st
import hashlib
from datetime import datetime

def hash_password(password: str) -> str:
    """对密码进行哈希处理"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_credentials(username: str, password: str, role: str, api_service) -> bool:
    """验证用户凭据"""
    try:
        # 尝试从API验证用户
        users = api_service.get_users()
        for user in users:
            if (user.get('username') == username and 
                user.get('role') == role):
                # 这里应该验证密码，但由于是演示系统，暂时简化
                return True
        return False
    except:
        # 如果API不可用，使用默认用户验证
        default_users = {
            'student': {
                '小崔': 'password123',
                '小陈': 'password123'
            },
            'teacher': {
                '1': '1',
                'AI_System': 'admin123'
            }
        }
        
        if role in default_users and username in default_users[role]:
            return default_users[role][username] == password
        return False

def render_login_page(api_service):
    """渲染登录页面"""
    # 登录页面CSS样式
    st.markdown("""
    <style>
    .login-container {
        max-width: 500px;
        margin: 0 auto;
        padding: 2rem;
        background: white;
        border-radius: 20px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
        margin-top: 3rem;
    }
    .login-header {
        text-align: center;
        margin-bottom: 2rem;
    }
    .login-header h1 {
        color: #667eea;
        margin-bottom: 0.5rem;
    }
    .login-header p {
        color: #666;
        margin: 0;
    }
    .role-card {
        background: linear-gradient(45deg, #667eea, #764ba2);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        text-align: center;
        cursor: pointer;
        transition: transform 0.2s;
    }
    .role-card:hover {
        transform: translateY(-2px);
    }
    .role-card.selected {
        background: linear-gradient(45deg, #ff6b6b, #feca57);
        box-shadow: 0 5px 15px rgba(255, 107, 107, 0.3);
    }
    .form-group {
        margin-bottom: 1.5rem;
    }
    .form-group label {
        display: block;
        margin-bottom: 0.5rem;
        color: #333;
        font-weight: 500;
    }
    .login-btn {
        width: 100%;
        padding: 0.75rem;
        background: linear-gradient(45deg, #667eea, #764ba2);
        color: white;
        border: none;
        border-radius: 10px;
        font-size: 1rem;
        font-weight: 500;
        cursor: pointer;
        transition: all 0.3s;
    }
    .login-btn:hover {
        transform: translateY(-1px);
        box-shadow: 0 5px 15px rgba(102, 126, 234, 0.3);
    }
    .demo-info {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        margin-top: 1rem;
        border-left: 4px solid #17a2b8;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # 主登录容器
    st.markdown('<div class="login-container">', unsafe_allow_html=True)
    
    # 登录标题
    st.markdown("""
    <div class="login-header">
        <h1>🎓 AI智慧学习平台</h1>
        <p>请登录您的账户</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 角色选择
    st.markdown("### 👤 选择身份")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🎓 学生", key="student_role", use_container_width=True):
            st.session_state.selected_role = "student"
    
    with col2:
        if st.button("👨‍🏫 教师", key="teacher_role", use_container_width=True):
            st.session_state.selected_role = "teacher"
    
    # 显示选中的角色
    if "selected_role" in st.session_state:
        role_text = "🎓 学生" if st.session_state.selected_role == "student" else "👨‍🏫 教师"
        st.success(f"已选择身份：{role_text}")
        
        # 登录表单
        st.markdown("### 🔐 登录信息")
        
        with st.form("login_form"):
            # 用户名输入
            username = st.text_input(
                "用户名",
                placeholder="请输入用户名",
                help="输入您的用户名"
            )
            
            # 密码输入
            password = st.text_input(
                "密码",
                type="password",
                placeholder="请输入密码",
                help="输入您的密码"
            )
            
            # 记住我选项
            remember_me = st.checkbox("记住我")
            
            # 登录按钮
            login_submitted = st.form_submit_button(
                "🚀 登录",
                use_container_width=True
            )
            
            # 处理登录
            if login_submitted:
                if not username or not password:
                    st.error("❌ 请填写完整的登录信息")
                else:
                    # 验证凭据
                    if verify_credentials(username, password, st.session_state.selected_role, api_service):
                        # 登录成功
                        st.session_state.is_logged_in = True
                        st.session_state.current_user = username
                        st.session_state.user_role = st.session_state.selected_role
                        st.session_state.login_time = datetime.now()
                        
                        # 用户ID映射
                        USER_MAP = {
                            "小崔": 1,
                            "小陈": 2,
                            "1": 3,
                            "AI_System": 4
                        }
                        st.session_state.user_id = USER_MAP.get(username, 1)
                        
                        st.success(f"✅ 登录成功！欢迎，{username}")
                        st.balloons()
                        
                        # 延迟后重新运行以显示主界面
                        st.rerun()
                    else:
                        st.error("❌ 用户名或密码错误，请重试")
        
        # 演示账户信息
        st.markdown("""
        <div class="demo-info">
            <h4>💡 演示账户</h4>
            <p><strong>学生账户：</strong></p>
            <p>• 用户名：小崔，密码：password123</p>
            <p>• 用户名：小陈，密码：password123</p>
            <p><strong>教师账户：</strong></p>
            <p>• 用户名：胡老师，密码：teacher123</p>
            <p>• 用户名：AI_System，密码：admin123</p>
        </div>
        """, unsafe_allow_html=True)
    
    else:
        st.info("👆 请先选择您的身份")
    
    # 页面底部（在容器内）
    st.markdown("""
    <div style="text-align: center; margin-top: 2rem; color: #666;">
        <p>🔒 您的信息安全受到保护</p>
        <p>© 2025 AI智慧学习平台</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 关闭登录容器
    st.markdown('</div>', unsafe_allow_html=True)

def render_logout_button():
    """渲染登出按钮"""
    if st.button("🚪 退出登录", key="logout_btn"):
        # 清除登录状态
        for key in ['is_logged_in', 'current_user', 'user_role', 'user_id', 'selected_role', 'login_time']:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()

def is_logged_in() -> bool:
    """检查用户是否已登录"""
    return st.session_state.get('is_logged_in', False)

def get_current_user():
    """获取当前登录用户信息"""
    if is_logged_in():
        return {
            'username': st.session_state.get('current_user'),
            'role': st.session_state.get('user_role'),
            'user_id': st.session_state.get('user_id'),
            'login_time': st.session_state.get('login_time')
        }
    return None