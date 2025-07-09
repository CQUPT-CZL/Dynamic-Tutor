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
    if 'user_role' not in st.session_state:
        st.session_state.user_role = "student"
    if 'current_user' not in st.session_state:
        st.session_state.current_user = None
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
    /* 隐藏侧边栏 */
    .css-1d391kg {
        display: none;
    }
    
    /* 隐藏侧边栏按钮 */
    .css-1rs6os {
        display: none;
    }
    
    /* 隐藏侧边栏展开按钮 */
    .css-17eq0hr {
        display: none;
    }
    
    /* 让主内容区域占满全宽 */
    .block-container {
        padding-left: 1rem !important;
        padding-right: 1rem !important;
        max-width: none !important;
        width: 88% !important;
    }
    
    /* 调整主容器宽度 */
    .main .block-container {
        max-width: 100% !important;
        padding-top: 1rem !important;
        padding-bottom: 1rem !important;
    }
    
    /* 隐藏Streamlit的默认菜单和footer */
    #MainMenu {
        visibility: hidden;
    }
    
    footer {
        visibility: hidden;
    }
    
    /* 隐藏"Made with Streamlit"标识 */
    .css-15zrgzn {
        display: none;
    }
    
    /* 确保内容占满全宽 */
    .stApp > div:first-child {
        margin-left: 0 !important;
    }
    
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

def render_role_selector(api_service):
    """渲染角色和用户选择区域"""
    st.markdown('<div class="user-selector">', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns([1.5, 2, 2, 1])
    
    with col1:
        st.write("### 👤 选择角色")
        role = st.selectbox(
            "角色类型:",
            options=["student", "teacher"],
            format_func=lambda x: "🎓 学生" if x == "student" else "👨‍🏫 教师",
            key="role_selector"
        )
    
    with col2:
        st.write("### 👨‍🎓 选择用户")
        # 从API获取用户数据
        try:
            users = api_service.get_users()
        except:
            users = []
        
        if not users:
            # 如果API不可用，使用默认用户列表
            if role == "student":
                user_list = ["小崔", "小陈"]
            else:
                user_list = ["胡老师", "AI_System"]
        else:
            # 根据角色过滤用户
            filtered_users = [user for user in users if user.get('role') == role]
            user_list = [user['username'] for user in filtered_users]
        
        if not user_list:
            st.warning(f"没有找到{role}角色的用户")
            return None, role
            
        selected_user = st.selectbox(
            "当前用户:",
            options=user_list,
            key="user_selector"
        )
    
    with col3:
        if selected_user:
            role_emoji = "🎓" if role == "student" else "👨‍🏫"
            st.success(f"✅ {role_emoji} {selected_user}")
            
            # 显示角色说明
            if role == "student":
                st.info("📚 学生模式：学习、练习、测评")
            else:
                st.info("🔧 教师模式：管理知识点、题目、图谱")
    
    with col4:
        if st.button("🔄 切换"):
            st.session_state.current_mission = None
            st.session_state.diagnosis_result = None
            st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    return selected_user, role