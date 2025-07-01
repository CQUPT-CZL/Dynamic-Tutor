import streamlit as st

# --- 模拟后端逻辑 ---
def get_all_knowledge_nodes():
    return {
        "ECH_DY": "二次函数定义",
        "ECH_TXXZ": "图像与性质",
        "ECH_ZZWT": "最值问题"
    }

def get_a_question_for_node(node_id):
    questions = {
        "ECH_DY": "请写出二次函数的一般式、顶点式和零点式。",
        "ECH_TXXZ": "函数 f(x) = -2(x-1)² + 5 的开口方向、对称轴和顶点坐标分别是什么？",
        "ECH_ZZWT": "求函数 f(x) = x² - 6x + 8 的最小值。"
    }
    return questions.get(node_id, "抱歉，暂未收录该知识点的题目。")

# --- 页面渲染 ---
st.set_page_config(page_title="自由练习", page_icon="📚")

if not st.session_state.user_id:
    st.warning("请先在主程序页面选择学生！")
    st.stop()

st.title("📚 自由练习")
st.write("你可以从下方选择你感兴趣或想要巩固的知识点，系统会为你提供一道相关的练习题。")

nodes = get_all_knowledge_nodes()
selected_node_name = st.selectbox(
    "请选择一个知识点:",
    options=nodes.values()
)

if selected_node_name:
    # 反向查找ID
    selected_node_id = [id for id, name in nodes.items() if name == selected_node_name][0]
    
    question = get_a_question_for_node(selected_node_id)
    
    st.info(f"你选择了 **{selected_node_name}**，来试试这道题吧！")
    st.latex(question)
    
    answer = st.text_area("请在此处作答：")
    if st.button("提交"):
        st.success("提交成功！(自由练习模式暂不提供诊断)")