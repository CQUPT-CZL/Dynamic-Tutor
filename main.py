import streamlit as st

# --- 页面基础设置 ---
st.set_page_config(
    page_title="AI自适应学习系统",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 初始化Session State ---
# Session State是Streamlit中用于在不同页面间保持变量的关键
if 'user_id' not in st.session_state:
    st.session_state.user_id = None
if 'current_mission' not in st.session_state:
    st.session_state.current_mission = None
if 'diagnosis_result' not in st.session_state:
    st.session_state.diagnosis_result = None

# --- 主页面内容 ---
st.title("🧠 AI自适应学习系统・原型")
st.markdown("---")

st.sidebar.title("👨‍🎓 学生中心")
# --- 用户选择 ---
# 在真实系统中，这里会是登录界面
# 在原型中，我们用一个下拉框来模拟用户切换
user_list = ["小明", "小红", "小刚"]
selected_user = st.sidebar.selectbox(
    "请选择当前学生:",
    options=user_list,
    index=user_list.index(st.session_state.user_id) if st.session_state.user_id else 0
)

# 当用户切换时，重置状态
if st.session_state.user_id != selected_user:
    st.session_state.user_id = selected_user
    st.session_state.current_mission = None
    st.session_state.diagnosis_result = None
    st.rerun() # 重新运行页面以更新状态

st.sidebar.success(f"当前学生: **{st.session_state.user_id}**")
st.sidebar.info("请从左侧选择一个页面开始你的学习之旅。")


st.header("欢迎使用AI自适应学习系统！")
st.write(f"你好，**{st.session_state.user_id}**！本系统将根据你的学习情况，为你量身定制学习路径。")
st.image("https://images.unsplash.com/photo-1541339907198-e08756dedf3f?q=80&w=2070", caption="开启你的智慧学习之旅")