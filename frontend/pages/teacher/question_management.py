#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
教师端 - 题目管理页面
实现题目的增删改查功能
"""

import streamlit as st
import pandas as pd
import json
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
    
    # 搜索和筛选
    col1, col2, col3, col4, col5 = st.columns([1.5, 1, 1, 1, 1])
    
    with col1:
        search_term = st.text_input("🔍 搜索题目", placeholder="输入关键词搜索...")
    
    with col2:
        question_type_filter = st.selectbox("📋 题目类型", ["全部", "选择题", "填空题", "解答题"])
    
    with col3:
        status_filter = st.selectbox("📊 状态", ["全部", "已发布", "草稿"])
    
    with col4:
        # 知识点筛选
        try:
            knowledge_response = api_service.get_knowledge_nodes()
            knowledge_nodes = knowledge_response.get('knowledge_points', [])
            
            
            # 添加"全部知识点"选项
            knowledge_options = [{"node_id": "", "node_name": "全部知识点"}] + knowledge_nodes
            
            selected_knowledge = st.selectbox(
                "📚 知识点",
                options=knowledge_options,
                format_func=lambda x: x['node_name']
            )
            knowledge_node_id = selected_knowledge['node_id'] if selected_knowledge['node_id'] else ""
        except Exception as e:
            st.warning(f"⚠️ 获取知识点列表失败: {str(e)}")
            knowledge_node_id = ""
    
    with col5:
        # 分页控制
        page_size = st.selectbox("📄 每页显示", [10, 20, 50, 100], index=1)
        if 'current_page' not in st.session_state:
            st.session_state.current_page = 1
    
    # 转换筛选条件
    type_param = "" if question_type_filter == "全部" else question_type_filter
    status_param = "" if status_filter == "全部" else ("published" if status_filter == "已发布" else "draft")
    
    try:
        # 获取题目列表
        response = api_service.get_questions(
            page=st.session_state.current_page,
            page_size=page_size,
            search=search_term,
            question_type=type_param,
            status=status_param,
            knowledge_node_id=knowledge_node_id
        )
        
        questions = response.get('questions', [])
        pagination = response.get('pagination', {})
        
        # 显示分页信息
        if pagination:
            st.write(f"📊 共 {pagination.get('total', 0)} 条记录，第 {pagination.get('page', 1)} / {pagination.get('total_pages', 1)} 页")
        
        if questions:
            for question in questions:
                status_color = "🟢" if question['status'] == "published" else "🟡"
                status_text = "已发布" if question['status'] == "published" else "草稿"
                with st.expander(f"{status_color} 题目 #{question['question_id']} - {question['question_type']}", expanded=False):
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.write(f"**题目内容:**")
                        st.write(question['question_text'])
                        # 显示题目图片（如果有）
                        if question.get('question_image_url'):
                            st.write("**题目图片:**")
                            try:
                                image_url = question['question_image_url']
                                if not image_url.startswith('http'):
                                    image_url = f"http://localhost:8000{image_url}"
                                st.image(image_url, caption="题目配图", use_container_width=True)
                            except Exception as e:
                                st.warning(f"⚠️ 无法加载图片: {str(e)}")
                        # 显示选择题选项
                        if question['question_type'] == '选择题' and question.get('options'):
                            st.write("**选项:**")
                            if isinstance(question['options'], str):
                                try:
                                    options = json.loads(question['options'])
                                except:
                                    options = question['options']
                            else:
                                options = question['options']
                            if isinstance(options, dict):
                                for key, value in options.items():
                                    st.write(f"  {key}. {value}")
                            elif isinstance(options, list):
                                for i, option in enumerate(options):
                                    st.write(f"  {chr(65+i)}. {option}")
                        st.write(f"**答案:** {question['answer']}")
                        st.write(f"**解析:** {question['analysis']}")
                        st.write(f"**难度系数:** {question['difficulty']} | **状态:** {status_text}")
                        st.write(f"**创建者:** {question.get('creator_name', '未知')}")
                    with col2:
                        if st.button(f"✏️ 编辑", key=f"edit_q_{question['question_id']}"):
                            st.session_state[f"editing_q_{question['question_id']}"] = True
                            st.rerun()
                        if question['status'] == "draft":
                            if st.button(f"📤 发布", key=f"publish_{question['question_id']}"):
                                try:
                                    api_service.update_question(question['question_id'], {"status": "published"})
                                    st.success("✅ 题目已发布！")
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"❌ 发布失败: {str(e)}")
                        if st.button(f"🗑️ 删除", key=f"delete_q_{question['question_id']}"):
                            if st.session_state.get(f"confirm_delete_q_{question['question_id']}", False):
                                try:
                                    api_service.delete_question(question['question_id'])
                                    st.success(f"✅ 已删除题目 #{question['question_id']}")
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"❌ 删除失败: {str(e)}")
                            else:
                                st.session_state[f"confirm_delete_q_{question['question_id']}"] = True
                                st.warning("⚠️ 再次点击确认删除")
            
            # 分页导航
            if pagination and pagination.get('total_pages', 1) > 1:
                col1, col2, col3, col4, col5 = st.columns([1, 1, 2, 1, 1])
                
                with col1:
                    if pagination.get('has_prev', False):
                        if st.button("⬅️ 上一页"):
                            st.session_state.current_page -= 1
                            st.rerun()
                    else:
                        st.button("⬅️ 上一页", disabled=True)
                
                with col2:
                    if st.button("🏠 首页"):
                        st.session_state.current_page = 1
                        st.rerun()
                
                with col3:
                    # 页码跳转
                    new_page = st.number_input(
                        "跳转到页码", 
                        min_value=1, 
                        max_value=pagination.get('total_pages', 1),
                        value=st.session_state.current_page,
                        key="page_jump"
                    )
                    if new_page != st.session_state.current_page:
                        st.session_state.current_page = new_page
                        st.rerun()
                
                with col4:
                    if st.button("🔚 末页"):
                        st.session_state.current_page = pagination.get('total_pages', 1)
                        st.rerun()
                
                with col5:
                    if pagination.get('has_next', False):
                        if st.button("➡️ 下一页"):
                            st.session_state.current_page += 1
                            st.rerun()
                    else:
                        st.button("➡️ 下一页", disabled=True)
        else:
            st.info("📭 没有找到符合条件的题目")
            
    except Exception as e:
        st.error(f"❌ 无法获取题目列表: {str(e)}")
        return

def render_question_mapping(api_service, user_id):
    """渲染题目与知识点关联页面"""
    st.subheader("🔗 题目与知识点关联")
    
    # 获取题目列表
    try:
        response = api_service.get_questions(page=1, page_size=100)
        questions = response.get('questions', [])
    except Exception as e:
        st.error(f"❌ 无法获取题目列表: {str(e)}")
        return
    
    if not questions:
        st.info("📭 暂无题目")
        return
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.write("### 📝 选择题目")
        selected_question = st.selectbox(
            "选择题目",
            options=questions,
            format_func=lambda x: f"#{x['question_id']}: {x['question_text'][:50]}..."
        )
            
    with col2:
        st.write("### 📚 选择知识点")
        # 获取知识点列表
        try:
            knowledge_response = api_service.get_knowledge_nodes()
            knowledge_nodes = knowledge_response.get('knowledge_points', [])
            
            if not knowledge_nodes:
                # 使用临时数据
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
        except Exception as e:
            st.warning(f"⚠️ 无法获取知识点列表，使用默认数据: {str(e)}")
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
    
    if st.button("🔗 建立关联", use_container_width=True):
        if selected_question and selected_nodes:
            try:
                success_count = 0
                for node in selected_nodes:
                    try:
                        result = api_service.create_question_node_mapping(
                            selected_question['question_id'],
                            node['node_id']
                        )
                        if result and result.get('status') == 'success':
                            success_count += 1
                        else:
                            st.warning(f"⚠️ 关联知识点 {node['node_name']} 失败")
                    except Exception as e:
                        st.warning(f"⚠️ 关联知识点 {node['node_name']} 失败: {str(e)}")
                
                if success_count > 0:
                    st.success(f"✅ 成功关联题目 #{selected_question['question_id']} 与 {success_count} 个知识点")
                    st.rerun()
            except Exception as e:
                st.error(f"❌ 建立关联失败: {str(e)}")
        else:
            st.warning("⚠️ 请选择题目和知识点")
    
    # 显示现有关联
    st.markdown("---")
    st.subheader("📋 现有关联关系")
    
    try:
        mappings_response = api_service.get_question_node_mappings()
        mappings = mappings_response.get('mappings', [])
        
        if mappings:
            # 添加删除功能
            for mapping in mappings:
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.write(f"📝 #{mapping['question_id']}: {mapping['question_text'][:50]}... ↔ 🎯 {mapping['node_name']}")
                with col2:
                    if st.button("🗑️ 删除", key=f"del_mapping_{mapping.get('mapping_id', mapping['question_id'])}_{mapping['node_id']}"):
                        try:
                            result = api_service.delete_question_node_mapping(
                                mapping['question_id'], 
                                mapping['node_id']
                            )
                            if result and result.get('status') == 'success':
                                st.success("✅ 关联已删除")
                                st.rerun()
                            else:
                                st.error("❌ 删除关联失败")
                        except Exception as e:
                            st.error(f"❌ 删除关联失败: {str(e)}")
        else:
            st.info("📭 暂无关联关系")
            
    except Exception as e:
        st.error(f"❌ 获取关联关系失败: {str(e)}")
        # 显示临时数据
        st.info("💡 显示示例数据")
        mappings = [
            {"question_id": 1, "question_text": "解方程 x² - 5x + 6 = 0", "node_id": "math_001", "node_name": "一元二次方程"},
            {"question_id": 2, "question_text": "函数 f(x) = 2x + 1", "node_id": "math_002", "node_name": "函数的概念"}
        ]
        
        if mappings:
            df = pd.DataFrame(mappings)
            st.dataframe(df, use_container_width=True)

def render_question_stats(api_service):
    """渲染题目统计信息"""
    st.subheader("📊 题目统计")
    try:
        stats = api_service.get_questions_stats()
        if not stats:
            stats = {
                "total_questions": 0,
                "published_questions": 0,
                "draft_questions": 0,
                "type_distribution": {"选择题": 0, "填空题": 0, "解答题": 0},
                "avg_difficulty": 0.0,
                "recent_added": 0,
                "difficulty_distribution": {
                    "简单 (0.0-0.3)": 0,
                    "中等 (0.3-0.7)": 0,
                    "困难 (0.7-1.0)": 0
                }
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
        
        if sum(stats["type_distribution"].values()) > 0:
            df_type = pd.DataFrame({
                "类型": list(stats["type_distribution"].keys()),
                "数量": list(stats["type_distribution"].values())
            })
            st.bar_chart(df_type.set_index("类型"))
        else:
            st.info("📭 暂无题目类型数据")
        
        # 难度分布
        st.subheader("🎯 难度分布")
        
        difficulty_ranges = stats.get("difficulty_distribution", {
            "简单 (0.0-0.3)": 0,
            "中等 (0.3-0.7)": 0,
            "困难 (0.7-1.0)": 0
        })
        
        if sum(difficulty_ranges.values()) > 0:
            df_diff = pd.DataFrame({
                "难度": list(difficulty_ranges.keys()),
                "数量": list(difficulty_ranges.values())
            })
            st.bar_chart(df_diff.set_index("难度"))
        else:
            st.info("📭 暂无难度分布数据")
            
    except Exception as e:
        st.error(f"❌ 获取统计信息失败: {str(e)}")
        st.info("💡 显示示例统计数据")
        
        # 显示示例数据
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("📝 总题目数", "--")
        with col2:
            st.metric("📤 已发布", "--")
        with col3:
            st.metric("📝 草稿", "--")
        with col4:
            st.metric("🆕 本周新增", "--")


def render_add_question(api_service, user_id):
    """渲染添加题目页面"""
    st.subheader("➕ 添加新题目")
    
    with st.form("add_question_form"):
        # 基本信息
        col1, col2 = st.columns([2, 1])
        
        with col1:
            question_text = st.text_area("📝 题目内容", placeholder="请输入题目内容...")
            question_type = st.selectbox("📋 题目类型", ["选择题", "填空题", "解答题"])
            
            # 选择题选项
            options = {}
            if question_type == "选择题":
                st.write("**选项设置:**")
                option_a = st.text_input("选项 A", placeholder="输入选项A内容")
                option_b = st.text_input("选项 B", placeholder="输入选项B内容")
                option_c = st.text_input("选项 C", placeholder="输入选项C内容")
                option_d = st.text_input("选项 D", placeholder="输入选项D内容")
                options = {"A": option_a, "B": option_b, "C": option_c, "D": option_d}
            
            answer = st.text_input("✅ 正确答案", placeholder="输入正确答案")
            analysis = st.text_area("📖 答案解析", placeholder="请输入答案解析...")
        
        with col2:
            difficulty = st.slider("🎯 难度系数", 0.0, 1.0, 0.5, 0.1)
            status = st.selectbox("📊 状态", ["draft", "published"])
            
            # 图片URL输入
            question_image_url = st.text_input("🖼️ 题目图片链接", placeholder="请输入图片URL地址（可选）")
        
        # 提交按钮
        submitted = st.form_submit_button("✅ 添加题目", use_container_width=True)
        
        if submitted:
            if not question_text or not answer:
                st.error("❌ 请填写题目内容和答案")
            elif question_type == "选择题" and not all(options.values()):
                st.error("❌ 选择题请填写所有选项")
            else:
                try:
                    # 准备题目数据
                    question_data = {
                        "question_text": question_text,
                        "question_type": question_type,
                        "answer": answer,
                        "analysis": analysis,
                        "difficulty": difficulty,
                        "status": status,
                        "created_by": user_id
                    }
                    
                    # 添加选项（如果是选择题）
                    if question_type == "选择题":
                        question_data["options"] = json.dumps(options)
                    
                    # 添加图片URL（如果提供）
                    if question_image_url and question_image_url.strip():
                        question_data["question_image_url"] = question_image_url.strip()
                    
                    # 调用API创建题目
                    response = api_service.create_question(question_data)
                    
                    if response:
                        st.success("✅ 题目添加成功！")
                        st.rerun()
                    else:
                        st.error("❌ 题目添加失败")
                        
                except Exception as e:
                    st.error(f"❌ 添加题目失败: {str(e)}")