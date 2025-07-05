import streamlit as st
import pandas as pd

def render_knowledge_map_page(api_service, current_user):
    """渲染知识图谱页面"""
    st.write("### 🗺️ 我的知识图谱")
    if not current_user:
        st.warning("请先选择用户")
        return
    
    st.info(f"👨‍🎓 当前学习者：**{current_user}**")
    
    # 获取知识图谱数据
    knowledge_map_data = api_service.get_knowledge_map(current_user)
    
    # 转换为DataFrame格式
    if knowledge_map_data:
        df_data = []
        for item in knowledge_map_data:
            df_data.append({
                '知识点': item.get('node_name', ''),
                '我的掌握度': item.get('mastery', 0.0),
                '难度': item.get('difficulty', 1)
            })
        df = pd.DataFrame(df_data)
    else:
        df = pd.DataFrame(columns=['知识点', '我的掌握度', '难度'])

    # 知识图谱概览
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

    # 详细知识图谱表格
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
            )
        },
        use_container_width=True,
        hide_index=True
    )

    # 掌握度可视化分析
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

    # 学习建议
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