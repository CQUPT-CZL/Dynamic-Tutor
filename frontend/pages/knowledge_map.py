import streamlit as st
import pandas as pd

def render_knowledge_map_page(api_service, current_user, user_id):
    """渲染知识图谱页面"""
    st.write("### 🗺️ 我的知识图谱")
    if not current_user:
        st.warning("请先选择用户")
        return
    
    st.info(f"👨‍🎓 当前学习者：**{current_user}**")
    
    # 获取知识图谱数据
    print(current_user)
    print(user_id)
    knowledge_map_data = api_service.get_knowledge_map(user_id)
    print(knowledge_map_data)
    print(2)
    # 转换为DataFrame格式
    if knowledge_map_data:
        df_data = []
        for item in knowledge_map_data:
            # 确保这里使用的键名与你的API返回结果一致
            # 根据你之前的SQL查询，返回的键名应该是 'mastery_score' 和 'node_difficulty'
            df_data.append({
                '知识点名称': item.get('node_name', ''), # <<< 修正点 1: 将'知识点'改为'知识点名称'
                '我的掌握度': item.get('mastery', 0.0), # <<< 修正点 2: 键名与后端SQL查询结果保持一致
                '难度': item.get('node_difficulty', '未定义') # <<< 修正点 3: 键名与后端SQL查询结果保持一致
            })
        df = pd.DataFrame(df_data)
    else:
        # <<< 修正点 4: 创建空DataFrame时也使用正确的列名
        df = pd.DataFrame(columns=['知识点名称', '我的掌握度', '难度'])
    print(df)
    # 知识图谱概览
    st.markdown("### 📊 学习概览")
    
    # 你的这部分代码写得很好，对空数据的处理很到位！
    col1, col2, col3, col4 = st.columns(4)
    total_nodes = len(df)
    with col1:
        st.metric("总知识点", f"{total_nodes}个")
    with col2:
        mastered_nodes = len(df[df['我的掌握度'] >= 0.8])
        mastered_percentage = f"{mastered_nodes/total_nodes:.0%}" if total_nodes > 0 else "0%"
        st.metric("已掌握", f"{mastered_nodes}个", mastered_percentage)
    with col3:
        learning_nodes = len(df[(df['我的掌握度'] >= 0.3) & (df['我的掌握度'] < 0.8)])
        learning_percentage = f"{learning_nodes/total_nodes:.0%}" if total_nodes > 0 else "0%"
        st.metric("学习中", f"{learning_nodes}个", learning_percentage)
    with col4:
        avg_mastery = df['我的掌握度'].mean() if not df.empty else 0
        st.metric("平均掌握度", f"{avg_mastery:.1%}")

    # 详细知识图谱表格
    st.write("### 📋 详细知识点掌握情况")
    st.dataframe(
        df,
        column_config={
            "我的掌握度": st.column_config.ProgressColumn(
                "掌握度",
                help="系统评估你对该知识点的掌握程度",
                min_value=0.0,
                max_value=1.0,
                format="%.1f%%" # 建议用百分比格式
            )
        },
        use_container_width=True,
        hide_index=True
    )

    # 掌握度可视化分析
    if not df.empty:
        st.write("### 📈 掌握度可视化分析")

        col1, col2 = st.columns(2)
        with col1:
            st.write("#### 各知识点掌握度")
            # <<< 修正点 5: 使用正确的列名 '知识点名称' 作为索引
            mastery_data = df.set_index('知识点名称')['我的掌握度']
            st.bar_chart(mastery_data)

        with col2:
            st.write("#### 掌握度分布")
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
            st.success("🎉 太棒了！你的平均掌握度达到了优秀水平！可以挑战更高难度的知识点。")
        elif avg_mastery >= 0.6:
            st.info("👍 不错！你的学习进展良好，继续保持！")
            # <<< 修正点 6: 使用正确的列名 '知识点名称'
            weak_points = df[df['我的掌握度'] < 0.5]['知识点名称'].tolist()
            if weak_points:
                st.warning(f"🎯 **重点关注**: {', '.join(weak_points)}")
        else:
            st.warning("💪 还有很大提升空间，建议制定系统的学习计划！")
            # <<< 修正点 7: 使用正确的列名 '知识点名称'
            priority_points = df.nsmallest(2, '我的掌握度')['知识点名称'].tolist()
            if priority_points:
                st.info(f"📚 **优先学习**: {', '.join(priority_points)}")