import streamlit as st
import pandas as pd
import json

def generate_d3_html(graph_data_with_mastery: dict) -> str:
    """
    根据整合后的图谱数据，生成包含 D3.js 可视化逻辑的完整 HTML。
    （此函数无需修改，它已经准备好接收处理好的数据）
    """
    data_json = json.dumps(graph_data_with_mastery)

    html_template = f"""
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="utf-8">
        <title>D3 Force-Directed Graph</title>
        <style>
            body, html {{ margin: 0; padding: 0; width: 100%; height: 100%; overflow: hidden; }}
            #graph-container {{ width: 100%; height: 100%; }}
            .tooltip {{
                position: absolute;
                text-align: center;
                width: auto;
                height: auto;
                padding: 8px 12px;
                font: 12px sans-serif;
                background: rgba(25, 25, 25, 0.85);
                color: white;
                border: 0px;
                border-radius: 8px;
                pointer-events: none;
                opacity: 0;
                transition: opacity 0.2s;
            }}
            .node-label {{
                pointer-events: none;
                font-size: 10px;
                font-weight: bold;
                fill: white;
                text-shadow: 0 1px 0 #000, 1px 0 0 #000, 0 -1px 0 #000, -1px 0 0 #000;
            }}
        </style>
    </head>
    <body>
        <div id="graph-container"></div>
        <div class="tooltip" id="tooltip"></div>
        <script src="https://d3js.org/d3.v7.min.js"></script>
        <script>
            const graphData = {data_json};
            const nodes = graphData.nodes;
            const links = graphData.links;

            const container = document.getElementById('graph-container');
            const width = container.clientWidth;
            const height = container.clientHeight;
            const svg = d3.select(container).append("svg")
                .attr("viewBox", [0, 0, width, height])
                .attr("width", width)
                .attr("height", height);
            
            const tooltip = d3.select("#tooltip");

            const simulation = d3.forceSimulation(nodes)
                .force("link", d3.forceLink(links).id(d => d.id).distance(120))
                .force("charge", d3.forceManyBody().strength(-350))
                .force("center", d3.forceCenter(width / 2, height / 2).strength(0.1))
                .force("x", d3.forceX().strength(0.05))
                .force("y", d3.forceY().strength(0.05));

            const link = svg.append("g")
                .attr("stroke", "#999")
                .attr("stroke-opacity", 0.6)
                .selectAll("line")
                .data(links)
                .join("line")
                .attr("stroke-width", 1.5);

            const nodeGroup = svg.append("g")
                .selectAll(".node-group")
                .data(nodes)
                .join("g")
                .attr("class", "node-group");
            
            const nodeRadius = d => 25 + d.mastery * 35;
            
            // 水袋背景 (容器)
            nodeGroup.append("circle")
                .attr("r", nodeRadius)
                .attr("fill", "rgba(173, 216, 230, 0.3)")
                .attr("stroke", "#666")
                .attr("stroke-width", 1.5);
            
            // 创建全局defs元素用于剪裁路径
            const defs = svg.append("defs");
            
            // 为每个节点创建剪裁路径
             nodes.forEach(d => {{
                 const clipPath = defs.append("clipPath")
                     .attr("id", `water-clip-${{d.id}}`);
                 
                 clipPath.append("rect")
                     .attr("x", -nodeRadius(d))
                     .attr("y", nodeRadius(d) - (nodeRadius(d) * 2 * d.mastery)) // 从底部开始向上填充
                     .attr("width", nodeRadius(d) * 2)
                     .attr("height", nodeRadius(d) * 2 * d.mastery);
             }});

            // 水 (应用剪裁)
             nodeGroup.append("circle")
                 .attr("r", nodeRadius)
                 .attr("fill", d => d3.interpolateBlues(d.mastery * 0.8 + 0.2)) // 掌握度越高，蓝色越深
                 .attr("clip-path", d => `url(#water-clip-${{d.id}})`);

            // 知识点名称标签
            nodeGroup.append("text")
                .attr("class", "node-label")
                .attr("text-anchor", "middle")
                .attr("dy", ".3em")
                .text(d => d.name);

            // 添加交互
             nodeGroup
                 .on("mouseover", (event, d) => {{
                     tooltip.transition().duration(200).style("opacity", .9);
                     tooltip.html(`<b>${{d.name}}</b><br/>掌握度: ${{(d.mastery * 100).toFixed(0)}}%<br/>难度: ${{d.difficulty}}`)
                         .style("left", (event.pageX + 15) + "px")
                         .style("top", (event.pageY - 28) + "px");
                 }})
                 .on("mouseout", () => {{
                     tooltip.transition().duration(500).style("opacity", 0);
                 }});

            nodeGroup.call(d3.drag()
                .on("start", dragstarted)
                .on("drag", dragged)
                .on("end", dragended));

            simulation.on("tick", () => {{
                 link.attr("x1", d => d.source.x).attr("y1", d => d.source.y)
                     .attr("x2", d => d.target.x).attr("y2", d => d.target.y);
                 nodeGroup.attr("transform", d => `translate(${{d.x}},${{d.y}})`);
             }});

            function dragstarted(event, d) {{ if (!event.active) simulation.alphaTarget(0.3).restart(); d.fx = d.x; d.fy = d.y; }}
            function dragged(event, d) {{ d.fx = event.x; d.fy = event.y; }}
            function dragended(event, d) {{ if (!event.active) simulation.alphaTarget(0); d.fx = null; d.fy = null; }}
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
    st.success("💡 **交互提示**：可以拖动节点，鼠标悬浮可查看详情。")

    try:
        # 3. 获取完整的图谱结构数据
        graph_data = api_service.get_knowledge_graph_data()
        
        if graph_data and "nodes" in graph_data and "edges" in graph_data:
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

