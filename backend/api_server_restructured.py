#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI智慧学习平台 - 后端API服务器
使用FastAPI框架，提供RESTful API接口
重构版本：按角色分离API模块
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# 导入通用模块
from api.common.system import router as system_router
from api.common.users import router as users_router

# 导入学生端模块
from api.student.recommendation import router as student_recommendation_router
from api.student.diagnosis import router as student_diagnosis_router
from api.student.knowledge_map import router as student_knowledge_map_router
from api.student.questions import router as student_questions_router
from api.student.wrong_questions import router as student_wrong_questions_router
from api.student.stats import router as student_stats_router

# 导入教师端模块
from api.teacher.class_management import router as teacher_class_router
from api.teacher.student_analytics import router as teacher_analytics_router
from api.teacher.assignment_management import router as teacher_assignment_router
from api.teacher.knowledge_management import router as teacher_knowledge_router

# 创建FastAPI应用
app = FastAPI(
    title="AI智慧学习平台API",
    description="提供个性化学习推荐和智能诊断服务 - 按角色分离版本",
    version="2.0.0"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501"],  # Streamlit默认端口
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册通用路由
app.include_router(system_router)
app.include_router(users_router)

# 注册学生端路由（添加前缀）
app.include_router(student_recommendation_router, prefix="/student")
app.include_router(student_diagnosis_router, prefix="/student")
app.include_router(student_knowledge_map_router, prefix="/student")
app.include_router(student_questions_router, prefix="/student")
app.include_router(student_wrong_questions_router, prefix="/student")
app.include_router(student_stats_router, prefix="/student")

# 注册教师端路由（添加前缀）
app.include_router(teacher_class_router, prefix="/teacher")
app.include_router(teacher_analytics_router, prefix="/teacher")
app.include_router(teacher_assignment_router, prefix="/teacher")
app.include_router(teacher_knowledge_router, prefix="/teacher")

# 错误处理
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "error": "服务器内部错误",
            "detail": str(exc)
        }
    )

# 角色路由信息
@app.get("/api-info")
async def get_api_info():
    """获取API路由信息"""
    return {
        "message": "🎓 AI智慧学习平台API - 角色分离版本",
        "version": "2.0.0",
        "structure": {
            "common": {
                "description": "通用接口",
                "routes": ["/", "/health", "/users"]
            },
            "student": {
                "description": "学生端接口",
                "routes": [
                    "/student/recommendation",
                    "/student/diagnose", 
                    "/student/knowledge-map",
                    "/student/questions",
                    "/student/wrong-questions",
                    "/student/stats"
                ]
            },
            "teacher": {
                "description": "教师端接口",
                "routes": [
                    "/teacher/class",
                    "/teacher/analytics", 
                    "/teacher/assignment",
                    "/teacher/knowledge"
                ]
            }
        },
        "docs": "/docs"
    }

if __name__ == "__main__":
    import uvicorn
    
    print("🚀 启动AI智慧学习平台API服务器（角色分离版本）...")
    print("📖 API文档地址: http://localhost:8000/docs")
    print("🔗 前端地址: http://localhost:8501")
    print("📊 API信息: http://localhost:8000/api-info")
    
    uvicorn.run(
        "api_server_restructured:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )