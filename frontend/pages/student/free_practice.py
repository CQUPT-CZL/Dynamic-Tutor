import streamlit as st
import random
import pandas as pd
from components import render_simple_question, QuestionPracticeComponent



def render_free_practice_page(api_service, current_user, user_id):
    """渲染自由练习页面"""
    st.write("### 📚 自由练习")
    if not current_user:
        st.warning("请先选择用户")
        return
    
    st.info(f"👨‍🎓 当前学习者：**{current_user}**")
    
    # 初始化session state
    if 'selected_node_name' not in st.session_state:
        st.session_state.selected_node_name = None
    if 'selected_question_index' not in st.session_state:
        st.session_state.selected_question_index = 0
    if 'current_questions' not in st.session_state:
        st.session_state.current_questions = None
    if 'current_node_for_questions' not in st.session_state:
        st.session_state.current_node_for_questions = None
    
    # 知识点选择区域
    # 获取知识点数据
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
    
    # 简化的知识点选择
    if not df.empty:
        # 添加掌握度标识到知识点名称
        knowledge_options_with_mastery = []
        for _, row in df.iterrows():
            knowledge_name = row['知识点名称']
            mastery = row['我的掌握度']
            
            # 添加掌握度标识
            if mastery >= 0.8:
                status_icon = "🟢"
            elif mastery >= 0.5:
                status_icon = "🟡"
            elif mastery > 0:
                status_icon = "🔴"
            else:
                status_icon = "⚪"
            
            display_name = f"{status_icon} {knowledge_name} ({mastery:.0%})"
            knowledge_options_with_mastery.append((display_name, knowledge_name, mastery))
        
        # 按掌握度排序（掌握度低的在前，需要优先练习）
        knowledge_options_with_mastery.sort(key=lambda x: x[2])
        
        knowledge_options = ["请选择知识点..."] + [kp[0] for kp in knowledge_options_with_mastery]
        selected_knowledge_display = st.selectbox(
            "🎯 选择练习知识点：",
            options=knowledge_options,
            key="knowledge_selector",
            help="🟢已掌握 🟡学习中 🔴需加强 ⚪未开始"
        )
        
        if selected_knowledge_display and selected_knowledge_display != "请选择知识点...":
            # 找到对应的知识点名称
            selected_knowledge_name = None
            current_mastery = 0.0
            for display_name, knowledge_name, mastery in knowledge_options_with_mastery:
                if display_name == selected_knowledge_display:
                    selected_knowledge_name = knowledge_name
                    current_mastery = mastery
                    break
            
            if selected_knowledge_name:
                # 显示选中知识点的详细信息
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("当前掌握度", f"{current_mastery:.0%}")
                with col2:
                    # 获取知识点难度
                    difficulty = df[df['知识点名称'] == selected_knowledge_name]['难度'].iloc[0]
                    st.metric("难度等级", difficulty)
                with col3:
                    if st.button("🚀 开始练习", key="start_practice_btn", help="点击开始练习选中的知识点"):
                        st.session_state.selected_node_name = selected_knowledge_name
                        st.session_state.selected_question_index = 0
                        # 清除题目缓存，强制重新获取
                        st.session_state.current_questions = None
                        st.session_state.current_node_for_questions = None
                        # 清除诊断结果
                        if 'show_diagnosis' in st.session_state:
                            st.session_state.show_diagnosis = False
                        if 'diagnosis_result' in st.session_state:
                            st.session_state.diagnosis_result = None
                        st.rerun()
                
                # 显示学习建议
                if current_mastery < 0.3:
                    st.info("💡 **学习建议**：这个知识点对你来说还比较新，建议先复习相关概念再做练习。")
                elif current_mastery < 0.8:
                    st.success("💪 **学习建议**：你对这个知识点有一定了解，多做练习可以进一步提高掌握度。")
                else:
                    st.success("🎉 **学习建议**：你已经很好地掌握了这个知识点！可以尝试挑战更高难度的内容。")
    else:
        st.warning("⚠️ 暂无知识点数据")
    
    st.divider()
    
    # 题目练习区域
    if st.session_state.selected_node_name:
        selected_node_name = st.session_state.selected_node_name
        
        # 显示选中的知识点信息
        # st.write(f"### 🎯 当前练习：{selected_node_name}")
        
        # 获取该知识点的掌握度信息
        mastery = api_service.get_user_mastery(user_id, selected_node_name)
        
        # 添加美化的CSS样式
        st.markdown("""
        <style>
        .elegant-button {
            background: linear-gradient(135deg, #74b9ff 0%, #0984e3 100%);
            color: white;
            padding: 0.6rem 1.2rem;
            border: none;
            border-radius: 10px;
            font-weight: 500;
            font-size: 0.9rem;
            cursor: pointer;
            transition: all 0.3s ease;
            box-shadow: 0 3px 12px rgba(116, 185, 255, 0.3);
            width: 100%;
            text-align: center;
        }
        .elegant-button:hover {
            transform: translateY(-1px);
            box-shadow: 0 5px 15px rgba(116, 185, 255, 0.4);
        }
        .secondary-button {
            background: linear-gradient(135deg, #fd79a8 0%, #e84393 100%);
            color: white;
            padding: 0.6rem 1.2rem;
            border: none;
            border-radius: 10px;
            font-weight: 500;
            font-size: 0.9rem;
            cursor: pointer;
            transition: all 0.3s ease;
            box-shadow: 0 3px 12px rgba(253, 121, 168, 0.3);
            width: 100%;
            text-align: center;
        }
        .secondary-button:hover {
            transform: translateY(-1px);
            box-shadow: 0 5px 15px rgba(253, 121, 168, 0.4);
        }
        .info-card {
            background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
            padding: 1rem;
            border-radius: 12px;
            border-left: 4px solid #667eea;
            margin: 0.5rem 0;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        </style>
        """, unsafe_allow_html=True)
        
        # 美化的信息展示区域
        st.markdown(f"""
        <div class="info-card">
            <h4 style="margin: 0; color: #2d3436;">🎯 当前练习：{selected_node_name}</h4>
            <p style="margin: 0.5rem 0 0 0; color: #636e72;">掌握度：{mastery:.0%} | 继续加油！💪</p>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            if st.button("🔄 换个题目", key="change_question_btn", help="随机切换到其他题目"):
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
        with col2:
            if st.button("🔙 重新选择", key="back_to_map", help="返回知识点选择界面"):
                st.session_state.selected_node_name = None
                # 清除题目缓存
                st.session_state.current_questions = None
                st.session_state.current_node_for_questions = None
                # 清除诊断结果
                st.session_state.show_diagnosis = False
                st.session_state.diagnosis_result = None
                st.rerun()
        with col3:
            if st.button("📊 查看进度", key="view_progress", help="查看学习进度统计"):
                st.info("📈 学习进度功能开发中...")
        
        # 获取题目（使用缓存机制）
        if (st.session_state.current_node_for_questions != selected_node_name or 
            st.session_state.current_questions is None):
            st.session_state.current_questions = api_service.get_questions_for_node(selected_node_name)
            st.session_state.current_node_for_questions = selected_node_name
        
        questions = st.session_state.current_questions
        
        if questions:
            current_question = questions[st.session_state.selected_question_index]
            
            # 使用通用做题组件
            st.write("### 🤔 练习题目")
            
            # 创建做题组件实例
            question_component = QuestionPracticeComponent(api_service, user_id)
            
            # 自定义提交处理函数
            def handle_submit(answer):
                with st.spinner("🔍 正在诊断你的答案..."):
                    question_id = current_question.get('question_id', st.session_state.selected_question_index + 1) if isinstance(current_question, dict) else st.session_state.selected_question_index + 1
                    diagnosis_result = api_service.diagnose_answer(
                        user_id=str(user_id),
                        question_id=str(question_id),
                        answer=answer,
                        answer_type="text"
                    )
                
                if "error" not in diagnosis_result:
                    st.success("✅ 提交成功！")
                    question_component.render_diagnosis_result(diagnosis_result, mastery_before=mastery)
                else:
                    st.error(f"❌ 诊断失败: {diagnosis_result['error']}")
                    st.info("💡 请检查网络连接或稍后重试")
            
            # 自定义导航处理函数
            def handle_next():
                if st.session_state.selected_question_index < len(questions) - 1:
                    st.session_state.selected_question_index += 1
                    st.rerun()
            
            def handle_prev():
                if st.session_state.selected_question_index > 0:
                    st.session_state.selected_question_index -= 1
                    st.rerun()
            
            # 渲染完整的做题界面
            result = question_component.render_complete_question_interface(
                question=current_question,
                question_index=st.session_state.selected_question_index,
                total_questions=len(questions),
                key_suffix=f"{selected_node_name}_{st.session_state.selected_question_index}",
                show_difficulty=True,
                show_navigation=True,
                on_submit=handle_submit,
                on_next=handle_next,
                on_prev=handle_prev
            )
            
            # 额外的操作按钮
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("🎲 随机题目", key="random_question"):
                    if len(questions) > 1:
                        # 确保不选择当前题目
                        new_index = st.session_state.selected_question_index
                        while new_index == st.session_state.selected_question_index:
                            new_index = random.randint(0, len(questions) - 1)
                        st.session_state.selected_question_index = new_index
                        st.rerun()
                    else:
                        st.info("只有一道题目，无法随机切换")
            
            with col2:
                if st.button("🔄 换个题目", key="change_question_btn_bottom"):
                    if len(questions) > 1:
                        # 确保不选择当前题目
                        new_index = st.session_state.selected_question_index
                        while new_index == st.session_state.selected_question_index:
                            new_index = random.randint(0, len(questions) - 1)
                        st.session_state.selected_question_index = new_index
                        st.rerun()
                    else:
                        st.info("只有一道题目，无法切换")
            

            
            # 学习提示
            st.write("### 💡 学习提示")
            
            if mastery < 0.3:
                st.warning("🔰 这个知识点对你来说还比较新，建议先复习相关概念再做练习。")
                st.info("📖 推荐：先复习基础知识，再进行练习。")
            elif mastery < 0.8:
                st.info("📈 你对这个知识点有一定了解，多做练习可以进一步提高掌握度。")
                st.success("💪 继续努力，你正在进步！")
            else:
                st.success("🎉 你已经很好地掌握了这个知识点！")
                st.info("🚀 可以尝试挑战更高难度的知识点，或者帮助其他同学学习。")
        else:
            st.warning("该知识点暂无练习题目")
    else:
        st.info("👆 请从上方选择一个知识点开始练习")