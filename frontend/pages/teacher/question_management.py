#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
教师端 - 题目管理页面
实现题目的增删改查功能
"""

import streamlit as st
import pandas as pd
from datetime import datetime

def render_question_management_page(api_service, current_user, user_id):
    """渲染题目管理页面"""
    st.markdown("""
    <div class="practice-card">
        <h2>📝 题目管理</h2>
        <p>管理系统中的所有题目，支持增删改查操作</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 创建标签页
    tab1, tab2, tab3, tab4 = st.tabs(["📋 题目列表", "➕ 添加题目", "🔗 关联知识点", "📊 统计信息"])
    
    with tab1:
        render_question_list(api_service, user_id)
    
    with tab2:
        render_add_question(api_service, user_id)
    
    with tab3:
        render_question_mapping(api_service, user_id)
    
    with tab4:
        render_question_stats(api_service)

def render_question_list(api_service, user_id):
    """渲染题目列表"""
    st.subheader("📋 题目列表")
    
    # 搜索和过滤
    col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
    with col1:
        search_term = st.text_input("🔍 搜索题目", placeholder="输入题目内容或ID")
    with col2:
        type_filter = st.selectbox("📝 题目类型", ["全部", "选择题", "填空题", "解答题"])
    with col3:
        status_filter = st.selectbox("📊 状态", ["全部", "草稿", "已发布"])
    with col4:
        if st.button("🔄 刷新列表"):
            st.rerun()
    
    try:
        # 调用API获取题目列表
        # questions = api_service.get_questions()
        
        # 临时使用模拟数据
        questions = [
            {
                "question_id": 1,
                "question_text": "解方程 x² - 5x + 6 = 0",
                "question_type": "解答题",
                "difficulty": 0.6,
                "answer": "x = 2 或 x = 3",
                "analysis": "使用因式分解法：(x-2)(x-3)=0",
                "status": "已发布",
                "created_by": user_id,
                "question_image_url": None
            },
            {
                "question_id": 2,
                "question_text": "函数 f(x) = 2x + 1 的图像经过点 (0, ?)?",
                "question_type": "填空题",
                "difficulty": 0.3,
                "answer": "1",
                "analysis": "将x=0代入函数得f(0)=2×0+1=1",
                "status": "已发布",
                "created_by": user_id,
                "question_image_url": None
            },
            {
                "question_id": 3,
                "question_text": "下列哪个是二次函数？\nA. y = x + 1\nB. y = x² + 1\nC. y = 1/x\nD. y = √x",
                "question_type": "选择题",
                "difficulty": 0.4,
                "answer": "B",
                "analysis": "二次函数的一般形式为y=ax²+bx+c(a≠0)",
                "status": "草稿",
                "created_by": user_id,
                "question_image_url": None
            }
        ]
        
        # 应用过滤条件
        filtered_questions = questions
        if search_term:
            filtered_questions = [q for q in filtered_questions 
                                if search_term.lower() in q['question_text'].lower()]
        
        if type_filter != "全部":
            filtered_questions = [q for q in filtered_questions if q['question_type'] == type_filter]
        
        if status_filter != "全部":
            filtered_questions = [q for q in filtered_questions if q['status'] == status_filter]
        
        if not filtered_questions:
            st.info("📭 没有找到符合条件的题目")
            return
        
        # 显示题目列表
        for i, question in enumerate(filtered_questions):
            status_color = "🟢" if question['status'] == "已发布" else "🟡"
            with st.expander(f"{status_color} 题目 #{question['question_id']} - {question['question_type']}", expanded=False):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.write(f"**题目内容:**")
                    st.write(question['question_text'])
                    st.write(f"**答案:** {question['answer']}")
                    st.write(f"**解析:** {question['analysis']}")
                    st.write(f"**难度系数:** {question['difficulty']} | **状态:** {question['status']}")
                    
                    if question['question_image_url']:
                        st.image(question['question_image_url'], caption="题目图片")
                
                with col2:
                    if st.button(f"✏️ 编辑", key=f"edit_q_{question['question_id']}"):
                        st.session_state[f"editing_q_{question['question_id']}"] = True
                        st.rerun()
                    
                    if question['status'] == "草稿":
                        if st.button(f"📤 发布", key=f"publish_{question['question_id']}"):
                            # 调用API发布题目
                            # api_service.publish_question(question['question_id'])
                            st.success("✅ 题目已发布！")
                            st.rerun()
                    
                    if st.button(f"🗑️ 删除", key=f"delete_q_{question['question_id']}"):
                        if st.session_state.get(f"confirm_delete_q_{question['question_id']}", False):
                            # 调用API删除题目
                            # api_service.delete_question(question['question_id'])
                            st.success(f"✅ 已删除题目 #{question['question_id']}")
                            st.rerun()
                        else:
                            st.session_state[f"confirm_delete_q_{question['question_id']}"] = True
                            st.warning("⚠️ 再次点击确认删除")
                
                # 编辑模式
                if st.session_state.get(f"editing_q_{question['question_id']}", False):
                    st.markdown("---")
                    st.subheader("✏️ 编辑题目")
                    
                    new_text = st.text_area("题目内容", value=question['question_text'], 
                                          key=f"edit_text_{question['question_id']}")
                    new_type = st.selectbox("题目类型", ["选择题", "填空题", "解答题"], 
                                          index=["选择题", "填空题", "解答题"].index(question['question_type']), 
                                          key=f"edit_type_{question['question_id']}")
                    new_difficulty = st.slider("难度系数", 0.0, 1.0, question['difficulty'], 
                                              key=f"edit_diff_{question['question_id']}")
                    new_answer = st.text_input("答案", value=question['answer'], 
                                             key=f"edit_answer_{question['question_id']}")
                    new_analysis = st.text_area("解析", value=question['analysis'], 
                                               key=f"edit_analysis_{question['question_id']}")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("💾 保存修改", key=f"save_q_{question['question_id']}"):
                            # 调用API更新题目
                            # api_service.update_question(question['question_id'], {
                            #     'question_text': new_text,
                            #     'question_type': new_type,
                            #     'difficulty': new_difficulty,
                            #     'answer': new_answer,
                            #     'analysis': new_analysis
                            # })
                            st.success("✅ 题目更新成功！")
                            del st.session_state[f"editing_q_{question['question_id']}"]
                            st.rerun()
                    
                    with col2:
                        if st.button("❌ 取消编辑", key=f"cancel_q_{question['question_id']}"):
                            del st.session_state[f"editing_q_{question['question_id']}"]
                            st.rerun()
        
    except Exception as e:
        st.error(f"❌ 获取题目列表失败: {str(e)}")
        st.info("💡 请确保后端API服务正常运行")

def render_add_question(api_service, user_id):
    """渲染添加题目界面"""
    st.subheader("➕ 添加新题目")
    
    with st.form("add_question_form"):
        question_text = st.text_area("📝 题目内容", placeholder="输入题目内容...")
        
        col1, col2 = st.columns(2)
        with col1:
            question_type = st.selectbox("📝 题目类型", ["选择题", "填空题", "解答题"])
            difficulty = st.slider("🎯 难度系数", 0.0, 1.0, 0.5, step=0.1)
        
        with col2:
            answer = st.text_input("✅ 答案", placeholder="输入正确答案")
            status = st.selectbox("📊 状态", ["草稿", "已发布"])
        
        analysis = st.text_area("📖 解析", placeholder="输入题目解析...")
        
        # 图片上传
        uploaded_file = st.file_uploader("🖼️ 上传题目图片 (可选)", type=['png', 'jpg', 'jpeg'])
        
        submitted = st.form_submit_button("➕ 添加题目", use_container_width=True)
        
        if submitted:
            if not question_text or not answer:
                st.error("❌ 请填写题目内容和答案")
            else:
                try:
                    # 处理图片上传
                    image_url = None
                    if uploaded_file is not None:
                        # 这里应该实现图片上传到服务器的逻辑
                        # image_url = api_service.upload_image(uploaded_file)
                        image_url = f"/images/{uploaded_file.name}"
                    
                    # 调用API添加题目
                    # api_service.create_question({
                    #     'question_text': question_text,
                    #     'question_type': question_type,
                    #     'difficulty': difficulty,
                    #     'answer': answer,
                    #     'analysis': analysis,
                    #     'status': status,
                    #     'created_by': user_id,
                    #     'question_image_url': image_url
                    # })
                    
                    st.success(f"✅ 成功添加题目！")
                    st.balloons()
                    
                except Exception as e:
                    st.error(f"❌ 添加题目失败: {str(e)}")

def render_question_mapping(api_service, user_id):
    """渲染题目与知识点关联界面"""
    st.subheader("🔗 题目与知识点关联")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("### 📝 选择题目")
        # 获取题目列表
        try:
            # questions = api_service.get_questions()
            questions = [
                {"question_id": 1, "question_text": "解方程 x² - 5x + 6 = 0"},
                {"question_id": 2, "question_text": "函数 f(x) = 2x + 1 的图像经过点 (0, ?)"},
                {"question_id": 3, "question_text": "下列哪个是二次函数？"}
            ]
            
            selected_question = st.selectbox(
                "选择题目",
                options=questions,
                format_func=lambda x: f"#{x['question_id']}: {x['question_text'][:50]}..."
            )
        except:
            st.error("❌ 无法获取题目列表")
            return
    
    with col2:
        st.write("### 📚 选择知识点")
        # 获取知识点列表
        try:
            # knowledge_nodes = api_service.get_knowledge_nodes()
            knowledge_nodes = [
                {"node_id": "math_001", "node_name": "一元二次方程"},
                {"node_id": "math_002", "node_name": "函数的概念"},
                {"node_id": "math_003", "node_name": "导数与微分"}
            ]
            
            selected_nodes = st.multiselect(
                "选择关联的知识点",
                options=knowledge_nodes,
                format_func=lambda x: f"{x['node_id']}: {x['node_name']}"
            )
        except:
            st.error("❌ 无法获取知识点列表")
            return
    
    if st.button("🔗 建立关联", use_container_width=True):
        if selected_question and selected_nodes:
            try:
                for node in selected_nodes:
                    # api_service.create_question_node_mapping(
                    #     selected_question['question_id'], 
                    #     node['node_id']
                    # )
                    pass
                
                st.success(f"✅ 成功关联题目 #{selected_question['question_id']} 与 {len(selected_nodes)} 个知识点")
            except Exception as e:
                st.error(f"❌ 建立关联失败: {str(e)}")
        else:
            st.warning("⚠️ 请选择题目和知识点")
    
    # 显示现有关联
    st.markdown("---")
    st.subheader("📋 现有关联关系")
    
    try:
        # mappings = api_service.get_question_node_mappings()
        mappings = [
            {"question_id": 1, "question_text": "解方程 x² - 5x + 6 = 0", "node_id": "math_001", "node_name": "一元二次方程"},
            {"question_id": 2, "question_text": "函数 f(x) = 2x + 1", "node_id": "math_002", "node_name": "函数的概念"}
        ]
        
        if mappings:
            df = pd.DataFrame(mappings)
            st.dataframe(df, use_container_width=True)
        else:
            st.info("📭 暂无关联关系")
            
    except Exception as e:
        st.error(f"❌ 获取关联关系失败: {str(e)}")

def render_question_stats(api_service):
    """渲染题目统计信息"""
    st.subheader("📊 题目统计")
    
    try:
        # 调用API获取统计数据
        # stats = api_service.get_question_stats()
        
        # 临时使用模拟数据
        stats = {
            "total_questions": 156,
            "published_questions": 120,
            "draft_questions": 36,
            "type_distribution": {"选择题": 60, "填空题": 45, "解答题": 51},
            "avg_difficulty": 0.58,
            "recent_added": 8
        }
        
        # 显示统计卡片
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("📝 总题目数", stats["total_questions"])
        
        with col2:
            st.metric("📤 已发布", stats["published_questions"])
        
        with col3:
            st.metric("📝 草稿", stats["draft_questions"])
        
        with col4:
            st.metric("🆕 本周新增", stats["recent_added"])
        
        # 题目类型分布图表
        st.subheader("📊 题目类型分布")
        
        df_type = pd.DataFrame({
            "类型": list(stats["type_distribution"].keys()),
            "数量": list(stats["type_distribution"].values())
        })
        
        st.bar_chart(df_type.set_index("类型"))
        
        # 难度分布
        st.subheader("🎯 难度分布")
        
        difficulty_ranges = {
            "简单 (0.0-0.3)": 45,
            "中等 (0.3-0.7)": 78,
            "困难 (0.7-1.0)": 33
        }
        
        df_diff = pd.DataFrame({
            "难度": list(difficulty_ranges.keys()),
            "数量": list(difficulty_ranges.values())
        })
        
        st.bar_chart(df_diff.set_index("难度"))
        
        # 最近活动
        st.subheader("📅 最近活动")
        recent_activities = [
            "✅ 添加了选择题: 二次函数的性质",
            "📤 发布了填空题: 函数的定义域",
            "✏️ 修改了解答题: 导数的应用",
            "🔗 关联了题目与知识点: 三角函数"
        ]
        
        for activity in recent_activities:
            st.write(f"• {activity}")
            
    except Exception as e:
        st.error(f"❌ 获取统计信息失败: {str(e)}")
        st.info("💡 请确保后端API服务正常运行")