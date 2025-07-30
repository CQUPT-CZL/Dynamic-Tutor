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

def render_recommended_tasks_page(api_service, current_user, user_id):
    """渲染推荐任务页面"""
    if not current_user:
        st.warning("⚠️ 请先选择用户")
        return
    
    # 初始化session_state
    if 'current_recommendation' not in st.session_state:
        st.session_state.current_recommendation = None
    if 'task_started' not in st.session_state:
        st.session_state.task_started = False
    if 'loading_recommendation' not in st.session_state:
        st.session_state.loading_recommendation = False
    
    # 页面标题
    st.markdown("""
    <div style="text-align: center; padding: 20px 0;">
        <h1 style="color: #2E3440; margin-bottom: 10px;">🎯 今日推荐任务</h1>
        <p style="color: #5E81AC; font-size: 18px;">AI为你量身定制的个性化学习任务</p>
    </div>
    """, unsafe_allow_html=True)
    
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
        
        # 超大醒目按钮
        col1, col2, col3 = st.columns([0.5, 3, 0.5])
        with col2:
            if st.button(
                "🎯 获取我的专属学习任务包", 
                key="get_recommendation", 
                use_container_width=True, 
                type="primary",
                help="点击获取AI为你定制的个性化学习任务"
            ):
                st.session_state.loading_recommendation = True
                st.rerun()
    
    # 加载推荐任务
    elif st.session_state.loading_recommendation:
        st.markdown("""
        <div style="text-align: center; padding: 50px;">
            <div style="font-size: 3em; margin-bottom: 20px;">🤖</div>
            <h3>AI正在为你分析学习数据...</h3>
            <p>请稍候，我们正在根据你的学习情况生成个性化任务</p>
        </div>
        """, unsafe_allow_html=True)
        
        # 模拟加载过程
        time.sleep(2)
        
        try:
            # 获取推荐任务
            recommendation = api_service.get_daily_recommendation(user_id)
            if recommendation and 'missions' in recommendation:
                st.session_state.current_recommendation = recommendation
                st.session_state.loading_recommendation = False
                st.rerun()
            else:
                st.error("获取推荐任务失败，请稍后重试")
                st.session_state.loading_recommendation = False
        except Exception as e:
            st.error(f"获取推荐任务失败: {str(e)}")
            st.session_state.loading_recommendation = False
    
    # 显示推荐任务
    elif st.session_state.current_recommendation:
        recommendation = st.session_state.current_recommendation
        
        # 显示任务概览
        total_tasks = len(recommendation.get('missions', []))
        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
            color: white;
            padding: 25px;
            border-radius: 15px;
            margin-bottom: 25px;
            text-align: center;
        ">
            <h2 style="margin: 0 0 10px 0;">🎉 今日为你准备了 {total_tasks} 个学习任务</h2>
            <p style="margin: 0; opacity: 0.9;">每个任务都经过AI精心筛选，适合你的当前学习阶段</p>
        </div>
        """, unsafe_allow_html=True)
        
        # 显示任务列表
        for idx, mission in enumerate(recommendation.get('missions', [])):
            mission_info = get_mission_type_info(mission.get('type', 'UNKNOWN'))
            
            # 任务卡片
            st.markdown(f"""
            <div style="
                background: {mission_info['bg_gradient']};
                color: white;
                padding: 25px;
                border-radius: 15px;
                margin-bottom: 20px;
                box-shadow: 0 4px 16px rgba(0,0,0,0.1);
            ">
                <div style="display: flex; align-items: center; justify-content: space-between;">
                    <div>
                        <div style="font-size: 2em; margin-bottom: 10px;">{mission_info['icon']}</div>
                        <h3 style="margin: 0 0 5px 0;">{mission_info['name']}</h3>
                        <p style="margin: 0; opacity: 0.9;">{mission.get('description', '个性化学习任务')}</p>
                    </div>
                    <div style="text-align: right;">
                        <div style="font-size: 1.2em; font-weight: bold;">{len(mission.get('questions', []))} 题</div>
                        <div style="opacity: 0.8; font-size: 0.9em;">预计用时: {mission.get('estimated_time', '15-20')}分钟</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # 任务详情
            with st.expander("📋 查看任务详情", expanded=False):
                questions = mission.get('questions', [])
                if questions:
                    st.markdown("**题目列表：**")
                    for q_idx, question in enumerate(questions):
                        col_a, col_b = st.columns([3, 1])
                        with col_a:
                            st.write(f"{q_idx + 1}. {question.get('title', '题目')}")
                        with col_b:
                            st.write(f"难度: {question.get('difficulty', '中等')}")
                else:
                    st.info("暂无题目信息")
            
            # 开始任务按钮
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button(
                    f"🚀 开始{mission_info['name']}", 
                    key=f"start_mission_{idx}",
                    use_container_width=True,
                    type="primary"
                ):
                    st.session_state.task_started = True
                    st.session_state.current_mission = mission
                    st.rerun()
        
        # 重新开始按钮
        st.markdown("---")
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🔄 重新获取推荐", key="refresh_recommendation", use_container_width=True):
                st.session_state.current_recommendation = None
                st.session_state.task_started = False
                st.rerun()
    
    # 任务进行中
    if st.session_state.task_started and 'current_mission' in st.session_state:
        mission = st.session_state.current_mission
        mission_info = get_mission_type_info(mission.get('type', 'UNKNOWN'))
        
        # 任务标题
        st.markdown(f"""
        <div style="
            background: {mission_info['bg_gradient']};
            color: white;
            padding: 20px;
            border-radius: 15px;
            margin-bottom: 20px;
            text-align: center;
        ">
            <h2 style="margin: 0;">{mission_info['icon']} {mission_info['name']}</h2>
            <p style="margin: 5px 0 0 0; opacity: 0.9;">{mission.get('description', '')}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # 使用QuestionPracticeComponent进行练习
        questions = mission.get('questions', [])
        if questions:
            practice_component = QuestionPracticeComponent(api_service, user_id)
            practice_component.render_practice_session(questions)
        else:
            st.error("任务中没有题目")
        
        # 返回按钮
        if st.button("⬅️ 返回任务列表"):
            st.session_state.task_started = False
            if 'current_mission' in st.session_state:
                del st.session_state.current_mission
            st.rerun()