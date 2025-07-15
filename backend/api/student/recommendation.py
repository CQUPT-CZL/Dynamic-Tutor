#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
学习推荐接口 - 动态随机版本
每次调用会随机返回一种类型的学习任务包
"""

from fastapi import APIRouter, HTTPException
import time
import random

# --- 我们在这里定义四种推荐任务的生成函数 ---

def create_new_knowledge_mission(user_id: str):
    """生成一个“新知探索”任务包"""
    return {
        "mission_id": f"mission_nk_{int(time.time())}",
        "mission_type": "NEW_KNOWLEDGE",
        "metadata": {
            "title": "新知识解锁：条件概率！",
            "objective": "通过本次任务，你将掌握条件概率的定义和基本计算方法。",
            "reason": f"AI发现你({user_id})已经完全掌握了‘概率的定义与性质’，现在是深入学习的最佳时机！"
        },
        "payload": {
            "target_node": {
                "id": "conditional_probability",
                "name": "条件概率"
            },
            "steps": [
                {
                    "step": 1,
                    "type": "CONCEPT_LEARNING",
                    "content": { "title": "核心概念", "text": "条件概率P(B|A)指的是在事件A发生的条件下，事件B发生的概率..." }
                },
                {
                    "step": 2,
                    "type": "QUESTION_PRACTICE",
                    "content": { "question_id": 1, "difficulty": 0.4, "prompt": "我们先来做一道基础题热身一下！" }
                }
            ]
        }
    }

def create_weak_point_mission(user_id: str):
    """生成一个“弱点巩固”任务包"""
    return {
        "mission_id": f"mission_wpc_{int(time.time())}",
        "mission_type": "WEAK_POINT_CONSOLIDATION",
        "metadata": {
            "title": "专项巩固：随机事件的关系与运算",
            "objective": "彻底解决在判断事件关系时遇到的困难。",
            "reason": f"AI注意到你({user_id})在之前的练习中，对‘事件的互斥与独立’辨析不清。我们一起来攻克它！"
        },
        "payload": {
            "target_node": {
                "id": "random_event",
                "name": "随机事件及其关系与运算"
            },
            "steps": [
                {
                    "step": 1,
                    "type": "WRONG_QUESTION_REVIEW",
                    "content": { "question_id": 2, "prompt": "我们先回顾一下你上次做错的这道题。" }
                },
                {
                    "step": 2,
                    "type": "QUESTION_PRACTICE",
                    "content": { "question_id": 1, "difficulty": 0.5, "prompt": "现在来做一道类似的题目。" }
                }
            ]
        }
    }

def create_skill_enhancement_mission(user_id: str):
    """生成一个“核心能力提升”任务包"""
    return {
        "mission_id": f"mission_se_{int(time.time())}",
        "mission_type": "SKILL_ENHANCEMENT",
        "metadata": {
            "title": "解题逻辑专项训练！",
            "objective": "通过3个案例，提升你分析复杂问题的逻辑推理能力。",
            "reason": f"AI发现你({user_id})的知识点掌握和计算都很扎实，但在面对复杂问题时，解题步骤的规划上还有提升空间。"
        },
        "payload": {
            "target_skill": "Logical Reasoning",
            "questions": [
                { "question_id": 3, "prompt": "案例一：这是一个需要分步讨论的问题。" },
                { "question_id": 4, "prompt": "案例二：尝试从反面思考这个问题。" }
            ]
        }
    }

def create_exploratory_mission(user_id: str):
    """生成一个“兴趣探索”任务包"""
    return {
        "mission_id": f"mission_exp_{int(time.time())}",
        "mission_type": "EXPLORATORY",
        "metadata": {
            "title": "休息一下，看看概率论的奇妙应用！",
            "objective": "了解中心极限定理在现实世界中的巨大威力。",
            "reason": f"你({user_id})最近的学习状态太棒了！我们来放松一下，看看你学的知识有多酷！"
        },
        "payload": {
            "content_type": "ARTICLE",
            "title": "为什么社会调查只需要访问1000人？中心极限定理的魔力",
            "body": "你是否好奇，为什么民意调查只访问一小部分人，就能预测整个国家的选举结果？这背后正是中心极限定理在发挥作用...",
            "image_url": "https://example.com/clt_story.png"
        }
    }


# --- API 路由 ---
router = APIRouter(prefix="/recommendation", tags=["学习推荐"])

@router.get("/{user_id}")
async def get_recommendation(user_id: str):
    """
    获取用户学习推荐。
    每次调用会从四种任务包中随机返回一种。
    """
    try:
        # 将所有推荐生成函数放入一个列表中
        mission_generators = [
            create_new_knowledge_mission,
            create_weak_point_mission,
            create_skill_enhancement_mission,
            create_exploratory_mission
        ]

        # 随机选择一个函数
        selected_generator = random.choice(mission_generators)

        # 调用选中的函数来生成推荐内容
        recommendation = selected_generator(user_id)
        
        return recommendation
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取推荐失败: {str(e)}")
