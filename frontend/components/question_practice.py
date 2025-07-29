#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
通用做题组件
封装所有做题相关的UI和逻辑，提供统一的做题界面
"""

import streamlit as st
import random
from typing import Dict, List, Any, Optional, Callable

class QuestionPracticeComponent:
    """通用做题组件类"""
    
    def __init__(self, api_service, user_id: str):
        self.api_service = api_service
        self.user_id = user_id
        
    def render_question_display(self, question: Dict[str, Any], 
                               question_index: int = 0, 
                               total_questions: int = 1,
                               show_difficulty: bool = True,
                               show_subject: bool = False) -> None:
        """渲染题目显示区域
        
        Args:
            question: 题目数据字典
            question_index: 当前题目索引
            total_questions: 总题目数
            show_difficulty: 是否显示难度
            show_subject: 是否显示科目
        """
        # 题目信息展示
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.info(f"题目 {question_index + 1} / {total_questions}")
            
        with col2:
            if show_difficulty:
                difficulty = question.get('difficulty', 0.5)
                if isinstance(difficulty, str):
                    try:
                        difficulty = float(difficulty)
                    except:
                        difficulty = 0.5
                        
                if difficulty <= 0.3:
                    st.success("🟢 简单")
                elif difficulty <= 0.7:
                    st.warning("🟡 中等")
                else:
                    st.error("🔴 困难")
        
        # 显示科目信息
        if show_subject and question.get('subject'):
            st.markdown(f"**📚 科目：** {question['subject']}")
            
        # 显示题目内容
        question_text = question.get('question_text', question.get('question', ''))
        if isinstance(question_text, dict):
            question_text = str(question_text)
        elif not isinstance(question_text, str):
            question_text = str(question_text)
        
        if question_text:
            st.write(f"**❓ 题目：**")
            self._render_math_content(question_text)
        
        # 显示题目图片（如果有）
        if question.get('question_image_url'):
            try:
                image_url = question['question_image_url']
                if not image_url.startswith('http'):
                    image_url = f"http://localhost:8000{image_url}"
                st.image(image_url, caption="题目配图", use_container_width=True)
            except Exception as e:
                st.warning(f"⚠️ 无法加载图片: {str(e)}")
    
    def render_answer_input(self, question: Dict[str, Any], 
                           key_suffix: str = "",
                           height: int = 150) -> Any:
        """渲染答题输入区域
        
        Args:
            question: 题目数据
            key_suffix: 输入框key的后缀，用于区分不同场景
            height: 文本框高度
            
        Returns:
            用户输入的答案
        """
        st.write("### ✍️ 作答区域")
        
        question_type = question.get('question_type', question.get('type', 'text_input'))
        question_id = question.get('question_id', question.get('id', 'unknown'))
        
        answer_key = f"answer_{question_id}_{key_suffix}" if key_suffix else f"answer_{question_id}"
        
        if question_type == 'multiple_choice' or question_type == '选择题':
            # 选择题
            options = question.get('options', [])
            if isinstance(options, str):
                try:
                    import json
                    options = json.loads(options)
                except:
                    options = []
            
            if isinstance(options, dict):
                # 如果是字典格式 {"A": "选项A", "B": "选项B"}
                option_list = [f"{k}. {v}" for k, v in options.items()]
            elif isinstance(options, list):
                # 如果是列表格式
                if options and not options[0].startswith(('A.', 'B.', 'C.', 'D.')):
                    option_list = [f"{chr(65+i)}. {option}" for i, option in enumerate(options)]
                else:
                    option_list = options
            else:
                option_list = []
            
            if option_list:
                answer = st.radio(
                    "请选择答案：",
                    option_list,
                    key=answer_key
                )
            else:
                st.warning("⚠️ 选择题缺少选项")
                answer = st.text_input("请输入答案：", key=answer_key)
                
        elif question_type == 'true_false' or question_type == '判断题':
            # 判断题
            answer = st.radio(
                "请判断正误：",
                ["正确", "错误"],
                key=answer_key
            )
        else:
            # 文本输入题（填空题、解答题等）
            answer = st.text_area(
                "请在此处输入你的解题过程和答案：",
                height=height,
                key=answer_key
            )
        
        return answer
    
    def render_action_buttons(self, 
                             question: Dict[str, Any],
                             answer: Any,
                             key_suffix: str = "",
                             show_submit: bool = True,
                             show_hint: bool = True,
                             show_navigation: bool = False,
                             current_index: int = 0,
                             total_questions: int = 1,
                             on_submit: Optional[Callable] = None,
                             on_next: Optional[Callable] = None,
                             on_prev: Optional[Callable] = None,
                             on_hint: Optional[Callable] = None) -> Dict[str, bool]:
        """渲染操作按钮区域
        
        Args:
            question: 题目数据
            answer: 用户答案
            key_suffix: 按钮key的后缀
            show_submit: 是否显示提交按钮
            show_hint: 是否显示提示按钮
            show_navigation: 是否显示导航按钮
            current_index: 当前题目索引
            total_questions: 总题目数
            on_submit: 提交回调函数
            on_next: 下一题回调函数
            on_prev: 上一题回调函数
            on_hint: 提示回调函数
            
        Returns:
            按钮点击状态字典
        """
        question_id = question.get('question_id', question.get('id', 'unknown'))
        
        # 计算需要的列数
        col_count = 0
        if show_submit: col_count += 1
        if show_hint: col_count += 1
        if show_navigation:
            if current_index > 0: col_count += 1  # 上一题
            if current_index < total_questions - 1: col_count += 1  # 下一题
        
        if col_count == 0:
            return {}
        
        # 创建列布局
        cols = st.columns(col_count)
        col_idx = 0
        
        button_states = {
            'submitted': False,
            'hint_clicked': False,
            'next_clicked': False,
            'prev_clicked': False
        }
        
        # 提交按钮
        if show_submit:
            with cols[col_idx]:
                submit_key = f"submit_{question_id}_{key_suffix}" if key_suffix else f"submit_{question_id}"
                submitted_key = f'submitted_{question_id}'
                is_submitted = st.session_state.get(submitted_key, False)
                
                # 根据提交状态显示不同的按钮文本和样式
                if is_submitted:
                    button_text = "✅ 已提交"
                    button_type = "secondary"
                    disabled = True
                else:
                    button_text = "📝 提交答案"
                    button_type = "primary"
                    disabled = False
                
                if st.button(button_text, type=button_type, key=submit_key, 
                           use_container_width=True, disabled=disabled):
                    if answer and str(answer).strip():
                        button_states['submitted'] = True
                        if on_submit:
                            on_submit(answer)
                        else:
                            self._default_submit_handler(question, answer)
                    else:
                        st.error("请先输入答案！")
            col_idx += 1
        
        # 提示按钮
        if show_hint:
            with cols[col_idx]:
                hint_key = f"hint_{question_id}_{key_suffix}" if key_suffix else f"hint_{question_id}"
                hint_state_key = f"hint_shown_{question_id}"
                
                if st.button("💡 获取提示", key=hint_key, use_container_width=True):
                    button_states['hint_clicked'] = True
                    if on_hint:
                        on_hint()
                    else:
                        # 将提示状态存储到session_state中，避免立即刷新
                        st.session_state[hint_state_key] = True
            col_idx += 1
        
        # 导航按钮
        if show_navigation:
            # 上一题按钮
            if current_index > 0:
                with cols[col_idx]:
                    prev_key = f"prev_{question_id}_{key_suffix}" if key_suffix else f"prev_{question_id}"
                    if st.button("⬅️ 上一题", key=prev_key, use_container_width=True):
                        button_states['prev_clicked'] = True
                        if on_prev:
                            on_prev()
                col_idx += 1
            
            # 下一题按钮
            if current_index < total_questions - 1:
                with cols[col_idx]:
                    next_key = f"next_{question_id}_{key_suffix}" if key_suffix else f"next_{question_id}"
                    if st.button("➡️ 下一题", key=next_key, use_container_width=True):
                        button_states['next_clicked'] = True
                        if on_next:
                            on_next()
                col_idx += 1
        
        return button_states
    
    def render_diagnosis_result(self, diagnosis_result: Dict[str, Any], 
                               show_detailed_scores: bool = True,
                               mastery_before: float = 0.0) -> None:
        """渲染诊断结果
        
        Args:
            diagnosis_result: 诊断结果数据
            show_detailed_scores: 是否显示详细评分
            mastery_before: 答题前的掌握度
        """
        st.divider()
        st.write("### 📋 诊断结果")
        
        # 获取诊断结果
        is_correct = diagnosis_result.get("is_correct", False)
        reason = diagnosis_result.get("reason", "无诊断信息")
        scores = diagnosis_result.get("scores", [])
        
        # 使用列布局显示主要诊断结果
        col_main, col_side = st.columns([3, 1])
        
        with col_main:
            # 根据正确性显示结果
            if is_correct:
                st.success("🎉 答案正确！")
                # 显示庆祝效果
                st.balloons()
            else:
                st.warning("⚠️ 答案需要改进")
                st.info("💡 **建议**: 请仔细检查解题步骤，或尝试从不同角度思考问题")
            
            # 显示详细分析
            if reason and reason != "无诊断信息":
                st.write("**📝 详细分析：**")
                st.markdown(reason)
        
        with col_side:
            # 显示掌握度提升（如果提供了之前的掌握度）
            if is_correct and mastery_before < 1.0:
                new_mastery = min(mastery_before + 0.1, 1.0)
                st.metric(
                    "掌握度提升", 
                    f"{new_mastery:.0%}", 
                    delta=f"+{(new_mastery - mastery_before):.0%}"
                )
        
        # 显示评分详情
        if show_detailed_scores and scores:
            with st.expander("📊 查看详细评分", expanded=is_correct):
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.write("### 答题表现评估")
                    
                    # 创建评分表格
                    score_data = []
                    for score_item in scores:
                        # 获取评分类别（支持中英文）
                        category_en = (score_item.get('Knowledge Mastery') or 
                                     score_item.get('Logical Reasoning') or 
                                     score_item.get('Calculation Accuracy') or 
                                     score_item.get('Behavioral Performance'))
                        category_cn = (score_item.get('知识掌握') or 
                                     score_item.get('解题逻辑') or 
                                     score_item.get('计算准确性') or 
                                     score_item.get('行为表现'))
                        
                        # 显示类别名称（优先使用中文）
                        category = category_cn or category_en or '未知类别'
                        score = score_item.get('score', 0)
                        feedback = score_item.get('feedback', '无反馈')
                        
                        score_data.append({
                            "评估维度": category, 
                            "得分": score, 
                            "反馈": feedback
                        })
                    
                    # 显示评分表格
                    if score_data:
                        st.table(score_data)
                
                with col2:
                    if score_data:
                        # 计算总分
                        total_score = sum(item["得分"] for item in score_data) / len(score_data)
                        st.metric("综合评分", f"{total_score:.1f}/1.0")
                        
                        # 根据总分给出鼓励性评语
                        if total_score >= 0.9:
                            st.success("🌟 优秀！你的解答非常出色，继续保持！")
                        elif total_score >= 0.7:
                            st.info("👍 不错！你的解答有一些亮点，还有提升空间。")
                        else:
                            st.warning("💪 加油！多加练习，你会做得更好！")
    
    def render_complete_question_interface(self, 
                                         question: Dict[str, Any],
                                         question_index: int = 0,
                                         total_questions: int = 1,
                                         key_suffix: str = "",
                                         show_difficulty: bool = True,
                                         show_subject: bool = False,
                                         show_navigation: bool = False,
                                         show_hint: bool = True,
                                         answer_height: int = 150,
                                         on_submit: Optional[Callable] = None,
                                         on_next: Optional[Callable] = None,
                                         on_prev: Optional[Callable] = None,
                                         on_hint: Optional[Callable] = None) -> Dict[str, Any]:
        """渲染完整的做题界面
        
        Args:
            question: 题目数据
            question_index: 当前题目索引
            total_questions: 总题目数
            key_suffix: 组件key后缀
            show_difficulty: 是否显示难度
            show_subject: 是否显示科目
            show_navigation: 是否显示导航按钮
            show_hint: 是否显示提示按钮
            answer_height: 答题框高度
            on_submit: 提交回调函数
            on_next: 下一题回调函数
            on_prev: 上一题回调函数
            on_hint: 提示回调函数
            
        Returns:
            包含用户答案和按钮状态的字典
        """
        # 渲染题目显示
        self.render_question_display(
            question=question,
            question_index=question_index,
            total_questions=total_questions,
            show_difficulty=show_difficulty,
            show_subject=show_subject
        )
        
        # 渲染答题输入
        answer = self.render_answer_input(
            question=question,
            key_suffix=key_suffix,
            height=answer_height
        )
        
        # 渲染操作按钮
        button_states = self.render_action_buttons(
            question=question,
            answer=answer,
            key_suffix=key_suffix,
            show_submit=True,
            show_hint=show_hint,
            show_navigation=show_navigation,
            current_index=question_index,
            total_questions=total_questions,
            on_submit=on_submit,
            on_next=on_next,
            on_prev=on_prev,
            on_hint=on_hint
        )
        
        # 在按钮区域之后显示诊断结果（全宽度显示）
        question_id = question.get('question_id', question.get('id', 'unknown'))
        
        # 添加重新提交按钮（如果已提交）
        submitted_key = f'submitted_{question_id}'
        if st.session_state.get(submitted_key, False):
            st.markdown("---")
            col_reset, col_space = st.columns([1, 3])
            with col_reset:
                if st.button("🔄 重新提交", key=f"reset_{question_id}_{key_suffix}", use_container_width=True):
                    # 重置提交状态和诊断结果
                    st.session_state[submitted_key] = False
                    st.session_state[f'show_diagnosis_{question_id}'] = False
                    st.session_state[f'submit_success_{question_id}'] = False
                    if f'diagnosis_result_{question_id}' in st.session_state:
                        del st.session_state[f'diagnosis_result_{question_id}']
                    st.rerun()
        
        # 显示提交成功消息
        if st.session_state.get(f'submit_success_{question_id}', False):
            st.success("✅ 提交成功！AI诊断结果已生成")
            # 显示后立即清除，避免重复显示
            st.session_state[f'submit_success_{question_id}'] = False
        
        # 显示提示信息（如果已点击获取提示）
        hint_state_key = f"hint_shown_{question_id}"
        if st.session_state.get(hint_state_key, False):
            st.info("💡 提示功能开发中...")
            # 添加关闭提示的按钮
            if st.button("❌ 关闭提示", key=f"close_hint_{question_id}_{key_suffix}"):
                st.session_state[hint_state_key] = False
                st.rerun()
        
        # 显示诊断结果
        if st.session_state.get(f'show_diagnosis_{question_id}', False):
            diagnosis_result = st.session_state.get(f'diagnosis_result_{question_id}')
            if diagnosis_result:
                self.render_diagnosis_result(diagnosis_result)
        
        return {'answer': answer, 'button_states': button_states}
    
    def _default_submit_handler(self, question: Dict[str, Any], answer: Any) -> None:
        """默认的提交处理函数"""
        question_id = question.get('question_id', question.get('id', 'unknown'))
        
        # 先设置提交状态，避免重复提交
        submit_key = f'submitted_{question_id}'
        if st.session_state.get(submit_key, False):
            return
        
        st.session_state[submit_key] = True
        
        with st.spinner("🤖 AI正在分析你的答案..."):
            try:
                diagnosis = self.api_service.diagnose_answer(
                    user_id=str(self.user_id),
                    question_id=str(question_id),
                    answer=str(answer),
                    answer_type="text"
                )
                
                if "error" not in diagnosis:
                    # 将诊断结果存储到session_state中，而不是直接渲染
                    st.session_state[f'diagnosis_result_{question_id}'] = diagnosis
                    st.session_state[f'show_diagnosis_{question_id}'] = True
                    # 将成功消息也存储到session_state中，避免立即刷新
                    st.session_state[f'submit_success_{question_id}'] = True
                else:
                    st.error(f"❌ 诊断失败: {diagnosis['error']}")
                    st.info("💡 请检查网络连接或稍后重试")
                    # 重置提交状态，允许重新提交
                    st.session_state[submit_key] = False
            except Exception as e:
                st.error(f"❌ 提交失败: {str(e)}")
                # 重置提交状态，允许重新提交
                st.session_state[submit_key] = False
    
    def _render_math_content(self, content: str) -> None:
        """智能渲染包含数学公式的内容
        
        Args:
            content: 要渲染的内容
        """
        # 检测是否包含复杂的LaTeX公式
        has_block_math = '$$' in content
        has_complex_latex = '\\begin{' in content or '\\end{' in content
        
        if has_block_math or has_complex_latex:
            # 处理包含块级公式的内容
            if has_block_math:
                # 分离文本和公式部分
                parts = content.split('$$')
                for i, part in enumerate(parts):
                    if i % 2 == 0:  # 普通文本部分
                        if part.strip():
                            # 处理行内公式
                            if '$' in part:
                                st.markdown(part)
                            else:
                                st.markdown(part)
                    else:  # LaTeX公式部分
                        try:
                            st.latex(part)
                        except Exception as e:
                            # 如果LaTeX渲染失败，回退到markdown
                            st.markdown(f"$${part}$$")
            else:
                # 尝试直接用latex渲染
                try:
                    st.latex(content)
                except Exception as e:
                    # 回退到markdown
                    st.markdown(content)
        else:
            # 简单内容直接用markdown渲染
            st.markdown(content)

# 便捷函数
def create_question_practice_component(api_service, user_id: str) -> QuestionPracticeComponent:
    """创建做题组件实例"""
    return QuestionPracticeComponent(api_service, user_id)

def render_simple_question(api_service, user_id: str, question: Dict[str, Any], 
                          key_suffix: str = "") -> Dict[str, Any]:
    """渲染简单的单题界面
    
    Args:
        api_service: API服务实例
        user_id: 用户ID
        question: 题目数据
        key_suffix: 组件key后缀
        
    Returns:
        包含用户答案和按钮状态的字典
    """
    component = QuestionPracticeComponent(api_service, user_id)
    return component.render_complete_question_interface(
        question=question,
        key_suffix=key_suffix,
        show_navigation=False,
        show_hint=True
    )

def render_question_with_navigation(question: Dict[str, Any],
                                   api_service = None,
                                   user_id: str = "",
                                   current_index: int = 0,
                                   total_questions: int = 1,
                                   key_suffix: str = "",
                                   on_submit: Optional[Callable] = None,
                                   on_next: Optional[Callable] = None,
                                   on_prev: Optional[Callable] = None,
                                   show_diagnosis: bool = True,
                                   submit_text: str = "提交答案",
                                   prev_text: str = "上一题") -> Dict[str, Any]:
    """渲染带导航的题目界面
    
    Args:
        question: 题目数据
        api_service: API服务实例
        user_id: 用户ID
        current_index: 当前题目索引
        total_questions: 总题目数
        key_suffix: 组件key后缀
        on_submit: 提交回调函数
        on_next: 下一题回调函数
        on_prev: 上一题回调函数
        show_diagnosis: 是否显示诊断结果
        submit_text: 提交按钮文本
        prev_text: 上一题按钮文本
        
    Returns:
        包含用户答案和按钮状态的字典
    """
    if not question:
        st.error("❌ 题目数据无效")
        return {'answer': None, 'button_states': {}}
    
    # 如果没有提供api_service，创建一个简单的组件
    if api_service and user_id:
        component = QuestionPracticeComponent(api_service, user_id)
        return component.render_complete_question_interface(
            question=question,
            question_index=current_index,
            total_questions=total_questions,
            key_suffix=key_suffix,
            show_navigation=True,
            on_submit=on_submit,
            on_next=on_next,
            on_prev=on_prev
        )
    else:
        # 简化版本，不依赖API服务
        st.write(f"**题目 {current_index + 1}/{total_questions}**")
        st.write(question.get('content', question.get('question', '')))
        
        # 简单的答题输入
        question_type = question.get('type', 'text')
        answer = None
        
        if question_type == 'choice' and question.get('options'):
            answer = st.radio("请选择答案：", question['options'], key=f"answer_{current_index}_{key_suffix}")
        elif question_type == 'judgment':
            answer = st.radio("请判断：", ["正确", "错误"], key=f"answer_{current_index}_{key_suffix}")
        else:
            answer = st.text_area("请输入答案：", key=f"answer_{current_index}_{key_suffix}")
        
        # 导航按钮
        col1, col2 = st.columns(2)
        button_states = {'submitted': False, 'prev_clicked': False, 'next_clicked': False}
        
        with col1:
            if on_prev and current_index > 0:
                if st.button(prev_text, key=f"prev_{current_index}_{key_suffix}"):
                    button_states['prev_clicked'] = True
                    on_prev()
        
        with col2:
            if answer and str(answer).strip():
                if st.button(submit_text, type="primary", key=f"submit_{current_index}_{key_suffix}"):
                    button_states['submitted'] = True
                    if on_submit:
                        on_submit(answer)
        
        return {'answer': answer, 'button_states': button_states}