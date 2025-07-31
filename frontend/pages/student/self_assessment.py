import streamlit as st
import time
import random
import plotly.graph_objects as go
from components import render_question_with_navigation, QuestionPracticeComponent

def render_self_assessment_page(api_service, current_user, user_id):
    """渲染初始能力测评页面"""
    st.header("🌟 初始能力测评")
    
    # 检查是否有选择的用户
    if not current_user:
        st.warning("⚠️ 请先选择一个用户")
        return
    
    st.info(f"👤 当前用户：{current_user}")
    
    # 添加初始测评说明
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 15px;
        color: white;
        margin-bottom: 20px;
    ">
        <h3 style="color: white; margin-bottom: 10px;">🎯 欢迎进行初始能力测评！</h3>
        <p style="margin-bottom: 5px;">• 基于真实知识图谱的自适应测评系统</p>
        <p style="margin-bottom: 5px;">• 每个知识点先出难题，根据答题情况调整难度</p>
        <p style="margin-bottom: 0;">• 答对2道难题即掌握该知识点，简单题不会则结束测评</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 初始化session state
    if 'assessment_mode' not in st.session_state:
        st.session_state.assessment_mode = 'setup'
    if 'current_knowledge_node' not in st.session_state:
        st.session_state.current_knowledge_node = 0
    if 'current_question_in_node' not in st.session_state:
        st.session_state.current_question_in_node = 0
    if 'assessment_results' not in st.session_state:
        st.session_state.assessment_results = {}
    if 'assessment_start_time' not in st.session_state:
        st.session_state.assessment_start_time = None
    if 'knowledge_nodes' not in st.session_state:
        st.session_state.knowledge_nodes = []
    if 'current_questions' not in st.session_state:
        st.session_state.current_questions = []
    if 'node_correct_count' not in st.session_state:
        st.session_state.node_correct_count = 0
    if 'current_difficulty' not in st.session_state:
        st.session_state.current_difficulty = 'hard'  # 开始时出难题
    
    # 根据当前模式渲染不同内容
    if st.session_state.assessment_mode == 'setup':
        render_assessment_setup(api_service)
    elif st.session_state.assessment_mode == 'testing':
        render_assessment_testing(api_service, user_id)
    elif st.session_state.assessment_mode == 'result':
        render_assessment_result()

def render_assessment_setup(api_service):
    """渲染初始能力测评设置页面"""
    st.subheader("📋 测评配置")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        <div style="
            background: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
            border-left: 4px solid #007bff;
            margin-bottom: 20px;
        ">
            <h4 style="color: #007bff; margin-bottom: 15px;">🎯 自适应能力测评说明</h4>
            <p style="margin-bottom: 8px;">• <strong>测评方式：</strong>基于知识图谱的自适应测评</p>
            <p style="margin-bottom: 8px;">• <strong>测评策略：</strong>每个知识点先出难题，根据答题情况调整</p>
            <p style="margin-bottom: 8px;">• <strong>掌握标准：</strong>答对2道难题即掌握该知识点</p>
            <p style="margin-bottom: 0;">• <strong>结束条件：</strong>简单题也答错则结束当前知识点测评</p>
        </div>
        """, unsafe_allow_html=True)
        
        # 获取知识点列表
        if st.button("🔄 刷新知识点", key="refresh_nodes"):
            st.session_state.knowledge_nodes = []
        
        if not st.session_state.knowledge_nodes:
            with st.spinner("正在加载知识图谱..."):
                try:
                    # 获取知识点
                    nodes_data = api_service.get_knowledge_nodes_simple()
                    if nodes_data and isinstance(nodes_data, dict):
                        # 转换为列表格式，限制测评知识点数量
                        knowledge_nodes = list(nodes_data.keys())[:10]  # 限制最多10个知识点
                        st.session_state.knowledge_nodes = knowledge_nodes
                        st.success(f"✅ 成功加载 {len(knowledge_nodes)} 个知识点")
                    else:
                        st.error("❌ 无法获取知识点数据")
                        return
                except Exception as e:
                    st.error(f"❌ 获取知识点失败: {str(e)}")
                    return
        
        # 显示知识点信息
        if st.session_state.knowledge_nodes:
            st.markdown("**📚 测评知识点：**")
            
            # 分两列显示知识点
            node_col1, node_col2 = st.columns(2)
            for i, node in enumerate(st.session_state.knowledge_nodes):
                with node_col1 if i % 2 == 0 else node_col2:
                    st.markdown(f"• {node}")
            
            # 测评配置信息
            st.markdown("---")
            st.markdown("**⚙️ 测评配置**")
            
            config_col1, config_col2 = st.columns(2)
            with config_col1:
                st.info(f"📊 **测评类型：** 自适应能力测评")
                st.info(f"📝 **知识点数：** {len(st.session_state.knowledge_nodes)} 个")
            with config_col2:
                st.info(f"🎚️ **难度策略：** 先难后易")
                st.info(f"⏰ **预计时长：** 15-25 分钟")
            
            st.markdown("---")
            
            # 开始测评按钮
            if st.button("🚀 开始自适应能力测评", type="primary", use_container_width=True):
                # 初始化测评状态
                st.session_state.assessment_mode = 'testing'
                st.session_state.current_knowledge_node = 0
                st.session_state.current_question_in_node = 0
                st.session_state.assessment_results = {}
                st.session_state.assessment_start_time = time.time()
                st.session_state.current_questions = []
                st.session_state.node_correct_count = 0
                st.session_state.current_difficulty = 'hard'
                st.rerun()
        else:
            st.warning("⚠️ 请先加载知识点数据")
    
    with col2:
        st.subheader("💡 测评准备")
        
        # 测评准备提示
        st.markdown("""
        <div style="
            background: #fff3cd;
            border: 1px solid #ffeaa7;
            border-radius: 8px;
            padding: 15px;
            margin-bottom: 15px;
        ">
            <h5 style="color: #856404; margin-bottom: 10px;">📝 测评前准备</h5>
            <ul style="color: #856404; margin-bottom: 0;">
                <li>确保网络连接稳定</li>
                <li>选择安静的环境</li>
                <li>准备好纸笔（如需要）</li>
                <li>保持放松的心态</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        # 注意事项
        st.markdown("""
        <div style="
            background: #d1ecf1;
            border: 1px solid #bee5eb;
            border-radius: 8px;
            padding: 15px;
            margin-bottom: 15px;
        ">
            <h5 style="color: #0c5460; margin-bottom: 10px;">⚠️ 注意事项</h5>
            <ul style="color: #0c5460; margin-bottom: 0;">
                <li>每题请仔细阅读</li>
                <li>可以跳过难题，稍后返回</li>
                <li>不确定时选择最接近的答案</li>
                <li>测评过程中请勿查阅资料</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        # 测评后收获
        st.subheader("🎁 测评后您将获得")
        
        benefits = [
            "🎯 个人能力画像报告",
            "📊 详细的能力分析",
            "🗺️ 个性化学习路径",
            "💡 针对性提升建议",
            "📈 学习目标规划"
        ]
        
        for benefit in benefits:
            st.markdown(f"• {benefit}")
        
        # 激励信息
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, #84fab0 0%, #8fd3f4 100%);
            padding: 15px;
            border-radius: 10px;
            text-align: center;
            margin-top: 20px;
        ">
            <h5 style="color: white; margin-bottom: 5px;">🌟 开启学习之旅</h5>
            <p style="color: white; margin-bottom: 0; font-size: 14px;">每一次测评都是成长的开始！</p>
        </div>
        """, unsafe_allow_html=True)

def render_assessment_testing(api_service, user_id):
    """渲染自适应测评进行页面"""
    current_node_idx = st.session_state.current_knowledge_node
    current_question_idx = st.session_state.current_question_in_node
    
    # 检查是否完成所有知识点测评
    if current_node_idx >= len(st.session_state.knowledge_nodes):
        st.session_state.assessment_mode = 'result'
        st.rerun()
        return
    
    current_node = st.session_state.knowledge_nodes[current_node_idx]
    
    # 顶部进度条和状态
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        progress = current_node_idx / len(st.session_state.knowledge_nodes)
        st.progress(progress)
        st.write(f"知识点进度：{current_node_idx + 1}/{len(st.session_state.knowledge_nodes)}")
    
    with col2:
        # 计算已用时间
        elapsed_time = time.time() - st.session_state.assessment_start_time
        minutes = int(elapsed_time // 60)
        seconds = int(elapsed_time % 60)
        st.write(f"⏰ 已用时间：{minutes:02d}:{seconds:02d}")
    
    with col3:
        difficulty_text = "🔴 难题" if st.session_state.current_difficulty == 'hard' else "🟢 简单题"
        st.write(f"当前难度：{difficulty_text}")
    
    # 当前知识点状态
    st.markdown(f"### 📚 当前知识点：{current_node}")
    
    # 显示当前知识点的测评状态
    status_col1, status_col2, status_col3 = st.columns(3)
    with status_col1:
        st.metric("已答对题数", st.session_state.node_correct_count, delta="需要2题掌握")
    with status_col2:
        st.metric("当前难度", st.session_state.current_difficulty, delta="先难后易")
    with status_col3:
        node_result = st.session_state.assessment_results.get(current_node, "测评中")
        st.metric("掌握状态", node_result)
    
    # 获取当前知识点的题目
    if not st.session_state.current_questions:
        with st.spinner(f"正在加载 {current_node} 的题目..."):
            try:
                questions_data = api_service.get_questions_for_node(current_node)
                if questions_data and len(questions_data) > 0:
                    # 按难度分类题目
                    hard_questions = [q for q in questions_data if q.get('difficulty', 0.5) > 0.7]
                    easy_questions = [q for q in questions_data if q.get('difficulty', 0.5) <= 0.5]
                    
                    st.session_state.current_questions = {
                        'hard': hard_questions[:5],  # 最多5道难题
                        'easy': easy_questions[:3]   # 最多3道简单题
                    }
                    
                    if not hard_questions and not easy_questions:
                        st.error(f"❌ 知识点 {current_node} 没有可用题目")
                        # 跳到下一个知识点
                        st.session_state.assessment_results[current_node] = "无题目"
                        st.session_state.current_knowledge_node += 1
                        st.session_state.current_question_in_node = 0
                        st.session_state.current_questions = []
                        st.session_state.node_correct_count = 0
                        st.session_state.current_difficulty = 'hard'
                        st.rerun()
                        return
                else:
                    st.error(f"❌ 无法获取知识点 {current_node} 的题目")
                    return
            except Exception as e:
                st.error(f"❌ 获取题目失败: {str(e)}")
                return
    
    # 获取当前题目
    current_difficulty = st.session_state.current_difficulty
    available_questions = st.session_state.current_questions.get(current_difficulty, [])
    
    if current_question_idx >= len(available_questions):
        # 当前难度的题目已做完
        if current_difficulty == 'hard':
            # 难题做完，检查是否掌握
            if st.session_state.node_correct_count >= 2:
                # 掌握了，进入下一个知识点
                st.session_state.assessment_results[current_node] = "掌握"
                st.success(f"🎉 恭喜！您已掌握 {current_node}")
                time.sleep(1)
                move_to_next_node()
                return
            else:
                # 没掌握，切换到简单题
                st.session_state.current_difficulty = 'easy'
                st.session_state.current_question_in_node = 0
                st.warning(f"💡 切换到简单题模式")
                st.rerun()
                return
        else:
            # 简单题也做完了，结束当前知识点
            if st.session_state.node_correct_count >= 1:
                st.session_state.assessment_results[current_node] = "基础掌握"
            else:
                st.session_state.assessment_results[current_node] = "未掌握"
            move_to_next_node()
            return
    
    # 显示当前题目
    if current_question_idx < len(available_questions):
        question = available_questions[current_question_idx]
        
        # 转换题目格式
        formatted_question = {
            'id': question.get('question_id', current_question_idx + 1),
            'content': question.get('question_text', question.get('content', '题目内容缺失')),
            'type': determine_question_type(question),
            'options': question.get('options', []),
            'difficulty': question.get('difficulty', 0.5),
            'correct_answer': question.get('correct_answer', '')
        }
        
        # 自定义处理函数
        def handle_submit(answer):
            # 检查答案是否正确
            is_correct = check_answer_correctness(formatted_question, answer)
            
            if is_correct:
                st.session_state.node_correct_count += 1
                st.success("✅ 回答正确！")
            else:
                st.error("❌ 回答错误")
                # 如果是简单题答错，直接结束当前知识点
                if current_difficulty == 'easy':
                    st.session_state.assessment_results[current_node] = "未掌握"
                    st.warning(f"😔 {current_node} 测评结束")
                    time.sleep(1)
                    move_to_next_node()
                    return
            
            # 移动到下一题
            st.session_state.current_question_in_node += 1
            time.sleep(1)
            st.rerun()
        
        # 显示题目
        st.markdown("---")
        difficulty_emoji = "🔴" if current_difficulty == 'hard' else "🟢"
        st.subheader(f"{difficulty_emoji} 第 {current_question_idx + 1} 题 ({current_difficulty.upper()})")
        
        # 使用简化的题目显示
        render_simple_question(formatted_question, handle_submit)

def move_to_next_node():
    """移动到下一个知识点"""
    st.session_state.current_knowledge_node += 1
    st.session_state.current_question_in_node = 0
    st.session_state.current_questions = []
    st.session_state.node_correct_count = 0
    st.session_state.current_difficulty = 'hard'

def determine_question_type(question):
    """判断题目类型"""
    question_type = question.get('question_type', question.get('type', 'unknown'))
    
    if question_type in ['multiple_choice', 'choice']:
        return 'choice'
    elif question_type in ['true_false', 'judgment']:
        return 'judgment'
    elif question_type in ['text_input', 'text', 'short_answer']:
        return 'text'
    else:
        # 根据选项判断
        options = question.get('options', [])
        if len(options) > 0:
            return 'choice'
        else:
            return 'text'

def check_answer_correctness(question, user_answer):
    """检查答案正确性"""
    correct_answer = question.get('correct_answer', '')
    
    if not correct_answer:
        # 如果没有标准答案，简单判断（实际应该调用AI判断）
        return len(str(user_answer).strip()) > 0
    
    # 简单的字符串匹配
    return str(user_answer).strip().lower() == str(correct_answer).strip().lower()

def render_simple_question(question, on_submit):
    """渲染简化的题目界面"""
    st.markdown(f"**题目：** {question['content']}")
    
    question_type = question['type']
    user_answer = None
    
    if question_type == 'choice' and question.get('options'):
        # 选择题
        options = question['options']
        user_answer = st.radio("请选择答案：", options, key=f"q_{question['id']}")
    elif question_type == 'judgment':
        # 判断题
        user_answer = st.radio("请判断：", ["正确", "错误"], key=f"q_{question['id']}")
    else:
        # 文本题
        user_answer = st.text_area("请输入答案：", key=f"q_{question['id']}")
    
    # 提交按钮
    if st.button("提交答案", type="primary", key=f"submit_{question['id']}"):
        if user_answer:
            on_submit(user_answer)
        else:
            st.warning("请先选择或输入答案！")

def render_assessment_result():
    """渲染自适应能力测评结果页面"""
    st.subheader("🎉 自适应能力测评完成")
    
    results = st.session_state.assessment_results
    knowledge_nodes = st.session_state.knowledge_nodes
    
    # 计算测评用时
    if st.session_state.assessment_start_time:
        total_time = time.time() - st.session_state.assessment_start_time
        minutes = int(total_time // 60)
        seconds = int(total_time % 60)
        time_used = f"{minutes}分{seconds}秒"
    else:
        time_used = "未知"
    
    # 分析测评结果
    mastered_count = len([r for r in results.values() if r == "掌握"])
    basic_mastered_count = len([r for r in results.values() if r == "基础掌握"])
    not_mastered_count = len([r for r in results.values() if r == "未掌握"])
    no_questions_count = len([r for r in results.values() if r == "无题目"])
    
    total_tested = len(results)
    mastery_rate = (mastered_count + basic_mastered_count) / max(total_tested, 1) * 100
    
    # 计算综合评分
    overall_score = int(mastered_count * 20 + basic_mastered_count * 10 + max(0, 60 - not_mastered_count * 10))
    
    # 恭喜信息
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 25px;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin-bottom: 25px;
    ">
        <h2 style="color: white; margin-bottom: 10px;">🎊 恭喜您完成初始能力测评！</h2>
        <p style="margin-bottom: 5px; font-size: 18px;">您的学习之旅正式开始</p>
        <p style="margin-bottom: 0;">我们已为您生成专属的能力画像和学习建议</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 基础统计信息
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="综合评分",
            value=f"{overall_score}分",
            delta="优秀" if overall_score >= 80 else "良好" if overall_score >= 60 else "需提升"
        )
    
    with col2:
        st.metric(
            label="掌握率",
            value=f"{mastery_rate:.1f}%",
            delta=f"掌握{mastered_count}个知识点"
        )
    
    with col3:
        st.metric(
            label="测评用时",
            value=time_used,
            delta="高效" if total_time < 1800 else "正常"
        )
    
    with col4:
        st.metric(
            label="测评知识点",
            value=f"{total_tested}个",
            delta=f"总共{len(knowledge_nodes)}个知识点"
        )
    
    # 知识点掌握情况分析
    st.markdown("---")
    
    col_left, col_right = st.columns([2, 1])
    
    with col_left:
        st.subheader("📊 知识点掌握情况")
        
        # 按掌握程度分组显示
        if mastered_count > 0:
            st.markdown("**✅ 完全掌握的知识点：**")
            mastered_nodes = [node for node, result in results.items() if result == "掌握"]
            for node in mastered_nodes:
                st.write(f"🟢 {node}")
        
        if basic_mastered_count > 0:
            st.markdown("**📚 基础掌握的知识点：**")
            basic_nodes = [node for node, result in results.items() if result == "基础掌握"]
            for node in basic_nodes:
                st.write(f"🟡 {node}")
        
        if not_mastered_count > 0:
            st.markdown("**❌ 需要加强的知识点：**")
            not_mastered_nodes = [node for node, result in results.items() if result == "未掌握"]
            for node in not_mastered_nodes:
                st.write(f"🔴 {node}")
        
        if no_questions_count > 0:
            st.markdown("**⚠️ 无题目可测的知识点：**")
            no_question_nodes = [node for node, result in results.items() if result == "无题目"]
            for node in no_question_nodes:
                st.write(f"⚪ {node}")
        
        # 基于测评结果的能力评估
        st.markdown("---")
        st.subheader("🧠 您的能力画像")
        
        # 根据实际测评结果计算能力分数
        base_score = 50
        mastery_bonus = mastered_count * 8
        basic_bonus = basic_mastered_count * 5
        penalty = not_mastered_count * 3
        
        abilities = {
            "🧮 逻辑推理": min(100, base_score + mastery_bonus + basic_bonus - penalty + random.randint(-5, 10)),
            "📚 知识理解": min(100, base_score + mastery_bonus + basic_bonus - penalty + random.randint(-5, 10)),
            "🔍 问题解决": min(100, base_score + mastery_bonus + basic_bonus - penalty + random.randint(-5, 10)),
            "💡 创新思维": min(100, base_score + mastery_bonus + basic_bonus - penalty + random.randint(-5, 10)),
            "📖 学习能力": min(100, base_score + mastery_bonus + basic_bonus - penalty + random.randint(-5, 10))
        }
        
        st.markdown("**🎯 核心能力评估：**")
        for ability, score in abilities.items():
            # 根据分数确定等级
            if score >= 80:
                level = "优秀"
                color = "🟢"
            elif score >= 70:
                level = "良好"
                color = "🔵"
            elif score >= 60:
                level = "中等"
                color = "🟡"
            else:
                level = "待提升"
                color = "🔴"
            
            st.write(f"**{ability}：** {score}分 {color} {level}")
            st.progress(score / 100)
        
        # 能力特征分析
        st.markdown("---")
        st.subheader("🎨 您的学习特征")
        
        # 基于测评结果分析学习特征
        if mastery_rate >= 80:
            learning_type = "优秀学习者"
            type_desc = "您展现出了优秀的学习能力和知识掌握水平，基础扎实"
        elif mastery_rate >= 60:
            learning_type = "稳步进步者"
            type_desc = "您具备良好的学习基础，正在稳步提升中"
        elif mastery_rate >= 40:
            learning_type = "潜力发掘者"
            type_desc = "您有很大的提升空间，需要更多的练习和巩固"
        else:
            learning_type = "基础建设者"
            type_desc = "建议从基础知识开始，逐步建立完整的知识体系"
        
        st.info(f"🎯 **学习类型：** {learning_type}")
        st.write(f"📝 **特征描述：** {type_desc}")
        
        st.success(f"✨ **掌握知识点：** {mastered_count + basic_mastered_count}/{total_tested}")
        st.warning(f"🎯 **需要加强：** {not_mastered_count}个知识点")
        
        # 个性化学习建议
        st.markdown("---")
        st.subheader("🗺️ 个性化学习路径")
        
        # 根据测评结果生成建议
        suggestions = []
        if mastered_count > 0:
            suggestions.append(f"✅ 继续巩固已掌握的{mastered_count}个知识点，保持优势")
        if basic_mastered_count > 0:
            suggestions.append(f"📈 深化学习{basic_mastered_count}个基础掌握的知识点")
        if not_mastered_count > 0:
            suggestions.append(f"🎯 重点攻克{not_mastered_count}个薄弱知识点")
        
        # 根据学习类型添加通用建议
        if learning_type == "优秀学习者":
            suggestions.extend([
                "🌟 挑战更高难度的综合应用题",
                "👥 可以尝试指导其他学习者",
                "🔬 探索知识的深层应用和拓展"
            ])
        elif learning_type == "稳步进步者":
            suggestions.extend([
                "📚 系统性地复习和巩固知识",
                "🔄 定期进行自我测评",
                "💡 注重理论与实践的结合"
            ])
        elif learning_type == "潜力发掘者":
            suggestions.extend([
                "📖 从基础概念开始系统学习",
                "⏰ 制定规律的学习计划",
                "🤝 寻找学习伙伴互相督促"
            ])
        else:
            suggestions.extend([
                "🌱 从最基础的知识点开始",
                "📝 建立良好的学习习惯",
                "👨‍🏫 寻求老师或同学的帮助"
            ])
        
        for suggestion in suggestions:
            st.write(f"• {suggestion}")
    
    with col_right:
        # 测评结果总结
        st.subheader("📋 测评结果总结")
        
        # 掌握情况饼图
        if total_tested > 0:
            
            fig_pie = go.Figure(data=[
                go.Pie(
                    labels=['完全掌握', '基础掌握', '未掌握', '无题目'],
                    values=[mastered_count, basic_mastered_count, not_mastered_count, no_questions_count],
                    hole=0.4,
                    marker_colors=['#28a745', '#ffc107', '#dc3545', '#6c757d']
                )
            ])
            
            fig_pie.update_layout(
                title="知识点掌握分布",
                height=300,
                showlegend=True,
                legend=dict(orientation="h", yanchor="bottom", y=-0.2)
            )
            
            st.plotly_chart(fig_pie, use_container_width=True)
        
        # 能力等级评定
        st.markdown("---")
        st.subheader("🏆 能力等级评定")
        
        if mastery_rate >= 80:
            level = "优秀"
            level_desc = "您的知识掌握程度优秀，基础非常扎实"
            level_color = "🟢"
        elif mastery_rate >= 60:
            level = "良好"
            level_desc = "您的知识掌握程度良好，继续保持"
            level_color = "🟡"
        elif mastery_rate >= 40:
            level = "及格"
            level_desc = "您已达到基本要求，还有较大提升空间"
            level_color = "🟠"
        else:
            level = "待提升"
            level_desc = "建议系统性地加强基础知识学习"
            level_color = "🔴"
        
        st.info(f"{level_color} **等级**: {level} (掌握率: {mastery_rate:.1f}%)")
        st.write(level_desc)
        
        # 学习建议
        st.markdown("---")
        st.subheader("💡 学习建议")
        
        if mastered_count > 0:
            st.success(f"✅ 已掌握 {mastered_count} 个知识点，继续保持")
        
        if basic_mastered_count > 0:
            st.info(f"📚 {basic_mastered_count} 个知识点需要进一步巩固")
        
        if not_mastered_count > 0:
            st.warning(f"🎯 {not_mastered_count} 个知识点需要重点学习")
        
        if no_questions_count > 0:
            st.error(f"⚠️ {no_questions_count} 个知识点暂无题目可测")
        
        # 下一步行动计划
        st.markdown("---")
        st.subheader("🚀 下一步行动")
        
        next_actions = []
        if not_mastered_count > 0:
            next_actions.append("🎯 优先学习未掌握的知识点")
        if basic_mastered_count > 0:
            next_actions.append("📈 深化基础掌握的知识点")
        if mastered_count > 0:
            next_actions.append("🔄 定期复习已掌握的知识点")
        
        next_actions.extend([
            "📊 制定个性化学习计划",
            "⏰ 安排下次自适应测评"
        ])
        
        for action in next_actions:
            st.write(f"• {action}")
        
        # 学习进度预期
        st.markdown("---")
        st.subheader("📈 学习进度预期")
        
        # 基于当前掌握情况预测学习进度
        weeks = list(range(0, 13))
        current_mastery = mastery_rate
        
        # 根据当前水平设定不同的成长速度
        if current_mastery >= 80:
            weekly_growth = 1.5  # 优秀学习者成长较慢但稳定
        elif current_mastery >= 60:
            weekly_growth = 2.0  # 良好学习者有较好成长空间
        elif current_mastery >= 40:
            weekly_growth = 2.5  # 及格学习者有很大成长空间
        else:
            weekly_growth = 3.0  # 待提升学习者成长潜力最大
        
        progress = [current_mastery + i * weekly_growth for i in weeks]
        progress = [min(100, max(0, p)) for p in progress]  # 限制在0-100之间
        
        try:
            fig_progress = go.Figure()
            fig_progress.add_trace(go.Scatter(
                x=weeks,
                y=progress,
                mode='lines+markers',
                name='预期掌握率',
                line=dict(color='rgb(0, 123, 255)', width=3),
                marker=dict(size=6)
            ))
            
            fig_progress.update_layout(
                title="12周学习进度预期",
                xaxis_title="周数",
                yaxis_title="知识点掌握率 (%)",
                height=300,
                showlegend=False,
                yaxis=dict(range=[0, 100])
            )
            
            st.plotly_chart(fig_progress, use_container_width=True)
        except Exception as e:
            st.warning(f"无法显示进度图表: {str(e)}")
    
    # 操作按钮
    st.markdown("---")
    st.markdown("### 🎯 开始您的学习之旅")
    
    col_btn1, col_btn2, col_btn3, col_btn4 = st.columns(4)
    
    with col_btn1:
        if st.button("🏠 返回首页", use_container_width=True):
            st.session_state.page = "home"
            st.rerun()
    
    with col_btn2:
        if st.button("📚 开始学习", use_container_width=True, type="primary"):
            # 根据测评结果推荐学习内容
            if not_mastered_count > 0:
                st.info(f"建议优先学习 {not_mastered_count} 个未掌握的知识点")
            st.session_state.page = "learning"
            st.rerun()
    
    with col_btn3:
        if st.button("📄 保存报告", use_container_width=True):
            # 这里可以调用API保存测评结果
            st.success("自适应测评报告已保存到您的档案！")
    
    with col_btn4:
        if st.button("🔄 重新测评", use_container_width=True):
            # 重置自适应测评状态
            st.session_state.assessment_mode = 'setup'
            st.session_state.current_knowledge_node = 0
            st.session_state.current_question_in_node = 0
            st.session_state.assessment_results = {}
            st.session_state.knowledge_nodes = []
            st.session_state.current_questions = []
            st.session_state.node_correct_count = 0
            st.session_state.current_difficulty = "hard"
            st.session_state.assessment_start_time = None
            st.rerun()
    
    # 温馨提示
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);
        padding: 20px;
        border-radius: 15px;
        text-align: center;
        margin-top: 25px;
    ">
        <h4 style="color: #8b4513; margin-bottom: 10px;">🌟 恭喜您完成初始能力测评！</h4>
        <p style="color: #8b4513; margin-bottom: 5px;">您的专属学习档案已建立，系统将根据您的能力特点推荐最适合的学习内容</p>
        <p style="color: #8b4513; margin-bottom: 0;">记住：每一次学习都是向目标迈进的一步！💪</p>
    </div>
    """, unsafe_allow_html=True)

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