#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI智慧学习平台 - 教师端API模块
"""

from .student_analytics import router as analytics_router
from .knowledge_management import router as knowledge_router
from .question_management import router as question_router

__all__ = [
    "analytics_router", 
    "knowledge_router",
    "question_router"
]

__version__ = "1.0.0"