#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI智慧学习平台 - 后端API服务器
使用FastAPI框架，提供RESTful API接口
重构版本：接口按功能分离到不同模块
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# 导入所有路由模块
from api.system import router as system_router
from api.users import router as users_router
from api.recommendation import router as recommendation_router
from api.diagnosis import router as diagnosis_router
from api.knowledge_map import router as knowledge_map_router
from api.questions import router as questions_router
from api.wrong_questions import router as wrong_questions_router
from api.stats import router as stats_router

# 创建FastAPI应用
app = FastAPI(
    title="AI智慧学习平台API",
    description="提供个性化学习推荐和智能诊断服务",
    version="1.0.0"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501"],  # Streamlit默认端口
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册所有路由
app.include_router(system_router)
app.include_router(users_router)
app.include_router(recommendation_router)
app.include_router(diagnosis_router)
app.include_router(knowledge_map_router)
app.include_router(questions_router)
app.include_router(wrong_questions_router)
app.include_router(stats_router)

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

if __name__ == "__main__":
    import uvicorn
    
    print("🚀 启动AI智慧学习平台API服务器...")
    print("📖 API文档地址: http://localhost:8000/docs")
    print("🔗 前端地址: http://localhost:8501")
    
    uvicorn.run(
        "api_server_new:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 