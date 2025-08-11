import streamlit as st
import pandas as pd
import os
from Survey_Data import SurveyData
from ultis import *
from metrics_cal import nps_table, calc_nps_from_series, calc_nss_from_series
from cross_analysis import cross_analysis
from analysis import *
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

# 检查题号列表是否为空
if not qids:
    st.sidebar.error("错误: 未找到有效题号，请检查数据格式")
    st.stop()

# 根据分析类型设置参数
if analysis_type in ['nps', 'nss', 'nss_detail', 'rank']:
    qid = st.sidebar.selectbox("选择题号", qids)
    # 运行分析按钮
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
elif analysis_type == 'cross':
    # 添加计算方式选择框
    row_col = st.sidebar.selectbox("选择行变量题号", qids)
    
    # 添加计算方式选择框
    calc_method = st.sidebar.selectbox('计算方式', ['不计算', 'NPS'], index=0)
    # 根据题型和选择设置统计函数和行名
    _, row_qtype = survey.get_answers_by_qid(row_col, return_qtype=True)

    col_col = st.sidebar.selectbox("选择列变量题号", qids)

    # 获取选项标签
    row_meta = survey.qinfo[survey.qinfo['original_qid'] == row_col].iloc[0]
    col_meta = survey.qinfo[survey.qinfo['original_qid'] == col_col].iloc[0]
    row_labels = row_meta.get('options', {})
    col_labels = col_meta.get('options', {})

    cross_args = {
        "row_qid": row_col,
        "col_qid": col_col,
        "row_labels": row_labels,
        "col_labels": col_labels,
        "is_nps": calc_method == 'NPS'
    }
    # 运行分析按钮（确保在交叉分析分支内）
    if st.sidebar.button("运行分析"):
        with st.spinner("分析中..."):
            result = cross_analysis_handler(survey, cross_args)
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