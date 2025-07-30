import streamlit as st
import time
import plotly.graph_objects as go
import json
from streamlit_agraph import agraph, Node, Edge, Config

# 从现有文件导入必要的函数
def get_student_thinking_radar_data(api_service, user_id):
    """获取学生做题思维雷达图数据 - 返回前3个知识点的数据"""
    try:
        profile_data = api_service.get_user_profile(user_id)
        print(profile_data)
        
        if not profile_data or 'analysis_by_node' not in profile_data:
            return None
            
        # 获取前3个知识点
        nodes_data = profile_data['analysis_by_node'][:3]
        
        # 为每个知识点生成雷达图数据
        radar_data_list = []
        for node_data in nodes_data:
            node_name = node_data.get('node_name', '未知知识点')
            avg_scores = node_data.get('average_scores', {})
            
            radar_data = {}
            dimensions = ['知识掌握', '解题逻辑', '计算准确性', '行为表现']
            
            for dim_name in dimensions:
                if dim_name in avg_scores:
                    radar_data[dim_name] = round(avg_scores[dim_name], 2)
                else:
                    radar_data[dim_name] = 0.0
            
            radar_data_list.append({
                'name': node_name,
                'data': radar_data
            })
        
        return radar_data_list
        
    except Exception as e:
        print(f"获取雷达图数据失败: {e}")
        return None

def render_thinking_radar_chart(radar_data, title="📊 做题思维雷达图"):
    """渲染单个知识点的做题思维雷达图（超美化版）"""
    if not radar_data:
        return None
    
    categories = list(radar_data.keys())
    values = list(radar_data.values())
    # 闭合雷达图
    categories += [categories[0]]
    values += [values[0]]

    fig = go.Figure()
    
    # 外圈渐变背景
    fig.add_trace(go.Scatterpolar(
        r=[1, 1, 1, 1, 1],
        theta=categories,
        fill='toself',
        fillcolor='rgba(248, 250, 252, 0.8)',
        line=dict(color='rgba(226, 232, 240, 0.3)', width=1),
        name='',
        showlegend=False,
        hoverinfo='skip'
    ))
    
    # 内圈渐变背景
    fig.add_trace(go.Scatterpolar(
        r=[0.8, 0.8, 0.8, 0.8, 0.8],
        theta=categories,
        fill='toself',
        fillcolor='rgba(241, 245, 249, 0.6)',
        line=dict(color='rgba(226, 232, 240, 0.5)', width=1),
        name='',
        showlegend=False,
        hoverinfo='skip'
    ))
    
    # 主雷达区域 - 使用渐变填充
    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself',
        name='做题思维能力',
        line=dict(
            color='#3b82f6',
            width=3,
            shape='spline'
        ),
        fillcolor='rgba(59, 130, 246, 0.15)',
        marker=dict(
            size=12,
            color='#3b82f6',
            symbol='circle',
            line=dict(width=3, color='white')
        ),
        hovertemplate='<b>%{theta}</b><br>掌握度: %{r:.1%}<extra></extra>',
        opacity=0.9
    ))
    
    # 简化的数据点标记（仅悬停显示）
    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=categories,
        mode='markers',
        marker=dict(
            size=12,
            color='#fbbf24',
            symbol='circle',
            line=dict(width=2, color='white')
        ),
        showlegend=False,
        hovertemplate='<b>%{theta}</b><br>掌握度: %{r:.1%}<extra></extra>',
        opacity=0.9
    ))
    
    # 添加能力等级区域
    level_colors = [
        'rgba(239, 68, 68, 0.08)',   # 红色 - 初级
        'rgba(249, 115, 22, 0.06)',  # 橙色
        'rgba(234, 179, 8, 0.05)',   # 黄色
        'rgba(132, 204, 22, 0.04)',  # 黄绿色
        'rgba(34, 197, 94, 0.03)'    # 绿色 - 高级
    ]
    for i, color in enumerate(level_colors):
        level = (i + 1) * 0.2
        fig.add_trace(go.Scatterpolar(
            r=[level] * len(categories),
            theta=categories,
            fill='toself',
            fillcolor=color,
            line=dict(width=0),
            name='',
            showlegend=False,
            hoverinfo='skip'
        ))
    
    fig.update_layout(
        polar=dict(
            bgcolor='rgba(255,255,255,0.95)',
            radialaxis=dict(
                visible=False,
                range=[0, 1],
                gridcolor='rgba(148, 163, 184, 0.2)',
                linecolor='rgba(148, 163, 184, 0.3)',
                tickfont=dict(
                    size=11,
                    color='#64748b',
                    family='Inter, sans-serif'
                ),
                angle=90,
                layer='below traces'
            ),
            angularaxis=dict(
                gridcolor='rgba(148, 163, 184, 0.15)',
                linecolor='rgba(148, 163, 184, 0.3)',
                tickfont=dict(
                    size=13,
                    color='#374151',
                    family='Inter, sans-serif',
                    weight='bold'
                ),
                rotation=45  # 旋转45度，让中间的两个维度竖直排列
            )
        ),
        showlegend=False,
        title=dict(
            text=title,
            font=dict(
                size=16,
                color='#1f2937',
                family='Inter, sans-serif',
                weight='bold'
            ),
            x=0.5,
            y=0.95,
            xanchor='center',  # 确保标题居中
            yanchor='top'
        ),
        width=400,
        height=400,
        margin=dict(l=40, r=40, t=60, b=40),
        paper_bgcolor='rgba(248, 250, 252, 0.8)',
        plot_bgcolor='rgba(248, 250, 252, 0.8)',
        hovermode='closest',
        font=dict(family='Inter, sans-serif'),
        hoverlabel=dict(
            bgcolor='white',
            font_size=12,
            font_family='Inter, sans-serif'
        ),
        # 减少交互效果
        dragmode=False,
        clickmode='none'
    )
    return fig



def get_knowledge_graph_data_with_mastery(api_service, user_id):
    """获取包含掌握度信息的知识图谱数据"""
    try:
        # 1. 获取用户的知识点掌握度数据
        knowledge_map_data = api_service.get_knowledge_map(user_id)
        
        # 验证数据有效性
        if not knowledge_map_data or not isinstance(knowledge_map_data, list):
            knowledge_map_data = []
        
        # 2. 将掌握度数据转换为字典
        mastery_map = {}
        if knowledge_map_data:
            for item in knowledge_map_data:
                if isinstance(item, dict):
                    mastery_map[item.get('node_name', '')] = float(item.get('mastery', 0.0))
        
        # 3. 获取完整的图谱结构数据
        graph_data = api_service.get_knowledge_graph_data()
        
        # 验证图谱结构数据
        if not graph_data or not isinstance(graph_data, dict):
            return None
        
        if "nodes" not in graph_data or "edges" not in graph_data:
            return None
        
        if not graph_data["nodes"] or not isinstance(graph_data["nodes"], list):
            return None
        
        # 4. 为图谱数据添加掌握度信息
        all_nodes = graph_data.get('nodes', [])
        all_edges = graph_data.get('edges', [])
        
        # 为模块节点计算掌握情况
        for node in all_nodes:
            if node.get('type') == '模块' or node.get('node_type') == '模块':
                # 计算该模块的知识点掌握情况
                module_knowledge_ids = set(
                    edge['target'] for edge in all_edges 
                    if edge['source'] == node['id'] and edge['relation'] == '包含'
                )
                
                if module_knowledge_ids:
                    # 计算已掌握的知识点数量（掌握度 > 0.5 视为已掌握）
                    mastered_count = 0
                    for kid in module_knowledge_ids:
                        # 通过知识点ID找到对应的知识点名称
                        knowledge_node = next((n for n in all_nodes if n['id'] == kid), None)
                        if knowledge_node:
                            knowledge_name = knowledge_node.get('name', '')
                            mastery = mastery_map.get(knowledge_name, 0)
                            if mastery > 0.5:
                                mastered_count += 1
                    
                    total_count = len(module_knowledge_ids)
                    node['mastered_count'] = mastered_count
                    node['total_count'] = total_count
                    node['mastery'] = mastered_count / total_count if total_count > 0 else 0
                else:
                    node['mastered_count'] = 0
                    node['total_count'] = 0
                    node['mastery'] = 0
            else:
                # 为知识点节点添加掌握度
                node_name = node.get('name', '')
                node['mastery'] = mastery_map.get(node_name, 0)
        
        return graph_data
        
    except Exception as e:
        st.error(f"获取知识图谱数据失败: {e}")
        return None

def generate_module_nodes(graph_data, mastery_map):
    """生成模块节点用于概览视图"""
    from streamlit_agraph import Node, Edge
    
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
        # 计算该模块的知识点掌握情况
        module_knowledge_ids = set(
            edge['target'] for edge in all_edges 
            if edge['source'] == module['id'] and edge['relation'] == '包含'
        )
        
        if module_knowledge_ids:
            # 计算已掌握的知识点数量（掌握度 > 0.5 视为已掌握）
            mastered_count = 0
            for kid in module_knowledge_ids:
                # 通过知识点ID找到对应的知识点名称
                knowledge_node = next((node for node in all_nodes if node['id'] == kid), None)
                if knowledge_node:
                    knowledge_name = knowledge_node.get('name', '')
                    mastery = mastery_map.get(knowledge_name, 0)
                    if mastery > 0.5:
                        mastered_count += 1
            
            total_count = len(module_knowledge_ids)
            mastery_ratio = mastered_count / total_count if total_count > 0 else 0
        else:
            mastered_count = 0
            total_count = 0
            mastery_ratio = 0
        
        # 根据掌握比例设置颜色
        if mastery_ratio >= 0.8:
            color = "#198754"  # 绿色
        elif mastery_ratio >= 0.5:
            color = "#ffc107"  # 黄色
        elif mastery_ratio > 0:
            color = "#dc3545"  # 红色
        else:
            color = "#6c757d"  # 灰色
        
        module_nodes.append(Node(
            id=module['id'],
            label=f"{module['name']} 📚\n{mastered_count}/{total_count}",
            size=45,  # 增大模块节点大小
            color=color,
            title=f"模块: {module['name']}\n掌握情况: {mastered_count}/{total_count} ({mastery_ratio:.1%})\n点击查看详情"
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
    from streamlit_agraph import Node, Edge
    
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
                size=45,  # 增大知识点节点大小
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

def render_home_page(api_service, current_user, user_id):
    """渲染学生首页"""
    if not current_user:
        st.warning("⚠️ 请先选择用户")
        return
    
    # # 页面标题
    # st.markdown("""
    # <div style="text-align: center; padding: 30px 0;">
    #     <h1 style="color: #2E3440; margin-bottom: 10px;">🏠 学习首页</h1>
    #     <p style="color: #5E81AC; font-size: 20px;">欢迎回来！这是你的学习总览</p>
    # </div>
    # """, unsafe_allow_html=True)

    # st.markdown("---")
    st.markdown("")
    st.markdown("")
    
    # 雷达图区域 - 展示前3个知识点的雷达图
    st.markdown("""
    <h3 style="color: #2E3440; margin-bottom: 15px; text-align: center;">📊 知识点思维雷达图</h3>
    """, unsafe_allow_html=True)
    
    # 获取并展示3个知识点的雷达图
    radar_data_list = get_student_thinking_radar_data(api_service, user_id)
    if radar_data_list and len(radar_data_list) > 0:
        # 使用3列布局展示雷达图
        cols = st.columns(min(3, len(radar_data_list)))
        
        for idx, radar_item in enumerate(radar_data_list[:3]):
            with cols[idx]:
                fig = render_thinking_radar_chart(radar_item['data'], f"📈 {radar_item['name']}")
                if fig:
                    st.plotly_chart(fig, use_container_width=True)
    else:
        st.markdown("""
        <div style="
            text-align: center;
            padding: 40px;
            color: #666;
        ">
            <div style="font-size: 3em; margin-bottom: 15px;">📊</div>
            <h4>暂无数据</h4>
            <p>完成一些练习后即可查看你的思维雷达图</p>
        </div>
        """, unsafe_allow_html=True)
    
    # 学习进度概览 - 使用美观的卡片样式
    st.markdown("""
    <div style="margin: 20px 0 15px 0;">
        <h3 style="color: #2E3440; text-align: center; margin-bottom: 15px;">📊 学习进度概览</h3>
    </div>
    """, unsafe_allow_html=True)
    
    try:
        # 获取用户统计数据作为学习概览
        stats = api_service.get_user_stats(user_id)
        wrong_questions = api_service.get_wrong_questions(user_id)
        
        # 直接使用API返回的统计数据
        total_questions = stats.get("total_questions_answered", 0)
        correct_rate = stats.get('correct_rate', 0.0)
        study_time = stats.get('study_time_today', 0)
        streak_days = stats.get('streak_days', 0)
        
        # 统计卡片样式
        metric_style = """
        <div style="
            background: white;
            padding: 20px;
            border-radius: 15px;
            box-shadow: 0 4px 16px rgba(0,0,0,0.1);
            text-align: center;
            margin: 10px 5px;
        ">
            <div style="font-size: 2em; margin-bottom: 10px;">{icon}</div>
            <div style="font-size: 2em; font-weight: bold; color: {color}; margin-bottom: 5px;">{value}</div>
            <div style="color: #666; font-size: 0.9em;">{label}</div>
            <div style="color: #4CAF50; font-size: 0.8em; margin-top: 5px;">{delta}</div>
        </div>
        """
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(metric_style.format(
                icon="📝",
                value=stats.get("total_questions_answered", 0),
                label="今日完成题目",
                color="#2196F3",
                delta="+3 题"
            ), unsafe_allow_html=True)
        
        with col2:
            correct_rate_percent = correct_rate * 100
            st.markdown(metric_style.format(
                icon="🎯",
                value=f"{correct_rate_percent:.1f}%",
                label="正确率",
                color="#4CAF50" if correct_rate_percent >= 80 else "#FF9800" if correct_rate_percent >= 60 else "#F44336",
                delta="+5%"
            ), unsafe_allow_html=True)
        
        with col3:
            st.markdown(metric_style.format(
                icon="⏰",
                value=f"{study_time}分钟",
                label="学习时长",
                color="#9C27B0",
                delta="+10分钟"
            ), unsafe_allow_html=True)
        
        with col4:
            st.markdown(metric_style.format(
                icon="🔥",
                value=f"{streak_days}天",
                label="连续学习天数",
                color="#FF5722",
                delta="+1天"
            ), unsafe_allow_html=True)
            
    except Exception as e:
        st.info("📚 开始学习后，这里将显示你的学习统计数据")
    st.markdown("")
    st.markdown("")
    st.markdown("")
    # 知识图谱部分
    st.markdown("""
    <div style="text-align: center;">
        <h3 style="color: #2E3440; margin-bottom: 15px;">🗺️ 知识图谱</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # 初始化session state
    if 'kg_view' not in st.session_state:
        st.session_state['kg_view'] = 'overview'
    if 'selected_module' not in st.session_state:
        st.session_state['selected_module'] = None
    
    try:
        # 获取知识图谱数据
        graph_data = get_knowledge_graph_data_with_mastery(api_service, user_id)
        
        if graph_data and "nodes" in graph_data and "edges" in graph_data:
            # 获取掌握度数据
            knowledge_map_data = api_service.get_knowledge_map(user_id)
            mastery_map = {}
            if knowledge_map_data:
                for item in knowledge_map_data:
                    if isinstance(item, dict):
                        mastery_map[item.get('node_name', '')] = float(item.get('mastery', 0.0))
            
            # 配置agraph
            from streamlit_agraph import agraph, Config
            config = Config(
                width="100%",
                height=500,
                directed=True,
                physics=False,
                hierarchical=False,
                nodeHighlightBehavior=True,
                highlightColor="#F7A7A6",
                staticGraph=False,
                staticGraphWithDragAndDrop=True,
                interaction={
                    "dragNodes": True,
                    "dragView": False,
                    "hideEdgesOnDrag": False,
                    "hideNodesOnDrag": False,
                    "hover": True,
                    "hoverConnectedEdges": True,
                    "keyboard": {"enabled": False},
                    "multiselect": False,
                    "navigationButtons": False,
                    "selectable": True,
                    "selectConnectedEdges": False,
                    "tooltipDelay": 300,
                    "zoomView": False
                }
            )
            
            # 根据当前视图状态显示不同内容
            if st.session_state['kg_view'] == 'overview':
                # st.success("💡 **交互提示**：点击任意模块节点查看该模块的详细知识点图谱")
                
                # 生成模块概览图
                module_nodes, module_edges = generate_module_nodes(graph_data, mastery_map)
                
                if module_nodes:
                    # 显示模块概览图谱
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
                    # st.success("💡 **交互提示**：可以拖拽节点调整布局，悬浮查看知识点详情")
                    # 显示知识点详细图谱
                    agraph(nodes=knowledge_nodes, edges=knowledge_edges, config=config)
                else:
                    st.warning(f"⚠️ 模块 '{module_name}' 暂无知识点数据。")
            
            # 图例说明
            # st.markdown("### 📖 图例说明")
            st.markdown("")
            st.markdown("")
            st.markdown("")
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.markdown("""
                🟢 **已掌握**
                (≥80%)
                """)
            with col2:
                st.markdown("""
                🟡 **学习中**
                (50%-80%)
                """)
            with col3:
                st.markdown("""
                🔴 **需加强**
                (1%-50%)
                """)
            with col4:
                st.markdown("""
                ⚪ **未开始**
                (0%)
                """)
        else:
            st.warning("⚠️ 暂无知识图谱关系数据可供展示。")
            
    except Exception as e:
        st.error(f"❌ 加载知识图谱失败: {str(e)}")
        st.info("📚 开始学习后，知识图谱将显示你的学习进度")