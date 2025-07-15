#!/bin/bash

# =======================================================
#      AI智慧学习平台 - 数据库强制同步脚本
# =======================================================

# --- 请在这里配置你的服务器信息 ---
# 你的阿里云服务器的公网IP地址
SERVER_IP="101.201.28.39" 
# 你登录服务器的用户名 (通常是 root 或你创建的普通用户)
SERVER_USER="czl"
# 你的项目在服务器上的绝对路径
SERVER_PROJECT_PATH="/home/czl/project/unveiling-the-list"


# --- 本地文件的路径 ---
LOCAL_DB_PATH="../data/my_database.db"

# --- 远程服务器上数据库的完整路径 ---
REMOTE_DB_PATH="${SERVER_PROJECT_PATH}/data/my_database.db"

# --- 开始执行 ---
echo "🚀 准备将本地数据库强制同步到服务器..."
echo "    - 本地文件: ${LOCAL_DB_PATH}"
echo "    - 目标服务器: ${SERVER_USER}@${SERVER_IP}"
echo "    - 目标路径: ${REMOTE_DB_PATH}"
echo ""

# 使用 scp 命令进行安全文件传输
# -i /path/to/your/key.pem 是可选的，如果你的SSH登录需要密钥文件，请取消注释并修改路径
# scp -i /path/to/your/key.pem "${LOCAL_DB_PATH}" "${SERVER_USER}@${SERVER_IP}:${REMOTE_DB_PATH}"

# 如果你是用密码登录，直接使用下面的命令
scp "${LOCAL_DB_PATH}" "${SERVER_USER}@${SERVER_IP}:${REMOTE_DB_PATH}"


# 检查上一个命令是否成功
if [ $? -eq 0 ]; then
    echo "✅ 数据库同步成功！服务器上的旧数据已被覆盖。"
    echo "下一步提醒：请登录服务器，重启你的后端服务以加载新数据。"
else
    echo "❌ 数据库同步失败！请检查你的服务器配置、网络连接或SSH权限。"
fi

