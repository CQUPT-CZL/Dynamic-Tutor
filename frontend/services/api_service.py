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

class APIService:
    """API服务类，提供所有前端需要的API调用方法"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json",
            "Accept": "application/json"
        })
    
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
    def get_users(self) -> List[Dict[str, str]]:
        """获取用户列表"""
        result = self._make_request("GET", "/users")
        return result if isinstance(result, list) else []
    
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
    
    def get_knowledge_nodes(self) -> Dict[str, str]:
        """获取知识节点"""
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