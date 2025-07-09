#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库连接模块
"""

import sqlite3
import os

def get_db_connection():
    """获取数据库连接"""
    # 获取当前文件所在目录的上级目录中的data文件夹
    current_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(current_dir, '..', '..', '..', 'data', 'my_database.db')
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn 