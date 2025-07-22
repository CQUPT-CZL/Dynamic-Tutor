#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
教师端 - 知识点管理页面
实现知识点的增删改查功能
"""

import streamlit as st
import pandas as pd
import time
from datetime import datetime

def render_knowledge_management_page(api_service, current_user, user_id):
    """渲染知识点管理页面"""
    
    # 添加自定义CSS样式
    st.markdown("""
    <style>
    .knowledge-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        color: white;
        margin-bottom: 2rem;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
    }
    .knowledge-card h2 {
        margin: 0;
        font-size: 2.5rem;
        font-weight: 700;
    }
    .knowledge-card p {
        margin: 0.5rem 0 0 0;
        font-size: 1.1rem;
        opacity: 0.9;
    }
    .stExpander {
        border: 1px solid #e0e0e0;
        border-radius: 10px;
        margin-bottom: 1rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .stExpander > div > div > div > div {
        padding: 1rem;
    }
    .metric-container {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        margin: 0.5rem 0;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="knowledge-card">
        <h2>📚 知识点管理</h2>
        <p>管理系统中的所有知识点，支持增删改查操作</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 创建标签页
    tab1, tab2, tab3, tab4 = st.tabs(["📋 知识点列表", "➕ 添加知识点", "🔗 知识点关系", "📊 统计信息"])
    
    with tab1:
        render_knowledge_list(api_service, user_id)
    
    with tab2:
        render_add_knowledge(api_service, user_id)
    
    with tab3:
        render_knowledge_relations(api_service)
    
    with tab4:
        render_knowledge_stats(api_service)

def render_knowledge_list(api_service, user_id):
    """渲染知识点列表"""
    st.subheader("📋 知识点列表")
    
    # 搜索和过滤
    col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
    with col1:
        search_term = st.text_input("🔍 搜索知识点", placeholder="输入知识点名称")
    with col2:
        level_filter = st.selectbox("📊 年级筛选", ["全部"] + list(range(1, 13)))
    with col3:
        # 添加难度范围过滤
        difficulty_range = st.slider("🎯 难度范围", 0.0, 1.0, (0.0, 1.0), step=0.1)
    with col4:
        if st.button("🔄 刷新列表", key="refresh_knowledge_list"):
            st.rerun()
    
    try:
        # 调用API获取知识点列表
        level_filter_value = None if level_filter == "全部" else str(level_filter)
        min_difficulty = difficulty_range[0] if difficulty_range[0] > 0.0 else None
        max_difficulty = difficulty_range[1] if difficulty_range[1] < 1.0 else None
        
        # 根据后端API调用正确的方法
        response = api_service.get_knowledge_nodes(
            level=level_filter_value,
            min_difficulty=min_difficulty,
            max_difficulty=max_difficulty
        )
        knowledge_nodes = response.get("knowledge_points", []) if response else []
        
        # 如果API调用失败，返回空数据
        if not knowledge_nodes:
            knowledge_nodes = [
                {
                    "node_id": "1",
                    "node_name": "这个范围内没有任何知识点～",
                    "node_difficulty": 0.7,
                    "level": 9,
                    "node_learning": "掌握一元二次方程的解法和应用"
                },
            ]
        
        # 应用过滤条件
        filtered_nodes = knowledge_nodes
        if search_term:
            filtered_nodes = [node for node in filtered_nodes 
                            if search_term.lower() in node['node_name'].lower()]
        
        if level_filter != "全部":
            filtered_nodes = [node for node in filtered_nodes if node['level'] == level_filter]
        
        if not filtered_nodes:
            st.info("📭 没有找到符合条件的知识点")
            return
        
        # 显示统计信息
        st.markdown("---")
        st.write(f"📊 找到 **{len(filtered_nodes)}** 个知识点")
        
        for i, node in enumerate(filtered_nodes):
            with st.expander(f"📚 {node['node_name']}", expanded=False):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.write(f"**年级:** {node['level']}年级 (难度系数: {node['node_difficulty']})")
                    st.write(f"**学习目标:** {node['node_learning']}")
                
                with col2:
                    # 添加详情查看按钮
                    if st.button(f"📖 详情", key=f"detail_{node['node_id']}"):
                        st.session_state[f"viewing_{node['node_id']}"] = True
                        st.rerun()
                    
                    if st.button(f"✏️ 编辑", key=f"edit_{node['node_id']}"):
                        st.session_state[f"editing_{node['node_id']}"] = True
                        st.rerun()
                    
                    if st.button(f"🗑️ 删除", key=f"delete_{node['node_id']}"):
                        if st.session_state.get(f"confirm_delete_{node['node_id']}", False):
                            try:
                                # 调用API删除知识点
                                result = api_service.delete_knowledge_node(node['node_id'])
                                
                                if result and result.get('status') == 'success':
                                    st.success(f"✅ 已删除知识点: {node['node_name']}")
                                    st.rerun()
                                else:
                                    st.error(f"❌ 删除失败: {result.get('message', '未知错误') if result else '网络错误'}")
                            except Exception as e:
                                st.error(f"❌ 删除知识点失败: {str(e)}")
                        else:
                            st.session_state[f"confirm_delete_{node['node_id']}"] = True
                            st.warning("⚠️ 再次点击确认删除")
                
                # 详情查看模式
                if st.session_state.get(f"viewing_{node['node_id']}", False):
                    st.markdown("---")
                    
                    # 在顶部添加关闭按钮
                    col_title, col_close = st.columns([4, 1])
                    with col_title:
                        st.subheader("📖 知识点详情")
                    with col_close:
                        if st.button("❌ 关闭", key=f"close_detail_{node['node_id']}", help="关闭详情页面"):
                            del st.session_state[f"viewing_{node['node_id']}"]
                            st.rerun()
                    
                    try:
                        # 调用API获取详细信息
                        detail_response = api_service.get_knowledge_node(node['node_id'])
                        
                        if detail_response:
                            node_info = detail_response.get('node_info', {})
                            prerequisites = detail_response.get('prerequisites', [])
                            next_nodes = detail_response.get('next_nodes', [])
                            
                            # 显示基本信息
                            st.write(f"**ID:** {node_info.get('node_id', 'N/A')}")
                            st.write(f"**名称:** {node_info.get('node_name', 'N/A')}")
                            st.write(f"**年级:** {node_info.get('level', 'N/A')}年级")
                            st.write(f"**难度系数:** {node_info.get('node_difficulty', 'N/A')}")
                            st.write(f"**学习目标:** {node_info.get('node_learning', 'N/A')}")
                            
                            # 显示前置知识点
                            if prerequisites:
                                st.subheader("🔗 前置知识点")
                                for prereq in prerequisites:
                                    st.write(f"• {prereq.get('node_name', 'N/A')} (ID: {prereq.get('node_id', 'N/A')})")
                            else:
                                st.info("📭 无前置知识点")
                            
                            # 显示后续知识点
                            if next_nodes:
                                st.subheader("➡️ 后续知识点")
                                for next_node in next_nodes:
                                    st.write(f"• {next_node.get('node_name', 'N/A')} (ID: {next_node.get('node_id', 'N/A')})")
                            else:
                                st.info("📭 无后续知识点")
                        else:
                            st.error("❌ 获取详情失败")
                    except Exception as e:
                        st.error(f"❌ 获取知识点详情失败: {str(e)}")
                
                # 编辑模式
                if st.session_state.get(f"editing_{node['node_id']}", False):
                    st.markdown("---")
                    st.subheader("✏️ 编辑知识点")
                    
                    new_name = st.text_input("知识点名称", value=node['node_name'], key=f"edit_name_{node['node_id']}")
                    grade_options = list(range(1, 13))
                    current_index = grade_options.index(node['level']) if node['level'] in grade_options else 0
                    new_level = st.selectbox("年级等级", grade_options, 
                                           index=current_index, 
                                           key=f"edit_level_{node['node_id']}")
                    new_difficulty = st.slider("难度系数", 0.0, 1.0, node['node_difficulty'], 
                                              key=f"edit_difficulty_{node['node_id']}")
                    new_learning = st.text_area("学习目标", value=node['node_learning'], 
                                               key=f"edit_learning_{node['node_id']}")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("💾 保存修改", key=f"save_{node['node_id']}"):
                            try:
                                # 调用API更新知识点
                                # print(new_name, new_level, new_difficulty, new_learning)
                                result = api_service.update_knowledge_node(int(node['node_id']), {
                                    'node_id': int(node['node_id']),
                                    'node_name': new_name,
                                    'level': int(new_level),
                                    'node_difficulty': new_difficulty,
                                    'node_learning': new_learning
                                })
                                
                                if result and result.get('status') == 'success':
                                    st.success("✅ 知识点更新成功！")
                                    del st.session_state[f"editing_{node['node_id']}"]
                                    st.rerun()
                                else:
                                    st.error(f"❌ 更新失败: {result.get('message', '未知错误') if result else '网络错误'}")
                            except Exception as e:
                                st.error(f"❌ 更新知识点失败: {str(e)}")
                    
                    with col2:
                        if st.button("❌ 取消编辑", key=f"cancel_{node['node_id']}"):
                            del st.session_state[f"editing_{node['node_id']}"]
                            st.rerun()
        
    except Exception as e:
        st.error(f"❌ 获取知识点列表失败: {str(e)}")
        st.info("💡 请确保后端API服务正常运行")

def render_add_knowledge(api_service, user_id):
    """渲染添加知识点界面"""
    st.subheader("➕ 添加新知识点")
    
    # 初始化session state
    if 'generated_learning_objective' not in st.session_state:
        st.session_state['generated_learning_objective'] = ''
    if 'use_generated_objective' not in st.session_state:
        st.session_state['use_generated_objective'] = False
    
    # 表单外的输入控件
    col1, col2 = st.columns(2)
    
    with col1:
        node_name = st.text_input("📚 知识点名称", placeholder="例如: 三角函数")
        level = st.selectbox("📊 年级等级", [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12])
    
    with col2:
        difficulty = st.slider("🎯 难度系数", 0.0, 1.0, 0.5, step=0.1)
        st.write("")
        st.write("")
    
    # 学习目标输入区域（表单外）
    col_learning1, col_learning2 = st.columns([4, 1])
    
    with col_learning1:
        # 如果有生成的内容且用户选择使用，则显示生成的内容
        default_value = st.session_state['generated_learning_objective'] if st.session_state['use_generated_objective'] else ''
        node_learning = st.text_area("🎯 学习目标", placeholder="描述学生需要掌握的知识点和技能", value=default_value)
    
    with col_learning2:
        st.write("")
        st.write("")
        # AI生成按钮和状态管理
        if 'ai_generating' not in st.session_state:
            st.session_state['ai_generating'] = False
        if 'generation_start_time' not in st.session_state:
            st.session_state['generation_start_time'] = None
            
        # 显示生成按钮或取消按钮
        if not st.session_state['ai_generating']:
            if st.button("🤖 AI生成", help="点击使用AI生成学习目标", key="ai_generate_btn"):
                if node_name.strip():
                    st.session_state['ai_generating'] = True
                    st.session_state['generation_start_time'] = time.time()
                    st.rerun()
                else:
                    st.warning("⚠️ 请先填写知识点名称")
        else:
            # 显示取消按钮和进度信息
            col_cancel1, col_cancel2 = st.columns([1, 1])
            with col_cancel1:
                if st.button("❌ 取消生成", key="cancel_generate_btn"):
                    st.session_state['ai_generating'] = False
                    st.session_state['generation_start_time'] = None
                    st.info("🔄 AI生成已取消")
                    st.rerun()
            
            with col_cancel2:
                # 显示生成时间
                if st.session_state['generation_start_time']:
                    elapsed = time.time() - st.session_state['generation_start_time']
                    st.write(f"⏱️ 已用时: {elapsed:.1f}秒")
            
            # 执行AI生成
            try:
                # 获取年级信息
                level_map = {0: "幼儿园", 1: "小学一年级", 2: "小学二年级", 3: "小学三年级", 
                           4: "小学四年级", 5: "小学五年级", 6: "小学六年级", 7: "初中一年级", 
                           8: "初中二年级", 9: "初中三年级", 10: "高中一年级", 11: "高中二年级", 12: "高中三年级"}
                level_str = level_map.get(level, f"年级{level}")
                
                # 显示生成状态
                with st.spinner(f"🤖 AI正在为'{node_name}'({level_str})生成学习目标..."):
                    # 调用AI生成接口
                    result = api_service.generate_learning_objective(node_name.strip(), level_str)
                    
                    # 重置生成状态
                    st.session_state['ai_generating'] = False
                    st.session_state['generation_start_time'] = None
                    
                    if result.get('status') == 'success':
                        # 保存生成的内容到session state
                        st.session_state['generated_learning_objective'] = result.get('learning_objective', '')
                        st.session_state['use_generated_objective'] = True
                        st.success("✅ AI生成成功！内容已自动填充到学习目标框中")
                        st.rerun()
                    else:
                        st.error(f"❌ AI生成失败: {result.get('message', '未知错误')}")
                        
            except Exception as e:
                # 重置生成状态
                st.session_state['ai_generating'] = False
                st.session_state['generation_start_time'] = None
                st.error(f"❌ AI生成失败: {str(e)}")
        
        # 添加清除按钮
        if st.session_state['use_generated_objective'] and st.session_state['generated_learning_objective']:
            if st.button("🗑️ 清除", help="清除AI生成的内容", key="clear_generated_btn"):
                st.session_state['generated_learning_objective'] = ''
                st.session_state['use_generated_objective'] = False
                st.rerun()
    
    # 表单部分（只包含前置知识点选择和提交按钮）
    with st.form("add_knowledge_form"):
        
        # 前置知识点选择
        st.subheader("🔗 前置知识点（可选）")
        
        # 获取现有知识点供选择
        try:
            existing_response = api_service.get_knowledge_nodes()
            existing_nodes = existing_response.get("knowledge_points", []) if existing_response else []
            
            if existing_nodes:
                # 创建选择框
                node_options = [f"{node['node_name']} (ID: {node['node_id']})" for node in existing_nodes]
                selected_prerequisites = st.multiselect(
                    "选择前置知识点",
                    options=node_options,
                    help="可以选择多个前置知识点"
                )
                
                # 提取选中的节点ID
                prerequisites = []
                for selected in selected_prerequisites:
                    # 从选项中提取ID
                    node_id = selected.split("ID: ")[1].rstrip(")")
                    prerequisites.append(node_id)
            else:
                st.info("📭 暂无现有知识点可选择")
                prerequisites_input = st.text_input("前置知识点", placeholder="输入前置知识点名称或ID，多个用逗号分隔")
                prerequisites = [p.strip() for p in prerequisites_input.split(',') if p.strip()] if prerequisites_input.strip() else []
                
        except Exception as e:
            st.warning(f"⚠️ 获取现有知识点失败: {str(e)}，使用手动输入模式")
            prerequisites_input = st.text_input("前置知识点", placeholder="输入前置知识点名称或ID，多个用逗号分隔")
            prerequisites = [p.strip() for p in prerequisites_input.split(',') if p.strip()] if prerequisites_input.strip() else []
        
        submitted = st.form_submit_button("➕ 添加知识点", use_container_width=True)
        
        if submitted:
            if not node_name or not node_learning:
                st.error("❌ 请填写所有必填字段")
            else:
                try:
                    # 调用API添加知识点
                    result = api_service.create_knowledge_node({
                        'node_name': node_name,
                        'node_difficulty': difficulty,
                        'level': level,
                        'node_learning': node_learning,
                        'prerequisites': prerequisites
                    })
                    
                    if result.get('status') == 'success':
                        st.success(f"✅ 成功添加知识点: {node_name} (ID: {result.get('node_id')})")
                        st.balloons()
                    else:
                        st.error(f"❌ 添加知识点失败: {result.get('message', '未知错误')}")
                    
                except Exception as e:
                    st.error(f"❌ 添加知识点失败: {str(e)}")

def render_knowledge_relations(api_service):
    """渲染知识点关系页面"""
    st.subheader("🔗 知识点关系管理")
    
    # 选择知识点查看其关系
    col1, col2 = st.columns([2, 1])
    
    with col1:
        node_id_input = st.text_input("🔍 输入知识点ID", placeholder="输入要查看关系的知识点ID")
    
    with col2:
        if st.button("🔍 查看关系", key="view_relations"):
            if node_id_input.strip():
                st.session_state['selected_node_id'] = node_id_input.strip()
                st.rerun()
    
    # 显示选中知识点的关系
    if st.session_state.get('selected_node_id'):
        node_id = st.session_state['selected_node_id']
        
        try:
            # 获取知识点详情
            detail_response = api_service.get_knowledge_node(node_id)
            
            if detail_response:
                node_info = detail_response.get('node_info', {})
                prerequisites = detail_response.get('prerequisites', [])
                next_nodes = detail_response.get('next_nodes', [])
                
                st.markdown("---")
                st.subheader(f"📚 {node_info.get('node_name', 'N/A')} 的关系图")
                
                # 创建三列布局显示关系
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.markdown("### 🔗 前置知识点")
                    if prerequisites:
                        for prereq in prerequisites:
                            with st.container():
                                st.markdown(f"""
                                <div style="background-color: #e8f4fd; padding: 10px; margin: 5px 0; border-radius: 5px; border-left: 4px solid #1f77b4;">
                                    <strong>{prereq.get('node_name', 'N/A')}</strong><br>
                                    <small>ID: {prereq.get('node_id', 'N/A')} | 年级: {prereq.get('level', 'N/A')}</small>
                                </div>
                                """, unsafe_allow_html=True)
                    else:
                        st.info("📭 无前置知识点")
                
                with col2:
                    st.markdown("### 🎯 当前知识点")
                    st.markdown(f"""
                    <div style="background-color: #fff2e8; padding: 15px; margin: 5px 0; border-radius: 5px; border: 2px solid #ff7f0e; text-align: center;">
                        <h4>{node_info.get('node_name', 'N/A')}</h4>
                        <p><strong>年级:</strong> {node_info.get('level', 'N/A')}</p>
                        <p><strong>难度:</strong> {node_info.get('node_difficulty', 'N/A')}</p>
                        <p><strong>ID:</strong> {node_info.get('node_id', 'N/A')}</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col3:
                    st.markdown("### ➡️ 后续知识点")
                    if next_nodes:
                        for next_node in next_nodes:
                            with st.container():
                                st.markdown(f"""
                                <div style="background-color: #e8f5e8; padding: 10px; margin: 5px 0; border-radius: 5px; border-left: 4px solid #2ca02c;">
                                    <strong>{next_node.get('node_name', 'N/A')}</strong><br>
                                    <small>ID: {next_node.get('node_id', 'N/A')}</small>
                                </div>
                                """, unsafe_allow_html=True)
                    else:
                        st.info("📭 无后续知识点")
                
                # 添加学习路径建议
                st.markdown("---")
                st.subheader("🛤️ 学习路径建议")
                
                if prerequisites:
                    st.write("**建议学习顺序:**")
                    for i, prereq in enumerate(prerequisites, 1):
                        st.write(f"{i}. {prereq.get('node_name', 'N/A')}")
                    st.write(f"{len(prerequisites) + 1}. **{node_info.get('node_name', 'N/A')}** (当前)")
                    if next_nodes:
                        for i, next_node in enumerate(next_nodes, len(prerequisites) + 2):
                            st.write(f"{i}. {next_node.get('node_name', 'N/A')}")
                else:
                    st.info("💡 这是一个基础知识点，可以直接开始学习")
                    
            else:
                st.error("❌ 未找到该知识点")
                
        except Exception as e:
            st.error(f"❌ 获取知识点关系失败: {str(e)}")
    
    # 显示所有知识点的简单列表供参考
    st.markdown("---")
    st.subheader("📋 知识点参考列表")
    
    try:
        response = api_service.get_knowledge_nodes()
        if response and response.get("knowledge_points"):
            knowledge_points = response["knowledge_points"]
            
            # 创建一个简单的表格显示
            df_data = []
            for kp in knowledge_points:
                df_data.append({
                    "ID": kp.get("node_id", "N/A"),
                    "名称": kp.get("node_name", "N/A"),
                    "年级": kp.get("level", "N/A"),
                    "难度": kp.get("node_difficulty", "N/A")
                })
            
            if df_data:
                df = pd.DataFrame(df_data)
                st.dataframe(df, use_container_width=True)
        else:
            st.info("📭 暂无知识点数据")
    except Exception as e:
        st.error(f"❌ 获取知识点列表失败: {str(e)}")

def render_knowledge_stats(api_service):
    """渲染知识点统计信息"""
    st.subheader("📊 知识点统计")
    
    try:
        # 获取所有知识点数据进行统计
        response = api_service.get_knowledge_nodes()
        if response and response.get("knowledge_points"):
            knowledge_points = response["knowledge_points"]
            
            # 计算统计数据
            total_nodes = len(knowledge_points)
            difficulties = [kp.get('node_difficulty', 0) for kp in knowledge_points if kp.get('node_difficulty') is not None]
            avg_difficulty = sum(difficulties) / len(difficulties) if difficulties else 0
            
            # 年级分布统计
            level_counts = {}
            for kp in knowledge_points:
                level = kp.get('level', 'Unknown')
                level_counts[f"{level}年级"] = level_counts.get(f"{level}年级", 0) + 1
            
            # 难度分布统计
            difficulty_ranges = {"简单(0-0.3)": 0, "中等(0.3-0.7)": 0, "困难(0.7-1.0)": 0}
            for diff in difficulties:
                if diff <= 0.3:
                    difficulty_ranges["简单(0-0.3)"] += 1
                elif diff <= 0.7:
                    difficulty_ranges["中等(0.3-0.7)"] += 1
                else:
                    difficulty_ranges["困难(0.7-1.0)"] += 1
            
            # 显示统计卡片
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("📚 总知识点数", total_nodes)
            
            with col2:
                st.metric("📊 平均难度", f"{avg_difficulty:.2f}")
            
            with col3:
                max_level = max([kp.get('level', 0) for kp in knowledge_points]) if knowledge_points else 0
                st.metric("📈 最高年级", f"{max_level}年级")
            
            with col4:
                min_level = min([kp.get('level', 12) for kp in knowledge_points]) if knowledge_points else 0
                st.metric("📉 最低年级", f"{min_level}年级")
            
            # 年级分布图表
            st.subheader("📊 年级分布")
            if level_counts:
                df_level = pd.DataFrame({
                    "年级": list(level_counts.keys()),
                    "数量": list(level_counts.values())
                })
                st.bar_chart(df_level.set_index("年级"))
            else:
                st.info("📭 暂无年级分布数据")
            
            # 难度分布图表
            st.subheader("🎯 难度分布")
            if any(difficulty_ranges.values()):
                df_difficulty = pd.DataFrame({
                    "难度等级": list(difficulty_ranges.keys()),
                    "数量": list(difficulty_ranges.values())
                })
                st.bar_chart(df_difficulty.set_index("难度等级"))
            else:
                st.info("📭 暂无难度分布数据")
            
            # 详细数据表
            st.subheader("📋 详细统计表")
            
            # 年级统计表
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**年级分布:**")
                if level_counts:
                    for level, count in sorted(level_counts.items()):
                        percentage = (count / total_nodes) * 100
                        st.write(f"• {level}: {count} 个 ({percentage:.1f}%)")
            
            with col2:
                st.write("**难度分布:**")
                for diff_range, count in difficulty_ranges.items():
                    percentage = (count / total_nodes) * 100 if total_nodes > 0 else 0
                    st.write(f"• {diff_range}: {count} 个 ({percentage:.1f}%)")
            
            # 知识点列表预览
            st.subheader("🔍 知识点预览")
            
            # 按难度排序显示前5个最难的知识点
            sorted_by_difficulty = sorted(knowledge_points, 
                                        key=lambda x: x.get('node_difficulty', 0), 
                                        reverse=True)[:5]
            
            if sorted_by_difficulty:
                st.write("**最具挑战性的知识点:**")
                for i, kp in enumerate(sorted_by_difficulty, 1):
                    st.write(f"{i}. {kp.get('node_name', 'N/A')} (难度: {kp.get('node_difficulty', 'N/A')}, {kp.get('level', 'N/A')}年级)")
        
        else:
            st.info("📭 暂无知识点数据可供统计")
            
            # 显示空状态的统计卡片
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("📚 总知识点数", 0)
            
            with col2:
                st.metric("📊 平均难度", "0.00")
            
            with col3:
                st.metric("📈 最高年级", "N/A")
            
            with col4:
                st.metric("📉 最低年级", "N/A")
            
    except Exception as e:
        st.error(f"❌ 获取统计信息失败: {str(e)}")
        st.info("💡 请确保后端API服务正常运行")
        
        # 显示错误状态的统计卡片
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("📚 总知识点数", "错误")
        
        with col2:
            st.metric("📊 平均难度", "错误")
        
        with col3:
            st.metric("📈 最高年级", "错误")
        
        with col4:
            st.metric("📉 最低年级", "错误")