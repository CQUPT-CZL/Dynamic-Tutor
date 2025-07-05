#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI智慧学习平台 - 系统启动脚本（详细输出模式）
同时启动前端和后端，显示所有输出到终端，同时保存到日志文件
"""

import subprocess
import sys
import os
import time
import signal
import threading
from pathlib import Path
from datetime import datetime
from typing import TextIO

def check_dependencies():
    """检查依赖是否安装"""
    try:
        import streamlit
        import fastapi
        import uvicorn
        print("✅ 所有依赖已安装")
        return True
    except ImportError as e:
        print(f"❌ 缺少依赖: {e}")
        print("请运行: pip install -r backend/requirements.txt")
        return False

def setup_logs():
    """设置日志目录和文件"""
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backend_log = logs_dir / f"backend_verbose_{timestamp}.log"
    frontend_log = logs_dir / f"frontend_verbose_{timestamp}.log"
    
    return backend_log, frontend_log

def start_backend():
    """启动后端API服务器"""
    print("🚀 启动后端API服务器...")
    backend_dir = Path("backend")
    if not backend_dir.exists():
        print("❌ 后端目录不存在，请确保backend目录存在")
        return None, None
    
    # 设置日志文件
    backend_log, _ = setup_logs()
    
    # 先初始化数据库
    print("🔧 初始化数据库...")
    try:
        init_result = subprocess.run(
            [sys.executable, "init_database.py"],
            cwd=backend_dir,
            capture_output=True,
            text=True
        )
        if init_result.returncode == 0:
            print("✅ 数据库初始化成功")
        else:
            print(f"⚠️ 数据库初始化警告: {init_result.stderr}")
    except Exception as e:
        print(f"⚠️ 数据库初始化失败: {e}")
    
    try:
        # 打开日志文件
        log_file = open(backend_log, 'w', encoding='utf-8')
        
        # 切换到后端目录并启动服务器
        process = subprocess.Popen(
            [sys.executable, "api_server.py"],
            cwd=backend_dir,
            # 输出到管道，然后读取并同时写入终端和文件
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        print(f"✅ 后端服务器启动成功，日志文件: {backend_log}")
        
        # 启动日志输出线程
        def log_output():
            if process.stdout:
                for line in iter(process.stdout.readline, ''):
                    if line:
                        print(line.rstrip())
                        log_file.write(line)
                        log_file.flush()
        
        log_thread = threading.Thread(target=log_output, daemon=True)
        log_thread.start()
        
        return process, log_file
    except Exception as e:
        print(f"❌ 后端服务器启动失败: {e}")
        return None, None

def start_frontend():
    """启动前端Streamlit应用"""
    print("🎨 启动前端Streamlit应用...")
    frontend_dir = Path("frontend")
    if not frontend_dir.exists():
        print("❌ 前端目录不存在，请确保frontend目录存在")
        return None, None
    
    # 设置日志文件
    _, frontend_log = setup_logs()
    
    try:
        # 打开日志文件
        log_file = open(frontend_log, 'w', encoding='utf-8')
        
        # 切换到前端目录并启动Streamlit
        process = subprocess.Popen(
            [sys.executable, "-m", "streamlit", "run", "app.py", "--server.port", "8501"],
            cwd=frontend_dir,
            # 输出到管道，然后读取并同时写入终端和文件
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        print(f"✅ 前端应用启动成功，日志文件: {frontend_log}")
        
        # 启动日志输出线程
        def log_output():
            if process.stdout:
                for line in iter(process.stdout.readline, ''):
                    if line:
                        print(line.rstrip())
                        log_file.write(line)
                        log_file.flush()
        
        log_thread = threading.Thread(target=log_output, daemon=True)
        log_thread.start()
        
        return process, log_file
    except Exception as e:
        print(f"❌ 前端应用启动失败: {e}")
        return None, None

def wait_for_backend():
    """等待后端服务器启动"""
    import requests
    max_attempts = 30
    for i in range(max_attempts):
        try:
            response = requests.get("http://localhost:8000/health", timeout=2)
            if response.status_code == 200:
                print("✅ 后端API服务器已就绪")
                return True
        except:
            pass
        time.sleep(1)
        print(f"⏳ 等待后端服务器启动... ({i+1}/{max_attempts})")
    
    print("❌ 后端服务器启动超时")
    return False

def main():
    """主函数"""
    print("🎓 AI智慧学习平台 - 系统启动（详细输出模式）")
    print("=" * 50)
    
    # 检查依赖
    if not check_dependencies():
        return
    
    # 启动后端
    backend_process, backend_log_file = start_backend()
    if not backend_process:
        return
    
    # 等待后端启动
    if not wait_for_backend():
        backend_process.terminate()
        if backend_log_file:
            backend_log_file.close()
        return
    
    # 启动前端
    frontend_process, frontend_log_file = start_frontend()
    if not frontend_process:
        backend_process.terminate()
        if backend_log_file:
            backend_log_file.close()
        return
    
    print("\n" + "=" * 50)
    print("🎉 系统启动成功！")
    print("📖 API文档: http://localhost:8000/docs")
    print("🎨 前端应用: http://localhost:8501")
    print("📝 日志文件保存在 logs/ 目录中")
    print("=" * 50)
    print("按 Ctrl+C 停止所有服务")
    
    try:
        # 等待用户中断
        while True:
            time.sleep(1)
            
            # 检查进程是否还在运行
            if backend_process.poll() is not None:
                print("❌ 后端服务器意外停止")
                break
            if frontend_process.poll() is not None:
                print("❌ 前端应用意外停止")
                break
                
    except KeyboardInterrupt:
        print("\n🛑 正在停止服务...")
    
    finally:
        # 清理进程和日志文件
        if backend_process:
            backend_process.terminate()
            backend_process.wait()
            print("✅ 后端服务器已停止")
        
        if frontend_process:
            frontend_process.terminate()
            frontend_process.wait()
            print("✅ 前端应用已停止")
        
        # 关闭日志文件
        if backend_log_file:
            backend_log_file.close()
        if frontend_log_file:
            frontend_log_file.close()
        
        print("👋 系统已完全停止")

if __name__ == "__main__":
    main() 