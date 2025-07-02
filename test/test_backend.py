#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append('.')

from backend.backend import diagnose_answer

print("🧪 测试后端诊断功能...")
print("=" * 40)

# 测试文字答案诊断
result = diagnose_answer('小明', 'q001', 'x=2, x=3', 'text')
print(f"✅ 诊断结果: {result}")

# 测试图片答案诊断
result2 = diagnose_answer('小红', 'q002', 'image_data_here', 'image')
print(f"✅ 图片诊断结果: {result2}")

print("\n🎉 后端功能测试完成！")
print("📋 请检查 logs/ 目录下的日志文件")