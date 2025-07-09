#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI智慧学习平台 - 教师端API模块
"""

from .class_management import router as class_router
from .student_analytics import router as analytics_router
from .assignment_management import router as assignment_router
from .knowledge_management import router as knowledge_router

__all__ = [
    "class_router",
    "analytics_router", 
    "assignment_router",
    "knowledge_router"
]

__version__ = "1.0.0"