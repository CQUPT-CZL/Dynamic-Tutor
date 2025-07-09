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
    tab1, tab2, tab3, tab4 = st.tabs(["🕸️ 图谱可视化", "🔗 关系管理", "🤖 AI建议", "📊 图谱分析"])
    
    with tab1:
        render_graph_visualization(api_service, user_id)
    
    with tab2:
        render_relationship_management(api_service, user_id)
    
    with tab3:
        render_ai_suggestions(api_service, user_id)
    
    with tab4:
        render_graph_analysis(api_service)

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
        # graph_data = api_service.get_knowledge_graph()
        
        # 临时使用模拟数据
        nodes = [
            {"id": "math_001", "name": "一元二次方程", "level": "中级", "difficulty": 0.7},
            {"id": "math_002", "name": "函数的概念", "level": "初级", "difficulty": 0.5},
            {"id": "math_003", "name": "导数与微分", "level": "高级", "difficulty": 0.9},
            {"id": "math_004", "name": "二次函数", "level": "中级", "difficulty": 0.6},
            {"id": "math_005", "name": "函数的性质", "level": "中级", "difficulty": 0.65}
        ]
        
        edges = [
            {"source": "math_002", "target": "math_004", "relation": "prerequisite", "status": "published"},
            {"source": "math_004", "target": "math_001", "relation": "related", "status": "published"},
            {"source": "math_002", "target": "math_005", "relation": "prerequisite", "status": "published"},
            {"source": "math_005", "target": "math_003", "relation": "prerequisite", "status": "draft"}
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
                # nodes = api_service.get_knowledge_nodes()
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
            except:
                st.error("❌ 无法获取知识点列表")
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
                options=["prerequisite", "related", "contains", "similar"],
                format_func=lambda x: {
                    "prerequisite": "前置关系",
                    "related": "相关关系", 
                    "contains": "包含关系",
                    "similar": "相似关系"
                }[x]
            )
        
        status = st.selectbox("状态", ["draft", "published"], 
                             format_func=lambda x: "草稿" if x == "draft" else "已发布")
        
        submitted = st.form_submit_button("➕ 添加关系", use_container_width=True)
        
        if submitted:
            if source_node['node_id'] == target_node['node_id']:
                st.error("❌ 源知识点和目标知识点不能相同")
            else:
                try:
                    # api_service.create_knowledge_edge({
                    #     'source_node_id': source_node['node_id'],
                    #     'target_node_id': target_node['node_id'],
                    #     'relation_type': relation_type,
                    #     'status': status,
                    #     'created_by': user_id
                    # })
                    
                    st.success(f"✅ 成功添加关系: {source_node['node_name']} → {target_node['node_name']}")
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"❌ 添加关系失败: {str(e)}")
    
    # 现有关系列表
    st.markdown("---")
    st.markdown("### 📋 现有关系列表")
    
    try:
        # edges = api_service.get_knowledge_edges()
        edges = [
            {
                "edge_id": 1,
                "source_node_id": "math_002",
                "target_node_id": "math_004",
                "relation_type": "prerequisite",
                "status": "published",
                "source_name": "函数的概念",
                "target_name": "二次函数"
            },
            {
                "edge_id": 2,
                "source_node_id": "math_004",
                "target_node_id": "math_001",
                "relation_type": "related",
                "status": "published",
                "source_name": "二次函数",
                "target_name": "一元二次方程"
            },
            {
                "edge_id": 3,
                "source_node_id": "math_005",
                "target_node_id": "math_003",
                "relation_type": "prerequisite",
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
                "prerequisite": "➡️",
                "related": "🔗",
                "contains": "📚",
                "similar": "🔄"
            }.get(edge['relation_type'], "🔗")
            
            with st.expander(f"{status_color} {edge['source_name']} {relation_emoji} {edge['target_name']}", expanded=False):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.write(f"**关系ID:** {edge['edge_id']}")
                    st.write(f"**源知识点:** {edge['source_name']} ({edge['source_node_id']})")
                    st.write(f"**目标知识点:** {edge['target_name']} ({edge['target_node_id']})")
                    st.write(f"**关系类型:** {edge['relation_type']}")
                    st.write(f"**状态:** {edge['status']}")
                
                with col2:
                    if edge['status'] == "draft":
                        if st.button(f"📤 发布", key=f"publish_edge_{edge['edge_id']}"):
                            # api_service.publish_knowledge_edge(edge['edge_id'])
                            st.success("✅ 关系已发布！")
                            st.rerun()
                    
                    if st.button(f"🗑️ 删除", key=f"delete_edge_{edge['edge_id']}"):
                        if st.session_state.get(f"confirm_delete_edge_{edge['edge_id']}", False):
                            # api_service.delete_knowledge_edge(edge['edge_id'])
                            st.success(f"✅ 已删除关系")
                            st.rerun()
                        else:
                            st.session_state[f"confirm_delete_edge_{edge['edge_id']}"] = True
                            st.warning("⚠️ 再次点击确认删除")
        
    except Exception as e:
        st.error(f"❌ 获取关系列表失败: {str(e)}")

def render_ai_suggestions(api_service, user_id):
    """渲染AI建议界面"""
    st.subheader("🤖 AI智能建议")
    
    st.info("💡 AI系统会根据知识点内容和现有关系，智能推荐可能的知识点关系")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        if st.button("🔍 获取AI建议", use_container_width=True):
            with st.spinner("🤖 AI正在分析知识点关系..."):
                # 模拟AI分析过程
                import time
                time.sleep(2)
                
                # 存储AI建议到session state
                st.session_state.ai_suggestions = [
                    {
                        "source": "math_001",
                        "target": "math_004", 
                        "relation": "related",
                        "confidence": 0.85,
                        "reason": "一元二次方程与二次函数在数学概念上密切相关",
                        "source_name": "一元二次方程",
                        "target_name": "二次函数"
                    },
                    {
                        "source": "math_002",
                        "target": "math_005",
                        "relation": "prerequisite", 
                        "confidence": 0.92,
                        "reason": "理解函数概念是学习函数性质的前提",
                        "source_name": "函数的概念",
                        "target_name": "函数的性质"
                    },
                    {
                        "source": "math_005",
                        "target": "math_003",
                        "relation": "prerequisite",
                        "confidence": 0.78,
                        "reason": "函数性质的理解有助于学习导数概念",
                        "source_name": "函数的性质",
                        "target_name": "导数与微分"
                    }
                ]
                st.success("✅ AI分析完成！")
                st.rerun()
    
    with col2:
        if st.button("🗑️ 清除建议", use_container_width=True):
            if 'ai_suggestions' in st.session_state:
                del st.session_state.ai_suggestions
                st.rerun()
    
    # 显示AI建议
    if 'ai_suggestions' in st.session_state:
        st.markdown("### 🎯 AI推荐的关系")
        
        for i, suggestion in enumerate(st.session_state.ai_suggestions):
            confidence_color = "🟢" if suggestion['confidence'] > 0.8 else "🟡" if suggestion['confidence'] > 0.6 else "🔴"
            
            with st.expander(f"{confidence_color} {suggestion['source_name']} → {suggestion['target_name']} (置信度: {suggestion['confidence']:.2f})", expanded=False):
                st.write(f"**关系类型:** {suggestion['relation']}")
                st.write(f"**AI分析原因:** {suggestion['reason']}")
                st.write(f"**置信度:** {suggestion['confidence']:.2f}")
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button(f"✅ 采纳建议", key=f"accept_{i}"):
                        try:
                            # api_service.create_knowledge_edge({
                            #     'source_node_id': suggestion['source'],
                            #     'target_node_id': suggestion['target'],
                            #     'relation_type': suggestion['relation'],
                            #     'status': 'draft',
                            #     'created_by': 4  # AI_System用户ID
                            # })
                            
                            st.success("✅ 已采纳AI建议并创建关系！")
                            # 从建议列表中移除
                            st.session_state.ai_suggestions.pop(i)
                            st.rerun()
                            
                        except Exception as e:
                            st.error(f"❌ 创建关系失败: {str(e)}")
                
                with col2:
                    if st.button(f"❌ 拒绝建议", key=f"reject_{i}"):
                        st.session_state.ai_suggestions.pop(i)
                        st.info("已拒绝该建议")
                        st.rerun()
    else:
        st.info("🤖 点击上方按钮获取AI智能建议")

def render_graph_analysis(api_service):
    """渲染图谱分析界面"""
    st.subheader("📊 知识图谱分析")
    
    try:
        # 获取图谱分析数据
        # analysis = api_service.get_graph_analysis()
        
        # 临时使用模拟数据
        analysis = {
            "total_nodes": 25,
            "total_edges": 18,
            "avg_degree": 1.44,
            "connected_components": 2,
            "diameter": 4,
            "clustering_coefficient": 0.35
        }
        
        # 基本统计
        st.markdown("### 📈 基本统计")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("📚 知识点数量", analysis["total_nodes"])
            st.metric("🔗 关系数量", analysis["total_edges"])
        
        with col2:
            st.metric("📊 平均度数", f"{analysis['avg_degree']:.2f}")
            st.metric("🌐 连通分量", analysis["connected_components"])
        
        with col3:
            st.metric("📏 图直径", analysis["diameter"])
            st.metric("🔄 聚类系数", f"{analysis['clustering_coefficient']:.2f}")
        
        # 节点重要性分析
        st.markdown("### 🎯 节点重要性分析")
        
        importance_data = [
            {"node_id": "math_002", "node_name": "函数的概念", "degree": 4, "betweenness": 0.25, "pagerank": 0.18},
            {"node_id": "math_004", "node_name": "二次函数", "degree": 3, "betweenness": 0.15, "pagerank": 0.14},
            {"node_id": "math_001", "node_name": "一元二次方程", "degree": 2, "betweenness": 0.08, "pagerank": 0.12},
            {"node_id": "math_005", "node_name": "函数的性质", "degree": 2, "betweenness": 0.12, "pagerank": 0.11},
            {"node_id": "math_003", "node_name": "导数与微分", "degree": 1, "betweenness": 0.02, "pagerank": 0.08}
        ]
        
        df_importance = pd.DataFrame(importance_data)
        st.dataframe(df_importance, use_container_width=True)
        
        # 图谱健康度
        st.markdown("### 🏥 图谱健康度")
        
        health_metrics = {
            "连通性": 85,  # 基于连通分量数量
            "完整性": 72,  # 基于孤立节点数量
            "平衡性": 68,  # 基于度分布
            "层次性": 78   # 基于前置关系的层次结构
        }
        
        for metric, score in health_metrics.items():
            progress_color = "normal" if score >= 70 else "inverse"
            st.metric(f"📊 {metric}", f"{score}%")
            st.progress(score / 100)
        
        # 改进建议
        st.markdown("### 💡 改进建议")
        
        suggestions = [
            "🔗 建议为孤立的知识点添加更多关系连接",
            "📚 考虑添加更多基础知识点作为高级概念的前置条件",
            "🎯 平衡不同难度等级知识点的分布",
            "🔄 检查是否存在循环依赖关系"
        ]
        
        for suggestion in suggestions:
            st.write(f"• {suggestion}")
        
        # 导出功能
        st.markdown("### 📤 导出功能")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📊 导出分析报告"):
                # 生成分析报告
                report = generate_analysis_report(analysis, importance_data, health_metrics)
                st.download_button(
                    label="📥 下载报告",
                    data=report,
                    file_name=f"knowledge_graph_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                    mime="text/plain"
                )
        
        with col2:
            if st.button("🕸️ 导出图谱数据"):
                # 导出图谱数据为JSON
                graph_data = {
                    "nodes": importance_data,
                    "edges": [
                        {"source": "math_002", "target": "math_004", "relation": "prerequisite"},
                        {"source": "math_004", "target": "math_001", "relation": "related"}
                    ]
                }
                st.download_button(
                    label="📥 下载数据",
                    data=json.dumps(graph_data, ensure_ascii=False, indent=2),
                    file_name=f"knowledge_graph_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json"
                )
        
        with col3:
            if st.button("📈 生成可视化"):
                st.info("🎨 可视化功能开发中...")
        
    except Exception as e:
        st.error(f"❌ 获取图谱分析失败: {str(e)}")
        st.info("💡 请确保后端API服务正常运行")

def generate_analysis_report(analysis, importance_data, health_metrics):
    """生成分析报告"""
    report = f"""
知识图谱分析报告
生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

=== 基本统计 ===
知识点数量: {analysis['total_nodes']}
关系数量: {analysis['total_edges']}
平均度数: {analysis['avg_degree']:.2f}
连通分量: {analysis['connected_components']}
图直径: {analysis['diameter']}
聚类系数: {analysis['clustering_coefficient']:.2f}

=== 重要节点 ===
"""
    
    for node in importance_data[:5]:
        report += f"{node['node_name']} (度数: {node['degree']}, PageRank: {node['pagerank']:.2f})\n"
    
    report += "\n=== 健康度评估 ===\n"
    for metric, score in health_metrics.items():
        report += f"{metric}: {score}%\n"
    
    return report