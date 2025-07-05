import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

def load_user_wrong_questions(api_service, user_id):
    """通过API加载用户的错题数据"""
    try:
        # 通过API获取用户错题数据
        wrong_questions = api_service.get_wrong_questions(user_id)
        
        if not wrong_questions:
            return []
        
        wrong_questions_list = []
        
        for wrong_q in wrong_questions:
            try:
                wrong_questions_list.append({
                    "题目ID": wrong_q.get("question_id", ""),
                    "题目内容": wrong_q.get("question_text", "题目内容未找到"),
                    "错误次数": wrong_q.get("wrong_count", 0),
                    "首次错误时间": wrong_q.get("first_wrong_time", ""),
                    "最近错误时间": wrong_q.get("last_wrong_time", ""),
                    "知识点": wrong_q.get("knowledge_points", "未知"),
                    "难度": wrong_q.get("difficulty", "未知"),
                    "状态": wrong_q.get("status", "未知")
                })
            except Exception as item_error:
                st.warning(f"处理错题记录时出错: {item_error}")
                continue
        
        return wrong_questions_list
    
    except Exception as e:
        st.error(f"加载错题数据时出错: {type(e).__name__}: {e}")
        return []

def render_wrong_questions_page(api_service, current_user, user_id):
    """渲染错题集页面"""
    # 检查用户是否已选择
    if not current_user:
        st.warning("⚠️ 请先选择一个用户")
        return
    
    st.write("### 📚 我的错题集")
    st.info(f"👨‍🎓 当前学习者：**{current_user}**")
    
    # 通过API加载错题数据
    wrong_questions_data = load_user_wrong_questions(api_service, user_id)
    
    # 错题集功能区域
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("🔍 错题回顾")
        
        # 错题筛选选项
        filter_option = st.selectbox(
            "筛选条件",
            ["全部错题", "最近一周", "最近一月", "按科目筛选", "按难度筛选"]
        )
        
        if filter_option == "按科目筛选":
            subject = st.selectbox("选择科目", ["数学", "语文", "英语", "物理", "化学", "生物"])
        elif filter_option == "按难度筛选":
            difficulty = st.selectbox("选择难度", ["简单", "中等", "困难"])
        
        # 错题列表展示区域
        st.markdown("---")
        st.subheader("📋 错题列表")
        
        # 使用加载的错题数据
        wrong_questions = []
        for q_data in wrong_questions_data:
            wrong_questions.append({
                "id": q_data["题目ID"],
                "subject": "数学",  # 可以从知识点推断科目
                "question": q_data["题目内容"],
                "your_answer": "用户答案",  # 需要从数据中获取
                "correct_answer": "正确答案",  # 需要从数据中获取
                "difficulty": q_data["难度"],
                "date": q_data["最近错误时间"],
                "times_wrong": q_data["错误次数"]
            })
        
        # 显示错题
        for i, question in enumerate(wrong_questions):
            with st.expander(f"❌ {question['subject']} - {question['question'][:30]}..."):
                st.markdown(f"**📚 科目：** {question['subject']}")
                st.markdown(f"**📅 错误日期：** {question['date']}")
                st.markdown(f"**🎯 难度：** {question['difficulty']}")
                st.markdown(f"**🔄 错误次数：** {question['times_wrong']}")
                
                st.markdown("**❓ 题目：**")
                st.write(question['question'])
                
                col_a, col_b = st.columns(2)
                with col_a:
                    st.markdown("**❌ 你的答案：**")
                    st.error(question['your_answer'])
                
                with col_b:
                    st.markdown("**✅ 正确答案：**")
                    st.success(question['correct_answer'])
                
                # 操作按钮
                btn_col1, btn_col2, btn_col3 = st.columns(3)
                with btn_col1:
                    if st.button(f"🔄 重新练习", key=f"retry_{question['id']}"):
                        st.info("跳转到练习模式...")
                
                with btn_col2:
                    if st.button(f"📖 查看解析", key=f"explain_{question['id']}"):
                        st.info("显示详细解析...")
                
                with btn_col3:
                    if st.button(f"✅ 标记已掌握", key=f"master_{question['id']}"):
                        st.success("已标记为掌握！")
    
    with col2:
        st.subheader("📊 错题统计")
        
        # 统计信息
        total_wrong = len(wrong_questions)
        st.metric("总错题数", total_wrong)
        
        # 按科目统计
        subject_stats = {}
        for q in wrong_questions:
            subject = q['subject']
            subject_stats[subject] = subject_stats.get(subject, 0) + 1
        
        st.markdown("**📚 按科目分布：**")
        for subject, count in subject_stats.items():
            st.write(f"• {subject}: {count} 题")
        
        # 按难度统计
        difficulty_stats = {}
        for q in wrong_questions:
            difficulty = q['difficulty']
            difficulty_stats[difficulty] = difficulty_stats.get(difficulty, 0) + 1
        
        st.markdown("**🎯 按难度分布：**")
        for difficulty, count in difficulty_stats.items():
            st.write(f"• {difficulty}: {count} 题")
        
        st.markdown("---")
        
        # 学习建议
        st.subheader("💡 学习建议")
        
        if total_wrong > 0:
            # 找出错误最多的科目
            max_subject = max(subject_stats.items(), key=lambda x: x[1])
            st.info(f"🎯 重点关注：{max_subject[0]}科目，共有{max_subject[1]}道错题")
            
            # 找出错误次数最多的题目
            max_wrong_times = max(wrong_questions, key=lambda x: x['times_wrong'])
            if max_wrong_times['times_wrong'] > 2:
                st.warning(f"⚠️ 反复错误：{max_wrong_times['subject']}科目中有题目错误{max_wrong_times['times_wrong']}次，建议重点复习")
        
        # 快速操作
        st.markdown("---")
        st.subheader("⚡ 快速操作")
        
        if st.button("🔄 开始错题专项练习", use_container_width=True):
            st.success("正在准备错题专项练习...")
        
        if st.button("📊 生成错题分析报告", use_container_width=True):
            st.success("正在生成分析报告...")
        
        if st.button("🗑️ 清空已掌握错题", use_container_width=True):
            st.warning("确认清空已掌握的错题？")