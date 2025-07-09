#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据模型定义
"""

from pydantic import BaseModel
from typing import Optional

class DiagnosisRequest(BaseModel):
    user_id: str
    question_id: str
    answer: str
    answer_type: str = "text"
    time_spent: Optional[int] = None
    confidence: Optional[float] = None

class DiagnosisResponse(BaseModel):
    status: str
    diagnosis: str
    hint: Optional[str] = None
    correct_answer: str
    next_recommendation: Optional[str] = None 