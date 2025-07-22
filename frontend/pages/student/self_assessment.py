import streamlit as st
import time
import random
from components import render_question_with_navigation, QuestionPracticeComponent

def render_self_assessment_page(api_service, current_user, user_id):
    """渲染自我测评页面"""
    st.header("🎯 自我测评")
    
    # 检查是否有选择的用户
    if not current_user:
        st.warning("⚠️ 请先选择一个用户")
        return
    
    st.info(f"👤 当前用户：{current_user}")
    
    # 初始化session state
    if 'assessment_mode' not in st.session_state:
        st.session_state.assessment_mode = 'setup'
    if 'current_question' not in st.session_state:
        st.session_state.current_question = 0
    if 'assessment_answers' not in st.session_state:
        st.session_state.assessment_answers = []
    if 'assessment_start_time' not in st.session_state:
        st.session_state.assessment_start_time = None
    
    # 根据当前模式渲染不同内容
    if st.session_state.assessment_mode == 'setup':
        render_assessment_setup()
    elif st.session_state.assessment_mode == 'testing':
        render_assessment_testing()
    elif st.session_state.assessment_mode == 'result':
        render_assessment_result()

def render_assessment_setup():
    """渲染测评设置页面"""
    st.subheader("📋 测评设置")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # 测评类型选择
        assessment_type = st.selectbox(
            "🎯 选择测评类型",
            ["综合能力测评", "单科专项测评", "薄弱环节诊断", "学习状态评估"]
        )
        
        # 根据测评类型显示不同选项
        if assessment_type == "单科专项测评":
            subject = st.selectbox(
                "📚 选择科目",
                ["数学", "语文", "英语", "物理", "化学", "生物", "历史", "地理", "政治"]
            )
        
        # 难度级别
        difficulty = st.select_slider(
            "🎚️ 难度级别",
            options=["基础", "进阶", "提高", "竞赛"],
            value="进阶"
        )
        
        # 题目数量
        question_count = st.slider(
            "📝 题目数量",
            min_value=5,
            max_value=50,
            value=20,
            step=5
        )
        
        # 时间限制
        time_limit = st.slider(
            "⏰ 时间限制（分钟）",
            min_value=10,
            max_value=120,
            value=30,
            step=5
        )
        
        # 测评说明
        st.markdown("---")
        st.markdown("**📖 测评说明：**")
        st.markdown(f"• 测评类型：{assessment_type}")
        st.markdown(f"• 难度级别：{difficulty}")
        st.markdown(f"• 题目数量：{question_count} 题")
        st.markdown(f"• 时间限制：{time_limit} 分钟")
        st.markdown("• 请在规定时间内完成所有题目")
        st.markdown("• 测评结果将提供详细的能力分析报告")
        
        # 开始测评按钮
        if st.button("🚀 开始测评", type="primary", use_container_width=True):
            # 保存测评配置
            st.session_state.assessment_config = {
                'type': assessment_type,
                'subject': subject if assessment_type == "单科专项测评" else None,
                'difficulty': difficulty,
                'question_count': question_count,
                'time_limit': time_limit
            }
            st.session_state.assessment_mode = 'testing'
            st.session_state.current_question = 0
            st.session_state.assessment_answers = []
            st.session_state.assessment_start_time = time.time()
            st.rerun()
    
    with col2:
        st.subheader("📊 历史测评记录")
        
        # 历史记录
        history_records = [
            {
                "date": "2024-01-15",
                "type": "数学专项",
                "score": 85,
                "duration": "25分钟"
            },
            {
                "date": "2024-01-10",
                "type": "综合能力",
                "score": 78,
                "duration": "45分钟"
            },
            {
                "date": "2024-01-05",
                "type": "英语专项",
                "score": 92,
                "duration": "20分钟"
            }
        ]
        
        for record in history_records:
            with st.container():
                st.markdown(f"**📅 {record['date']}**")
                st.markdown(f"🎯 {record['type']}")
                st.markdown(f"📊 得分：{record['score']}分")
                st.markdown(f"⏱️ 用时：{record['duration']}")
                st.markdown("---")
        
        # 能力趋势
        st.subheader("📈 能力趋势")
        st.line_chart([78, 82, 85, 88, 92])

def render_assessment_testing():
    """渲染测评进行页面"""
    config = st.session_state.assessment_config
    current_q = st.session_state.current_question
    
    # 顶部进度条和时间
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        progress = (current_q + 1) / config['question_count']
        st.progress(progress)
        st.write(f"题目进度：{current_q + 1}/{config['question_count']}")
    
    with col2:
        # 计算剩余时间
        elapsed_time = time.time() - st.session_state.assessment_start_time
        remaining_time = config['time_limit'] * 60 - elapsed_time
        
        if remaining_time > 0:
            minutes = int(remaining_time // 60)
            seconds = int(remaining_time % 60)
            st.write(f"⏰ 剩余时间：{minutes:02d}:{seconds:02d}")
        else:
            st.error("⏰ 时间已到！")
            st.session_state.assessment_mode = 'result'
            st.rerun()
    
    with col3:
        if st.button("⏸️ 暂停测评"):
            st.warning("测评已暂停，点击继续按钮恢复")
    
    # 题目数据
    questions = generate_sample_questions(config)
    
    if current_q < len(questions):
        question = questions[current_q]
        
        # 转换题目格式以适配新组件
        formatted_question = {
            'id': current_q + 1,
            'content': question['question'],
            'type': 'choice' if question['type'] == 'multiple_choice' else 
                   ('judgment' if question['type'] == 'true_false' else 'text'),
            'options': question.get('options', []),
            'difficulty': question['difficulty'],
            'subject': question['subject']
        }
        
        # 自定义处理函数
        def handle_prev():
            if current_q > 0:
                st.session_state.current_question -= 1
                st.rerun()
        
        def handle_next(answer):
            # 保存答案
            if len(st.session_state.assessment_answers) <= current_q:
                st.session_state.assessment_answers.append(answer)
            else:
                st.session_state.assessment_answers[current_q] = answer
            
            if current_q < config['question_count'] - 1:
                st.session_state.current_question += 1
                st.rerun()
            else:
                st.session_state.assessment_mode = 'result'
                st.rerun()
        
        def handle_submit(answer):
            # 测评模式下不需要诊断，直接进入下一题
            handle_next(answer)
        
        # 使用新的做题组件
        st.markdown("---")
        st.subheader(f"第 {current_q + 1} 题")
        st.markdown(f"**📚 科目：** {question['subject']}")
        st.markdown(f"**🎯 难度：** {question['difficulty']}")
        
        render_question_with_navigation(
            question=formatted_question,
            api_service=st.session_state.api_service,
            user_id=st.session_state.user_id,
            current_index=current_q,
            total_questions=config['question_count'],
            key_suffix="assessment",
            on_submit=handle_submit,
            on_next=handle_next,
            on_prev=handle_prev if current_q > 0 else None,
            show_diagnosis=False,  # 测评模式不显示诊断
            submit_text="下一题" if current_q < config['question_count'] - 1 else "完成测评",
            prev_text="上一题"
        )

def render_assessment_result():
    """渲染测评结果页面"""
    st.subheader("📊 测评结果")
    
    config = st.session_state.assessment_config
    answers = st.session_state.assessment_answers
    
    # 计算测评用时
    if st.session_state.assessment_start_time:
        total_time = time.time() - st.session_state.assessment_start_time
        minutes = int(total_time // 60)
        seconds = int(total_time % 60)
        time_used = f"{minutes}分{seconds}秒"
    else:
        time_used = "未知"
    
    # 评分计算
    score = random.randint(70, 95)
    accuracy = random.randint(65, 90)
    
    # 结果概览
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("总分", f"{score}分", delta=f"+{score-80}")
    
    with col2:
        st.metric("正确率", f"{accuracy}%", delta=f"+{accuracy-75}%")
    
    with col3:
        st.metric("用时", time_used)
    
    with col4:
        st.metric("完成题数", f"{len(answers)}/{config['question_count']}")
    
    # 详细分析
    st.markdown("---")
    
    col_left, col_right = st.columns([2, 1])
    
    with col_left:
        st.subheader("📈 能力分析")
        
        # 各维度能力评估
        abilities = {
            "基础知识掌握": random.randint(70, 95),
            "逻辑推理能力": random.randint(65, 90),
            "问题解决能力": random.randint(75, 92),
            "知识应用能力": random.randint(68, 88),
            "创新思维能力": random.randint(60, 85)
        }
        
        for ability, score in abilities.items():
            st.write(f"**{ability}：** {score}分")
            st.progress(score / 100)
        
        # 优势与不足
        st.markdown("---")
        st.subheader("💪 优势与不足")
        
        # 找出最高和最低分
        max_ability = max(abilities.items(), key=lambda x: x[1])
        min_ability = min(abilities.items(), key=lambda x: x[1])
        
        st.success(f"✅ **优势领域：** {max_ability[0]}（{max_ability[1]}分）")
        st.error(f"⚠️ **待提升：** {min_ability[0]}（{min_ability[1]}分）")
        
        # 学习建议
        st.markdown("---")
        st.subheader("💡 学习建议")
        
        suggestions = [
            f"继续保持{max_ability[0]}方面的优势，可以尝试更高难度的挑战",
            f"重点加强{min_ability[0]}的训练，建议多做相关练习",
            "保持规律的学习节奏，定期进行自我测评",
            "可以尝试与同学讨论，互相学习提高"
        ]
        
        for i, suggestion in enumerate(suggestions, 1):
            st.write(f"{i}. {suggestion}")
    
    with col_right:
        st.subheader("🎯 等级评定")
        
        # 根据分数确定等级
        if score >= 90:
            level = "优秀"
            level_color = "🟢"
        elif score >= 80:
            level = "良好"
            level_color = "🔵"
        elif score >= 70:
            level = "中等"
            level_color = "🟡"
        else:
            level = "待提升"
            level_color = "🔴"
        
        st.markdown(f"### {level_color} {level}")
        st.markdown(f"**当前水平：** {score}分")
        
        # 排名信息
        st.markdown("---")
        st.subheader("📊 排名信息")
        
        percentile = random.randint(60, 95)
        st.write(f"超过了 {percentile}% 的用户")
        
        # 历史对比
        st.markdown("---")
        st.subheader("📈 历史对比")
        
        # 历史分数
        history_scores = [75, 78, 82, 85, score]
        st.line_chart(history_scores)
        
        improvement = score - history_scores[-2] if len(history_scores) > 1 else 0
        if improvement > 0:
            st.success(f"📈 比上次提升了 {improvement} 分！")
        elif improvement < 0:
            st.warning(f"📉 比上次下降了 {abs(improvement)} 分")
        else:
            st.info("📊 与上次持平")
    
    # 操作按钮
    st.markdown("---")
    col_btn1, col_btn2, col_btn3 = st.columns(3)
    
    with col_btn1:
        if st.button("🔄 重新测评", use_container_width=True):
            st.session_state.assessment_mode = 'setup'
            st.session_state.current_question = 0
            st.session_state.assessment_answers = []
            st.session_state.assessment_start_time = None
            st.rerun()
    
    with col_btn2:
        if st.button("📄 下载报告", use_container_width=True):
            st.success("测评报告已生成！")
    
    with col_btn3:
        if st.button("📚 针对性练习", use_container_width=True):
            st.info("正在为您推荐针对性练习...")

def generate_sample_questions(config):
    """生成示例题目"""
    questions = []
    
    # 根据配置生成不同类型的题目
    for i in range(config['question_count']):
        if config['type'] == "单科专项测评" and config['subject']:
            subject = config['subject']
        else:
            subject = random.choice(["数学", "语文", "英语", "物理", "化学"])
        
        question_types = ['multiple_choice', 'true_false', 'text_input']
        q_type = random.choice(question_types)
        
        if q_type == 'multiple_choice':
            question = {
                'type': 'multiple_choice',
                'subject': subject,
                'difficulty': config['difficulty'],
                'question': f"这是第{i+1}道{subject}选择题，请选择正确答案。",
                'options': ['A. 选项A', 'B. 选项B', 'C. 选项C', 'D. 选项D'],
                'correct_answer': 'A. 选项A'
            }
        elif q_type == 'true_false':
            question = {
                'type': 'true_false',
                'subject': subject,
                'difficulty': config['difficulty'],
                'question': f"这是第{i+1}道{subject}判断题，请判断正误。",
                'correct_answer': '正确'
            }
        else:
            question = {
                'type': 'text_input',
                'subject': subject,
                'difficulty': config['difficulty'],
                'question': f"这是第{i+1}道{subject}简答题，请简要回答。",
                'correct_answer': '示例答案'
            }
        
        questions.append(question)
    
    return questions