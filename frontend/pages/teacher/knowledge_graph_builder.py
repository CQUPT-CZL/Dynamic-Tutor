#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
教师端 - 知识图谱构建页面
实现知识图谱的可视化和管理功能
"""

import streamlit as st
import pandas as pd
import json
from datetime import datetime

def render_knowledge_graph_builder_page(api_service, current_user, user_id):
    """渲染知识图谱构建页面"""
    st.markdown("""
    <div class="node-info">
        <h2>🕸️ 知识图谱构建</h2>
        <p>构建和管理知识点之间的关系，创建完整的知识图谱</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 创建标签页
    tab1, tab2 = st.tabs(["🕸️ 图谱可视化", "🔗 关系管理"])
    
    with tab1:
        render_graph_visualization(api_service, user_id)
    
    with tab2:
        render_relationship_management(api_service, user_id)

def render_graph_visualization(api_service, user_id):
    """渲染知识图谱可视化"""
    st.subheader("🕸️ 知识图谱可视化")

    # 获取知识图谱数据
    try:
        graph_data = api_service.get_knowledge_graph_data()
        all_nodes = graph_data.get('nodes', [])
        all_edges = graph_data.get('edges', [])
        
        # 如果没有数据，则显示提示信息
        if not all_nodes or not all_edges:
            st.info("📭 暂无知识图谱数据，请先在下方添加知识点和关系。")
            return

    except Exception as e:
        st.error(f"❌ 加载知识图谱失败: {str(e)}")
        st.info("💡 请确保后端API服务正常运行")
        return

    # 提取模块用于下拉选择
    modules = [node for node in all_nodes if node.get('node_type') == '模块']
    
    if not modules:
        st.info("ℹ️ 暂无模块可供选择，请先创建模块。")
        return

    # 控制面板
    col1, col3, col5 = st.columns([2, 1, 1])
    
    with col1:
        # 使用模块名称作为选项
        module_names = [m['name'] for m in modules]
        selected_module_name = st.selectbox("📚 选择模块", options=module_names, index=0)
        # 根据选择的名称找到对应的模块ID
        selected_module_id = next((m['id'] for m in modules if m['name'] == selected_module_name), None)

    with col3:
        show_labels = st.checkbox("🏷️ 显示标签", value=True)
    
    with col5:
        if st.button("🔄 刷新图谱"):
            st.rerun()

    if not selected_module_id:
        st.error("❌ 无法找到所选模块。")
        return

    # 根据选择的模块筛选节点和边，不展示模块节点
    # 找出模块包含的所有知识点ID
    module_kp_ids = {edge['target'] for edge in all_edges if edge['source'] == selected_module_id and edge['relation'] == '包含'}
    
    # 只筛选知识点节点
    nodes = [node for node in all_nodes if node['id'] in module_kp_ids]
    
    # 只筛选模块内知识点之间的“指向”关系
    edges = [
        edge for edge in all_edges 
        if (edge['source'] in module_kp_ids and 
            edge['target'] in module_kp_ids and 
            edge['relation'] == '指向')
    ]

    if not nodes:
        st.info("ℹ️ 当前模块下没有知识点或关系。")
        return

    # 创建并显示图谱
    graph_html = create_graph_html(nodes, edges, show_labels, 30)
    st.components.v1.html(graph_html, height=600)
    
    # 更新图例
    st.markdown("### 📖 图例说明")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        **节点类型:**
        - 🟢 **概念/定理** (难度 < 0.5)
        - 🟡 **概念/定理** (0.5 ≤ 难度 < 0.8)
        - 🔴 **概念/定理** (难度 ≥ 0.8)
        """)
    with col2:
        st.markdown("""
        **关系类型:**
        - <span style='color:#337ab7; font-weight:bold;'>--►</span> **指向** (知识点之间)
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
        **关系状态:**
        - **(实线)** 已发布
        - **(虚线)** 草稿
        """)

def create_graph_html(nodes, edges, show_labels, node_size):
    """创建知识图谱的HTML可视化"""
    html_template = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <script src="https://d3js.org/d3.v7.min.js"></script>
        <style>
            #graph svg {{
                border: 2px solid #f0f2f6;
                border-radius: 8px;
            }}
            .node {{
                stroke: #fff;
                stroke-width: 2px;
                cursor: pointer;
            }}
            .link {{
                stroke-opacity: 0.7;
                stroke-width: 2px;
            }}
            .link.包含 {{
                stroke: #888;
            }}
            .link.指向 {{
                stroke: #337ab7;
            }}
            .label {{
                font-family: Arial, sans-serif;
                font-size: 12px;
                text-anchor: middle;
                pointer-events: none;
                fill: #333;
            }}
            .tooltip {{
                position: absolute;
                background: rgba(0, 0, 0, 0.8);
                color: white;
                padding: 8px;
                border-radius: 4px;
                font-size: 12px;
                pointer-events: none;
                opacity: 0;
                transition: opacity 0.2s;
            }}
        </style>
    </head>
    <body>
        <div id="graph"></div>
        <div class="tooltip" id="tooltip"></div>
        
        <script>
            const nodes = {json.dumps(nodes)};
            const links = {json.dumps(edges)};

            const container = d3.select("#graph");
            const width = container.node().getBoundingClientRect().width || 800;
            const height = 600;

            const svg = container.append("svg")
                .attr("width", width)
                .attr("height", height);

            const g = svg.append("g");

            // 定义箭头
            svg.append("defs").selectAll("marker")
                .data(["指向"])
                .enter().append("marker")
                .attr("id", d => `arrow-${{d}}`)
                .attr("viewBox", "0 -5 10 10")
                .attr("refX", {node_size + 5})
                .attr("refY", 0)
                .attr("markerWidth", 6)
                .attr("markerHeight", 6)
                .attr("orient", "auto")
                .append("path")
                .attr("fill", "#337ab7")
                .attr("d", "M0,-5L10,0L0,5");

            const simulation = d3.forceSimulation(nodes)
                .force("link", d3.forceLink(links).id(d => d.id).distance(d => d.relation === '包含' ? 100 : 150))
                .force("charge", d3.forceManyBody().strength(-600))
                .force("center", d3.forceCenter(width / 2, height / 2));
            
            const link = g.append("g")
                .selectAll("line")
                .data(links)
                .enter().append("line")
                .attr("class", d => `link ${{d.relation}}`)
                .style("stroke-dasharray", d => d.status === "draft" ? "5,5" : "none")
                .attr("marker-end", d => d.relation === '指向' ? `url(#arrow-${{d.relation}})` : null);
            
            const node = g.append("g")
                .selectAll("circle")
                .data(nodes)
                .enter().append("circle")
                .attr("class", "node")
                .attr("r", {node_size})
                .style("fill", d => {{
                    if (d.type === '模块') return "#337ab7"; // 蓝色
                    const difficulty = d.difficulty || 0;
                    if (difficulty < 0.5) return "#5cb85c"; // 绿色
                    if (difficulty < 0.8) return "#f0ad4e"; // 黄色
                    return "#d9534f"; // 红色
                }})
                .call(d3.drag()
                    .on("start", dragstarted)
                    .on("drag", dragged)
                    .on("end", dragended));
            
            const label = g.append("g")
                .selectAll("text")
                .data(nodes)
                .enter().append("text")
                .attr("class", "label")
                .text(d => d.name)
                .style("display", {"'block'" if show_labels else "'none'"});
            
            const tooltip = d3.select("#tooltip");
            
            node.on("mouseover", function(event, d) {{
                tooltip.style("opacity", .9);
                tooltip.html(`
                    <strong>${{d.name}}</strong><br/>
                    ID: ${{d.id}}<br/>
                    类型: ${{d.type || 'N/A'}}<br/>
                    ${{d.type !== '模块' ? `等级: ${{d.level || 'N/A'}}<br/>` : ''}}
                    ${{d.type !== '模块' ? `难度: ${{d.difficulty || 'N/A'}}` : ''}}
                `)
                .style("left", (event.pageX + 10) + "px")
                .style("top", (event.pageY - 28) + "px");
            }})
            .on("mouseout", function(d) {{
                tooltip.style("opacity", 0);
            }});
            
            simulation.on("tick", () => {{
                const r = {node_size};
                node
                    .attr("cx", d => d.x = Math.max(r, Math.min(width - 2 * r, d.x)))
                    .attr("cy", d => d.y = Math.max(r, Math.min(height - 2 * r, d.y)));

                link
                    .attr("x1", d => d.source.x)
                    .attr("y1", d => d.source.y)
                    .attr("x2", d => d.target.x)
                    .attr("y2", d => d.target.y);
                
                label
                    .attr("x", d => d.x)
                    .attr("y", d => d.y + 5);
            }}); 
            
            function dragstarted(event, d) {{
                if (!event.active) simulation.alphaTarget(0.3).restart();
                d.fx = d.x;
                d.fy = d.y;
            }}
            
            function dragged(event, d) {{
                d.fx = event.x;
                d.fy = event.y;
            }}
            
            function dragended(event, d) {{
                if (!event.active) simulation.alphaTarget(0);
                d.fx = null;
                d.fy = null;
            }}
        </script>
    </body>
    </html>
    """
    return html_template

def render_relationship_management(api_service, user_id):
    """渲染关系管理界面"""
    st.subheader("🔗 知识点关系管理")
    
    # 添加新关系
    st.markdown("### ➕ 添加新关系")
    
    with st.form("add_relationship_form"):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # 获取知识点列表
            try:
                nodes_response = api_service.get_knowledge_nodes()
                nodes = nodes_response.get('knowledge_points', []) if isinstance(nodes_response, dict) else []
                
                # 如果没有数据，则显示提示信息
                if not nodes:
                    st.warning("⚠️ 暂无知识点，请先在“知识点管理”页面添加。")
                    source_node = None
                    target_node = None
                else:
                    source_node = st.selectbox(
                        "源知识点",
                        options=nodes,
                        format_func=lambda x: f"{x['node_id']}: {x['node_name']}"
                    )
            except Exception as e:
                st.error(f"❌ 无法获取知识点列表: {str(e)}")
                return
        
        with col2:
            target_node = st.selectbox(
                "目标知识点",
                options=nodes,
                format_func=lambda x: f"{x['node_id']}: {x['node_name']}"
            )
        
        with col3:
            relation_type = st.selectbox(
                "关系类型",
                options=["is_prerequisite_for"],
                format_func=lambda x: {
                    "is_prerequisite_for": "前置关系"
                }[x]
            )
        
        status = st.selectbox("状态", ["draft", "published"], 
                             format_func=lambda x: "草稿" if x == "draft" else "已发布")
        
        submitted = st.form_submit_button("➕ 添加关系", use_container_width=True)
        
        if submitted:
            if source_node['node_id'] == target_node['node_id']:
                st.error("❌ 源知识点和目标知识点不能相同")
            else:
                # 检查边是否已存在
                try:
                    existing_edges = api_service.get_knowledge_edges()
                    
                    # 检查是否已存在相同的边
                    edge_exists = False
                    for edge in existing_edges:
                        if (edge['source_node_id'] == str(source_node['node_id']) and 
                            edge['target_node_id'] == str(target_node['node_id']) and 
                            edge['relation_type'] == relation_type):
                            edge_exists = True
                            break
                    
                    if edge_exists:
                        st.warning(f"⚠️ 关系已存在: {source_node['node_name']} → {target_node['node_name']}")
                    else:
                        # 添加新关系
                        result = api_service.create_knowledge_edge(
                            source_node_id=str(source_node['node_id']),
                            target_node_id=str(target_node['node_id']),
                            relation_type=relation_type,
                            status=status  # 传递状态
                        )
                        
                        if result and result.get('status') == 'success':
                            st.success(f"✅ 成功添加关系: {source_node['node_name']} → {target_node['node_name']}")
                            st.rerun()
                        else:
                            error_message = result.get('message') if result else '未知错误'
                            st.error(f"❌ 添加关系失败: {error_message}")
                    
                except Exception as e:
                    st.error(f"❌ 检查或添加关系失败: {str(e)}")
    
    # 现有关系列表
    st.markdown("---")
    st.markdown("### 📋 现有关系列表")
    
    try:
        edges = api_service.get_knowledge_edges()
        
        # 如果没有数据，则直接返回
        if not edges:
            st.info("📭 暂无知识点关系")
            return
        
        for edge in edges:
            status_color = "🟢" if edge['status'] == "published" else "🟡"
            relation_emoji = {
                "is_prerequisite_for": "➡️"
            }.get(edge['relation_type'], "🔗")
            
            edge_id = edge.get('id', edge.get('edge_id', 0))
            
            with st.expander(f"{status_color} {edge['source_name']} {relation_emoji} {edge['target_name']}", expanded=False):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.write(f"**关系ID:** {edge_id}")
                    st.write(f"**源知识点:** {edge['source_name']} ({edge['source_node_id']})")
                    st.write(f"**目标知识点:** {edge['target_name']} ({edge['target_node_id']})")
                    st.write(f"**关系类型:** {edge['relation_type']}")
                    st.write(f"**状态:** {edge['status']}")
                
                with col2:
                    if edge['status'] == "draft":
                        if st.button(f"📤 发布", key=f"publish_edge_{edge_id}"):
                            st.info("📤 发布功能开发中...")
                    
                    # 检查是否处于确认删除状态
                    confirm_key = f"confirm_delete_edge_{edge_id}"
                    is_confirming = st.session_state.get(confirm_key, False)
                    
                    if is_confirming:
                        st.warning("⚠️ 确认删除此关系？")
                        col_confirm, col_cancel = st.columns(2)
                        
                        with col_confirm:
                            if st.button(f"✅ 确认删除", key=f"confirm_delete_{edge_id}", use_container_width=True):
                                try:
                                    # 使用 edge_id 来删除关系
                                    result = api_service.delete_knowledge_edge(edge_id)
                                    
                                    # 清除确认状态
                                    st.session_state[confirm_key] = False
                                    
                                    if result and result.get('status') == 'success':
                                        st.success(f"✅ 已删除关系 (ID: {edge_id})")
                                        st.rerun()
                                    else:
                                        error_message = result.get('message') if result else '未知错误'
                                        st.error(f"❌ 删除关系失败: {error_message}")
                                except Exception as e:
                                    # 清除确认状态
                                    st.session_state[confirm_key] = False
                                    st.error(f"❌ 删除关系失败: {str(e)}")
                        
                        with col_cancel:
                            if st.button(f"❌ 取消", key=f"cancel_delete_{edge_id}", use_container_width=True):
                                st.session_state[confirm_key] = False
                                st.rerun()
                    else:
                        if st.button(f"🗑️ 删除", key=f"delete_edge_{edge_id}"):
                            st.session_state[confirm_key] = True
                            st.rerun()
        
    except Exception as e:
        st.error(f"❌ 获取关系列表失败: {str(e)}")