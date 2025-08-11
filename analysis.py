from ultis import *
from metrics_cal import *
from cross_analysis import cross_analysis

def cross_analysis_handler(survey, cross_args):
    """
    处理交叉分析
    参数:
        survey: SurveyData对象
        cross_args: 交叉分析参数
    返回:
        all_tables: 包含所有交叉分析结果的字典
    """
    if not cross_args:
        raise ValueError("cross分析需指定cross_args参数")
    # 获取行列变量数据
    row_qid = cross_args['row_qid']
    col_qid = cross_args['col_qid']
    row_labels = cross_args.get('row_labels')
    is_nps = cross_args.get('is_nps', False)

    # 执行交叉分析
    cross_result = cross_analysis(
        survey=survey,
        row_qid=row_qid,
        col_qid=col_qid,
        row_labels=row_labels,
        is_nps=is_nps
    )

    # 处理结果
    all_tables = {}
    if isinstance(cross_result, dict):
        # 多选题与单选题/数值题的交叉分析结果
        all_tables.update(cross_result)
    else:
        # 获取行变量标签
        row_label = survey.qinfo.loc[survey.qinfo['original_qid'] == row_qid, 'short_name'].iloc[0]
        all_tables[row_label] = cross_result

    return all_tables

def nps_analysis(survey, qid):
    """
    处理NPS分析
    参数:
        survey: SurveyData对象
        qid: 题号
    返回:
        table: 包含NPS分析结果的字典
    """
    answers, qtype = survey.get_answers_by_qid(qid, return_qtype=True)
    check_question_type(qtype, 'S', qid)
    nps_df = nps_table(answers) 
    table = {}
    table[qid] = nps_df
    print(f'{qid} NPS 分析完成!')
    return table

def nss_analysis(survey, qid):
    """
    处理NSS分析
    参数:
        survey: SurveyData对象
        qid: 题号
    返回:
        table: 包含NSS分析结果的字典
    """
    answers, qtype = survey.get_answers_by_qid(qid, return_qtype=True)
    check_question_type(qtype, 'S', qid)
    subtitle_map = survey.qinfo.set_index('raw_col')['short_name'].to_dict()
    nss_df = calc_nss_table(answers, short_names=subtitle_map)
    table = {}
    table[qid] = nss_df
    print(f'{qid} NSS 分析完成!')
    return table

def nss_detail_analysis(survey, qid):
    """
    处理NSS详细分析
    参数:
        survey: SurveyData对象
        qid: 题号
    返回:
        table: 包含NSS详细分析结果的字典
    """
    answers, qtype = survey.get_answers_by_qid(qid, return_qtype=True)
    check_question_type(qtype, 'M', qid)
    options_cols, txt_cols, option_names, _ = preprocess_multi_choice(survey.qinfo, qid)
    multi_df = calc_nss_detail(survey.df, options_cols, option_names)
    table = {}
    table[qid] = multi_df
    print(f'{qid} NSS 分析完成!')
    
    multi_text = collect_openended_texts(survey.df, txt_cols)
    table['others'] = pd.DataFrame({'others补充': multi_text})
    print(f'{qid} NSS细节 导出完成!')
    return table

def rank_analysis(survey, qid):
    """
    处理排序题分析
    参数:
        survey: SurveyData对象
        qid: 题号
    返回:
        table: 包含排序题分析结果的字典
    """
    answers, qtype = survey.get_answers_by_qid(qid, return_qtype=True)
    check_question_type(qtype, 'R', qid)
    options_cols, txt_cols, option_names, _ = preprocess_multi_choice(survey.qinfo, qid)
    max_rank = 5
    subtitle_map = survey.qinfo.set_index('raw_col')['short_name'].to_dict()
    rank_df = rank_table(answers, max_rank, options_cols, short_names=subtitle_map)
    table = {}
    table[qid] = rank_df

    rank_text = collect_openended_texts(survey.df, txt_cols)
    table['others'] = pd.DataFrame({'others补充': rank_text})

    print(f'{qid} 排序题分析完成!')
    return table