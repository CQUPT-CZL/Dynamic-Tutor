import streamlit as st
import sqlite3
from streamlit_mermaid import st_mermaid

DB_FILE = "./my_database.db"

def generate_mermaid_code():
    # --- 同样先从数据库读取数据 ---
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    nodes = cursor.execute("SELECT node_id, node_name FROM knowledge_nodes").fetchall()
    edges = cursor.execute("SELECT source_node_id, target_node_id FROM knowledge_edges WHERE relation_type = 'is_prerequisite_for'").fetchall()
    conn.close()

    # --- 动态生成Mermaid代码字符串 ---
    mermaid_string = "graph TD;\n" # TD表示从上到下
    for node_id, node_name in nodes:
        # Mermaid节点语法: ID["显示文本"]
        mermaid_string += f'    {node_id}["{node_name}"];\n'

    for source_id, target_id in edges:
        # Mermaid边语法: A --> B
        mermaid_string += f'    {source_id} --> {target_id};\n'

    return mermaid_string

# --- 在Streamlit页面中渲染 ---
st.title("📚 知识图谱-Mermaid动态展示")

mermaid_code = generate_mermaid_code()
st_mermaid(mermaid_code, height="600px")

# 也可以把代码本身展示出来
with st.expander("查看Mermaid源代码"):
    st.code(mermaid_code, language="mermaid")

## streamlit run show_KG.py 