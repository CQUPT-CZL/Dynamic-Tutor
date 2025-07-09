# -*- coding: utf-8 -*-
"""
模拟API服务 - 用于前端界面测试
当后端API未实现时，提供模拟数据支持前端界面展示
"""

import json
import time
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import random

class MockAPIService:
    """模拟API服务类"""
    
    def __init__(self):
        self.base_url = "http://localhost:8000"
        self._init_mock_data()
    
    def _init_mock_data(self):
        """初始化模拟数据"""
        # 模拟知识点数据
        self.mock_knowledge_nodes = [
            {
                "id": 1,
                "name": "函数基础",
                "description": "函数的定义、调用和参数传递",
                "difficulty_level": 1,
                "subject": "数学",
                "grade": "高一",
                "created_at": "2024-01-15T10:00:00",
                "updated_at": "2024-01-15T10:00:00",
                "status": "active"
            },
            {
                "id": 2,
                "name": "二次函数",
                "description": "二次函数的图像和性质",
                "difficulty_level": 2,
                "subject": "数学",
                "grade": "高一",
                "created_at": "2024-01-16T10:00:00",
                "updated_at": "2024-01-16T10:00:00",
                "status": "active"
            },
            {
                "id": 3,
                "name": "导数概念",
                "description": "导数的定义和几何意义",
                "difficulty_level": 3,
                "subject": "数学",
                "grade": "高二",
                "created_at": "2024-01-17T10:00:00",
                "updated_at": "2024-01-17T10:00:00",
                "status": "active"
            },
            {
                "id": 4,
                "name": "三角函数",
                "description": "正弦、余弦、正切函数的性质",
                "difficulty_level": 2,
                "subject": "数学",
                "grade": "高一",
                "created_at": "2024-01-18T10:00:00",
                "updated_at": "2024-01-18T10:00:00",
                "status": "active"
            },
            {
                "id": 5,
                "name": "向量运算",
                "description": "向量的加法、减法和数量积",
                "difficulty_level": 2,
                "subject": "数学",
                "grade": "高二",
                "created_at": "2024-01-19T10:00:00",
                "updated_at": "2024-01-19T10:00:00",
                "status": "active"
            }
        ]
        
        # 模拟题目数据
        self.mock_questions = [
            {
                "id": 1,
                "title": "函数定义域求解",
                "content": "求函数 f(x) = √(x-1) + 1/(x-2) 的定义域",
                "question_type": "选择题",
                "options": ["[1,2)∪(2,+∞)", "(1,2)∪(2,+∞)", "[1,+∞)", "(1,+∞)"],
                "correct_answer": "[1,2)∪(2,+∞)",
                "difficulty_level": 2,
                "subject": "数学",
                "grade": "高一",
                "status": "published",
                "created_at": "2024-01-15T11:00:00",
                "updated_at": "2024-01-15T11:00:00",
                "knowledge_nodes": [1]
            },
            {
                "id": 2,
                "title": "二次函数最值",
                "content": "已知二次函数 f(x) = x² - 4x + 3，求其在区间[0,3]上的最小值",
                "question_type": "解答题",
                "options": [],
                "correct_answer": "最小值为-1，在x=2处取得",
                "difficulty_level": 2,
                "subject": "数学",
                "grade": "高一",
                "status": "published",
                "created_at": "2024-01-16T11:00:00",
                "updated_at": "2024-01-16T11:00:00",
                "knowledge_nodes": [2]
            },
            {
                "id": 3,
                "title": "导数计算",
                "content": "计算函数 f(x) = x³ - 2x² + x - 1 的导数",
                "question_type": "填空题",
                "options": [],
                "correct_answer": "f'(x) = 3x² - 4x + 1",
                "difficulty_level": 3,
                "subject": "数学",
                "grade": "高二",
                "status": "draft",
                "created_at": "2024-01-17T11:00:00",
                "updated_at": "2024-01-17T11:00:00",
                "knowledge_nodes": [3]
            }
        ]
        
        # 模拟知识点关系数据
        self.mock_knowledge_edges = [
            {
                "id": 1,
                "source_node_id": 1,
                "target_node_id": 2,
                "relationship_type": "prerequisite",
                "strength": 0.8,
                "description": "函数基础是学习二次函数的前提",
                "created_at": "2024-01-20T10:00:00"
            },
            {
                "id": 2,
                "source_node_id": 2,
                "target_node_id": 3,
                "relationship_type": "prerequisite",
                "strength": 0.9,
                "description": "二次函数是学习导数的基础",
                "created_at": "2024-01-20T10:30:00"
            },
            {
                "id": 3,
                "source_node_id": 1,
                "target_node_id": 4,
                "relationship_type": "related",
                "strength": 0.6,
                "description": "函数基础与三角函数相关",
                "created_at": "2024-01-20T11:00:00"
            }
        ]
        
        # 模拟用户数据
        self.mock_users = [
            {"id": 1, "name": "小崔", "role": "student", "grade": "高一"},
            {"id": 2, "name": "小陈", "role": "student", "grade": "高二"},
            {"id": 3, "name": "胡老师", "role": "teacher", "subject": "数学"},
            {"id": 4, "name": "AI_System", "role": "system", "description": "AI系统用户"}
        ]
    
    # ==================== 用户相关API ====================
    
    def get_users(self) -> List[Dict[str, Any]]:
        """获取用户列表"""
        return self.mock_users
    
    def get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        """根据ID获取用户信息"""
        for user in self.mock_users:
            if user["id"] == user_id:
                return user
        return None
    
    # ==================== 知识点管理API ====================
    
    def get_knowledge_nodes(self, page: int = 1, page_size: int = 10, 
                           search: str = "", difficulty: Optional[int] = None) -> Dict[str, Any]:
        """获取知识点列表"""
        nodes = self.mock_knowledge_nodes.copy()
        
        # 搜索过滤
        if search:
            nodes = [node for node in nodes if search.lower() in node["name"].lower() 
                    or search.lower() in node["description"].lower()]
        
        # 难度过滤
        if difficulty is not None:
            nodes = [node for node in nodes if node["difficulty_level"] == difficulty]
        
        # 分页
        total = len(nodes)
        start = (page - 1) * page_size
        end = start + page_size
        nodes = nodes[start:end]
        
        return {
            "data": nodes,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size
        }
    
    def get_knowledge_node(self, node_id: int) -> Optional[Dict[str, Any]]:
        """获取单个知识点详情"""
        for node in self.mock_knowledge_nodes:
            if node["id"] == node_id:
                return node
        return None
    
    def create_knowledge_node(self, node_data: Dict[str, Any]) -> Dict[str, Any]:
        """创建知识点"""
        new_id = max([node["id"] for node in self.mock_knowledge_nodes]) + 1
        new_node = {
            "id": new_id,
            "name": node_data["name"],
            "description": node_data.get("description", ""),
            "difficulty_level": node_data.get("difficulty_level", 1),
            "subject": node_data.get("subject", "数学"),
            "grade": node_data.get("grade", "高一"),
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "status": "active"
        }
        self.mock_knowledge_nodes.append(new_node)
        return new_node
    
    def update_knowledge_node(self, node_id: int, node_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """更新知识点"""
        for i, node in enumerate(self.mock_knowledge_nodes):
            if node["id"] == node_id:
                self.mock_knowledge_nodes[i].update(node_data)
                self.mock_knowledge_nodes[i]["updated_at"] = datetime.now().isoformat()
                return self.mock_knowledge_nodes[i]
        return None
    
    def delete_knowledge_node(self, node_id: int) -> bool:
        """删除知识点"""
        for i, node in enumerate(self.mock_knowledge_nodes):
            if node["id"] == node_id:
                del self.mock_knowledge_nodes[i]
                return True
        return False
    
    def get_knowledge_nodes_stats(self) -> Dict[str, Any]:
        """获取知识点统计信息"""
        total = len(self.mock_knowledge_nodes)
        difficulty_stats = {}
        subject_stats = {}
        grade_stats = {}
        
        for node in self.mock_knowledge_nodes:
            # 难度统计
            diff = node["difficulty_level"]
            difficulty_stats[diff] = difficulty_stats.get(diff, 0) + 1
            
            # 学科统计
            subject = node["subject"]
            subject_stats[subject] = subject_stats.get(subject, 0) + 1
            
            # 年级统计
            grade = node["grade"]
            grade_stats[grade] = grade_stats.get(grade, 0) + 1
        
        return {
            "total_nodes": total,
            "difficulty_distribution": difficulty_stats,
            "subject_distribution": subject_stats,
            "grade_distribution": grade_stats
        }
    
    # ==================== 题目管理API ====================
    
    def get_questions(self, page: int = 1, page_size: int = 10, 
                     search: str = "", question_type: str = "", 
                     status: str = "") -> Dict[str, Any]:
        """获取题目列表"""
        questions = self.mock_questions.copy()
        
        # 搜索过滤
        if search:
            questions = [q for q in questions if search.lower() in q["title"].lower() 
                        or search.lower() in q["content"].lower()]
        
        # 题型过滤
        if question_type:
            questions = [q for q in questions if q["question_type"] == question_type]
        
        # 状态过滤
        if status:
            questions = [q for q in questions if q["status"] == status]
        
        # 分页
        total = len(questions)
        start = (page - 1) * page_size
        end = start + page_size
        questions = questions[start:end]
        
        return {
            "data": questions,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size
        }
    
    def get_question(self, question_id: int) -> Optional[Dict[str, Any]]:
        """获取单个题目详情"""
        for question in self.mock_questions:
            if question["id"] == question_id:
                return question
        return None
    
    def create_question(self, question_data: Dict[str, Any]) -> Dict[str, Any]:
        """创建题目"""
        new_id = max([q["id"] for q in self.mock_questions]) + 1
        new_question = {
            "id": new_id,
            "title": question_data["title"],
            "content": question_data["content"],
            "question_type": question_data.get("question_type", "选择题"),
            "options": question_data.get("options", []),
            "correct_answer": question_data.get("correct_answer", ""),
            "difficulty_level": question_data.get("difficulty_level", 1),
            "subject": question_data.get("subject", "数学"),
            "grade": question_data.get("grade", "高一"),
            "status": question_data.get("status", "draft"),
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "knowledge_nodes": question_data.get("knowledge_nodes", [])
        }
        self.mock_questions.append(new_question)
        return new_question
    
    def update_question(self, question_id: int, question_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """更新题目"""
        for i, question in enumerate(self.mock_questions):
            if question["id"] == question_id:
                self.mock_questions[i].update(question_data)
                self.mock_questions[i]["updated_at"] = datetime.now().isoformat()
                return self.mock_questions[i]
        return None
    
    def delete_question(self, question_id: int) -> bool:
        """删除题目"""
        for i, question in enumerate(self.mock_questions):
            if question["id"] == question_id:
                del self.mock_questions[i]
                return True
        return False
    
    def get_questions_stats(self) -> Dict[str, Any]:
        """获取题目统计信息"""
        total = len(self.mock_questions)
        type_stats = {}
        status_stats = {}
        difficulty_stats = {}
        
        for question in self.mock_questions:
            # 题型统计
            qtype = question["question_type"]
            type_stats[qtype] = type_stats.get(qtype, 0) + 1
            
            # 状态统计
            status = question["status"]
            status_stats[status] = status_stats.get(status, 0) + 1
            
            # 难度统计
            diff = question["difficulty_level"]
            difficulty_stats[diff] = difficulty_stats.get(diff, 0) + 1
        
        return {
            "total_questions": total,
            "type_distribution": type_stats,
            "status_distribution": status_stats,
            "difficulty_distribution": difficulty_stats
        }
    
    # ==================== 知识图谱API ====================
    
    def get_knowledge_edges(self) -> List[Dict[str, Any]]:
        """获取知识点关系列表"""
        return self.mock_knowledge_edges
    
    def create_knowledge_edge(self, edge_data: Dict[str, Any]) -> Dict[str, Any]:
        """创建知识点关系"""
        new_id = max([edge["id"] for edge in self.mock_knowledge_edges]) + 1
        new_edge = {
            "id": new_id,
            "source_node_id": edge_data["source_node_id"],
            "target_node_id": edge_data["target_node_id"],
            "relationship_type": edge_data.get("relationship_type", "related"),
            "strength": edge_data.get("strength", 0.5),
            "description": edge_data.get("description", ""),
            "created_at": datetime.now().isoformat()
        }
        self.mock_knowledge_edges.append(new_edge)
        return new_edge
    
    def delete_knowledge_edge(self, edge_id: int) -> bool:
        """删除知识点关系"""
        for i, edge in enumerate(self.mock_knowledge_edges):
            if edge["id"] == edge_id:
                del self.mock_knowledge_edges[i]
                return True
        return False
    
    def get_knowledge_graph_data(self) -> Dict[str, Any]:
        """获取知识图谱数据"""
        nodes = [{
            "id": node["id"],
            "name": node["name"],
            "difficulty_level": node["difficulty_level"],
            "subject": node["subject"],
            "grade": node["grade"]
        } for node in self.mock_knowledge_nodes]
        
        edges = [{
            "source": edge["source_node_id"],
            "target": edge["target_node_id"],
            "type": edge["relationship_type"],
            "strength": edge["strength"]
        } for edge in self.mock_knowledge_edges]
        
        return {
            "nodes": nodes,
            "edges": edges
        }
    
    def get_graph_analysis(self) -> Dict[str, Any]:
        """获取图谱分析数据"""
        nodes_count = len(self.mock_knowledge_nodes)
        edges_count = len(self.mock_knowledge_edges)
        
        # 模拟一些分析指标
        return {
            "total_nodes": nodes_count,
            "total_edges": edges_count,
            "connectivity": round(edges_count / max(nodes_count, 1), 2),
            "avg_degree": round(2 * edges_count / max(nodes_count, 1), 2),
            "health_score": random.randint(75, 95),
            "coverage_rate": random.randint(80, 100),
            "complexity_index": round(random.uniform(0.3, 0.8), 2)
        }
    
    def get_ai_suggestions(self) -> List[Dict[str, Any]]:
        """获取AI建议"""
        suggestions = [
            {
                "type": "missing_relationship",
                "source_node": "函数基础",
                "target_node": "向量运算",
                "suggested_type": "related",
                "confidence": 0.75,
                "reason": "两个概念在解析几何中经常同时使用"
            },
            {
                "type": "weak_connection",
                "source_node": "三角函数",
                "target_node": "向量运算",
                "suggested_type": "prerequisite",
                "confidence": 0.68,
                "reason": "向量的夹角计算需要三角函数知识"
            },
            {
                "type": "redundant_relationship",
                "source_node": "函数基础",
                "target_node": "导数概念",
                "current_type": "related",
                "suggested_action": "strengthen",
                "confidence": 0.82,
                "reason": "导数是函数的重要概念，关系应该更强"
            }
        ]
        return suggestions

# 创建全局实例
mock_api = MockAPIService()