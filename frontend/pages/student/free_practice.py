import streamlit as st
import random
import pandas as pd

def render_free_practice_page(api_service, current_user, user_id):
    """渲染自由练习页面"""
    st.write("### 📚 自由练习")
    if not current_user:
        st.warning("请先选择用户")
        return
    
    st.info(f"👨‍🎓 当前学习者：**{current_user}**")
    
    # 初始化session state
    if 'show_knowledge_map' not in st.session_state:
        st.session_state.show_knowledge_map = True
    if 'selected_node_name' not in st.session_state:
        st.session_state.selected_node_name = None
    if 'selected_question_index' not in st.session_state:
        st.session_state.selected_question_index = 0
    if 'current_questions' not in st.session_state:
        st.session_state.current_questions = None
    if 'current_node_for_questions' not in st.session_state:
        st.session_state.current_node_for_questions = None
    
    # 知识图谱展示区域
    col1, col2 = st.columns([3, 1])
    with col1:
        st.write("### 🗺️ 我的知识图谱")
    with col2:
        if st.button("📊 收起/展开图谱", key="toggle_knowledge_map"):
            st.session_state.show_knowledge_map = not st.session_state.show_knowledge_map
            st.rerun()
    
    if st.session_state.show_knowledge_map:
        # 获取知识图谱数据
        knowledge_map_data = api_service.get_knowledge_map(user_id)
        
        if knowledge_map_data:
            df_data = []
            for item in knowledge_map_data:
                df_data.append({
                    '知识点名称': item.get('node_name', ''),
                    '我的掌握度': item.get('mastery', 0.0),
                    '难度': item.get('node_difficulty', '未定义')
                })
            df = pd.DataFrame(df_data)
        else:
            df = pd.DataFrame(columns=['知识点名称', '我的掌握度', '难度'])
        
        # 知识图谱概览
        st.markdown("#### 📊 学习概览")
        col1, col2, col3, col4 = st.columns(4)
        total_nodes = len(df)
        with col1:
            st.metric("总知识点", f"{total_nodes}个")
        with col2:
            mastered_nodes = len(df[df['我的掌握度'] >= 0.8])
            mastered_percentage = f"{mastered_nodes/total_nodes:.0%}" if total_nodes > 0 else "0%"
            st.metric("已掌握", f"{mastered_nodes}个", mastered_percentage)
        with col3:
            learning_nodes = len(df[(df['我的掌握度'] >= 0.3) & (df['我的掌握度'] < 0.8)])
            learning_percentage = f"{learning_nodes/total_nodes:.0%}" if total_nodes > 0 else "0%"
            st.metric("学习中", f"{learning_nodes}个", learning_percentage)
        with col4:
            avg_mastery = df['我的掌握度'].mean() if not df.empty else 0
            st.metric("平均掌握度", f"{avg_mastery:.1%}")
        
        # 可点击的知识点列表
        st.write("#### 🎯 选择练习知识点")
        if not df.empty:
            # 创建可点击的知识点按钮
            cols = st.columns(3)  # 每行显示3个知识点
            for idx, (_, row) in enumerate(df.iterrows()):
                col_idx = idx % 3
                with cols[col_idx]:
                    node_name = row['知识点名称']
                    mastery = row['我的掌握度']
                    difficulty = row['难度']
                    
                    # 根据掌握度设置颜色
                    if mastery >= 0.8:
                        color = "🟢"  # 绿色 - 已掌握
                    elif mastery >= 0.3:
                        color = "🟡"  # 黄色 - 学习中
                    else:
                        color = "🔴"  # 红色 - 待学习
                    
                    button_text = f"{color} {node_name}\n掌握度: {mastery:.0%}"
                    
                    if st.button(button_text, key=f"node_{node_name}", use_container_width=True):
                        st.session_state.selected_node_name = node_name
                        st.session_state.selected_question_index = 0  # 重置题目索引
                        # 清除题目缓存，强制重新获取
                        st.session_state.current_questions = None
                        st.session_state.current_node_for_questions = None
                        # 清除诊断结果
                        st.session_state.show_diagnosis = False
                        st.session_state.diagnosis_result = None
                        st.rerun()
        else:
            st.info("暂无知识点数据")
        
        st.divider()
    
    # 题目练习区域
    if st.session_state.selected_node_name:
        selected_node_name = st.session_state.selected_node_name
        
        # 显示选中的知识点信息
        st.write(f"### 🎯 当前练习：{selected_node_name}")
        
        # 获取该知识点的掌握度信息
        mastery = api_service.get_user_mastery(user_id, selected_node_name)
        
        col1, col2, col3, col4 = st.columns([2, 2, 2, 2])
        with col1:
            st.metric("知识点", selected_node_name)
        with col2:
            st.metric("我的掌握度", f"{mastery:.0%}")
        with col3:
            if st.button("🔄 换个题目", type="secondary", key="change_question_btn"):
                # 确保题目列表已加载
                if (st.session_state.current_node_for_questions != selected_node_name or 
                    st.session_state.current_questions is None):
                    st.session_state.current_questions = api_service.get_questions_for_node(selected_node_name)
                    st.session_state.current_node_for_questions = selected_node_name
                
                questions = st.session_state.current_questions
                if questions and len(questions) > 1:
                    # 确保不选择当前题目
                    new_index = st.session_state.selected_question_index
                    while new_index == st.session_state.selected_question_index:
                        new_index = random.randint(0, len(questions) - 1)
                    st.session_state.selected_question_index = new_index
                    # 清除诊断结果
                    st.session_state.show_diagnosis = False
                    st.session_state.diagnosis_result = None
                    st.rerun()
                elif questions and len(questions) == 1:
                    st.info("只有一道题目，无法切换")
        with col4:
            if st.button("🔙 重新选择知识点", key="back_to_map"):
                st.session_state.selected_node_name = None
                # 清除题目缓存
                st.session_state.current_questions = None
                st.session_state.current_node_for_questions = None
                # 清除诊断结果
                st.session_state.show_diagnosis = False
                st.session_state.diagnosis_result = None
                st.rerun()
        
        # 获取题目（使用缓存机制）
        if (st.session_state.current_node_for_questions != selected_node_name or 
            st.session_state.current_questions is None):
            st.session_state.current_questions = api_service.get_questions_for_node(selected_node_name)
            st.session_state.current_node_for_questions = selected_node_name
        
        questions = st.session_state.current_questions
        
        if questions:
            current_question = questions[st.session_state.selected_question_index]
            
            # 题目展示
            st.write("### 🤔 练习题目")
            col1, col2 = st.columns([3, 1])
            with col1:
                st.info(f"题目 {st.session_state.selected_question_index + 1} / {len(questions)}")
            with col2:
                if isinstance(current_question, dict):
                    difficulty = current_question.get('difficulty', 0.5)
                    if difficulty <= 0.3:
                        st.success("🟢 简单")
                    elif difficulty <= 0.7:
                        st.warning("🟡 中等")
                    else:
                        st.error("🔴 困难")
            
            # 显示题目文本
            question_text = current_question.get('question_text', current_question) if isinstance(current_question, dict) else current_question
            st.latex(question_text)
            
            # 答题区域
            st.write("### ✍️ 作答区域")
            answer = st.text_area(
                "请在此处输入你的解题过程和答案：", 
                height=150, 
                key=f"practice_answer_{selected_node_name}_{st.session_state.selected_question_index}"
            )
            
            # 操作按钮
            col1, col2, col3, col4 = st.columns(4)
            
            # 初始化session state用于存储诊断结果
            if 'diagnosis_result' not in st.session_state:
                st.session_state.diagnosis_result = None
            if 'show_diagnosis' not in st.session_state:
                st.session_state.show_diagnosis = False
            
            with col1:
                if st.button("📝 提交答案", type="primary", key="submit_practice_answer"):
                    if answer:
                        # 调用诊断API
                        with st.spinner("🔍 正在诊断你的答案..."):
                            # 获取正确的question_id
                            question_id = current_question.get('question_id', st.session_state.selected_question_index + 1) if isinstance(current_question, dict) else st.session_state.selected_question_index + 1
                            diagnosis_result = api_service.diagnose_answer(
                                user_id=str(user_id),
                                question_id=str(question_id),  # 使用数据库中的真实question_id
                                answer=answer,
                                answer_type="text"
                            )
                        
                        if "error" not in diagnosis_result:
                            st.session_state.diagnosis_result = diagnosis_result
                            st.session_state.show_diagnosis = True
                            st.success("✅ 提交成功！")
                            st.rerun()
                        else:
                            st.error(f"❌ 诊断失败: {diagnosis_result['error']}")
                            st.info("💡 请检查网络连接或稍后重试")
                    else:
                        st.error("请先输入答案！")
            
            with col2:
                if len(questions) > 1 and st.session_state.selected_question_index < len(questions) - 1:
                    if st.button("➡️ 下一题", key="next_question"):
                        st.session_state.selected_question_index += 1
                        # 清除诊断结果
                        st.session_state.show_diagnosis = False
                        st.session_state.diagnosis_result = None
                        st.rerun()
            
            with col3:
                if st.session_state.selected_question_index > 0:
                    if st.button("⬅️ 上一题", key="prev_question"):
                        st.session_state.selected_question_index -= 1
                        # 清除诊断结果
                        st.session_state.show_diagnosis = False
                        st.session_state.diagnosis_result = None
                        st.rerun()
            
            with col4:
                if st.button("🎲 随机题目", key="random_question"):
                    if len(questions) > 1:
                        # 确保不选择当前题目
                        new_index = st.session_state.selected_question_index
                        while new_index == st.session_state.selected_question_index:
                            new_index = random.randint(0, len(questions) - 1)
                        st.session_state.selected_question_index = new_index
                        # 清除诊断结果
                        st.session_state.show_diagnosis = False
                        st.session_state.diagnosis_result = None
                        st.rerun()
                    else:
                        st.info("只有一道题目，无法随机切换")
            
            # 显示诊断结果（在列布局之外，占用全宽度）
            if st.session_state.show_diagnosis and st.session_state.diagnosis_result:
                st.divider()
                st.write("### 📋 诊断结果")
                
                diagnosis_result = st.session_state.diagnosis_result
                
                # 获取诊断结果
                is_correct = diagnosis_result.get("is_correct", False)
                reason = diagnosis_result.get("reason", "无诊断信息")
                scores = diagnosis_result.get("scores", [])
                
                # 根据正确性显示结果
                if is_correct:
                    st.success(f"🎉 答案正确！{reason}")
                    # 显示庆祝效果和掌握度提升
                    st.balloons()
                    if mastery < 1.0:
                        new_mastery = min(mastery + 0.1, 1.0)
                        st.success(f"🎉 掌握度提升！{mastery:.0%} → {new_mastery:.0%}")
                else:
                    st.warning(f"⚠️ 答案需要改进：{reason}")
                    st.info("💡 **建议**: 请仔细检查解题步骤，或尝试从不同角度思考问题")
                    
                # 显示评分详情（如果有）
                if scores:
                    with st.expander("📊 查看详细评分", expanded=is_correct):
                        st.write("### 答题表现评估")
                        
                        # 创建评分表格
                        score_data = []
                        for score_item in scores:
                            # 获取评分类别（支持中英文）
                            category_en = score_item.get('Knowledge Mastery') or score_item.get('Logical Reasoning') or \
                                        score_item.get('Calculation Accuracy') or score_item.get('Behavioral Performance')
                            category_cn = score_item.get('知识掌握') or score_item.get('解题逻辑') or \
                                        score_item.get('计算准确性') or score_item.get('行为表现')
                            
                            # 显示类别名称（优先使用中文）
                            category = category_cn or category_en or '未知类别'
                            score = score_item.get('score', 0)
                            feedback = score_item.get('feedback', '无反馈')
                            
                            # 添加到表格数据
                            score_data.append({"评估维度": category, "得分": score, "反馈": feedback})
                        
                        # 显示评分表格
                        st.table(score_data)
                        
                        # 计算总分
                        if score_data:
                            total_score = sum(item["得分"] for item in score_data) / len(score_data)
                            st.write(f"**综合评分**: {total_score:.1f}/1.0")
                            
                            # 根据总分给出鼓励性评语
                            if total_score >= 0.9:
                                st.success("🌟 优秀！你的解答非常出色，继续保持！")
                            elif total_score >= 0.7:
                                st.info("👍 不错！你的解答有一些亮点，还有提升空间。")
                            else:
                                st.warning("💪 加油！多加练习，你会做得更好！")
                
                # 添加清除诊断结果的按钮
                if st.button("🗑️ 清除诊断结果", key="clear_diagnosis"):
                    st.session_state.show_diagnosis = False
                    st.session_state.diagnosis_result = None
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
            st.warning("该知识点暂无练习题目")
    else:
        st.info("👆 请从上方知识图谱中选择一个知识点开始练习")