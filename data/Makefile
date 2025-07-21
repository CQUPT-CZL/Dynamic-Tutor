# Makefile for database management
# 数据库管理的Makefile文件

# 变量定义
DB_FILE = my_database.db
SCHEMA_FILE = create_tables.sql
# CSV_FILE = ./raw/filtered_high_school_bracket_image.csv
IMPORT_SCRIPT = import_data.py
IMPORT_EDGES_SCRIPT = import_edges.py
SIMULATE_SCRIPT = simulate_student_data.py

# 默认目标
.PHONY: all clean rebuild import simulate help

# 显示帮助信息
help:
	@echo "📚 数据库管理命令:"
	@echo "  make clean       - 🗑️  删除现有数据库文件"
	@echo "  make rebuild     - 🔄 重新创建数据库（删除+创建表结构）"
	@echo "  make import      - 📥 导入模拟概率伦数据到数据库"
	@echo "  make simulate    - 🎭 模拟学生学习行为数据"
	@echo "  make all         - 🚀 完整流程（重建+导入所有数据）"
	@echo "  make help        - ❓ 显示此帮助信息"

# 删除数据库文件
clean:
	@echo "🗑️ 删除数据库文件..."
	@if [ -f $(DB_FILE) ]; then \
		rm -f $(DB_FILE) && echo "✅ 数据库文件已删除"; \
	else \
		echo "ℹ️  数据库文件不存在，无需删除"; \
	fi

# 重新创建数据库（删除旧的并创建表结构）
rebuild: clean
	@echo "🔄 重新创建数据库..."
	@if [ -f $(SCHEMA_FILE) ]; then \
		sqlite3 $(DB_FILE) < $(SCHEMA_FILE) && echo "✅ 数据库表结构创建成功"; \
	else \
		echo "❌ 错误：找不到schema文件 $(SCHEMA_FILE)"; \
		exit 1; \
	fi

# 导入概率伦数据
import:
	@echo "📥 导入模拟概率伦数据..."
	@if [ -f $(IMPORT_SCRIPT) ]; then \
		python3 $(IMPORT_SCRIPT) && echo "✅ 概率伦模拟数据导入完成"; \
	else \
		echo "❌ 错误：找不到导入脚本 $(IMPORT_SCRIPT)"; \
		exit 1; \
	fi

# 模拟学生学习行为数据
simulate:
	@echo "🎭 模拟学生学习行为数据..."
	@if [ -f $(SIMULATE_SCRIPT) ]; then \
		python3 $(SIMULATE_SCRIPT) && echo "✅ 学生学习行为数据模拟完成"; \
	else \
		echo "❌ 错误：找不到模拟脚本 $(SIMULATE_SCRIPT)"; \
		exit 1; \
	fi

# 完整流程：重建数据库并导入所有数据
all: rebuild import simulate
	@echo "🎉 数据库重建和所有数据导入全部完成！"

# 检查数据库状态
status:
	@echo "📊 数据库状态检查:"
	@if [ -f $(DB_FILE) ]; then \
		echo "✅ 数据库文件存在: $(DB_FILE)"; \
		sqlite3 $(DB_FILE) ".tables" | while read table; do \
			count=$$(sqlite3 $(DB_FILE) "SELECT COUNT(*) FROM $$table;"); \
			echo "  📋 表 $$table: $$count 条记录"; \
		done; \
	else \
		echo "❌ 数据库文件不存在"; \
	fi