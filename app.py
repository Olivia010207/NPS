import streamlit as st
import pandas as pd
import os
from Survey_Data import SurveyData
from ultis import *
from metrics_cal import *

# 设置页面配置
st.set_page_config(
    page_title="NPS分析工具",
    page_icon="📊",
    layout="wide"
)

# 页面标题
st.title("NPS分析工具")
st.markdown("这是一个用于分析问卷调查数据的交互式工具，支持NPS、NSS、排序题等多种分析类型。")

# 文件上传部分
st.sidebar.header("数据上传")
uploaded_file = st.sidebar.file_uploader("上传Excel文件", type="xlsx")

if uploaded_file is not None:
    # 读取数据
    survey = SurveyData(uploaded_file)
    survey.df = drop_invalid_samples(survey.df)
    st.session_state['survey'] = survey
    st.success("数据加载成功！")
    
    # 显示数据概览
    with st.expander("数据概览"):
        st.write(f"总样本数: {len(survey.df)}")
        st.write("题目信息:")
        st.dataframe(survey.qinfo)
else:
    st.info("请上传Excel文件开始分析")
    st.stop()

# 分析类型选择
st.sidebar.header("分析设置")
analysis_type = st.sidebar.selectbox(
    "选择分析类型",
    ["nps", "nss", "nss_detail", "rank", "cross"]
)

# 获取题号列表
qids = survey.qinfo['original_qid'].unique().tolist()

# 根据分析类型设置参数
if analysis_type == 'cross':
    row_col = st.sidebar.selectbox("选择行变量题号", qids)
    col_col = st.sidebar.selectbox("选择列变量题号", qids)
    stat_row_name = st.sidebar.text_input("统计行名", "NPS")
    
    cross_args = {
        "row_col": row_col,
        "col_col": col_col,
        "stat_row_name": stat_row_name
    }
    
    if st.sidebar.button("运行分析"):
        with st.spinner("分析中..."):
            result = cross_analysis_handler(survey, cross_args)
            st.session_state['result'] = result
            st.success("分析完成！")
else:
    qid = st.sidebar.selectbox("选择题号", qids)
    
    if st.sidebar.button("运行分析"):
        with st.spinner("分析中..."):
            if analysis_type == 'nps':
                result = nps_analysis(survey, qid)
            elif analysis_type == 'nss':
                result = nss_analysis(survey, qid)
            elif analysis_type == 'nss_detail':
                result = nss_detail_analysis(survey, qid)
            elif analysis_type == 'rank':
                result = rank_analysis(survey, qid)
            st.session_state['result'] = result
            st.success("分析完成！")

# 显示结果
if 'result' in st.session_state:
    st.header("分析结果")
    result = st.session_state['result']
    
    if analysis_type == 'cross':
        for label, df in result.items():
            st.subheader(f"交叉分析结果: {label}")
            st.dataframe(df)
    else:
        for label, df in result.items():
            st.subheader(f"{label} 分析结果")
            st.dataframe(df)

# 导出功能
if 'result' in st.session_state:
    st.sidebar.header("导出结果")
    if st.sidebar.button("导出到Excel"):
        # 创建临时文件
        import tempfile
        with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp:
            save_multi_tables_to_excel(result, "分析结果", analysis_type, os.path.dirname(tmp.name))
            st.sidebar.success(f"结果已导出到: {tmp.name}")
            st.sidebar.download_button(
                label="下载Excel文件",
                data=open(tmp.name, 'rb'),
                file_name="分析结果.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            os.unlink(tmp.name)