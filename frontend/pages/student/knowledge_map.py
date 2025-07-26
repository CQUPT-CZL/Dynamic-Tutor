import streamlit as st
import pandas as pd
import json

def generate_d3_html(graph_data_with_mastery: dict, show_labels: bool = True, node_size: int = 30) -> str:
    """
    根据整合后的图谱数据，生成包含 D3.js 可视化逻辑的完整 HTML。
    采用教师端样式，但保留学生端的掌握度展示功能。
    """
    data_json = json.dumps(graph_data_with_mastery)

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
            const graphData = {data_json};
            const nodes = graphData.nodes;
            const links = graphData.edges || graphData.links;

            const container = d3.select("#graph");
            const width = container.node().getBoundingClientRect().width || 800;
            const height = 600;

            const svg = container.append("svg")
                .attr("width", width)
                .attr("height", height);

            const g = svg.append("g");

            // 定义箭头
            svg.append("defs").selectAll("marker")
                .data(["指向", "is_prerequisite_for"])
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
                .attr("class", d => `link ${{d.relation || d.relation_type || 'default'}}`)
                .style("stroke-dasharray", d => d.status === "draft" ? "5,5" : "none")
                .attr("marker-end", d => (d.relation === '指向' || d.relation_type === 'is_prerequisite_for') ? `url(#arrow-${{d.relation || d.relation_type}})` : null);
            
            const node = g.append("g")
                .selectAll("circle")
                .data(nodes)
                .enter().append("circle")
                .attr("class", "node")
                .attr("r", {node_size})
                .style("fill", d => {{
                    if (d.type === '模块') return "#337ab7"; // 蓝色
                    
                    // 学生端特色：根据掌握度显示颜色
                    const mastery = d.mastery || 0;
                    if (mastery >= 0.8) return "#5cb85c"; // 绿色 - 已掌握
                    if (mastery >= 0.5) return "#f0ad4e"; // 黄色 - 学习中
                    if (mastery > 0) return "#d9534f"; // 红色 - 需要加强
                    return "#999"; // 灰色 - 未开始
                }})
                .style("stroke", d => {{
                    // 添加掌握度边框效果
                    const mastery = d.mastery || 0;
                    return mastery >= 0.8 ? "#449d44" : "#fff";
                }})
                .style("stroke-width", d => {{
                    const mastery = d.mastery || 0;
                    return mastery >= 0.8 ? "3px" : "2px";
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
                const masteryText = d.mastery !== undefined ? `<br/>掌握度: ${{(d.mastery * 100).toFixed(0)}}%` : '';
                tooltip.html(`
                    <strong>${{d.name}}</strong><br/>
                    ID: ${{d.id}}<br/>
                    类型: ${{d.type || 'N/A'}}<br/>
                    ${{d.type !== '模块' ? `等级: ${{d.level || 'N/A'}}<br/>` : ''}}
                    ${{d.type !== '模块' ? `难度: ${{d.difficulty || 'N/A'}}` : ''}}
                    ${{masteryText}}
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

def render_knowledge_map_page(api_service, current_user, user_id):
    """渲染知识图谱页面"""
    st.write("### 🗺️ 我的知识图谱")
    if not current_user:
        st.warning("请先选择用户")
        return
    
    st.info(f"👨‍🎓 当前学习者：**{current_user}**")
    
    # --- [MODIFIED] 数据获取与处理部分 ---
    # 1. 获取用户的知识点掌握度数据
    knowledge_map_data = api_service.get_knowledge_map(user_id)
    
    # 2. 将掌握度数据转换为DataFrame，用于后续的统计分析
    if knowledge_map_data:
        df_data = []
        for item in knowledge_map_data:
            # 使用您提供的真实数据键名
            df_data.append({
                '知识点名称': item.get('node_name', ''),
                '我的掌握度': item.get('mastery', 0.0),
                '难度': item.get('difficulty', '未定义') # 修正键名为'difficulty'
            })
        df = pd.DataFrame(df_data)
    else:
        df = pd.DataFrame(columns=['知识点名称', '我的掌握度', '难度'])
    
    # --- [NEW] D3.js 知识图谱可视化 ---
    st.markdown("### 🕸️ 知识关系图谱（交互式）")
    st.success("💡 **交互提示**：可以拖动节点，鼠标悬浮可查看详情。节点颜色表示掌握度：🟢已掌握 🟡学习中 🔴需加强 ⚪未开始")

    try:
        # 3. 获取完整的图谱结构数据
        graph_data = api_service.get_knowledge_graph_data()
        
        if graph_data and "nodes" in graph_data and "edges" in graph_data:
            all_nodes = graph_data.get('nodes', [])
            all_edges = graph_data.get('edges', [])
            
            # 提取模块用于下拉选择
            modules = [node for node in all_nodes if node.get('node_type') == '模块' or node.get('type') == '模块']
            
            if modules:
                # 控制面板
                col1, col2, col3 = st.columns([2, 1, 1])
                
                with col1:
                    # 使用模块名称作为选项
                    module_names = [m['name'] for m in modules]
                    selected_module_name = st.selectbox("📚 选择模块", options=module_names, index=0)
                    # 根据选择的名称找到对应的模块ID
                    selected_module_id = next((m['id'] for m in modules if m['name'] == selected_module_name), None)

                with col2:
                    show_labels = st.checkbox("🏷️ 显示标签", value=True)
                
                with col3:
                    if st.button("🔄 刷新图谱"):
                        st.rerun()

                if selected_module_id:
                    # 根据选择的模块筛选节点和边，不展示模块节点
                    # 找出模块包含的所有知识点ID
                    module_kp_ids = {edge['target'] for edge in all_edges if edge['source'] == selected_module_id and edge['relation'] == '包含'}
                    
                    # 只筛选知识点节点
                    nodes = [node for node in all_nodes if node['id'] in module_kp_ids]
                    
                    # 只筛选模块内知识点之间的"指向"关系
                    edges = [
                        edge for edge in all_edges 
                        if (edge['source'] in module_kp_ids and 
                            edge['target'] in module_kp_ids and 
                            edge['relation'] == '指向')
                    ]

                    if nodes:
                        # 4. 将用户的掌握度数据合并到图谱的节点信息中
                        mastery_map = {row['知识点名称']: row['我的掌握度'] for index, row in df.iterrows()}
                        for node in nodes:
                            node["mastery"] = mastery_map.get(node["name"], 0.0)
                        
                        # 5. 准备筛选后的图谱数据
                        filtered_graph_data = {
                            "nodes": nodes,
                            "edges": edges
                        }
                        
                        # 6. 生成并渲染HTML
                        html_code = generate_d3_html(filtered_graph_data, show_labels)
                        st.components.v1.html(html_code, height=600, scrolling=False)
                        
                        # 更新图例
                        st.markdown("### 📖 图例说明")
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.markdown("""
                            **节点颜色（掌握度）:**
                            - 🟢 **已掌握** (≥80%)
                            - 🟡 **学习中** (50%-80%)
                            - 🔴 **需加强** (1%-50%)
                            - ⚪ **未开始** (0%)
                            """)
                        with col2:
                            st.markdown("""
                            **关系类型:**
                            - <span style='color:#337ab7; font-weight:bold;'>--►</span> **指向** (知识点之间)
                            """, unsafe_allow_html=True)
                        with col3:
                            st.markdown("""
                            **交互功能:**
                            - **拖拽** 移动节点
                            - **悬浮** 查看详情
                            - **缩放** 调整视图
                            """)
                    else:
                        st.info("ℹ️ 当前模块下没有知识点或关系。")
                else:
                    st.error("❌ 无法找到所选模块。")
            else:
                # 如果没有模块，显示所有节点
                # 4. 将用户的掌握度数据合并到图谱的节点信息中
                mastery_map = {row['知识点名称']: row['我的掌握度'] for index, row in df.iterrows()}
                for node in graph_data["nodes"]:
                    node["mastery"] = mastery_map.get(node["name"], 0.0)
                
                # 5. 准备 D3.js 需要的 links 格式
                graph_data["links"] = graph_data["edges"]
                
                # 6. 生成并渲染HTML
                html_code = generate_d3_html(graph_data)
                st.components.v1.html(html_code, height=700, scrolling=False)
        else:
            st.warning("⚠️ 暂无知识图谱关系数据可供展示。")
    except Exception as e:
        st.error(f"❌ 知识图谱加载失败: {e}")


    # --- [RETAINED] 您原来的所有统计分析和图表代码 ---
    # 这部分代码无需修改，因为它现在使用了我们上面处理好的 DataFrame (df)
    
    st.markdown("### 📊 学习概览")
    
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

    st.write("### 📋 详细知识点掌握情况")
    st.dataframe(
        df,
        column_config={
            "我的掌握度": st.column_config.ProgressColumn(
                "掌握度",
                help="系统评估你对该知识点的掌握程度",
                min_value=0.0,
                max_value=1.0,
                format="%.0f%%" # 改为整数百分比，更直观
            )
        },
        use_container_width=True,
        hide_index=True
    )

    if not df.empty:
        st.write("### 📈 掌握度可视化分析")

        col1, col2 = st.columns(2)
        with col1:
            st.write("#### 各知识点掌握度")
            mastery_data = df.set_index('知识点名称')['我的掌握度']
            st.bar_chart(mastery_data)

        with col2:
            st.write("#### 掌握度分布")
            mastery_levels = {
                "未开始 (0)": len(df[df['我的掌握度'] == 0]),
                "初学 (0-0.3)": len(df[(df['我的掌握度'] > 0) & (df['我的掌握度'] <= 0.3)]),
                "学习中 (0.3-0.8)": len(df[(df['我的掌握度'] > 0.3) & (df['我的掌握度'] < 0.8)]),
                "已掌握 (0.8+)": len(df[df['我的掌握度'] >= 0.8])
            }
            distribution_df = pd.DataFrame(list(mastery_levels.items()), columns=['掌握度等级', '知识点数量'])
            st.bar_chart(distribution_df.set_index('掌握度等级'))

        st.write("### 💡 个性化学习建议")

        if avg_mastery >= 0.8:
            st.success("🎉 太棒了！你的平均掌握度达到了优秀水平！可以挑战更高难度的知识点。")
        elif avg_mastery >= 0.6:
            st.info("👍 不错！你的学习进展良好，继续保持！")
            weak_points = df[df['我的掌握度'] < 0.5]['知识点名称'].tolist()
            if weak_points:
                st.warning(f"🎯 **重点关注**: {', '.join(weak_points)}")
        else:
            st.warning("💪 还有很大提升空间，建议制定系统的学习计划！")
            priority_points = df.nsmallest(2, '我的掌握度')['知识点名称'].tolist()
            if priority_points:
                st.info(f"📚 **优先学习**: {', '.join(priority_points)}")

