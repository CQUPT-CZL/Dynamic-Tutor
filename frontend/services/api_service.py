#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
前端服务层 - API服务
封装所有与后端API的交互逻辑
"""

import streamlit as st
from typing import Dict, List, Any, Optional
import requests
import json
from .mock_api_service import mock_api

class APIService:
    """API服务类，提供所有前端需要的API调用方法"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.timeout = 10
        self.session.headers.update({
            "Content-Type": "application/json",
            "Accept": "application/json"
        })
        self._backend_available = None
        self._check_backend_availability()
    
    def _check_backend_availability(self):
        """检查后端API是否可用"""
        try:
            response = self.session.get(f"{self.base_url}/health", timeout=3)
            self._backend_available = response.status_code == 200
        except:
            self._backend_available = False
        
        if not self._backend_available:
            st.warning("🔧 后端API暂不可用，正在使用模拟数据进行界面展示")
    
    def is_backend_available(self) -> bool:
        """返回后端是否可用"""
        return self._backend_available
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """发送HTTP请求的通用方法"""
        url = f"{self.base_url}{endpoint}"
        try:
            response = self.session.request(method, url, **kwargs)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            st.error(f"API请求失败: {e}")
            return {"error": str(e)}
    
    # 系统相关
    def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        return self._make_request("GET", "/health")
    
    # 用户管理
    def get_users(self) -> List[Dict[str, Any]]:
        """获取用户列表"""
        if not self._backend_available:
            return mock_api.get_users()
        
        try:
            response = self._make_request("GET", "/api/users")
            return response.get("data", [])
        except Exception as e:
            st.error(f"获取用户列表失败: {str(e)}")
            return mock_api.get_users()
    
    # 学习推荐
    def get_recommendation(self, user_id: str) -> Dict[str, Any]:
        """获取用户推荐"""
        return self._make_request("GET", f"/recommendation/{user_id}")
    
    # 答案诊断
    def diagnose_answer(self, user_id: str, question_id: str, answer: str, 
                       answer_type: str = "text", time_spent: Optional[int] = None, 
                       confidence: Optional[float] = None) -> Dict[str, Any]:
        """诊断答案"""
        data = {
            "user_id": user_id,
            "question_id": question_id,
            "answer": answer,
            "answer_type": answer_type
        }
        if time_spent is not None:
            data["time_spent"] = str(time_spent)
        if confidence is not None:
            data["confidence"] = str(confidence)
        
        return self._make_request("POST", "/diagnose", json=data)
    
    def diagnose_image_answer(self, user_id: str, question_id: str, 
                            image_file, time_spent: Optional[int] = None, 
                            confidence: Optional[float] = None) -> Dict[str, Any]:
        """诊断图片答案"""
        try:
            files = {"image": image_file}
            data = {
                "user_id": user_id,
                "question_id": question_id
            }
            if time_spent is not None:
                data["time_spent"] = str(time_spent)
            if confidence is not None:
                data["confidence"] = str(confidence)
            
            url = f"{self.base_url}/diagnose/image"
            response = self.session.post(url, files=files, data=data)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            st.error(f"图片诊断API请求失败: {e}")
            return {"error": str(e)}
    
    # 知识图谱
    def get_knowledge_map(self, user_id: str) -> List[Dict[str, Any]]:
        """获取知识图谱"""
        result = self._make_request("GET", f"/knowledge-map/{user_id}")
        return result if isinstance(result, list) else []
    
    def get_knowledge_nodes_simple(self) -> Dict[str, str]:
        """获取知识节点（简单版本）"""
        result = self._make_request("GET", "/knowledge-map/get-nodes")
        # print('shizhidian')
        # print(result)
        # print('wancheng')
        return result.get("nodes", {}) if isinstance(result, dict) else {}
    
    def get_user_mastery(self, user_id: str, node_name: str) -> float:
        """获取用户掌握度"""
        result = self._make_request("GET", f"/knowledge-map/mastery/{user_id}/{node_name}")
        return result.get("mastery", 0.0) if isinstance(result, dict) else 0.0
    
    def update_user_mastery(self, user_id: str, node_name: str, mastery_score: float) -> Dict[str, Any]:
        """更新用户掌握度"""
        return self._make_request("POST", f"/knowledge-map/mastery/{user_id}/{node_name}", json={"mastery_score": mastery_score})
    
    # 练习题目
    def get_questions_for_node(self, node_name: str) -> List[str]:
        """获取知识点练习题"""
        result = self._make_request("GET", f"/questions/{node_name}")
        return result.get("questions", []) if isinstance(result, dict) else []
    
    # 错题集
    def get_wrong_questions(self, user_id: str) -> List[Dict[str, Any]]:
        """获取错题集"""
        result = self._make_request("GET", f"/wrong-questions/{user_id}")
        return result.get("wrong_questions", []) if isinstance(result, dict) else []
    
    def add_wrong_question(self, user_id: int, question_id: int, user_answer: str) -> bool:
        """添加错题"""
        data = {
            "user_id": user_id,
            "question_id": question_id,
            "user_answer": user_answer
        }
        result = self._make_request("POST", "/wrong_questions", json=data)
        return result.get("success", False)
    
    def remove_wrong_question(self, user_id: int, question_id: int) -> bool:
        """移除错题"""
        result = self._make_request("DELETE", f"/wrong_questions/{user_id}/{question_id}")
        return result.get("success", False)
    
    # ==================== 教师端API ====================
    
    # 知识点管理
    def get_knowledge_nodes(self, level: Optional[str] = None, 
                           min_difficulty: Optional[float] = None, 
                           max_difficulty: Optional[float] = None) -> Dict[str, Any]:
        """获取知识点列表"""
        if not self._backend_available:
            return mock_api.get_knowledge_nodes(1, 10, "", None)
        
        try:
            params = {}
            if level:
                params["level"] = level
            if min_difficulty is not None:
                params["min_difficulty"] = min_difficulty
            if max_difficulty is not None:
                params["max_difficulty"] = max_difficulty
            
            response = self._make_request("GET", "/teacher/knowledge/list", params=params)
            return response
        except Exception as e:
            st.error(f"获取知识点列表失败: {str(e)}")
            return mock_api.get_knowledge_nodes(1, 10, "", None)
    
    def get_knowledge_node(self, node_id: str) -> Optional[Dict[str, Any]]:
        """获取单个知识点详情"""
        if not self._backend_available:
            return mock_api.get_knowledge_node(node_id)
        
        try:
            response = self._make_request("GET", f"/teacher/knowledge/detail/{node_id}")
            return response
        except Exception as e:
            st.error(f"获取知识点详情失败: {str(e)}")
            return mock_api.get_knowledge_node(node_id)
    
    def create_knowledge_node(self, node_data: Dict[str, Any]) -> Dict[str, Any]:
        """创建知识点"""
        if not self._backend_available:
            return mock_api.create_knowledge_node(node_data)
        
        try:
            response = self._make_request("POST", "/teacher/knowledge/create", json=node_data)
            return response
        except Exception as e:
            st.error(f"创建知识点失败: {str(e)}")
            return mock_api.create_knowledge_node(node_data)
    
    def update_knowledge_node(self, node_id: str, node_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """更新知识点"""
        if not self._backend_available:
            return mock_api.update_knowledge_node(node_id, node_data)
        
        try:
            print('---')
            print(node_id, node_data)
            response = self._make_request("PUT", f"/teacher/knowledge/update/{node_id}", json=node_data)
            return response
        except Exception as e:
            st.error(f"更新知识点失败: {str(e)}")
            return mock_api.update_knowledge_node(node_id, node_data)
    
    def delete_knowledge_node(self, node_id: str) -> bool:
        """删除知识点"""
        if not self._backend_available:
            return mock_api.delete_knowledge_node(node_id)
        
        try:
            response = self._make_request("DELETE", f"/teacher/knowledge/delete/{node_id}")
            return response
        except Exception as e:
            st.error(f"删除知识点失败: {str(e)}")
            return mock_api.delete_knowledge_node(node_id)
    
    def get_knowledge_nodes_stats(self) -> Dict[str, Any]:
        """获取知识点统计信息"""
        if not self._backend_available:
            return mock_api.get_knowledge_nodes_stats()
        
        try:
            response = self._make_request("GET", "/api/teacher/knowledge-nodes/stats")
            return response.get("data", {})
        except Exception as e:
            st.error(f"获取知识点统计失败: {str(e)}")
            return mock_api.get_knowledge_nodes_stats()
    
    # 题目管理
    def get_questions(self, page: int = 1, page_size: int = 10, 
                     search: str = "", question_type: str = "", 
                     status: str = "") -> Dict[str, Any]:
        """获取题目列表"""
        if not self._backend_available:
            return mock_api.get_questions(page, page_size, search, question_type, status)
        
        try:
            params = {"page": page, "page_size": page_size}
            if search:
                params["search"] = search
            if question_type:
                params["question_type"] = question_type
            if status:
                params["status"] = status
            
            response = self._make_request("GET", "/api/teacher/questions", params=params)
            return response
        except Exception as e:
            st.error(f"获取题目列表失败: {str(e)}")
            return mock_api.get_questions(page, page_size, search, question_type, status)
    
    def get_question(self, question_id: int) -> Optional[Dict[str, Any]]:
        """获取单个题目详情"""
        if not self._backend_available:
            return mock_api.get_question(question_id)
        
        try:
            response = self._make_request("GET", f"/api/teacher/questions/{question_id}")
            return response.get("data")
        except Exception as e:
            st.error(f"获取题目详情失败: {str(e)}")
            return mock_api.get_question(question_id)
    
    def create_question(self, question_data: Dict[str, Any]) -> Dict[str, Any]:
        """创建题目"""
        if not self._backend_available:
            return mock_api.create_question(question_data)
        
        try:
            response = self._make_request("POST", "/api/teacher/questions", json=question_data)
            return response.get("data", {})
        except Exception as e:
            st.error(f"创建题目失败: {str(e)}")
            return mock_api.create_question(question_data)
    
    def update_question(self, question_id: int, question_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """更新题目"""
        if not self._backend_available:
            return mock_api.update_question(question_id, question_data)
        
        try:
            response = self._make_request("PUT", f"/api/teacher/questions/{question_id}", json=question_data)
            return response.get("data")
        except Exception as e:
            st.error(f"更新题目失败: {str(e)}")
            return mock_api.update_question(question_id, question_data)
    
    def delete_question(self, question_id: int) -> bool:
        """删除题目"""
        if not self._backend_available:
            return mock_api.delete_question(question_id)
        
        try:
            response = self._make_request("DELETE", f"/api/teacher/questions/{question_id}")
            return response.get("success", False)
        except Exception as e:
            st.error(f"删除题目失败: {str(e)}")
            return mock_api.delete_question(question_id)
    
    def get_questions_stats(self) -> Dict[str, Any]:
        """获取题目统计信息"""
        if not self._backend_available:
            return mock_api.get_questions_stats()
        
        try:
            response = self._make_request("GET", "/api/teacher/questions/stats")
            return response.get("data", {})
        except Exception as e:
            st.error(f"获取题目统计失败: {str(e)}")
            return mock_api.get_questions_stats()
    
    # 知识图谱管理
    def get_knowledge_edges(self) -> List[Dict[str, Any]]:
        """获取知识点关系列表"""
        if not self._backend_available:
            return mock_api.get_knowledge_edges()
        
        try:
            response = self._make_request("GET", "/api/teacher/knowledge-edges")
            return response.get("data", [])
        except Exception as e:
            st.error(f"获取知识点关系失败: {str(e)}")
            return mock_api.get_knowledge_edges()
    
    def create_knowledge_edge(self, edge_data: Dict[str, Any]) -> Dict[str, Any]:
        """创建知识点关系"""
        if not self._backend_available:
            return mock_api.create_knowledge_edge(edge_data)
        
        try:
            response = self._make_request("POST", "/api/teacher/knowledge-edges", json=edge_data)
            return response.get("data", {})
        except Exception as e:
            st.error(f"创建知识点关系失败: {str(e)}")
            return mock_api.create_knowledge_edge(edge_data)
    
    def delete_knowledge_edge(self, edge_id: int) -> bool:
        """删除知识点关系"""
        if not self._backend_available:
            return mock_api.delete_knowledge_edge(edge_id)
        
        try:
            response = self._make_request("DELETE", f"/api/teacher/knowledge-edges/{edge_id}")
            return response.get("success", False)
        except Exception as e:
            st.error(f"删除知识点关系失败: {str(e)}")
            return mock_api.delete_knowledge_edge(edge_id)
    
    def get_knowledge_graph_data(self) -> Dict[str, Any]:
        """获取知识图谱数据"""
        if not self._backend_available:
            return mock_api.get_knowledge_graph_data()
        
        try:
            response = self._make_request("GET", "/api/teacher/knowledge-graph/data")
            return response.get("data", {})
        except Exception as e:
            st.error(f"获取知识图谱数据失败: {str(e)}")
            return mock_api.get_knowledge_graph_data()
    
    def get_graph_analysis(self) -> Dict[str, Any]:
        """获取图谱分析数据"""
        if not self._backend_available:
            return mock_api.get_graph_analysis()
        
        try:
            response = self._make_request("GET", "/api/teacher/knowledge-graph/analysis")
            return response.get("data", {})
        except Exception as e:
            st.error(f"获取图谱分析失败: {str(e)}")
            return mock_api.get_graph_analysis()
    
    def get_ai_suggestions(self) -> List[Dict[str, Any]]:
        """获取AI建议"""
        if not self._backend_available:
            return mock_api.get_ai_suggestions()
        
        try:
            response = self._make_request("GET", "/api/teacher/knowledge-graph/ai-suggestions")
            return response.get("data", [])
        except Exception as e:
            st.error(f"获取AI建议失败: {str(e)}")
            return mock_api.get_ai_suggestions()
    
    # 用户统计
    def get_user_stats(self, user_id: str) -> Dict[str, Any]:
        """获取用户统计"""
        return self._make_request("GET", f"/stats/{user_id}")

# 全局API服务实例
def get_api_service() -> APIService:
    """获取全局API服务实例"""
    if "api_service" not in st.session_state:
        st.session_state.api_service = APIService()
    return st.session_state.api_service