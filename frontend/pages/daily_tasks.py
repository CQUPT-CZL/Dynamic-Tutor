from curses import use_default_colors
import streamlit as st
import time

def render_daily_tasks_page(api_service, current_user, user_id):
    """渲染今日任务页面"""
    st.markdown("## 📋 今日任务")
    
    if not current_user:
        st.warning("请先选择用户")
        return
    
    # 获取用户推荐
    recommendation = api_service.get_recommendation(user_id)
    
    if not recommendation or "error" in recommendation:
        st.info("暂无推荐任务")
        return
    
    # 显示推荐任务
    st.markdown(f"### 🎯 为 {current_user} 推荐的任务")
    
    # 任务卡片
    with st.container():
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            border-radius: 10px;
            color: white;
            margin: 10px 0;
        ">
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.markdown(f"**任务类型：** {recommendation.get('type', '未知')}")
            st.markdown(f"**推荐理由：** {recommendation.get('reason', '无')}")
            
            # 显示任务内容
            content = recommendation.get('content', {})
            if content:
                if content.get('knowledge_point'):
                    st.markdown(f"**知识点：** {content['knowledge_point']}")
                if content.get('difficulty'):
                    st.markdown(f"**难度：** {content['difficulty']}")
                if content.get('question_count'):
                    st.markdown(f"**题目数量：** {content['question_count']}")
        
        with col2:
            if st.button("开始任务", key="start_task"):
                st.success("任务已开始！")
                # 这里可以跳转到具体的练习页面
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    # 学习进度概览
    st.markdown("### 📊 学习进度概览")
    
    # 获取用户统计数据
    stats = api_service.get_user_stats(current_user)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("今日完成题目", stats.get("total_questions_answered", 0), "3")
    
    with col2:
        st.metric("正确率", f"{stats.get('correct_rate', 0.0)*100:.1f}%", "5%")
    
    with col3:
        st.metric("学习时长", f"{stats.get('study_time_today', 0)}分钟", "10分钟")
    
    with col4:
        st.metric("连续学习天数", f"{stats.get('streak_days', 0)}天", "1天")
    
    # 最近错题提醒
    st.markdown("### ❌ 最近错题提醒")
    
    # 获取错题数据
    wrong_questions = api_service.get_wrong_questions(current_user)
    
    if wrong_questions and len(wrong_questions) > 0:
        for i, question in enumerate(wrong_questions[:3]):
            with st.expander(f"错题 {i+1}: {question.get('question_text', '未知题目')[:30]}..."):
                st.write(f"**完整题目：** {question.get('question_text', '未知题目')}")
                st.write(f"**科目：** {question.get('subject', '未知')}")
                st.write(f"**错误日期：** {question.get('date', '未知')}")
                if st.button(f"重新练习", key=f"retry_{i}"):
                    st.info("跳转到练习页面...")
    else:
        st.success("🎉 最近没有错题，继续保持！")