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
    
    # 直接渲染图谱可视化，不使用标签页
    render_graph_visualization(api_service, user_id)

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

    # 显示知识图谱
    graph_html = create_graph_html(nodes, edges, show_labels, 30, api_service)
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
    
    # 边添加请求现在通过AJAX直接调用后端API，无需URL参数处理

def create_graph_html(nodes, edges, show_labels, node_size, api_service=None):
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
            .node.selected {{
                stroke: #ff6b6b;
                stroke-width: 4px;
                filter: drop-shadow(0 0 8px #ff6b6b);
            }}
            .link {{
                stroke-opacity: 0.7;
                stroke-width: 4px;
            }}
            .link.包含 {{
                stroke: #888;
            }}
            .link.指向 {{
                stroke: #337ab7;
            }}
            .preview-link {{
                stroke: #ff6b6b;
                stroke-width: 3px;
                stroke-dasharray: 5,5;
                opacity: 0.8;
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
            .context-menu {{
                position: absolute;
                background: white;
                border: 1px solid #ccc;
                border-radius: 4px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.2);
                padding: 8px 0;
                font-family: Arial, sans-serif;
                font-size: 14px;
                z-index: 1000;
                display: none;
            }}
            .context-menu-item {{
                padding: 8px 16px;
                cursor: pointer;
                border-bottom: 1px solid #eee;
            }}
            .context-menu-item:hover {{
                background-color: #f5f5f5;
            }}
            .context-menu-item:last-child {{
                border-bottom: none;
            }}
            .modal {{
                display: none;
                position: fixed;
                z-index: 1001;
                left: 0;
                top: 0;
                width: 100%;
                height: 100%;
                background-color: rgba(0,0,0,0.4);
            }}
            .modal-content {{
                background-color: #fefefe;
                margin: 15% auto;
                padding: 20px;
                border: 1px solid #888;
                border-radius: 8px;
                width: 400px;
                text-align: center;
                font-family: Arial, sans-serif;
            }}
            .modal-buttons {{
                margin-top: 20px;
            }}
            .modal-button {{
                padding: 8px 16px;
                margin: 0 8px;
                border: none;
                border-radius: 4px;
                cursor: pointer;
                font-size: 14px;
            }}
            .modal-button.confirm {{
                background-color: #5cb85c;
                color: white;
            }}
            .modal-button.cancel {{
                background-color: #d9534f;
                color: white;
            }}
            .status-indicator {{
                position: absolute;
                top: 10px;
                left: 10px;
                padding: 8px 12px;
                background: rgba(255, 255, 255, 0.9);
                border-radius: 4px;
                font-family: Arial, sans-serif;
                font-size: 12px;
                border: 1px solid #ddd;
            }}
        </style>
    </head>
    <body>
        <div id="graph"></div>
        <div class="tooltip" id="tooltip"></div>
        <div class="context-menu" id="contextMenu">
            <div class="context-menu-item" onclick="selectNode()">🎯 选择节点</div>
            <div class="context-menu-item" onclick="clearSelection()">🔄 清除选择</div>
        </div>
        <div class="context-menu" id="edgeContextMenu">
            <div class="context-menu-item" onclick="deleteEdge()">🗑️ 删除关系</div>
        </div>
        <div class="modal" id="confirmModal">
            <div class="modal-content">
                <h3>🔗 添加关系</h3>
                <p id="modalText"></p>
                <div class="modal-buttons">
                    <button class="modal-button confirm" onclick="confirmAddEdge()">✅ 确认添加</button>
                    <button class="modal-button cancel" onclick="cancelAddEdge()">❌ 取消</button>
                </div>
            </div>
        </div>
        <div class="status-indicator" id="statusIndicator">
            💡 右键点击节点选择，选择两个节点后自动创建关系
        </div>
        
        <script>
            const nodes = {json.dumps(nodes)};
            const links = {json.dumps(edges)};
            
            // 交互状态管理
            let selectedNodes = [];
            let previewLink = null;
            let currentContextNode = null;
            let currentContextEdge = null;

            const container = d3.select("#graph");
            const width = container.node().getBoundingClientRect().width || 800;
            const height = 600;

            const svg = container.append("svg")
                .attr("width", width)
                .attr("height", height)
                .on("click", function(event) {{
                    // 点击空白区域隐藏右键菜单
                    hideContextMenu();
                }});

            const g = svg.append("g");

            // 定义箭头
            svg.append("defs").selectAll("marker")
                .data(["指向", "preview"])
                .enter().append("marker")
                .attr("id", d => `arrow-${{d}}`)
                .attr("viewBox", "0 -5 10 10")
                .attr("refX", {node_size-2})
                .attr("refY", 0)
                .attr("markerWidth", 4)
                .attr("markerHeight", 4)
                .attr("orient", "auto")
                .append("path")
                .attr("fill", d => d === "preview" ? "#ff6b6b" : "#337ab7")
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
                .attr("marker-end", d => d.relation === '指向' ? `url(#arrow-${{d.relation}})` : null)
                .on("contextmenu", function(event, d) {{
                    event.preventDefault();
                    currentContextEdge = d;
                    showEdgeContextMenu(event.pageX, event.pageY);
                }});
            
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
                .on("contextmenu", function(event, d) {{
                    event.preventDefault();
                    currentContextNode = d;
                    showContextMenu(event.pageX, event.pageY);
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
                
                // 更新预览链接
                if (previewLink) {{
                    previewLink
                        .attr("x1", d => d.source.x)
                        .attr("y1", d => d.source.y)
                        .attr("x2", d => d.target.x)
                        .attr("y2", d => d.target.y);
                }}
                
                label
                    .attr("x", d => d.x)
                    .attr("y", d => d.y + 5);
            }}); 
            
            // 交互功能函数
            function showContextMenu(x, y) {{
                const menu = document.getElementById('contextMenu');
                menu.style.display = 'block';
                menu.style.left = x + 'px';
                menu.style.top = y + 'px';
            }}
            
            function hideContextMenu() {{
                document.getElementById('contextMenu').style.display = 'none';
                document.getElementById('edgeContextMenu').style.display = 'none';
            }}
            
            function showEdgeContextMenu(x, y) {{
                const menu = document.getElementById('edgeContextMenu');
                menu.style.display = 'block';
                menu.style.left = x + 'px';
                menu.style.top = y + 'px';
            }}
            
            function selectNode() {{
                if (!currentContextNode) return;
                
                // 检查节点是否已选择
                const nodeIndex = selectedNodes.findIndex(n => n.id === currentContextNode.id);
                if (nodeIndex === -1) {{
                    selectedNodes.push(currentContextNode);
                    updateNodeSelection();
                    
                    // 如果选择了两个节点，创建预览链接
                    if (selectedNodes.length === 2) {{
                        createPreviewLink();
                    }}
                    
                    updateStatusIndicator();
                }}
                
                hideContextMenu();
            }}
            
            function clearSelection() {{
                selectedNodes = [];
                removePreviewLink();
                updateNodeSelection();
                updateStatusIndicator();
                hideContextMenu();
            }}
            
            function updateNodeSelection() {{
                node.classed("selected", d => selectedNodes.some(n => n.id === d.id));
            }}
            
            function createPreviewLink() {{
                if (selectedNodes.length !== 2) return;
                
                const source = selectedNodes[0];
                const target = selectedNodes[1];
                
                // 检查是否已存在相同的边
                const existing = links.find(link => 
                    (link.source.id === source.id && link.target.id === target.id) ||
                    (link.source.id === target.id && link.target.id === source.id)
                );
                
                if (existing) {{
                    alert('⚠️ 这两个节点之间已存在关系！');
                    clearSelection();
                    return;
                }}
                
                // 创建预览链接
                previewLink = g.append("line")
                    .datum({{source: source, target: target}})
                    .attr("class", "preview-link")
                    .attr("marker-end", "url(#arrow-preview)");
                
                // 显示确认对话框
                showConfirmModal(source, target);
            }}
            
            function removePreviewLink() {{
                if (previewLink) {{
                    previewLink.remove();
                    previewLink = null;
                }}
            }}
            
            function showConfirmModal(source, target) {{
                const modal = document.getElementById('confirmModal');
                const modalText = document.getElementById('modalText');
                modalText.innerHTML = `确认要在 <strong>${{source.name}}</strong> 和 <strong>${{target.name}}</strong> 之间添加"指向"关系吗？`;
                modal.style.display = 'block';
            }}
            
            function confirmAddEdge() {{
                if (selectedNodes.length === 2) {{
                    const source = selectedNodes[0];
                    const target = selectedNodes[1];
                    
                    // 关闭模态框
                    document.getElementById('confirmModal').style.display = 'none';
                    
                    // 发送添加边的请求到后端
                    addEdgeToDatabase(source.id, target.id);
                }} else {{
                    cancelAddEdge();
                }}
            }}
            
            function cancelAddEdge() {{
                document.getElementById('confirmModal').style.display = 'none';
                clearSelection();
            }}
            
            function addEdgeToDatabase(sourceId, targetId) {{
                 // 1. 更新状态提示
                 const statusIndicator = document.getElementById('statusIndicator');
                 statusIndicator.innerHTML = '🔄 正在处理请求，请稍候...';
                 
                 // 2. 获取节点名称
                 const sourceNode = nodes.find(n => n.id === sourceId);
                 const targetNode = nodes.find(n => n.id === targetId);
                 const sourceName = sourceNode ? sourceNode.name : 'Unknown';
                 const targetName = targetNode ? targetNode.name : 'Unknown';
                 
                 // 3. 发送AJAX请求到后端API
                 fetch('http://localhost:8000/teacher/knowledge/edges', {{
                     method: 'POST',
                     headers: {{
                         'Content-Type': 'application/json',
                     }},
                     body: JSON.stringify({{
                         source_node_id: sourceId.toString(),
                         target_node_id: targetId.toString(),
                         relation_type: '指向'
                     }})
                 }})
                 .then(response => response.json())
                 .then(data => {{
                     if (data.status === 'success') {{
                         // 成功添加边
                         statusIndicator.innerHTML = `✅ 成功添加关系: ${{sourceName}} → ${{targetName}}`;
                         
                         // 添加新边到图谱中
                         const newEdge = {{
                             source: sourceNode,
                             target: targetNode,
                             type: '指向',
                             status: 'published'
                         }};
                         links.push(newEdge);
                         
                         // 重新渲染图谱
                         updateGraph();
                         
                         // 清除选择
                         clearSelection();
                     }} else {{
                         statusIndicator.innerHTML = `❌ 添加关系失败: ${{data.message || '未知错误'}}`;
                     }}
                 }})
                 .catch(error => {{
                     console.error('Error:', error);
                     statusIndicator.innerHTML = `❌ 添加关系失败: ${{error.message}}`;
                 }});
             }}
             
             function updateGraph() {{
                 // 重新绑定数据并更新图谱
                 const link = g.selectAll(".link")
                     .data(links, d => `${{d.source.id}}-${{d.target.id}}`);
                 
                 link.enter().append("line")
                     .attr("class", d => `link ${{d.type}}`)
                     .attr("marker-end", d => d.type === '指向' ? "url(#arrow)" : "")
                     .style("stroke-dasharray", d => d.status === 'draft' ? "5,5" : "none")
                     .on("contextmenu", function(event, d) {{
                         event.preventDefault();
                         currentContextEdge = d;
                         showEdgeContextMenu(event.pageX, event.pageY);
                     }});
                 
                 link.exit().remove();
                 
                 // 重新启动力导向布局
                 simulation.nodes(nodes);
                 simulation.force("link").links(links);
                 simulation.alpha(1).restart();
             }}
             
             function deleteEdge() {{
                 if (!currentContextEdge) return;
                 
                 const edge = currentContextEdge;
                 const sourceName = edge.source.name || 'Unknown';
                 const targetName = edge.target.name || 'Unknown';
                 
                 // 确认删除
                 if (confirm(`确认要删除 "${{sourceName}}" → "${{targetName}}" 的关系吗？`)) {{
                     // 更新状态提示
                     const statusIndicator = document.getElementById('statusIndicator');
                     statusIndicator.innerHTML = '🔄 正在删除关系，请稍候...';
                     
                     // 发送删除请求到后端API
                     fetch('http://localhost:8000/teacher/knowledge/edges', {{
                         method: 'DELETE',
                         headers: {{
                             'Content-Type': 'application/json',
                         }},
                         body: JSON.stringify({{
                             source_node_id: edge.source.id.toString(),
                             target_node_id: edge.target.id.toString(),
                             relation_type: edge.relation || '指向'
                         }})
                     }})
                     .then(response => response.json())
                     .then(data => {{
                         if (data.status === 'success') {{
                             // 成功删除边
                             statusIndicator.innerHTML = `✅ 成功删除关系: ${{sourceName}} → ${{targetName}}`;
                             
                             // 从图谱中移除边
                             const edgeIndex = links.findIndex(link => 
                                 link.source.id === edge.source.id && 
                                 link.target.id === edge.target.id &&
                                 link.relation === edge.relation
                             );
                             
                             if (edgeIndex !== -1) {{
                                 links.splice(edgeIndex, 1);
                                 updateGraph();
                             }}
                         }} else {{
                             statusIndicator.innerHTML = `❌ 删除关系失败: ${{data.message || '未知错误'}}`;
                         }}
                     }})
                     .catch(error => {{
                         console.error('Error:', error);
                         statusIndicator.innerHTML = `❌ 删除关系失败: ${{error.message}}`;
                     }});
                 }}
                 
                 hideContextMenu();
             }}
            
            function updateStatusIndicator() {{
                const indicator = document.getElementById('statusIndicator');
                if (selectedNodes.length === 0) {{
                    indicator.innerHTML = '💡 右键点击节点选择，选择两个节点后自动创建关系';
                }} else if (selectedNodes.length === 1) {{
                    indicator.innerHTML = `🎯 已选择: ${{selectedNodes[0].name}}，请选择第二个节点`;
                }} else {{
                    indicator.innerHTML = `🔗 已选择两个节点，正在创建关系...`;
                }}
            }}
            
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

# render_relationship_management 函数已删除