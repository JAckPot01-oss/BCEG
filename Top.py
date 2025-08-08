import pandas as pd
import streamlit as st
from io import BytesIO

st.set_page_config(page_title="年度前10大客户统计", layout="wide")

st.title("📊 年度前10大客户分析（营业收入入账值）")

# 上传文件
uploaded_files = st.file_uploader(
    "上传 2022–2025 年的收入 CSV 文件（UTF-8 编码）",
    type=["csv"],
    accept_multiple_files=True
)

if uploaded_files:
    top10_results = {}

    for uploaded_file in uploaded_files:
        # 获取年份（假设文件名中包含年份）
        file_name = uploaded_file.name
        year = ''.join(filter(str.isdigit, file_name))[:4]  # 从文件名提取前4位数字作为年份

        # 读取数据
        df = pd.read_csv(uploaded_file, encoding='utf-8', engine='python')

        # 清理列名
        df = df.rename(columns=lambda x: x.strip())

        # 选择列
        if '客商名称' not in df.columns or '营业收入入账值' not in df.columns:
            st.error(f"❌ {file_name} 缺少 '客商名称' 或 '营业收入入账值' 列")
            continue

        cleaned_data = df[['客商名称', '营业收入入账值']].copy()
        cleaned_data.columns = ['客户名称', '销售额']

        # 删除空值并合并同名客户
        cleaned_data = cleaned_data.dropna(subset=['销售额'])
        cleaned_data = cleaned_data.groupby('客户名称', as_index=False)['销售额'].sum()

        # 转换为万元
        cleaned_data['销售额'] = cleaned_data['销售额'] / 10000

        # 按销售额排序并取前10
        top10 = cleaned_data.sort_values(by='销售额', ascending=False).head(10)
        top10_results[year] = top10

        # 显示结果表
        st.subheader(f"{year} 年前10大客户")
        st.dataframe(top10, use_container_width=True)

    # 如果所有年份都有数据，则生成 Excel
    if top10_results:
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            for year, df_top10 in top10_results.items():
                df_top10.to_excel(writer, sheet_name=str(year), index=False)
        excel_data = output.getvalue()

        st.download_button(
            label="📥 下载前10大客户Excel文件",
            data=excel_data,
            file_name="Top10_Customers_2022_2025.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )