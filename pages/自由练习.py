import streamlit as st

# --- 页面基础设置 ---
st.set_page_config(
    page_title="自由练习", 
    page_icon="📚",
    layout="wide"
)

# --- 自定义CSS样式 ---
st.markdown("""
<style>
.practice-header {
    background: linear-gradient(90deg, #ff6b6b 0%, #feca57 100%);
    padding: 1.5rem 2rem;
    border-radius: 15px;
    margin-bottom: 2rem;
    color: white;
    text-align: center;
}
.practice-card {
    background: white;
    padding: 2rem;
    border-radius: 15px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    margin: 1rem 0;
    border-left: 5px solid #ff6b6b;
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
</style>
""", unsafe_allow_html=True)

# --- 检查用户状态 ---
if 'user_id' not in st.session_state or not st.session_state.user_id:
    st.warning("⚠️ 请先在主页选择学习者！")
    if st.button("🏠 返回主页"):
        st.switch_page("main.py")
    st.stop()

# --- 模拟后端逻辑 ---
def get_all_knowledge_nodes():
    """获取所有可用的知识节点"""
    return {
        "ECH_DY": "二次函数定义",
        "ECH_TXXZ": "图像与性质",
        "ECH_JXS": "三种解析式",
        "ECH_ZZWT": "最值问题",
        "ECH_GX": "与方程/不等式关系"
    }

def get_node_difficulty(node_id):
    """获取知识点难度"""
    difficulty_map = {
        "ECH_DY": 1,
        "ECH_TXXZ": 3,
        "ECH_JXS": 2,
        "ECH_ZZWT": 4,
        "ECH_GX": 3
    }
    return difficulty_map.get(node_id, 1)

def get_questions_for_node(node_id):
    """获取指定知识点的多个练习题"""
    questions = {
        "ECH_DY": [
            "请写出二次函数的一般式、顶点式和零点式。",
            "什么是二次函数？请举例说明。",
            "二次函数的定义域和值域分别是什么？"
        ],
        "ECH_TXXZ": [
            "函数 f(x) = -2(x-1)² + 5 的开口方向、对称轴和顶点坐标分别是什么？",
            "如何根据二次函数的解析式判断其图像的开口方向？",
            "二次函数 y = ax² + bx + c 的对称轴公式是什么？"
        ],
        "ECH_JXS": [
            "将二次函数 y = x² - 4x + 3 转换为顶点式。",
            "已知二次函数的顶点为(2, -1)，且过点(0, 3)，求其解析式。",
            "二次函数的三种解析式之间如何相互转换？"
        ],
        "ECH_ZZWT": [
            "求函数 f(x) = x² - 6x + 8 的最小值。",
            "在区间 [-1, 3] 上，函数 f(x) = x² - 2x + 5 的最值是多少？",
            "如何利用配方法求二次函数的最值？"
        ],
        "ECH_GX": [
            "二次函数 y = x² - 5x + 6 与 x 轴的交点坐标是什么？",
            "如何利用判别式判断二次函数与 x 轴的交点个数？",
            "解不等式 x² - 3x - 4 > 0。"
        ]
    }
    return questions.get(node_id, ["抱歉，暂未收录该知识点的题目。"])

def get_user_mastery(user_id, node_id):
    """获取用户对特定知识点的掌握度"""
    user_progress = {
        "小明": {"ECH_GX": 0.4, "ECH_DY": 0.9},
        "小红": {"ECH_DY": 1.0, "ECH_TXXZ": 0.8, "ECH_JXS": 0.6},
        "小刚": {"ECH_DY": 0.3}
    }
    return user_progress.get(user_id, {}).get(node_id, 0.0)

# --- 页面标题 ---
st.markdown('<div class="practice-header"><h1>📚 自由练习</h1><p>选择你感兴趣的知识点，开始自主学习！</p></div>', unsafe_allow_html=True)

# --- 用户信息显示 ---
col1, col2, col3 = st.columns([2, 1, 1])
with col1:
    st.info(f"👨‍🎓 当前学习者：**{st.session_state.user_id}**")
with col2:
    if st.button("🔄 换个题目", type="primary"):
        if 'selected_question_index' in st.session_state:
            del st.session_state.selected_question_index
        st.rerun()
with col3:
    if st.button("🏠 返回主页"):
        st.switch_page("main.py")

# --- 知识点选择 ---
st.markdown('<div class="practice-card">', unsafe_allow_html=True)
st.write("### 🎯 选择练习知识点")

nodes = get_all_knowledge_nodes()
node_options = []
for node_id, node_name in nodes.items():
    difficulty = get_node_difficulty(node_id)
    mastery = get_user_mastery(st.session_state.user_id, node_id)
    difficulty_stars = "⭐" * difficulty
    mastery_percent = f"{mastery:.0%}"
    node_options.append(f"{node_name} ({difficulty_stars}) - 掌握度: {mastery_percent}")

selected_option = st.selectbox(
    "请选择一个知识点:",
    options=node_options,
    key="knowledge_node_selector"
)

if selected_option:
    # 解析选择的知识点
    selected_node_name = selected_option.split(" (")[0]
    selected_node_id = [id for id, name in nodes.items() if name == selected_node_name][0]
    
    # 显示知识点信息
    difficulty = get_node_difficulty(selected_node_id)
    mastery = get_user_mastery(st.session_state.user_id, selected_node_id)
    
    st.markdown('<div class="node-info">', unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("知识点", selected_node_name)
    with col2:
        st.metric("难度等级", "⭐" * difficulty)
    with col3:
        st.metric("我的掌握度", f"{mastery:.0%}")
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # --- 题目展示 ---
    questions = get_questions_for_node(selected_node_id)
    
    # 题目选择逻辑
    if 'selected_question_index' not in st.session_state:
        st.session_state.selected_question_index = 0
    
    current_question = questions[st.session_state.selected_question_index]
    
    st.markdown('<div class="question-box">', unsafe_allow_html=True)
    st.write("### 🤔 练习题目")
    st.info(f"题目 {st.session_state.selected_question_index + 1} / {len(questions)}")
    st.latex(current_question)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # --- 答题区域 ---
    st.write("### ✍️ 作答区域")
    answer = st.text_area(
        "请在此处输入你的解题过程和答案：", 
        height=150, 
        key=f"practice_answer_{selected_node_id}_{st.session_state.selected_question_index}"
    )
    
    # --- 操作按钮 ---
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("📝 提交答案", type="primary"):
            if answer:
                st.success("✅ 提交成功！")
                st.info("💡 自由练习模式暂不提供详细诊断，但你的努力很棒！继续加油！")
                st.balloons()
                
                # 模拟学习进度更新
                if mastery < 1.0:
                    new_mastery = min(mastery + 0.1, 1.0)
                    st.success(f"🎉 掌握度提升！{mastery:.0%} → {new_mastery:.0%}")
            else:
                st.error("请先输入答案！")
    
    with col2:
        if len(questions) > 1 and st.session_state.selected_question_index < len(questions) - 1:
            if st.button("➡️ 下一题"):
                st.session_state.selected_question_index += 1
                st.rerun()
    
    with col3:
        if st.session_state.selected_question_index > 0:
            if st.button("⬅️ 上一题"):
                st.session_state.selected_question_index -= 1
                st.rerun()
    
    with col4:
        if st.button("🎲 随机题目"):
            import random
            st.session_state.selected_question_index = random.randint(0, len(questions) - 1)
            st.rerun()
    
    # --- 学习提示 ---
    st.write("### 💡 学习提示")
    
    if mastery < 0.3:
        st.warning("🔰 这个知识点对你来说还比较新，建议先复习相关概念再做练习。")
        st.info("📖 推荐：先去查看知识图谱，了解相关的基础知识点。")
    elif mastery < 0.8:
        st.info("📈 你对这个知识点有一定了解，多做练习可以进一步提高掌握度。")
        st.success("💪 继续努力，你正在进步！")
    else:
        st.success("🎉 你已经很好地掌握了这个知识点！")
        st.info("🚀 可以尝试挑战更高难度的知识点，或者帮助其他同学学习。")

else:
    st.markdown('</div>', unsafe_allow_html=True)

# --- 快速导航 ---
st.write("### 🚀 其他学习选项")
col1, col2 = st.columns(2)
with col1:
    if st.button("📋 开始今日任务", use_container_width=True):
        st.switch_page("pages/今日任务.py")
with col2:
    if st.button("🗺️ 查看知识图谱", use_container_width=True):
        st.switch_page("pages/我的知识图谱.py")