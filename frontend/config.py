import streamlit as st

def init_page_config():
    """初始化页面基础设置"""
    st.set_page_config(
        page_title="AI智慧学习平台",
        page_icon="🎓",
        layout="wide",
        initial_sidebar_state="collapsed"
    )

def init_session_state():
    """初始化Session State"""
    if 'user_name' not in st.session_state:
        st.session_state.user_name = "默认用户"
    if 'user_id' not in st.session_state:
        st.session_state.user_id = 1
    if 'current_mission' not in st.session_state:
        st.session_state.current_mission = None
    if 'diagnosis_result' not in st.session_state:
        st.session_state.diagnosis_result = None
    if 'selected_question_index' not in st.session_state:
        st.session_state.selected_question_index = 0

def load_custom_css():
    """加载自定义CSS样式"""
    st.markdown("""
    <style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        color: white;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .user-selector {
        background: linear-gradient(45deg, #ff6b6b, #feca57);
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        color: white;
    }
    .welcome-card {
        background: white;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin: 1rem 0;
        border-left: 5px solid #667eea;
    }
    .task-card {
        background: white;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin: 1rem 0;
        border-left: 5px solid #4facfe;
    }
    .knowledge-card {
        background: white;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin: 1rem 0;
        border-left: 5px solid #667eea;
    }
    .practice-card {
        background: white;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin: 1rem 0;
        border-left: 5px solid #ff6b6b;
    }
    .concept-box {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #28a745;
        margin: 1rem 0;
    }
    .question-box {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #17a2b8;
        margin: 1rem 0;
    }
    .node-info {
        background: linear-gradient(45deg, #667eea, #764ba2);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        margin: 1rem 0;
    }
    .stats-box {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        text-align: center;
        margin: 1rem 0;
    }
    /* 隐藏默认的标签页样式 */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        padding-left: 20px;
        padding-right: 20px;
        background-color: #f0f2f6;
        border-radius: 10px 10px 0px 0px;
        color: #262730;
        font-weight: 500;
    }
    .stTabs [aria-selected="true"] {
        background-color: #667eea;
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)

def render_header():
    """渲染顶部标题栏"""
    st.markdown('<div class="main-header"><h1>🎓 AI智慧学习平台</h1><p>个性化学习，智能化成长</p></div>', unsafe_allow_html=True)

def render_user_selector(api_service):
    """渲染用户选择区域"""
    st.markdown('<div class="user-selector">', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([2, 2, 1])
    with col1:
        st.write("### 👨‍🎓 选择学习者")
    with col2:
        # 从API获取用户数据
        users = api_service.get_users()
        
        if not users:
            st.warning("无法获取用户列表，请检查后端连接")
            return None
            
        user_list = [user['username'] for user in users]
        selected_user = st.selectbox(
            "当前学习者:",
            options=user_list,
            index=user_list.index(st.session_state.user_id) if st.session_state.user_id in user_list else 0,
            key="user_selector"
        )
        
        if st.session_state.user_id != selected_user:
            st.session_state.user_id = selected_user
            st.session_state.current_mission = None
            st.session_state.diagnosis_result = None
            st.rerun()
    with col3:
        st.success(f"✅ {st.session_state.user_id}")
    st.markdown('</div>', unsafe_allow_html=True)
    
    return st.session_state.user_id