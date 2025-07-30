import streamlit as st
import time
import plotly.graph_objects as go
import json
from components import render_simple_question, QuestionPracticeComponent

def get_student_thinking_radar_data(api_service, user_id):
    """获取学生做题思维雷达图数据"""
    try:
        # 调用用户画像API获取数据
        profile_data = api_service.get_user_profile(user_id)
        
        if not profile_data or 'analysis_by_node' not in profile_data:
            return None
            
        # 聚合所有知识点的四维数据
        dimension_totals = {
            '知识掌握': [],
            '解题逻辑': [],
            '计算准确性': [],
            '行为表现': []
        }
        
        for node_data in profile_data['analysis_by_node']:
            avg_scores = node_data.get('average_scores', {})
            for dim_name in dimension_totals.keys():
                if dim_name in avg_scores:
                    dimension_totals[dim_name].append(avg_scores[dim_name])
        
        # 计算每个维度的平均分
        radar_data = {}
        for dim_name, scores in dimension_totals.items():
            if scores:
                radar_data[dim_name] = round(sum(scores) / len(scores), 2)
            else:
                radar_data[dim_name] = 0.0
                
        return radar_data
        
    except Exception as e:
        print(f"获取雷达图数据失败: {e}")
        return None

def render_thinking_radar_chart(radar_data):
    """渲染做题思维雷达图"""
    if not radar_data:
        return
        
    # 准备雷达图数据
    categories = list(radar_data.keys())
    values = list(radar_data.values())
    
    # 创建雷达图
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself',
        name='做题思维能力',
        line=dict(color='#667eea', width=3),
        fillcolor='rgba(102, 126, 234, 0.3)',
        marker=dict(size=8, color='#667eea')
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 1],
                tickvals=[0.2, 0.4, 0.6, 0.8, 1.0],
                ticktext=['20%', '40%', '60%', '80%', '100%'],
                gridcolor='rgba(0,0,0,0.1)',
                linecolor='rgba(0,0,0,0.2)'
            ),
            angularaxis=dict(
                gridcolor='rgba(0,0,0,0.1)',
                linecolor='rgba(0,0,0,0.2)'
            )
        ),
        showlegend=False,
        title=dict(
            text="📊 做题思维雷达图",
            x=0.5,
            font=dict(size=18, color='#2E3440')
        ),
        width=400,
        height=400,
        margin=dict(l=50, r=50, t=80, b=50),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    
    return fig

def get_mission_type_info(mission_type):
    """获取任务类型的显示信息"""
    mission_info = {
        'NEW_KNOWLEDGE': {
            'icon': '🚀',
            'name': '新知探索',
            'color': '#4CAF50',
            'bg_gradient': 'linear-gradient(135deg, #4CAF50 0%, #45a049 100%)'
        },
        'WEAK_POINT_CONSOLIDATION': {
            'icon': '💪',
            'name': '弱点巩固',
            'color': '#FF9800',
            'bg_gradient': 'linear-gradient(135deg, #FF9800 0%, #F57C00 100%)'
        },
        'SKILL_ENHANCEMENT': {
            'icon': '⚡',
            'name': '技能提升',
            'color': '#2196F3',
            'bg_gradient': 'linear-gradient(135deg, #2196F3 0%, #1976D2 100%)'
        },
        'EXPLORATORY': {
            'icon': '🎨',
            'name': '兴趣探索',
            'color': '#9C27B0',
            'bg_gradient': 'linear-gradient(135deg, #9C27B0 0%, #7B1FA2 100%)'
        }
    }
    return mission_info.get(mission_type, {
        'icon': '📚',
        'name': '学习任务',
        'color': '#607D8B',
        'bg_gradient': 'linear-gradient(135deg, #607D8B 0%, #455A64 100%)'
    })

def render_daily_tasks_page(api_service, current_user, user_id):
    """渲染今日任务页面"""
    if not current_user:
        st.warning("⚠️ 请先选择用户")
        return
    
    # 初始化session_state来缓存推荐任务
    if 'current_recommendation' not in st.session_state:
        st.session_state.current_recommendation = None
    if 'task_started' not in st.session_state:
        st.session_state.task_started = False
    if 'loading_recommendation' not in st.session_state:
        st.session_state.loading_recommendation = False
    
    # 页面标题
    st.markdown("""
    <div style="text-align: center; padding: 20px 0;">
        <h1 style="color: #2E3440; margin-bottom: 10px;">📋 今日学习任务</h1>
        <p style="color: #5E81AC; font-size: 18px;">为你量身定制的智能学习计划</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 雷达图展示区域
    # st.markdown("""
    # <div style="
    #     background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
    #     padding: 20px;
    #     border-radius: 15px;
    #     margin: 20px 0;
    #     box-shadow: 0 4px 16px rgba(0,0,0,0.1);
    # ">
    # """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        # 获取并展示雷达图
        radar_data = get_student_thinking_radar_data(api_service, user_id)
        if radar_data:
            fig = render_thinking_radar_chart(radar_data)
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
    
    with col2:
        # 雷达图说明和数据详情
        st.markdown("### 🧠 你的做题思维分析")
        
        if radar_data:
            st.markdown("**📈 各维度能力评估：**")
            
            for dim_name, score in radar_data.items():
                # 计算百分比和颜色
                percentage = int(score * 100)
                if percentage >= 80:
                    color = "#4CAF50"  # 绿色
                    level = "优秀"
                elif percentage >= 60:
                    color = "#2196F3"  # 蓝色
                    level = "良好"
                elif percentage >= 40:
                    color = "#FF9800"  # 橙色
                    level = "一般"
                else:
                    color = "#F44336"  # 红色
                    level = "待提升"
                
                st.markdown(f"""
                <div style="
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    padding: 10px 15px;
                    margin: 8px 0;
                    background: white;
                    border-radius: 8px;
                    border-left: 4px solid {color};
                    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                ">
                    <span style="font-weight: 500;">{dim_name}</span>
                    <div style="display: flex; align-items: center; gap: 10px;">
                        <span style="color: {color}; font-weight: bold;">{percentage}%</span>
                        <span style="
                            background: {color};
                            color: white;
                            padding: 2px 8px;
                            border-radius: 12px;
                            font-size: 0.8em;
                        ">{level}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            # 总体评价
            avg_score = sum(radar_data.values()) / len(radar_data)
            avg_percentage = int(avg_score * 100)
            
            st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 15px;
                border-radius: 10px;
                margin-top: 15px;
                text-align: center;
            ">
                <h4 style="margin: 0 0 8px 0;">🎯 综合能力评估</h4>
                <div style="font-size: 1.5em; font-weight: bold;">{avg_percentage}%</div>
                <p style="margin: 5px 0 0 0; opacity: 0.9;">继续努力，你的进步很明显！</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="
                background: white;
                padding: 20px;
                border-radius: 10px;
                text-align: center;
                color: #666;
            ">
                <p>📚 开始做题练习，系统将为你生成专属的思维能力分析报告</p>
                <p>💡 雷达图将展示你在以下四个维度的表现：</p>
                <ul style="text-align: left; margin-top: 15px;">
                    <li><strong>知识掌握</strong> - 对知识点的理解程度</li>
                    <li><strong>解题逻辑</strong> - 逻辑推理和思维过程</li>
                    <li><strong>计算准确性</strong> - 计算和操作的准确度</li>
                    <li><strong>行为表现</strong> - 答题习惯和表达能力</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # 如果没有推荐任务，显示获取推荐按钮
    if st.session_state.current_recommendation is None and not st.session_state.loading_recommendation:
        # 显示醒目的获取推荐任务按钮
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 50px;
            border-radius: 25px;
            text-align: center;
            margin: 40px 0;
            box-shadow: 0 12px 40px rgba(102,126,234,0.3);
            color: white;
        ">
            <div style="font-size: 4em; margin-bottom: 25px;">🎁</div>
            <h2 style="margin: 0 0 20px 0; font-size: 2.2em; font-weight: bold;">获取你的专属学习任务包</h2>
            <p style="margin: 0 0 30px 0; font-size: 1.3em; opacity: 0.95; line-height: 1.5;">AI将根据你的学习情况和兴趣，为你量身定制个性化学习任务</p>
            <div style="
                background: rgba(255,255,255,0.15);
                padding: 20px;
                border-radius: 15px;
                margin: 25px 0;
                backdrop-filter: blur(10px);
            ">
                <div style="display: flex; justify-content: space-around; align-items: center; flex-wrap: wrap; gap: 20px;">
                    <div style="text-align: center;">
                        <div style="font-size: 2em; margin-bottom: 8px;">🚀</div>
                        <div style="font-size: 0.9em; opacity: 0.9;">新知探索</div>
                    </div>
                    <div style="text-align: center;">
                        <div style="font-size: 2em; margin-bottom: 8px;">💪</div>
                        <div style="font-size: 0.9em; opacity: 0.9;">弱点巩固</div>
                    </div>
                    <div style="text-align: center;">
                        <div style="font-size: 2em; margin-bottom: 8px;">⚡</div>
                        <div style="font-size: 0.9em; opacity: 0.9;">技能提升</div>
                    </div>
                    <div style="text-align: center;">
                        <div style="font-size: 2em; margin-bottom: 8px;">🎨</div>
                        <div style="font-size: 0.9em; opacity: 0.9;">兴趣探索</div>
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # 超大醒目按钮 - 占据更多空间
        st.markdown("""
        <style>
        .mega-button {
            background: linear-gradient(135deg, #FF6B6B 0%, #FF8E53 100%);
            color: white;
            padding: 30px 80px;
            font-size: 2em;
            font-weight: bold;
            border: none;
            border-radius: 60px;
            cursor: pointer;
            box-shadow: 0 15px 40px rgba(255,107,107,0.5);
            transition: all 0.3s ease;
            text-decoration: none;
            display: block;
            width: 80%;
            max-width: 600px;
            margin: 40px auto;
            text-align: center;
            min-height: 80px;
            line-height: 1.2;
        }
        .mega-button:hover {
            transform: translateY(-5px);
            box-shadow: 0 20px 50px rgba(255,107,107,0.7);
            background: linear-gradient(135deg, #FF8E53 0%, #FF6B6B 100%);
            scale: 1.02;
        }
        .mega-button:active {
            transform: translateY(-2px);
        }
        
        /* 覆盖Streamlit默认按钮样式 */
        .stButton > button {
            background: linear-gradient(135deg, #FF6B6B 0%, #FF8E53 100%) !important;
            color: white !important;
            padding: 30px 80px !important;
            font-size: 2em !important;
            font-weight: bold !important;
            border: none !important;
            border-radius: 60px !important;
            box-shadow: 0 15px 40px rgba(255,107,107,0.5) !important;
            transition: all 0.3s ease !important;
            width: 100% !important;
            min-height: 80px !important;
            line-height: 1.2 !important;
        }
        .stButton > button:hover {
            transform: translateY(-5px) !important;
            box-shadow: 0 20px 50px rgba(255,107,107,0.7) !important;
            background: linear-gradient(135deg, #FF8E53 0%, #FF6B6B 100%) !important;
            scale: 1.02 !important;
            border: none !important;
        }
        .stButton > button:active {
            transform: translateY(-2px) !important;
            background: linear-gradient(135deg, #FF6B6B 0%, #FF8E53 100%) !important;
        }
        .stButton > button:focus {
            box-shadow: 0 20px 50px rgba(255,107,107,0.7) !important;
            border: none !important;
        }
        </style>
        """, unsafe_allow_html=True)
        
        # 使用更宽的列布局让按钮更大
        col1, col2, col3 = st.columns([0.5, 3, 0.5])
        with col2:
            # 超大按钮
            if st.button(
                "🎯 获取我的专属学习任务包", 
                key="get_recommendation", 
                use_container_width=True, 
                type="primary",
                help="点击获取AI为你定制的个性化学习任务"
            ):
                st.session_state.loading_recommendation = True
                st.rerun()
            
            # 添加按钮下方的说明文字
            st.markdown("""
            <div style="
                text-align: center;
                margin-top: 25px;
                color: #666;
                font-size: 1.1em;
                font-weight: 500;
            ">
                💡 点击后AI将深度分析你的学习数据，生成专属任务
            </div>
            """, unsafe_allow_html=True)
        
        return
    
    # 如果正在加载推荐任务
    if st.session_state.loading_recommendation:
        # 显示加载界面
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 40px;
            border-radius: 20px;
            text-align: center;
            margin: 30px 0;
            box-shadow: 0 8px 32px rgba(102,126,234,0.2);
            color: white;
        ">
            <div style="font-size: 3em; margin-bottom: 20px;">🤖</div>
            <h2 style="margin: 0 0 15px 0; font-size: 1.8em;">AI正在为你量身定制学习任务</h2>
            <p style="margin: 0; font-size: 1.1em; opacity: 0.9;">请稍等片刻，我们正在分析你的学习情况...</p>
            <div style="margin-top: 25px; display: flex; justify-content: center; align-items: center;">
                 <div style="
                     display: flex;
                     gap: 8px;
                 ">
                     <div style="
                         width: 8px;
                         height: 8px;
                         background: rgba(255,255,255,0.9);
                         border-radius: 50%;
                         animation: bounce 1.4s infinite ease-in-out both;
                         animation-delay: -0.32s;
                     "></div>
                     <div style="
                         width: 8px;
                         height: 8px;
                         background: rgba(255,255,255,0.9);
                         border-radius: 50%;
                         animation: bounce 1.4s infinite ease-in-out both;
                         animation-delay: -0.16s;
                     "></div>
                     <div style="
                         width: 8px;
                         height: 8px;
                         background: rgba(255,255,255,0.9);
                         border-radius: 50%;
                         animation: bounce 1.4s infinite ease-in-out both;
                     "></div>
                 </div>
             </div>
         </div>
         <style>
         @keyframes bounce {
             0%, 80%, 100% {
                 transform: scale(0);
                 opacity: 0.5;
             }
             40% {
                 transform: scale(1);
                 opacity: 1;
             }
         }
         </style>
         """, unsafe_allow_html=True)
        
        # 调用API获取推荐
        try:
            with st.spinner("正在生成个性化任务推荐..."):
                recommendation = api_service.get_recommendation(user_id)
                st.session_state.current_recommendation = recommendation
                st.session_state.loading_recommendation = False
        except Exception as e:
            st.error(f"获取推荐任务时出错: {str(e)}")
            st.session_state.loading_recommendation = False
            recommendation = None
        
        # 重新运行页面以显示新内容
        st.rerun()
    
    # 显示推荐任务
    recommendation = st.session_state.current_recommendation
    
    if not recommendation or "error" in recommendation:
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, #E3F2FD 0%, #BBDEFB 100%);
            padding: 30px;
            border-radius: 15px;
            text-align: center;
            margin: 20px 0;
        ">
            <h3 style="color: #1976D2; margin-bottom: 10px;">🎯 暂无推荐任务</h3>
            <p style="color: #424242;">系统正在为你生成个性化学习任务，请稍后再试</p>
        </div>
        """, unsafe_allow_html=True)
        return
    
    # 获取任务类型信息
    mission_type = recommendation.get('mission_type', '')
    type_info = get_mission_type_info(mission_type)
    metadata = recommendation.get('metadata', {})
    payload = recommendation.get('payload', {})
    
    # 主任务卡片
    st.markdown(f"""
    <div style="
        background: {type_info['bg_gradient']};
        padding: 0;
        border-radius: 20px;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        margin: 20px 0;
        overflow: hidden;
    ">
        <div style="
            background: rgba(255,255,255,0.1);
            padding: 25px;
            color: white;
        ">
            <div style="display: flex; align-items: center; margin-bottom: 15px;">
                <span style="font-size: 2.5em; margin-right: 15px;">{type_info['icon']}</span>
                <div>
                    <h2 style="margin: 0; font-size: 1.8em;">{type_info['name']}</h2>
                    <p style="margin: 5px 0 0 0; opacity: 0.9; font-size: 1.1em;">{metadata.get('title', '无标题')}</p>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # 任务详情区域
    col1, col2 = st.columns([3, 1])
    
    with col1:
        # 任务目标
        st.markdown(f"""
        <div style="
            background: white;
            padding: 20px;
            border-radius: 15px;
            box-shadow: 0 4px 16px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        ">
            <div style="margin-bottom: 15px;">
                <strong>🎯 学习目标</strong>
                <p style='color: #424242; line-height: 1.6; margin: 8px 0;'>{metadata.get('objective', '无目标描述')}</p>
            </div>
            <div>
                <strong>💡 推荐理由</strong>
                <p style='color: #666; line-height: 1.6; font-style: italic; margin: 8px 0;'>{metadata.get('reason', '无推荐理由')}</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # 任务内容展示
        render_mission_content(mission_type, payload, api_service, user_id)
    
    with col2:
        # 任务操作面板
        with st.container(border=True):
            # 将标题放在容器内部
            st.markdown("**⚡ 快速操作**")
            
            # 垂直排列按钮，更美观的布局
            st.markdown("<div style='margin: 15px 0;'></div>", unsafe_allow_html=True)
            
            # 当用户点击"开始任务"按钮时
            if st.button("🚀 开始任务", key="start_task", use_container_width=True, type="primary"):
                st.session_state.task_started = True
                with st.spinner("任务加载中..."):
                    time.sleep(1)
                    st.success("✅ 任务已开始！")
                    st.balloons()
            
            # 显示任务状态
            if st.session_state.task_started:
                st.markdown("<div style='margin: 10px 0;'></div>", unsafe_allow_html=True)
                st.markdown("""
                <div style="
                    background: linear-gradient(135deg, #E8F5E8 0%, #C8E6C9 100%);
                    padding: 10px;
                    border-radius: 8px;
                    text-align: center;
                    margin: 10px 0;
                ">
                    <span style="color: #2E7D32; font-weight: bold;">🎯 任务进行中</span>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("<div style='margin: 10px 0;'></div>", unsafe_allow_html=True)
            
            # 当用户点击"换个任务"按钮时
            if st.button("🔄 换个任务", key="refresh_task", use_container_width=True):
                # 清除缓存的推荐任务，强制重新获取
                st.session_state.current_recommendation = None
                st.session_state.task_started = False
                st.session_state.loading_recommendation = False
                st.rerun()
            
            st.markdown("<div style='margin: 15px 0;'></div>", unsafe_allow_html=True)
    
    # 渲染学习进度和错题提醒
    render_stats_and_wrong_questions(api_service, user_id, current_user)

def render_mission_content(mission_type, payload, api_service, user_id):
    """渲染任务具体内容"""
    if mission_type in ['NEW_KNOWLEDGE', 'WEAK_POINT_CONSOLIDATION']:
        render_knowledge_mission(payload, api_service, user_id)
    elif mission_type == 'SKILL_ENHANCEMENT':
        render_skill_mission(payload, api_service, user_id)
    elif mission_type == 'EXPLORATORY':
        render_exploratory_mission(payload)

def render_knowledge_mission(payload, api_service, user_id):
    """渲染知识学习任务"""
    target_node = payload.get('target_node', {})
    steps = payload.get('steps', [])
    
    if target_node:
        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, #E8F5E8 0%, #C8E6C9 100%);
            padding: 15px;
            border-radius: 10px;
            margin: 15px 0;
        ">
            <strong>📚 目标知识点</strong>
            <h4 style='color: #2E7D32; margin: 5px 0;'>{target_node.get('name', '未知知识点')}</h4>
        </div>
        """, unsafe_allow_html=True)
    
    if steps:
        st.markdown(f"**📋 学习步骤 ({len(steps)}步)**")
        
        for i, step in enumerate(steps, 1):
            with st.expander(f"第{i}步: {get_step_type_name(step.get('type', ''))}"): 
                if step['type'] == 'CONCEPT_LEARNING':
                    content = step.get('content', {})
                    st.markdown(f"**{content.get('title', '概念学习')}**")
                    st.markdown(content.get('text', '暂无内容'))
                elif step['type'] == 'QUESTION_PRACTICE':
                    render_question_practice(step.get('content', {}), api_service, user_id)
                elif step['type'] == 'WRONG_QUESTION_REVIEW':
                    render_wrong_question_review(step.get('content', {}), api_service, user_id)

def render_skill_mission(payload, api_service, user_id):
    """渲染技能提升任务"""
    target_skill = payload.get('target_skill', '未知技能')
    questions = payload.get('questions', [])
    
    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, #E3F2FD 0%, #BBDEFB 100%);
        padding: 15px;
        border-radius: 10px;
        margin: 15px 0;
    ">
        <strong>⚡ 目标技能</strong>
        <h4 style='color: #1976D2; margin: 5px 0;'>{target_skill}</h4>
    </div>
    """, unsafe_allow_html=True)
    
    if questions:
        st.markdown(f"**🎯 练习题目 ({len(questions)}题)**")
        
        for i, question in enumerate(questions, 1):
            with st.expander(f"题目 {i}: {question.get('prompt', '练习题')[:20]}..."):
                render_question_practice(question, api_service, user_id)

def render_exploratory_mission(payload):
    """渲染探索性任务"""
    content_type = payload.get('content_type', '未知类型')
    title = payload.get('title', '无标题')
    body = payload.get('body', '无内容')
    
    image_section = f"<div style='margin-top: 15px;'><strong>🖼️ 相关图片:</strong> <a href='{payload.get('image_url')}' target='_blank'>查看图片</a></div>" if payload.get('image_url') else ""
    
    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, #F3E5F5 0%, #E1BEE7 100%);
        padding: 20px;
        border-radius: 15px;
        margin: 15px 0;
    ">
        <div style="margin-bottom: 10px;"><strong>🎨 内容类型:</strong> {content_type}</div>
        <div style="margin-bottom: 10px;"><strong>📖 标题:</strong> {title}</div>
        <div style="margin-bottom: 10px;"><strong>📝 内容:</strong></div>
        <p style='color: #4A148C; line-height: 1.6; margin: 8px 0;'>{body}</p>
        {image_section}
    </div>
    """, unsafe_allow_html=True)

def render_question_practice(content, api_service, user_id):
    """渲染练习题"""
    question_id = content.get('question_id')
    prompt = content.get('prompt', '开始练习吧！')
    difficulty = content.get('difficulty', 0.5)
    
    # 显示提示信息
    if prompt:
        st.markdown(f"**💬 提示:** {prompt}")
    
    if question_id:
        # 构造题目数据格式，适配做题组件
        question_data = {
            'question_id': question_id,
            'question_text': content.get('question_text', prompt),
            'question': content.get('question', prompt),
            'difficulty': difficulty,
            'question_type': content.get('question_type', 'text_input')
        }
        
        # 使用通用做题组件
        render_simple_question(
            api_service=api_service,
            user_id=user_id,
            question=question_data,
            key_suffix=f"daily_task_{question_id}"
        )
    else:
        st.warning("⚠️ 题目数据不完整，缺少question_id")

def render_wrong_question_review(content, api_service, user_id):
    """渲染错题回顾"""
    question_id = content.get('question_id')
    prompt = content.get('prompt', '让我们回顾一下这道题')
    
    # 显示回顾提示
    if prompt:
        st.markdown(f"**🔍 回顾提示:** {prompt}")
    
    if question_id:
        st.info(f"📋 题目ID: {question_id}")
        st.markdown("**🎯 重新作答:**")
        
        # 构造题目数据格式，适配做题组件
        question_data = {
            'question_id': question_id,
            'question_text': content.get('question_text', prompt),
            'question': content.get('question', prompt),
            'difficulty': content.get('difficulty', 0.5),
            'question_type': content.get('question_type', 'text_input')
        }
        
        # 使用通用做题组件
        render_simple_question(
            api_service=api_service,
            user_id=user_id,
            question=question_data,
            key_suffix=f"wrong_review_{question_id}"
        )
    else:
        st.warning("⚠️ 错题数据不完整，缺少question_id")

def get_step_type_name(step_type):
    """获取步骤类型的中文名称"""
    type_names = {
        'CONCEPT_LEARNING': '📚 概念学习',
        'QUESTION_PRACTICE': '✍️ 题目练习', 
        'WRONG_QUESTION_REVIEW': '🔍 错题回顾'
    }
    return type_names.get(step_type, '📝 学习步骤')

def render_stats_and_wrong_questions(api_service, user_id, current_user):
    """渲染学习进度和错题提醒部分"""
    # 学习进度概览
    st.markdown("""
    <div style="margin: 40px 0 20px 0;">
        <h2 style="color: #2E3440; text-align: center; margin-bottom: 20px;">📊 学习进度概览</h2>
    </div>
    """, unsafe_allow_html=True)
    
    # 获取用户统计数据
    stats = api_service.get_user_stats(user_id)
    
    col1, col2, col3, col4 = st.columns(4)
    
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
    
    with col1:
        st.markdown(metric_style.format(
            icon="📝",
            value=stats.get("total_questions_answered", 0),
            label="今日完成题目",
            color="#2196F3",
            delta="+3 题"
        ), unsafe_allow_html=True)
    
    with col2:
        correct_rate = stats.get('correct_rate', 0.0) * 100
        st.markdown(metric_style.format(
            icon="🎯",
            value=f"{correct_rate:.1f}%",
            label="正确率",
            color="#4CAF50" if correct_rate >= 80 else "#FF9800" if correct_rate >= 60 else "#F44336",
            delta="+5%"
        ), unsafe_allow_html=True)
    
    with col3:
        study_time = stats.get('study_time_today', 0)
        st.markdown(metric_style.format(
            icon="⏰",
            value=f"{study_time}分钟",
            label="学习时长",
            color="#9C27B0",
            delta="+10分钟"
        ), unsafe_allow_html=True)
    
    with col4:
        streak_days = stats.get('streak_days', 0)
        st.markdown(metric_style.format(
            icon="🔥",
            value=f"{streak_days}天",
            label="连续学习天数",
            color="#FF5722",
            delta="+1天"
        ), unsafe_allow_html=True)
    
    # 最近错题提醒
    st.markdown("""
    <div style="margin: 40px 0 20px 0;">
        <h2 style="color: #2E3440; text-align: center; margin-bottom: 20px;">❌ 最近错题提醒</h2>
    </div>
    """, unsafe_allow_html=True)
    
    # 获取错题数据
    wrong_questions = api_service.get_wrong_questions(user_id)
    
    if wrong_questions and len(wrong_questions) > 0:
        for i, question in enumerate(wrong_questions[:3]):
            question_text = question.get('question_text', '未知题目')
            if len(question_text) > 50:
                question_text = question_text[:50] + "..."
            
            # 错题卡片 - 使用完整的HTML结构
            st.markdown(f"""
            <div style="
                background: white;
                padding: 20px;
                border-radius: 15px;
                box-shadow: 0 4px 16px rgba(0,0,0,0.1);
                margin: 15px 0;
                border-left: 4px solid #F44336;
            ">
                <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                    <div style="flex: 1; padding-right: 20px;">
                        <div style="margin-bottom: 8px;"><strong>🔍 错题 {i+1}</strong></div>
                        <div style="margin-bottom: 5px;"><strong>题目:</strong> {question_text}</div>
                        <div style="margin-bottom: 5px;"><strong>📚 科目:</strong> {question.get('subject', '未知')}</div>
                        <div><strong>📅 错误日期:</strong> {question.get('date', '未知')}</div>
                    </div>
                    <div style="flex-shrink: 0;">
                        <button onclick="alert('功能开发中...')" style="
                            background: #4CAF50;
                            color: white;
                            border: none;
                            padding: 8px 16px;
                            border-radius: 5px;
                            cursor: pointer;
                            font-size: 14px;
                        ">🔄 重新练习</button>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, #E8F5E8 0%, #C8E6C9 100%);
            padding: 30px;
            border-radius: 15px;
            text-align: center;
            margin: 20px 0;
        ">
            <div style="font-size: 3em; margin-bottom: 15px;">🎉</div>
            <h3 style="color: #2E7D32; margin-bottom: 10px;">太棒了！</h3>
            <p style="color: #424242; font-size: 1.1em;">最近没有错题，继续保持这个好状态！</p>
        </div>
        """, unsafe_allow_html=True)