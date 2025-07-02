import streamlit as st
import time
import sys
import os
# 添加项目根目录到Python路径
project_root = os.path.join(os.path.dirname(__file__), '..', '..')
sys.path.insert(0, project_root)
from backend.backend import get_recommendation_for_user, diagnose_answer

def render_daily_tasks_page():
    """渲染今日任务页面"""
    st.write("### 📋 今日学习任务")
    st.info(f"👨‍🎓 当前学习者：**{st.session_state.user_id}**")
    
    col1, col2 = st.columns([1, 3])
    with col1:
        if st.button("🎲 获取新任务", type="primary", key="new_task_btn"):
            st.session_state.current_mission = None
            st.session_state.diagnosis_result = None
            st.rerun()
    
    # 获取或显示任务
    if not st.session_state.current_mission:
        with st.spinner("🤖 AI正在为你定制学习任务..."):
            time.sleep(1.5)
            st.session_state.current_mission = get_recommendation_for_user(st.session_state.user_id)

    mission = st.session_state.current_mission

    # 任务卡片设计
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

    # 答案输入方式选择
    answer_type = st.radio(
        "选择答题方式：",
        ["📝 文字输入", "📷 图片上传"],
        horizontal=True,
        key="answer_type_radio"
    )
    
    answer = None
    uploaded_image = None
    
    if answer_type == "📝 文字输入":
        answer = st.text_area("请在此处输入你的解题过程和答案：", height=150, key="mission_answer")
    else:
        st.write("📷 **上传答题图片**")
        uploaded_image = st.file_uploader(
            "请上传包含解题过程的图片",
            type=["png", "jpg", "jpeg", "gif", "bmp"],
            key="answer_image_uploader"
        )
        
        if uploaded_image is not None:
            # 显示上传的图片
            st.image(uploaded_image, caption="上传的答题图片", use_column_width=True)
            st.success("✅ 图片上传成功！")

    col1, col2 = st.columns([1, 3])
    with col1:
        if st.button("提交答案", type="primary", key="submit_answer_btn"):
            if answer or uploaded_image:
                with st.spinner("🤖 AI正在诊断你的答案..."):
                    # 根据答题方式传递不同的参数
                    if answer_type == "📝 文字输入":
                        diagnosis = diagnose_answer(
                            st.session_state.user_id, 
                            mission['content']['question_id'], 
                            answer,
                            answer_type="text"
                        )
                    else:
                        # 对于图片，传递图片信息
                        diagnosis = diagnose_answer(
                            st.session_state.user_id, 
                            mission['content']['question_id'], 
                            f"图片答案: {uploaded_image.name}",
                            answer_type="image",
                            image_data=uploaded_image
                        )
                    st.session_state.diagnosis_result = diagnosis
            else:
                if answer_type == "📝 文字输入":
                    st.error("请先输入答案！")
                else:
                    st.error("请先上传答题图片！")

    st.markdown('</div>', unsafe_allow_html=True)

    # 诊断结果显示
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
        if st.button("🔄 开始新任务", type="secondary", key="restart_task_btn"):
            st.session_state.current_mission = None
            st.session_state.diagnosis_result = None
            st.rerun()