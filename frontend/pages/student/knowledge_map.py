import streamlit as st
import pandas as pd
import json
from streamlit_agraph import agraph, Node, Edge, Config

def generate_d3_html(graph_data_with_mastery: dict, show_labels: bool = True, node_size: int = 30) -> str:
    """
    根据整合后的图谱数据，生成包含 D3.js 可视化逻辑的完整 HTML。
    支持两层级交互：章节概览 -> 章节详细展开
    """
    data_json = json.dumps(graph_data_with_mastery)
    show_labels_js = 'true' if show_labels else 'false'
    
    # 使用字符串拼接避免f-string中的JavaScript语法冲突
    html_template = """
    <!DOCTYPE html>
    <html>
    <head>
        <script src="https://d3js.org/d3.v7.min.js"></script>
        <style>
            #graph svg {
                border: 2px solid #e0e3e7;
                border-radius: 12px;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
            }
            .node {
                stroke: #fff;
                stroke-width: 2.5px;
                cursor: pointer;
                transition: all 0.3s ease;
            }
            .node:hover {
                stroke-width: 4px;
                filter: drop-shadow(0 0 8px rgba(0, 0, 0, 0.3));
                transform: scale(1.05);
            }
            .link {
                stroke-opacity: 0.8;
                stroke-width: 2.5px;
            }
            .link.包含 {
                stroke: #6c757d;
            }
            .link.指向 {
                stroke: #0d6efd;
                stroke-dasharray: 0;
            }
            .label {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                font-size: 15px;
                font-weight: 500;
                text-anchor: middle;
                pointer-events: none;
                fill: #212529;
                text-shadow: 0 1px 2px rgba(255, 255, 255, 0.8);
            }
            .label.white-text {
                fill: #ffffff;
                text-shadow: 0 1px 2px rgba(0, 0, 0, 0.8);
            }
            .label.dark-text {
                fill: #212529;
                text-shadow: 0 1px 2px rgba(255, 255, 255, 0.8);
            }
            .tooltip {
                position: absolute;
                background: rgba(33, 37, 41, 0.95);
                color: #ffffff;
                padding: 12px 15px;
                border-radius: 8px;
                font-size: 14px;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                pointer-events: none;
                opacity: 0;
                transition: opacity 0.2s;
                box-shadow: 0 6px 12px rgba(0, 0, 0, 0.25);
                border: 1px solid rgba(255, 255, 255, 0.1);
                max-width: 300px;
                line-height: 1.6;
                z-index: 1000;
            }
        </style>
    </head>
    <body>
        <div id="graph"></div>
        <div class="tooltip" id="tooltip"></div>
        
        <script>
            const graphData = """ + data_json + """;
            const showLabels = """ + show_labels_js + """;
            const nodeSize = """ + str(node_size) + """;
            
            let allNodes = graphData.nodes;
            let allLinks = graphData.edges || graphData.links;
            
            // 分离模块节点和知识点节点
            const moduleNodes = allNodes.filter(d => d.type === '模块');
            const knowledgeNodes = allNodes.filter(d => d.type !== '模块');
            
            // 当前状态：'overview' 或 'detail'
            let currentState = 'overview';
            let selectedModule = null;
            
            const container = d3.select("#graph");
            const width = container.node().getBoundingClientRect().width || 800;
            const height = 600;

            const svg = container.append("svg")
                .attr("width", width)
                .attr("height", height);

            const g = svg.append("g");
            
            // 添加缩放功能
            const zoom = d3.zoom()
                .scaleExtent([0.1, 4])
                .on("zoom", function(event) {
                    g.attr("transform", event.transform);
                });
            svg.call(zoom);

            // 定义箭头
            svg.append("defs").selectAll("marker")
                .data(["指向", "is_prerequisite_for"])
                .enter().append("marker")
                .attr("id", d => `arrow-${d}`)
                .attr("viewBox", "0 -5 10 10")
                .attr("refX", nodeSize + 5)
                .attr("refY", 0)
                .attr("markerWidth", 6)
                .attr("markerHeight", 6)
                .attr("orient", "auto")
                .append("path")
                .attr("fill", "#0d6efd")
                .attr("d", "M0,-5L10,0L0,5");

            let simulation;
            let link, node, label;
            
            // 初始化概览视图
            function initOverview() {
                currentState = 'overview';
                selectedModule = null;
                
                // 清除现有元素
                g.selectAll("*").remove();
                
                // 只显示模块节点
                const nodes = moduleNodes.map(d => ({...d}));
                const links = [];
                
                simulation = d3.forceSimulation(nodes)
                    .force("charge", d3.forceManyBody().strength(-800))
                    .force("center", d3.forceCenter(width / 2, height / 2))
                    .force("collision", d3.forceCollide().radius(Math.max(nodeSize * 1.8, 45)));
                
                // 创建连线组
                link = g.append("g")
                    .selectAll("line")
                    .data(links);
                
                // 创建节点组
                node = g.append("g")
                    .selectAll("circle")
                    .data(nodes)
                    .enter().append("circle")
                    .attr("class", "node")
                    .attr("r", Math.max(nodeSize * 1.5, 35))
                    .style("fill", "#0d6efd")
                    .style("cursor", "pointer")
                    .on("click", function(event, d) {
                        showModuleDetail(d);
                    })
                    .call(d3.drag()
                        .on("start", dragstarted)
                        .on("drag", dragged)
                        .on("end", dragended));
                
                // 创建标签组
                label = g.append("g")
                    .selectAll("text")
                    .data(nodes)
                    .enter().append("text")
                    .attr("class", "label white-text")
                    .text(d => d.name)  
                    .style("font-size", "16px")
                    .style("font-weight", "bold")
                    .style("text-anchor", "middle")
                    .style("pointer-events", "none");
                
                setupTooltip();
                simulation.on("tick", tick);
            }
            
            // 显示模块详细视图
            function showModuleDetail(moduleData) {
                currentState = 'detail';
                selectedModule = moduleData;
                
                // 获取该模块的知识点
                const moduleKnowledgeIds = new Set(
                    allLinks.filter(l => l.source === moduleData.id && l.relation === '包含')
                           .map(l => l.target)
                );
                
                const moduleKnowledgeNodes = knowledgeNodes.filter(d => moduleKnowledgeIds.has(d.id));
                const moduleKnowledgeLinks = allLinks.filter(l => 
                    moduleKnowledgeIds.has(l.source) && 
                    moduleKnowledgeIds.has(l.target) && 
                    l.relation === '指向'
                );
                
                // 准备节点数据
                const detailNodes = [
                    // 选中的模块节点（居中大显示）
                    {...moduleData, isSelected: true},
                    // 其他模块节点（缩小显示在边缘）
                    ...moduleNodes.filter(d => d.id !== moduleData.id).map(d => ({...d, isOther: true})),
                    // 该模块的知识点
                    ...moduleKnowledgeNodes.map(d => ({...d}))
                ];
                
                // 清除现有元素
                g.selectAll("*").remove();
                
                simulation = d3.forceSimulation(detailNodes)
                    .force("link", d3.forceLink(moduleKnowledgeLinks).id(d => d.id).distance(120))
                    .force("charge", d3.forceManyBody().strength(d => d.isSelected ? -1000 : d.isOther ? -200 : -400))
                    .force("center", d3.forceCenter(width / 2, height / 2))
                    .force("collision", d3.forceCollide().radius(d => {
                        if (d.isSelected) return Math.max(nodeSize * 1.8, 45);
                        if (d.isOther) return Math.max(nodeSize * 0.9, 20);
                        return nodeSize + 10;
                    }));
                
                // 创建连线
                link = g.append("g")
                    .selectAll("line")
                    .data(moduleKnowledgeLinks)
                    .enter().append("line")
                    .attr("class", d => `link ${d.relation || 'default'}`)
                    .attr("marker-end", d => d.relation === '指向' ? "url(#arrow-指向)" : null);
                
                // 创建节点
                node = g.append("g")
                    .selectAll("circle")
                    .data(detailNodes)
                    .enter().append("circle")
                    .attr("class", "node")
                    .attr("r", d => {
                        if (d.isSelected) return Math.max(nodeSize * 1.5, 35);
                        if (d.isOther) return Math.max(nodeSize * 0.7, 15);
                        return nodeSize;
                    })
                    .style("fill", d => {
                        if (d.isSelected) return "#0d6efd";
                        if (d.isOther) return "#6c757d";
                        if (d.type === '模块') return "#0d6efd";
                        
                        const mastery = d.mastery || 0;
                        if (mastery >= 0.8) return "#198754";
                        if (mastery >= 0.5) return "#ffc107";
                        if (mastery > 0) return "#dc3545";
                        return "#6c757d";
                    })
                    .style("cursor", d => d.isOther ? "pointer" : "default")
                    .on("click", function(event, d) {
                        if (d.isOther) {
                            showModuleDetail(d);
                        } else if (d.isSelected) {
                            initOverview();
                        }
                    })
                    .call(d3.drag()
                        .on("start", dragstarted)
                        .on("drag", dragged)
                        .on("end", dragended));
                
                // 创建标签
                label = g.append("g")
                    .selectAll("text")
                    .data(detailNodes)
                    .enter().append("text")
                    .attr("class", d => {
                        let classes = "label";
                        if (d.isSelected || d.isOther) {
                            classes += " white-text";
                        } else {
                            classes += " dark-text";
                        }
                        return classes;
                    })
                    .text(d => d.name)
                    .style("font-size", d => d.isSelected ? "14px" : d.isOther ? "10px" : "12px")
                    .style("font-weight", d => d.isSelected ? "bold" : "normal")
                    .style("text-anchor", "middle")
                    .style("pointer-events", "none")
                    .style("display", showLabels ? "block" : "none");
                
                setupTooltip();
                simulation.on("tick", tick);
            }

            // 设置提示框
            function setupTooltip() {
                const tooltip = d3.select("#tooltip");
                
                node.on("mouseover", function(event, d) {
                    tooltip.style("opacity", .9);
                    const masteryText = d.mastery !== undefined ? `<br/>掌握度: ${(d.mastery * 100).toFixed(0)}%` : '';
                    const clickHint = d.isSelected ? '<br/>💡 点击返回概览' : 
                                     d.isOther ? '<br/>💡 点击查看该模块' : 
                                     d.type === '模块' ? '<br/>💡 点击查看详情' : '';
                    tooltip.html(`
                        <strong>${d.name}</strong><br/>
                        ID: ${d.id}<br/>
                        类型: ${d.type || 'N/A'}<br/>
                        ${d.type !== '模块' ? `等级: ${d.level || 'N/A'}<br/>` : ''}
                        ${d.type !== '模块' ? `难度: ${d.difficulty || 'N/A'}` : ''}
                        ${masteryText}
                        ${clickHint}
                    `)
                    .style("left", (event.pageX + 10) + "px")
                    .style("top", (event.pageY - 28) + "px");
                })
                .on("mouseout", function(d) {
                    tooltip.style("opacity", 0);
                });
            }
            
            // tick 函数
            function tick() {
                if (node) {
                    node.attr("cx", d => {
                        const r = d.isSelected ? Math.max(nodeSize * 1.5, 35) : 
                                  d.isOther ? Math.max(nodeSize * 0.7, 15) : nodeSize;
                        return d.x = Math.max(r, Math.min(width - r, d.x));
                    })
                    .attr("cy", d => {
                        const r = d.isSelected ? Math.max(nodeSize * 1.5, 35) : 
                                  d.isOther ? Math.max(nodeSize * 0.7, 15) : nodeSize;
                        return d.y = Math.max(r, Math.min(height - r, d.y));
                    });
                }
                
                if (link) {
                    link.attr("x1", d => d.source.x)
                        .attr("y1", d => d.source.y)
                        .attr("x2", d => d.target.x)
                        .attr("y2", d => d.target.y);
                }
                
                if (label) {
                    label.attr("x", d => d.x)
                         .attr("y", d => d.y + (d.isSelected ? 8 : d.isOther ? 4 : 5));
                }
            } 
            
            function dragstarted(event, d) {
                if (!event.active) simulation.alphaTarget(0.3).restart();
                d.fx = d.x;
                d.fy = d.y;
            }
            
            function dragged(event, d) {
                d.fx = event.x;
                d.fy = event.y;
            }
            
            function dragended(event, d) {
                if (!event.active) simulation.alphaTarget(0);
                d.fx = null;
                d.fy = null;
            }
            
            // 初始化概览视图
            initOverview();
        </script>
    </body>
    </html>
    """
    return html_template

def generate_module_nodes(graph_data, mastery_map):
    """生成模块节点用于概览视图"""
    module_nodes = []
    module_edges = []
    
    if not graph_data or "nodes" not in graph_data:
        return module_nodes, module_edges
    
    all_nodes = graph_data.get('nodes', [])
    all_edges = graph_data.get('edges', [])
    
    # 提取模块节点
    modules = [node for node in all_nodes if node.get('type') == '模块' or node.get('node_type') == '模块']
    
    # 为每个模块创建Node对象
    for module in modules:
        # 计算该模块的平均掌握度
        module_knowledge_ids = set(
            edge['target'] for edge in all_edges 
            if edge['source'] == module['id'] and edge['relation'] == '包含'
        )
        
        if module_knowledge_ids:
            avg_mastery = sum(mastery_map.get(kid, 0) for kid in module_knowledge_ids) / len(module_knowledge_ids)
        else:
            avg_mastery = 0
        
        # 根据掌握度设置颜色
        if avg_mastery >= 0.8:
            color = "#198754"  # 绿色
        elif avg_mastery >= 0.5:
            color = "#ffc107"  # 黄色
        elif avg_mastery > 0:
            color = "#dc3545"  # 红色
        else:
            color = "#6c757d"  # 灰色
        
        module_nodes.append(Node(
            id=module['id'],
            label=f"{module['name']} 📚\n掌握度: {avg_mastery:.0%}",
            size=30,  # 调小模块节点大小
            color=color,
            title=f"模块: {module['name']}\n平均掌握度: {avg_mastery:.1%}\n点击查看详情"
        ))
    
    # 模块之间的关系（如果有的话）
    module_ids = set(module['id'] for module in modules)
    for edge in all_edges:
        if edge['source'] in module_ids and edge['target'] in module_ids:
            module_edges.append(Edge(
                source=edge['source'],
                target=edge['target'],
                label="",  # 移除"指向"文字标签
                color="#0d6efd"
            ))
    
    return module_nodes, module_edges

def generate_knowledge_points(graph_data, module_id, mastery_map):
    """生成指定模块的知识点详细图谱"""
    if not graph_data or "nodes" not in graph_data:
        return [], []
    
    all_nodes = graph_data.get('nodes', [])
    all_edges = graph_data.get('edges', [])
    
    # 获取该模块包含的知识点ID
    knowledge_ids = set(
        edge['target'] for edge in all_edges 
        if edge['source'] == module_id and edge['relation'] == '包含'
    )
    
    # 创建知识点节点
    knowledge_nodes = []
    for node in all_nodes:
        if node['id'] in knowledge_ids:
            mastery = mastery_map.get(node['name'], 0)
            
            # 根据掌握度设置颜色
            if mastery >= 0.8:
                color = "#198754"  # 绿色
            elif mastery >= 0.5:
                color = "#ffc107"  # 黄色
            elif mastery > 0:
                color = "#dc3545"  # 红色
            else:
                color = "#6c757d"  # 灰色
            
            knowledge_nodes.append(Node(
                id=node['id'],
                label=f"{node['name']}\n{mastery:.0%}",
                size=25,  # 调小知识点节点大小
                color=color,
                title=f"知识点: {node['name']}\n掌握度: {mastery:.1%}\n难度: {node.get('difficulty', 'N/A')}\n等级: {node.get('level', 'N/A')}"
            ))
    
    # 创建知识点之间的关系
    knowledge_edges = []
    for edge in all_edges:
        if (edge['source'] in knowledge_ids and 
            edge['target'] in knowledge_ids and 
            edge['relation'] == '指向'):
            knowledge_edges.append(Edge(
                source=edge['source'],
                target=edge['target'],
                label="",  # 移除"指向"文字标签
                color="#0d6efd"
            ))
    
    return knowledge_nodes, knowledge_edges

def render_knowledge_map_page(api_service, current_user, user_id):
    """渲染知识图谱页面"""
    st.write("### 🗺️ 我的知识图谱")
    if not current_user:
        st.warning("请先选择用户")
        return
    
    st.info(f"👨‍🎓 当前学习者：**{current_user}**")
    
    # 显示页面状态指示器
    status_container = st.container()
    with status_container:
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            if st.session_state.get('kg_data_loaded', False):
                st.success("📊 掌握度数据已加载")
            else:
                st.warning("📊 掌握度数据未加载")
        with col2:
            if st.session_state.get('graph_structure_data'):
                st.success("🗺️ 图谱结构已缓存")
            else:
                st.info("🗺️ 图谱结构待加载")
        with col3:
            view_status = st.session_state.get('kg_view', 'overview')
            if view_status == 'overview':
                st.info("👁️ 概览视图")
            else:
                st.info("🔍 详细视图")
        with col4:
            if st.button("🔄 刷新页面", key="refresh_page", help="清除所有缓存并重新加载"):
                # 清除所有知识图谱相关的session state
                keys_to_clear = ['kg_view', 'selected_module', 'kg_data_loaded', 
                               'kg_error_message', 'graph_structure_data']
                for key in keys_to_clear:
                    if key in st.session_state:
                        del st.session_state[key]
                st.rerun()
    
    st.markdown("---")  # 分隔线
    
    # 初始化session state
    if 'kg_view' not in st.session_state:
        st.session_state['kg_view'] = 'overview'
    if 'selected_module' not in st.session_state:
        st.session_state['selected_module'] = None
    if 'kg_data_loaded' not in st.session_state:
        st.session_state['kg_data_loaded'] = False
    if 'kg_error_message' not in st.session_state:
        st.session_state['kg_error_message'] = None
    
    # --- [ENHANCED] 数据获取与处理部分 ---
    # 1. 获取用户的知识点掌握度数据
    try:
        with st.spinner("🔄 正在加载知识图谱数据..."):
            knowledge_map_data = api_service.get_knowledge_map(user_id)
            
            # 验证数据有效性
            if not knowledge_map_data or not isinstance(knowledge_map_data, list):
                st.warning("⚠️ 暂无知识点掌握度数据，请联系管理员检查数据配置")
                knowledge_map_data = []
            
            # 2. 将掌握度数据转换为DataFrame，用于后续的统计分析
            if knowledge_map_data:
                df_data = []
                for item in knowledge_map_data:
                    if isinstance(item, dict):  # 确保item是字典类型
                        df_data.append({
                            '知识点名称': item.get('node_name', ''),
                            '我的掌握度': float(item.get('mastery', 0.0)),
                            '难度': item.get('difficulty', '未定义')
                        })
                df = pd.DataFrame(df_data)
                st.session_state['kg_data_loaded'] = True
                st.session_state['kg_error_message'] = None
            else:
                df = pd.DataFrame(columns=['知识点名称', '我的掌握度', '难度'])
                st.session_state['kg_data_loaded'] = False
                
    except Exception as e:
        st.error(f"❌ 加载知识点掌握度数据失败: {str(e)}")
        df = pd.DataFrame(columns=['知识点名称', '我的掌握度', '难度'])
        st.session_state['kg_data_loaded'] = False
        st.session_state['kg_error_message'] = str(e)
    
    # --- [NEW] 交互式知识图谱可视化 ---
    st.markdown("### 🕸️ 知识关系图谱（交互式）")
    
    # 使用Streamlit原生容器样式，避免CSS层级问题
    
    try:
        # 3. 获取完整的图谱结构数据
        if not st.session_state.get('graph_structure_data'):
            with st.spinner("🔄 正在加载知识图谱结构..."):
                graph_data = api_service.get_knowledge_graph_data()
                
                # 验证图谱结构数据
                if not graph_data or not isinstance(graph_data, dict):
                    raise ValueError("图谱结构数据格式无效")
                
                if "nodes" not in graph_data or "edges" not in graph_data:
                    raise ValueError("图谱结构数据缺少必要字段")
                
                if not graph_data["nodes"] or not isinstance(graph_data["nodes"], list):
                    raise ValueError("图谱节点数据为空或格式无效")
                
                # 缓存到session state
                st.session_state['graph_structure_data'] = graph_data
        else:
            graph_data = st.session_state['graph_structure_data']
        
        if graph_data and "nodes" in graph_data and "edges" in graph_data:
            # 将用户的掌握度数据转换为字典
            mastery_map = {row['知识点名称']: row['我的掌握度'] for index, row in df.iterrows()}
            
            # 配置agraph - 允许拖拽节点，禁用缩放功能，响应式宽度
            config = Config(
                width="100%",  # 使用百分比宽度，自适应容器
                height=600,
                directed=True,
                physics=False,
                hierarchical=False,
                nodeHighlightBehavior=True,
                highlightColor="#F7A7A6",
                staticGraph=False,
                staticGraphWithDragAndDrop=True,
                # 精确控制交互功能
                interaction={
                    "dragNodes": True,           # 允许拖拽节点
                    "dragView": False,          # 禁用视图拖拽
                    "hideEdgesOnDrag": False,
                    "hideNodesOnDrag": False,
                    "hover": True,
                    "hoverConnectedEdges": True,
                    "keyboard": {
                        "enabled": False
                    },
                    "multiselect": False,
                    "navigationButtons": False,  # 隐藏缩放按钮
                    "selectable": True,
                    "selectConnectedEdges": False,
                    "tooltipDelay": 300,
                    "zoomView": False           # 禁用缩放
                }
            )
            
            # 根据当前视图状态显示不同内容
            if st.session_state['kg_view'] == 'overview':
                st.success("💡 **交互提示**：点击任意模块节点查看该模块的详细知识点图谱")
                
                # 生成模块概览图
                module_nodes, module_edges = generate_module_nodes(graph_data, mastery_map)
                
                if module_nodes:
                    # 显示模块概览图谱（带样式容器）
                    with st.container():
                        # 使用Streamlit原生容器样式
                        with st.expander("🗺️ 模块概览图谱", expanded=True):
                            clicked_node_id = agraph(nodes=module_nodes, edges=module_edges, config=config)
                    
                    # 如果有模块被点击，切换到详细视图
                    if clicked_node_id:
                        st.session_state['kg_view'] = 'detail'
                        st.session_state['selected_module'] = clicked_node_id
                        st.rerun()
                else:
                    st.warning("⚠️ 暂无模块数据可供展示。")
            
            elif st.session_state['kg_view'] == 'detail':
                selected_module = st.session_state['selected_module']
                
                # 获取模块名称
                module_name = "未知模块"
                for node in graph_data.get('nodes', []):
                    if node['id'] == selected_module:
                        module_name = node['name']
                        break
                
                st.info(f"📚 **当前模块**：{module_name}")
                
                # 返回按钮
                if st.button("⬅️ 返回模块概览"):
                    st.session_state['kg_view'] = 'overview'
                    st.session_state['selected_module'] = None
                    st.rerun()
                
                # 生成该模块的详细知识点图谱
                knowledge_nodes, knowledge_edges = generate_knowledge_points(
                    graph_data, selected_module, mastery_map
                )
                
                if knowledge_nodes:
                    st.success("💡 **交互提示**：可以拖拽节点调整布局，悬浮查看知识点详情")
                    # 显示知识点详细图谱（使用原生容器）
                    with st.container():
                        with st.expander(f"🔍 {module_name} - 详细知识点图谱", expanded=True):
                            agraph(nodes=knowledge_nodes, edges=knowledge_edges, config=config)
                else:
                    st.warning(f"⚠️ 模块 '{module_name}' 暂无知识点数据。")
            
            # 图例说明
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
                - <span style='color:#0d6efd; font-weight:bold;'>--►</span> **指向** (知识点依赖)
                - <span style='color:#6c757d; font-weight:bold;'>--</span> **包含** (模块包含知识点)
                """, unsafe_allow_html=True)
            with col3:
                st.markdown("""
                **交互功能:**
                - **点击** 模块节点查看详情
                - **拖拽** 移动节点调整布局
                - **悬浮** 查看节点信息
                - **禁缩放** 固定图谱大小
                """)
        else:
            st.warning("⚠️ 暂无知识图谱关系数据可供展示。")
            # 提供数据刷新选项
            col1, col2 = st.columns([1, 4])
            with col1:
                if st.button("🔄 重新加载", key="reload_graph_data"):
                    # 清除缓存的图谱数据
                    if 'graph_structure_data' in st.session_state:
                        del st.session_state['graph_structure_data']
                    st.rerun()
            with col2:
                st.info("💡 如果问题持续存在，请联系管理员检查数据配置")
                
    except Exception as e:
        st.error(f"❌ 知识图谱加载失败: {str(e)}")
        
        # 显示详细错误信息和解决建议
        with st.expander("🔧 错误详情和解决建议", expanded=False):
            st.code(f"错误类型: {type(e).__name__}\n错误信息: {str(e)}")
            st.markdown("""
            **可能的解决方案:**
            1. 🔄 点击下方"重新加载"按钮重试
            2. 🌐 检查网络连接是否正常
            3. 🔧 联系管理员检查后端服务状态
            4. 📊 确认知识图谱数据已正确配置
            """)
        
        # 提供重新加载选项
        col1, col2 = st.columns([1, 4])
        with col1:
            if st.button("🔄 重新加载", key="reload_after_error"):
                # 清除所有相关的session state
                keys_to_clear = ['graph_structure_data', 'kg_data_loaded', 'kg_error_message']
                for key in keys_to_clear:
                    if key in st.session_state:
                        del st.session_state[key]
                st.rerun()
        with col2:
            st.info("💡 重新加载将清除缓存并重新获取所有数据")
        
        # 显示基本的状态信息
        st.markdown("### 📊 当前状态")
        status_col1, status_col2 = st.columns(2)
        with status_col1:
            data_status = "✅ 已加载" if st.session_state.get('kg_data_loaded') else "❌ 未加载"
            st.metric("知识点数据", data_status)
        with status_col2:
            graph_status = "✅ 已缓存" if st.session_state.get('graph_structure_data') else "❌ 未缓存"
            st.metric("图谱结构", graph_status)


    # 页面底部信息
    st.markdown("---")
    st.markdown("### 💡 使用提示")
    
    tip_col1, tip_col2 = st.columns(2)
    with tip_col1:
        st.markdown("""
        **如果图谱内容消失:**
        1. 🔄 点击页面顶部的"刷新页面"按钮
        2. 📊 检查状态指示器显示的数据加载状态
        3. 🌐 确认网络连接正常
        4. ⏱️ 等待数据加载完成（查看加载提示）
        """)
    
    with tip_col2:
        st.markdown("""
        **页面交互说明:**
        - 🖱️ 点击模块节点查看详细知识点
        - 🔙 使用"返回模块概览"按钮切换视图
        - 🎯 拖拽节点可调整图谱布局
        - 🔍 悬浮节点可查看详细信息
        """)
    
    # 调试信息（仅在开发模式下显示）
    if st.checkbox("🔧 显示调试信息", key="show_debug_info"):
        st.markdown("### 🔧 调试信息")
        debug_col1, debug_col2 = st.columns(2)
        
        with debug_col1:
            st.markdown("**Session State:**")
            debug_info = {
                'kg_view': st.session_state.get('kg_view', 'None'),
                'selected_module': st.session_state.get('selected_module', 'None'),
                'kg_data_loaded': st.session_state.get('kg_data_loaded', False),
                'has_graph_data': bool(st.session_state.get('graph_structure_data')),
                'error_message': st.session_state.get('kg_error_message', 'None')
            }
            st.json(debug_info)
        
        with debug_col2:
            st.markdown("**数据统计:**")
            if not df.empty:
                st.write(f"知识点数量: {len(df)}")
                st.write(f"平均掌握度: {df['我的掌握度'].mean():.2%}")
            else:
                st.write("暂无知识点数据")
            
            if st.session_state.get('graph_structure_data'):
                graph_data = st.session_state['graph_structure_data']
                st.write(f"图谱节点数: {len(graph_data.get('nodes', []))}")
                st.write(f"图谱边数: {len(graph_data.get('edges', []))}")
            else:
                st.write("暂无图谱结构数据")

