#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
前端组件模块
包含可复用的UI组件
"""

from .question_practice import (
    QuestionPracticeComponent,
    create_question_practice_component,
    render_simple_question,
    render_question_with_navigation
)

__all__ = [
    'QuestionPracticeComponent',
    'create_question_practice_component', 
    'render_simple_question',
    'render_question_with_navigation'
]