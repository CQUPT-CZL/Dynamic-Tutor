import streamlit as st
import time

# --- 模拟后端逻辑 ---
# 在真实项目中，这些函数应该是调用后端API的
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
            "mastery_update": {"ECH_GX": 0.9} # 假设更新了“函数与方程关系”的掌握度
        }
    else:
        return {
            "status": "failed",
            "diagnosis": "回答错误。别灰心，再想一想，是不是可以尝试用因式分解的方法来解决呢？",
            "mastery_update": {"ECH_GX": 0.4}
        }

# --- 页面渲染 ---
st.set_page_config(page_title="今日任务", page_icon="🎯")

if not st.session_state.user_id:
    st.warning("请先在主程序页面选择学生！")
    st.stop()

st.title(f"🎯 {st.session_state.user_id}的今日任务")
st.markdown("---")

# 如果没有当前任务，就从后端获取一个
if not st.session_state.current_mission:
    with st.spinner("AI正在为你定制学习任务..."):
        time.sleep(1.5)
        st.session_state.current_mission = get_recommendation_for_user(st.session_state.user_id)

mission = st.session_state.current_mission

# --- 任务卡片设计 ---
with st.container(border=True):
    st.subheader(f"任务类型: {mission['type']}")
    st.info(f"💡 **推荐理由**: {mission['reason']}")
    
    # 如果任务包含概念学习
    if "concept_text" in mission['content']:
        with st.expander("首先，我们来复习一下概念 📖"):
            st.write(mission['content']['concept_text'])

    # 题目展示与作答
    st.markdown("---")
    st.markdown(f"**练习题 (ID: {mission['content']['question_id']})**")
    st.latex(mission['content']['question_text']) # 使用latex格式显示数学公式
    
    answer = st.text_area("请在下方输入你的解题过程和答案：", height=150)
    
    if st.button("提交答案", type="primary"):
        st.session_state.diagnosis_result = diagnose_answer(
            st.session_state.user_id, 
            mission['content']['question_id'], 
            answer
        )

# --- 显示诊断结果 ---
if st.session_state.diagnosis_result:
    result = st.session_state.diagnosis_result
    if result['status'] == "success":
        st.success(f"🤖 **AI诊断**: {result['diagnosis']}")
        if st.button("太棒了，下一个任务！"):
            st.session_state.current_mission = None
            st.session_state.diagnosis_result = None
            st.rerun()
    elif result['status'] == "failed":
        st.error(f"🤖 **AI诊断**: {result['diagnosis']}")
    else:
        st.warning(result['message'])