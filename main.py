import streamlit as st
import pandas as pd

# --- 页面基础设置 ---
st.set_page_config(
    page_title="AI智慧学习平台",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="auto"
)

# --- 初始化Session State ---
if 'user_id' not in st.session_state:
    st.session_state.user_id = "小明"
if 'current_mission' not in st.session_state:
    st.session_state.current_mission = None
if 'diagnosis_result' not in st.session_state:
    st.session_state.diagnosis_result = None

# --- 自定义CSS样式 ---
st.markdown("""
<style>
.main-header {
    background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
    padding: 1rem 2rem;
    border-radius: 10px;
    margin-bottom: 2rem;
    color: white;
    text-align: center;
}
.user-info {
    background: linear-gradient(45deg, #ff6b6b, #feca57);
    padding: 0.5rem 1rem;
    border-radius: 20px;
    color: white;
    font-weight: bold;
    display: inline-block;
    margin-bottom: 1rem;
}
.welcome-card {
    background: white;
    padding: 2rem;
    border-radius: 15px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    margin: 1rem 0;
}
</style>
""", unsafe_allow_html=True)

# --- 顶部标题栏 ---
st.markdown('<div class="main-header"><h1>🎓 AI智慧学习平台</h1><p>个性化学习，智能化成长</p></div>', unsafe_allow_html=True)

# --- 侧边栏用户选择 ---
with st.sidebar:
    st.header("👨‍🎓 学习者中心")
    user_list = ["小明", "小红", "小刚"]
    selected_user = st.selectbox(
        "选择学习者:",
        options=user_list,
        index=user_list.index(st.session_state.user_id) if st.session_state.user_id in user_list else 0
    )
    
    if st.session_state.user_id != selected_user:
        st.session_state.user_id = selected_user
        st.session_state.current_mission = None
        st.session_state.diagnosis_result = None
        st.rerun()
    
    st.success(f"当前学习者: {st.session_state.user_id}")
    
    st.markdown("---")
    st.write("### 📚 导航")
    st.page_link("pages/今日任务.py", label="📋 今日任务", icon="📋")
    st.page_link("pages/我的知识图谱.py", label="🗺️ 知识图谱", icon="🗺️")
    st.page_link("pages/自由练习.py", label="📚 自由练习", icon="📚")

# --- 主页内容 ---
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

# --- 快速导航 ---
st.write("### 🚀 快速开始")
col1, col2, col3 = st.columns(3)
with col1:
    if st.button("📋 开始今日任务", use_container_width=True):
        st.switch_page("pages/今日任务.py")
with col2:
    if st.button("🗺️ 查看知识图谱", use_container_width=True):
        st.switch_page("pages/我的知识图谱.py")
with col3:
    if st.button("📚 自由练习", use_container_width=True):
        st.switch_page("pages/自由练习.py")