import streamlit as st
import pandas as pd

# --- 页面基础设置 ---
st.set_page_config(
    page_title="知识图谱", 
    page_icon="🗺️",
    layout="wide"
)

# --- 自定义CSS样式 ---
st.markdown("""
<style>
.knowledge-header {
    background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
    padding: 1.5rem 2rem;
    border-radius: 15px;
    margin-bottom: 2rem;
    color: white;
    text-align: center;
}
.knowledge-card {
    background: white;
    padding: 2rem;
    border-radius: 15px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    margin: 1rem 0;
    border-left: 5px solid #667eea;
}
.stats-box {
    background: #f8f9fa;
    padding: 1.5rem;
    border-radius: 10px;
    text-align: center;
    margin: 1rem 0;
}
</style>
""", unsafe_allow_html=True)

# --- 检查用户状态 ---
if 'user_id' not in st.session_state or not st.session_state.user_id:
    st.warning("⚠️ 请先在主页选择学习者！")
    if st.button("🏠 返回主页"):
        st.switch_page("main.py")
    st.stop()

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
        "小红": {"ECH_DY": 1.0, "ECH_TXXZ": 0.8, "ECH_JXS": 0.6},
        "小刚": {"ECH_DY": 0.3}
    }
    
    user_map = []
    for node_id, details in base_map.items():
        mastery = user_progress.get(user_id, {}).get(node_id, 0.0)
        user_map.append({
            "知识点ID": node_id,
            "知识点名称": details["name"],
            "难度": "⭐" * details["difficulty"],
            "我的掌握度": mastery
        })
    return pd.DataFrame(user_map)

# --- 页面标题 ---
st.markdown('<div class="knowledge-header"><h1>🗺️ 我的知识图谱</h1><p>可视化你的学习进度和知识掌握情况</p></div>', unsafe_allow_html=True)

# --- 用户信息显示 ---
col1, col2, col3 = st.columns([2, 1, 1])
with col1:
    st.info(f"👨‍🎓 当前学习者：**{st.session_state.user_id}**")
with col2:
    if st.button("🔄 刷新数据", type="primary"):
        st.rerun()
with col3:
    if st.button("🏠 返回主页"):
        st.switch_page("main.py")

# --- 获取知识图谱数据 ---
df = get_user_knowledge_map(st.session_state.user_id)

# --- 知识图谱概览 ---
st.markdown('<div class="knowledge-card">', unsafe_allow_html=True)
st.write("### 📊 学习概览")

col1, col2, col3, col4 = st.columns(4)
with col1:
    total_nodes = len(df)
    st.metric("总知识点", f"{total_nodes}个")
with col2:
    mastered_nodes = len(df[df['我的掌握度'] >= 0.8])
    st.metric("已掌握", f"{mastered_nodes}个", f"{mastered_nodes/total_nodes:.0%}")
with col3:
    learning_nodes = len(df[(df['我的掌握度'] >= 0.3) & (df['我的掌握度'] < 0.8)])
    st.metric("学习中", f"{learning_nodes}个", f"{learning_nodes/total_nodes:.0%}")
with col4:
    avg_mastery = df['我的掌握度'].mean()
    st.metric("平均掌握度", f"{avg_mastery:.1%}")

st.markdown('</div>', unsafe_allow_html=True)

# --- 详细知识图谱表格 ---
st.write("### 📋 详细知识点掌握情况")
st.dataframe(
    df,
    column_config={
        "我的掌握度": st.column_config.ProgressColumn(
            "掌握度",
            help="系统评估你对该知识点的掌握程度",
            min_value=0,
            max_value=1,
            format="%.1%"
        ),
        "知识点ID": st.column_config.TextColumn(
            "知识点ID",
            help="知识点的唯一标识符"
        ),
        "知识点名称": st.column_config.TextColumn(
            "知识点名称",
            help="知识点的具体名称"
        ),
        "难度": st.column_config.TextColumn(
            "难度等级",
            help="知识点的难度等级，⭐越多越难"
        )
    },
    use_container_width=True,
    hide_index=True
)

# --- 掌握度可视化分析 ---
st.write("### 📈 掌握度可视化分析")

col1, col2 = st.columns(2)
with col1:
    st.write("#### 各知识点掌握度")
    mastery_data = df.set_index('知识点名称')['我的掌握度']
    st.bar_chart(mastery_data)

with col2:
    st.write("#### 掌握度分布")
    # 创建掌握度分布数据
    mastery_levels = {
        "未开始 (0%)": len(df[df['我的掌握度'] == 0]),
        "初学 (1-30%)": len(df[(df['我的掌握度'] > 0) & (df['我的掌握度'] <= 0.3)]),
        "学习中 (31-79%)": len(df[(df['我的掌握度'] > 0.3) & (df['我的掌握度'] < 0.8)]),
        "已掌握 (80%+)": len(df[df['我的掌握度'] >= 0.8])
    }
    
    distribution_df = pd.DataFrame(list(mastery_levels.items()), columns=['掌握度等级', '知识点数量'])
    st.bar_chart(distribution_df.set_index('掌握度等级'))

# --- 学习建议 ---
st.write("### 💡 个性化学习建议")

if avg_mastery >= 0.8:
    st.success("🎉 太棒了！你的平均掌握度达到了优秀水平！")
    st.info("💪 建议：可以挑战更高难度的知识点，或者帮助其他同学学习。")
elif avg_mastery >= 0.6:
    st.info("👍 不错！你的学习进展良好，继续保持！")
    weak_points = df[df['我的掌握度'] < 0.5]['知识点名称'].tolist()
    if weak_points:
        st.warning(f"🎯 重点关注：{', '.join(weak_points)}")
else:
    st.warning("💪 还有很大提升空间，建议制定系统的学习计划！")
    priority_points = df.nsmallest(2, '我的掌握度')['知识点名称'].tolist()
    st.info(f"📚 优先学习：{', '.join(priority_points)}")

# --- 推荐学习路径 ---
st.write("### 🛤️ 推荐学习路径")

# 根据难度和掌握度推荐学习顺序
df_sorted = df.sort_values(['难度', '我的掌握度'])
unmastered = df_sorted[df_sorted['我的掌握度'] < 0.8]

if len(unmastered) > 0:
    st.write("根据你当前的掌握情况，建议按以下顺序学习：")
    for i, (_, row) in enumerate(unmastered.iterrows(), 1):
        progress_color = "🔴" if row['我的掌握度'] < 0.3 else "🟡" if row['我的掌握度'] < 0.8 else "🟢"
        st.write(f"{i}. {progress_color} **{row['知识点名称']}** ({row['难度']}) - 当前掌握度: {row['我的掌握度']:.1%}")
else:
    st.success("🎊 恭喜！你已经掌握了所有当前的知识点！")

# --- 快速导航 ---
st.write("### 🚀 快速开始学习")
col1, col2 = st.columns(2)
with col1:
    if st.button("📋 开始今日任务", use_container_width=True):
        st.switch_page("pages/今日任务.py")
with col2:
    if st.button("📚 自由练习", use_container_width=True):
        st.switch_page("pages/自由练习.py")