import streamlit as st
import time
from components import render_simple_question, QuestionPracticeComponent

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
    # 页面标题
    st.markdown("""
    <div style="text-align: center; padding: 20px 0;">
        <h1 style="color: #2E3440; margin-bottom: 10px;">📋 今日学习任务</h1>
        <p style="color: #5E81AC; font-size: 18px;">为你量身定制的智能学习计划</p>
    </div>
    """, unsafe_allow_html=True)
    
    if not current_user:
        st.warning("⚠️ 请先选择用户")
        return
    
    # 初始化session_state来缓存推荐任务
    if 'current_recommendation' not in st.session_state:
        st.session_state.current_recommendation = None
    if 'task_started' not in st.session_state:
        st.session_state.task_started = False
    
    # 获取用户推荐（只在没有缓存或需要刷新时获取）
    if st.session_state.current_recommendation is None:
        recommendation = api_service.get_recommendation(user_id)
        st.session_state.current_recommendation = recommendation
    else:
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
                with st.spinner("正在为你刷新任务..."):
                    time.sleep(1)
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