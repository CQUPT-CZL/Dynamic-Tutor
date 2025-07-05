import streamlit as st
import random

def render_free_practice_page(api_service, current_user):
    """渲染自由练习页面"""
    st.write("### 📚 自由练习")
    if not current_user:
        st.warning("请先选择用户")
        return
    
    st.info(f"👨‍🎓 当前学习者：**{current_user}**")
    
    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button("🔄 换个题目", type="primary", key="change_question_btn"):
            if 'selected_question_index' in st.session_state:
                del st.session_state.selected_question_index
            st.rerun()
    
    # 知识点选择
    st.markdown('<div class="practice-card">', unsafe_allow_html=True)
    st.write("### 🎯 选择练习知识点")

    # 获取知识节点
    nodes = api_service.get_knowledge_nodes()
    node_options = []
    for node_name in nodes.values():
        mastery = api_service.get_user_mastery(current_user, node_name)
        # 简化显示，暂时不显示难度
        mastery_percent = f"{mastery:.0%}"
        node_options.append(f"{node_name} - 掌握度: {mastery_percent}")

    selected_option = st.selectbox(
        "请选择一个知识点:",
        options=node_options,
        key="knowledge_node_selector"
    )

    if selected_option:
        # 解析选择的知识点
        selected_node_name = selected_option.split(" - 掌握度:")[0]
        
        # 显示知识点信息
        mastery = api_service.get_user_mastery(current_user, selected_node_name)
        
        st.markdown('<div class="node-info">', unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("知识点", selected_node_name)
        with col2:
            st.metric("难度等级", "⭐⭐⭐")  # 暂时显示固定难度
        with col3:
            st.metric("我的掌握度", f"{mastery:.0%}")
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # 题目展示
        questions = api_service.get_questions_for_node(selected_node_name)
        
        # 题目选择逻辑
        if 'selected_question_index' not in st.session_state:
            st.session_state.selected_question_index = 0
        
        current_question = questions[st.session_state.selected_question_index]
        
        st.markdown('<div class="question-box">', unsafe_allow_html=True)
        st.write("### 🤔 练习题目")
        st.info(f"题目 {st.session_state.selected_question_index + 1} / {len(questions)}")
        st.latex(current_question)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # 答题区域
        st.write("### ✍️ 作答区域")
        answer = st.text_area(
            "请在此处输入你的解题过程和答案：", 
            height=150, 
            key=f"practice_answer_{selected_node_name}_{st.session_state.selected_question_index}"
        )
        
        # 操作按钮
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("📝 提交答案", type="primary", key="submit_practice_answer"):
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
                if st.button("➡️ 下一题", key="next_question"):
                    st.session_state.selected_question_index += 1
                    st.rerun()
        
        with col3:
            if st.session_state.selected_question_index > 0:
                if st.button("⬅️ 上一题", key="prev_question"):
                    st.session_state.selected_question_index -= 1
                    st.rerun()
        
        with col4:
            if st.button("🎲 随机题目", key="random_question"):
                st.session_state.selected_question_index = random.randint(0, len(questions) - 1)
                st.rerun()
        
        # 学习提示
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