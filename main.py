import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="Steel Property Dashboard", layout="wide")
st.title("钢铁力学性能数据汇总平台")

uploaded_files = st.file_uploader(
    "上传钢铁力学性能 Excel 文件（可多选）",
    type=["xlsx", "xls"],
    accept_multiple_files=True
)

if uploaded_files:
    all_dfs = []
    for file in uploaded_files:
        try:
            df = pd.read_excel(file)
            df["来源文件"] = file.name
            all_dfs.append(df)
        except Exception as e:
            st.warning(f"文件 {file.name} 读取失败：{e}")

    if all_dfs:
        merged_df = pd.concat(all_dfs, ignore_index=True)
        st.success(f"成功合并 {len(uploaded_files)} 个文件，共 {len(merged_df)} 行数据")

        st.subheader("合并后的数据预览")
        st.dataframe(merged_df, use_container_width=True)

        st.subheader("力学性能可视化")

        numeric_cols = merged_df.select_dtypes(include=["float64", "int64"]).columns.tolist()

        if numeric_cols:
            col1, col2 = st.columns(2)

            with col1:
                y_axis = st.selectbox("选择要展示的性能指标", numeric_cols)

            with col2:
                possible_group_cols = [c for c in merged_df.columns 
                                       if "钢" in str(c) or "牌号" in str(c) or "种类" in str(c)]
                if possible_group_cols:
                    group_col = st.selectbox("按什么分组", possible_group_cols)
                else:
                    group_col = "来源文件"
                    st.info("未识别到钢种列，默认按来源文件分组展示")

            chart_data = merged_df.groupby(group_col)[y_axis].mean().reset_index()
            st.bar_chart(chart_data, x=group_col, y=y_axis)
            st.caption(f"图表说明：按 {group_col} 分组的 {y_axis} 平均值")

            st.subheader("趋势对比")
            st.line_chart(merged_df, x=group_col, y=y_axis)

        st.subheader("导出结果")
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            merged_df.to_excel(writer, index=False, sheet_name="合并汇总")
        excel_data = output.getvalue()

        st.download_button(
            label="下载合并后的 Excel",
            data=excel_data,
            file_name="steel_property_summary.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
else:
    st.info("请上传 Excel 文件开始使用")
