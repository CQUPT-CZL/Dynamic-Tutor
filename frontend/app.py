import streamlit as st
import sys
import os

# 添加当前目录到Python路径，以便导入模块
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 导入配置和页面模块
from config import init_page_config, init_session_state, load_custom_css, render_header, render_user_selector
from pages.home import render_home_page
from pages.daily_tasks import render_daily_tasks_page
from pages.knowledge_map import render_knowledge_map_page
from pages.free_practice import render_free_practice_page

def main():
    """主应用函数"""
    # 初始化页面配置
    init_page_config()
    
    # 初始化Session State
    init_session_state()
    
    # 加载自定义CSS样式
    load_custom_css()
    
    # 渲染顶部标题栏
    render_header()
    
    # 渲染用户选择区域
    render_user_selector()
    
    # 主导航标签页
    tab1, tab2, tab3, tab4 = st.tabs(["🏠 学习首页", "📋 今日任务", "🗺️ 知识图谱", "📚 自由练习"])
    
    # 渲染各个页面
    with tab1:
        render_home_page()
    
    with tab2:
        render_daily_tasks_page()
    
    with tab3:
        render_knowledge_map_page()
    
    with tab4:
        render_free_practice_page()

if __name__ == "__main__":
    main()