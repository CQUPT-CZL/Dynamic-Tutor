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
    
    # 控制面板
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        layout_type = st.selectbox("📐 布局类型", ["力导向", "层次", "圆形", "网格"])
    
    with col2:
        show_labels = st.checkbox("🏷️ 显示标签", value=True)
    
    with col3:
        node_size = st.slider("📏 节点大小", 10, 50, 20)
    
    with col4:
        if st.button("🔄 刷新图谱"):
            st.rerun()
    
    try:
        # 获取知识图谱数据
        graph_data = api_service.get_knowledge_graph_data()
        
        nodes = graph_data.get('nodes', [])
        edges = graph_data.get('edges', [])
        
        # 如果没有数据，使用默认数据
        if not nodes:
            nodes = [
                {"id": "math_001", "name": "一元二次方程", "level": "中级", "difficulty": 0.7},
                {"id": "math_002", "name": "函数的概念", "level": "初级", "difficulty": 0.5},
                {"id": "math_003", "name": "导数与微分", "level": "高级", "difficulty": 0.9},
                {"id": "math_004", "name": "二次函数", "level": "中级", "difficulty": 0.6},
                {"id": "math_005", "name": "函数的性质", "level": "中级", "difficulty": 0.65}
            ]
        
        if not edges:
            edges = [
                {"source": "math_002", "target": "math_004", "relation": "is_prerequisite_for", "status": "published"},
                {"source": "math_004", "target": "math_001", "relation": "is_prerequisite_for", "status": "published"},
                {"source": "math_002", "target": "math_005", "relation": "is_prerequisite_for", "status": "published"},
                {"source": "math_005", "target": "math_003", "relation": "is_prerequisite_for", "status": "draft"}
            ]
        
        # 创建图谱HTML
        graph_html = create_graph_html(nodes, edges, layout_type, show_labels, node_size)
        
        # 显示图谱
        st.components.v1.html(graph_html, height=600)
        
        # 图例
        st.markdown("### 📖 图例说明")
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            **节点颜色:**
            - 🟢 初级 (难度 < 0.5)
            - 🟡 中级 (0.5 ≤ 难度 < 0.8)
            - 🔴 高级 (难度 ≥ 0.8)
            """)
        
        with col2:
            st.markdown("""
            **边的类型:**
            - ➡️ 前置关系 (prerequisite)
            - 🔗 相关关系 (related)
            - 📚 包含关系 (contains)
            """)
        
    except Exception as e:
        st.error(f"❌ 加载知识图谱失败: {str(e)}")
        st.info("💡 请确保后端API服务正常运行")

def create_graph_html(nodes, edges, layout_type, show_labels, node_size):
    """创建知识图谱的HTML可视化"""
    # 这里使用D3.js创建一个简单的力导向图
    html_template = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <script src="https://d3js.org/d3.v7.min.js"></script>
        <style>
            .node {{
                stroke: #fff;
                stroke-width: 2px;
                cursor: pointer;
            }}
            .link {{
                stroke: #999;
                stroke-opacity: 0.6;
                stroke-width: 2px;
            }}
            .label {{
                font-family: Arial, sans-serif;
                font-size: 12px;
                text-anchor: middle;
                pointer-events: none;
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
            }}
        </style>
    </head>
    <body>
        <div id="graph"></div>
        <div class="tooltip" id="tooltip"></div>
        
        <script>
            const nodes = {json.dumps(nodes)};
            const links = {json.dumps(edges)};
            
            const width = 800;
            const height = 500;
            
            const svg = d3.select("#graph")
                .append("svg")
                .attr("width", width)
                .attr("height", height);
            
            const simulation = d3.forceSimulation(nodes)
                .force("link", d3.forceLink(links).id(d => d.id).distance(100))
                .force("charge", d3.forceManyBody().strength(-300))
                .force("center", d3.forceCenter(width / 2, height / 2));
            
            const link = svg.append("g")
                .selectAll("line")
                .data(links)
                .enter().append("line")
                .attr("class", "link")
                .style("stroke-dasharray", d => d.status === "draft" ? "5,5" : "none");
            
            const node = svg.append("g")
                .selectAll("circle")
                .data(nodes)
                .enter().append("circle")
                .attr("class", "node")
                .attr("r", {node_size})
                .style("fill", d => {{
                    if (d.difficulty < 0.5) return "#4CAF50";
                    if (d.difficulty < 0.8) return "#FFC107";
                    return "#F44336";
                }})
                .call(d3.drag()
                    .on("start", dragstarted)
                    .on("drag", dragged)
                    .on("end", dragended));
            
            const label = svg.append("g")
                .selectAll("text")
                .data(nodes)
                .enter().append("text")
                .attr("class", "label")
                .text(d => {"show_labels" and "d.name" or ""})
                .style("display", {"'block'" if show_labels else "'none'"});
            
            const tooltip = d3.select("#tooltip");
            
            node.on("mouseover", function(event, d) {{
                tooltip.transition().duration(200).style("opacity", .9);
                tooltip.html(`
                    <strong>${{d.name}}</strong><br/>
                    ID: ${{d.id}}<br/>
                    等级: ${{d.level}}<br/>
                    难度: ${{d.difficulty}}
                `)
                .style("left", (event.pageX + 10) + "px")
                .style("top", (event.pageY - 28) + "px");
            }})
            .on("mouseout", function(d) {{
                tooltip.transition().duration(500).style("opacity", 0);
            }});
            
            simulation.on("tick", () => {{
                link
                    .attr("x1", d => d.source.x)
                    .attr("y1", d => d.source.y)
                    .attr("x2", d => d.target.x)
                    .attr("y2", d => d.target.y);
                
                node
                    .attr("cx", d => d.x)
                    .attr("cy", d => d.y);
                
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
                
                # 如果没有数据，使用默认数据
                if not nodes:
                    nodes = [
                        {"node_id": "math_001", "node_name": "一元二次方程"},
                        {"node_id": "math_002", "node_name": "函数的概念"},
                        {"node_id": "math_003", "node_name": "导数与微分"},
                        {"node_id": "math_004", "node_name": "二次函数"},
                        {"node_id": "math_005", "node_name": "函数的性质"}
                    ]
                
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
                            relation_type=relation_type
                        )
                        
                        if result.get('status') == 'success':
                            st.success(f"✅ 成功添加关系: {source_node['node_name']} → {target_node['node_name']}")
                            st.rerun()
                        else:
                            st.error(f"❌ 添加关系失败: {result.get('message', '未知错误')}")
                    
                except Exception as e:
                    st.error(f"❌ 检查或添加关系失败: {str(e)}")
    
    # 现有关系列表
    st.markdown("---")
    st.markdown("### 📋 现有关系列表")
    
    try:
        edges = api_service.get_knowledge_edges()
        
        # 如果没有数据，使用默认数据
        if not edges:
            edges = [
                {
                    "id": 1,
                    "source_node_id": "math_002",
                    "target_node_id": "math_004",
                    "relation_type": "is_prerequisite_for",
                    "status": "published",
                    "source_name": "函数的概念",
                    "target_name": "二次函数"
                },
                {
                    "id": 2,
                    "source_node_id": "math_004",
                    "target_node_id": "math_001",
                    "relation_type": "is_prerequisite_for",
                    "status": "published",
                    "source_name": "二次函数",
                    "target_name": "一元二次方程"
                },
                {
                    "id": 3,
                    "source_node_id": "math_005",
                    "target_node_id": "math_003",
                    "relation_type": "is_prerequisite_for",
                    "status": "draft",
                    "source_name": "函数的性质",
                    "target_name": "导数与微分"
                }
            ]
        
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
                                    result = api_service.delete_knowledge_edge(
                                        source_node_id=str(edge['source_node_id']),
                                        target_node_id=str(edge['target_node_id']),
                                        relation_type=edge['relation_type']
                                    )
                                    print(result)
                                    # 清除确认状态
                                    st.session_state[confirm_key] = False
                                    
                                    if result:
                                        st.success(f"✅ 已删除关系")
                                        st.rerun()
                                    else:
                                        st.error("❌ 删除关系失败")
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