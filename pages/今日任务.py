import streamlit as st
import time

# --- 页面基础设置 ---
st.set_page_config(
    page_title="今日任务", 
    page_icon="📋",
    layout="wide"
)

# --- 自定义CSS样式 ---
st.markdown("""
<style>
.task-header {
    background: linear-gradient(90deg, #4facfe 0%, #00f2fe 100%);
    padding: 1.5rem 2rem;
    border-radius: 15px;
    margin-bottom: 2rem;
    color: white;
    text-align: center;
}
.task-card {
    background: white;
    padding: 2rem;
    border-radius: 15px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    margin: 1rem 0;
    border-left: 5px solid #4facfe;
}
.concept-box {
    background: #f8f9fa;
    padding: 1.5rem;
    border-radius: 10px;
    border-left: 4px solid #28a745;
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
def get_recommendation_for_user(user_id):
    """模拟为用户生成一个推荐任务"""
    if user_id == "小明":
        return {
            "mission_id": "M001",
            "reason": "根据你上次的练习，我们发现你对 **二次函数零点** 的概念有些混淆。",
            "type": "概念重学与练习",
            "content": {
                "concept_text": "函数零点的定义：对于函数y=f(x)，我们把使f(x)=0的实数x叫做这个函数的零点。",
                "question_text": "求函数 f(x) = x² - 5x + 6 的零点。",
                "question_id": "Q102"
            }
        }
    elif user_id == "小红":
        return {
            "mission_id": "M002",
            "reason": "你已经掌握了二次函数的基础性质，非常棒！我们来挑战一个新知识点吧！",
            "type": "新知探索",
            "content": {
                "concept_text": "函数最值的定义：函数在某个区间内的最大值或最小值。",
                "question_text": "求函数 f(x) = x² - 2x + 3 在区间 [0, 3] 上的最大值和最小值。",
                "question_id": "Q201"
            }
        }
    else:
        return {
            "mission_id": "M003",
            "reason": "让我们从一个基础题开始今天的学习吧！",
            "type": "基础练习",
            "content": {
                 "question_text": "判断函数 f(x) = x³ 的奇偶性。",
                 "question_id": "Q301"
            }
        }

def diagnose_answer(user_id, question_id, answer):
    """模拟诊断用户的答案"""
    if not answer:
        return {"status": "error", "message": "答案不能为空哦！"}
    # 模拟AI思考过程
    time.sleep(2) 
    if "x=2" in answer and "x=3" in answer:
        return {
            "status": "success",
            "diagnosis": "回答正确！你对因式分解法求解二次方程掌握得很扎实。",
            "next_recommendation": "建议你继续学习二次函数的图像性质。"
        }
    else:
        return {
            "status": "partial",
            "diagnosis": "答案不够完整。提示：可以尝试因式分解 x² - 5x + 6 = (x-2)(x-3)。",
            "hint": "当 (x-2)(x-3) = 0 时，x = 2 或 x = 3"
        }

# --- 页面标题 ---
st.markdown('<div class="task-header"><h1>📋 今日学习任务</h1><p>AI为你精心准备的个性化学习任务</p></div>', unsafe_allow_html=True)

# --- 用户信息显示 ---
col1, col2, col3 = st.columns([2, 1, 1])
with col1:
    st.info(f"👨‍🎓 当前学习者：**{st.session_state.user_id}**")
with col2:
    if st.button("🎲 获取新任务", type="primary"):
        st.session_state.current_mission = None
        st.session_state.diagnosis_result = None
        st.rerun()
with col3:
    if st.button("🏠 返回主页"):
        st.switch_page("main.py")

# --- 获取或显示任务 ---
if not st.session_state.current_mission:
    with st.spinner("🤖 AI正在为你定制学习任务..."):
        time.sleep(1.5)
        st.session_state.current_mission = get_recommendation_for_user(st.session_state.user_id)

mission = st.session_state.current_mission

# --- 任务卡片设计 ---
st.markdown('<div class="task-card">', unsafe_allow_html=True)
st.subheader(f"📚 任务类型: {mission['type']}")
st.success(f"💡 **推荐理由**: {mission['reason']}")

# 如果任务包含概念学习
if "concept_text" in mission['content']:
    st.markdown('<div class="concept-box">', unsafe_allow_html=True)
    st.write("### 📖 知识回顾")
    st.markdown(f"**{mission['content']['concept_text']}**")
    st.markdown('</div>', unsafe_allow_html=True)

# 题目展示与作答
st.markdown("---")
st.write("### 🤔 练习题目")
st.info(f"题目ID: {mission['content']['question_id']}")
st.latex(mission['content']['question_text'])

answer = st.text_area("请在此处输入你的解题过程和答案：", height=150, key="mission_answer")

col1, col2 = st.columns([1, 3])
with col1:
    if st.button("提交答案", type="primary"):
        if answer:
            with st.spinner("🤖 AI正在诊断你的答案..."):
                diagnosis = diagnose_answer(
                    st.session_state.user_id, 
                    mission['content']['question_id'], 
                    answer
                )
                st.session_state.diagnosis_result = diagnosis
        else:
            st.error("请先输入答案！")

st.markdown('</div>', unsafe_allow_html=True)

# --- 诊断结果显示 ---
if st.session_state.diagnosis_result:
    result = st.session_state.diagnosis_result
    st.markdown("---")
    st.write("### 🔍 AI诊断结果")
    
    if result['status'] == 'success':
        st.success(f"✅ {result['diagnosis']}")
        if 'next_recommendation' in result:
            st.info(f"💡 下一步建议：{result['next_recommendation']}")
        st.balloons()
    elif result['status'] == 'partial':
        st.warning(f"⚠️ {result['diagnosis']}")
        if 'hint' in result:
            st.info(f"💡 提示：{result['hint']}")
    else:
        st.error(f"❌ {result['message']}")
    
    # 重新开始按钮
    if st.button("🔄 开始新任务", type="secondary"):
        st.session_state.current_mission = None
        st.session_state.diagnosis_result = None
        st.rerun()