import streamlit as st
import pandas as pd

def render_home_page():
    """渲染学习首页"""
    st.markdown('<div class="welcome-card">', unsafe_allow_html=True)
    st.header(f"欢迎回来，{st.session_state.user_id}！🌟")
    st.write("### 🎯 你的学习概览")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("今日学习时长", "45分钟", "↗️ +15分钟")
    with col2:
        st.metric("掌握知识点", "12个", "↗️ +2个")
    with col3:
        st.metric("学习连续天数", "7天", "🔥")

    st.write("### 📈 学习进度")
    progress_data = pd.DataFrame({
        '日期': ['周一', '周二', '周三', '周四', '周五', '周六', '周日'],
        '学习时长(分钟)': [30, 45, 25, 60, 40, 35, 45]
    })
    st.line_chart(progress_data.set_index('日期'))

    st.write("### 🎉 最近成就")
    achievements = [
        "🏆 连续学习7天",
        "📚 完成二次函数基础学习",
        "⭐ 获得'勤奋学习者'徽章",
        "🎯 今日任务完成率100%"
    ]
    for achievement in achievements:
        st.success(achievement)

    st.image("https://images.unsplash.com/photo-1522202176988-66273c2fd55f?q=80&w=2071", 
             caption="继续你的学习之旅！", use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)