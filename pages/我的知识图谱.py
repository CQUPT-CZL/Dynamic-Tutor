import streamlit as st
import pandas as pd

# --- 模拟后端逻辑 ---
def get_user_knowledge_map(user_id):
    """模拟获取用户的知识图谱掌握情况"""
    base_map = {
        "ECH_DY": {"name": "二次函数定义", "difficulty": 1},
        "ECH_TXXZ": {"name": "图像与性质", "difficulty": 3},
        "ECH_JXS": {"name": "三种解析式", "difficulty": 2},
        "ECH_ZZWT": {"name": "最值问题", "difficulty": 4},
        "ECH_GX": {"name": "与方程/不等式关系", "difficulty": 3}
    }
    
    user_progress = {
        "小明": {"ECH_GX": 0.4, "ECH_DY": 0.9},
        "小红": {"ECH_DY": 1.0, "ECH_TXXZ": 0.8},
        "小刚": {}
    }
    
    user_map = []
    for node_id, details in base_map.items():
        mastery = user_progress.get(user_id, {}).get(node_id, 0.0) # 默认为0
        user_map.append({
            "知识点ID": node_id,
            "知识点名称": details["name"],
            "难度": "⭐" * details["difficulty"],
            "我的掌握度": mastery
        })
    return pd.DataFrame(user_map)
    

# --- 页面渲染 ---
st.set_page_config(page_title="我的知识图谱", page_icon="🗺️")

if not st.session_state.user_id:
    st.warning("请先在主程序页面选择学生！")
    st.stop()

st.title(f"🗺️ {st.session_state.user_id}的“函数”知识图谱")
st.write("这里展示了你对各个知识点的掌握情况，AI会根据这个来为你推荐学习任务哦！")

df = get_user_knowledge_map(st.session_state.user_id)

# 用进度条来可视化掌握度
st.dataframe(
    df,
    column_config={
        "我的掌握度": st.column_config.ProgressColumn(
            "掌握度",
            help="系统评估你对该知识点的掌握程度",
            format="%.2f",
            min_value=0.0,
            max_value=1.0,
        ),
    },
    hide_index=True,
    use_container_width=True
)