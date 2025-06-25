from metrics_cal import *
from Survey_Data import SurveyData
from ultis import *


def batch_analysis_and_export(survey, qids, analysis_type,
                              cross_args=None):

    """
    输入
        survey:      SurveyData对象
        qids=[]:        单个题号（str）或题号list
        analysis_type:  'nps', 'nss', 'nss_detail', 'rank', 'open'
        excel_out_dir:  输出文件夹
        cross_args: dict，cross分析专用，如
        {
            "row_col":                 # 行变量题号
            "col_col":                # 列变量题号
            "row_names": [...],         # (可选)子题友好短名列表（按顺序）
            "row_labels": {...},            # (可选)行标签dict
            "col_labels": {...},            # (可选)列标签dict
            "stat_func": func,              # (可选)统计函数如calc_nps_from_series
            "stat_row_name": "NPS"          # (可选)统计行名
        }
    """
    if analysis_type == 'cross':
        # cross_args需用户传入
        if not cross_args:
            raise ValueError("cross分析需指定cross_args参数")
        # 获取行列变量数据
        list_row_col = cross_args['row_col']    # 这里直接传 Series 列表
        col_qid = cross_args['col_col']
        row_names = cross_args.get('row_names') # 子题友好短名列表（按顺序）

        if isinstance(list_row_col, str):
        # 自动查 row_col 的题型
            row_qtype = survey.qinfo.loc[survey.qinfo['original_qid'] == list_row_col, 'qtype'].iloc[0]

        if row_qtype == 'M':
            # 多选题，自动只取非填空/dummy子题
            options_cols, _, option_names, _ = preprocess_multi_choice(survey.qinfo, list_row_col)
            list_row_col = options_cols
            row_names = [option_names.get(c, c) for c in options_cols]
        else:
            # 非多选题（单选、打分矩阵等）按原来的来
            # 查到DataFrame的唯一列名
            cols = survey.get_columns_by_original_qid(list_row_col)
            list_row_col = cols
            row_names = [survey.qinfo.set_index('raw_col').loc[c, 'short_name'] for c in cols]
        
        # 获取列变量数据
        if isinstance(col_qid, str):
            col_series = survey.get_answers_by_qid(col_qid, return_qtype=False).iloc[:, 0]
            col_label = col_qid
        else:
            raise ValueError("col_col 必须传题号字符串！")
        all_tables = {}
        # 批量子题 cross_analysis
        for i, row_qid in enumerate(list_row_col):
            # 自动获取该题Series
            row_series = survey.df[row_qid]
            row_label = row_names[i] if row_names else row_qid
            cross_df = cross_analysis(
                row_series, col_series,
                row_labels=cross_args.get('row_labels'),
                col_labels=cross_args.get('col_labels'),
                stat_func=cross_args.get('stat_func'),
                stat_row_name=cross_args.get('stat_row_name'),
            )
            
            all_tables[row_label] = cross_df
        # 写入Excel，sheet名也用row_label
        # out_file_prefix = f"{cross_args['row_col']}_{col_label}"
        # save_multi_tables_to_excel(all_tables, out_file_prefix, analysis_type, excel_out_dir)
        # print(f'cross分析完成: ({cross_args['row_col']} x {col_label})')
        return all_tables

    if isinstance(qids, str):
        qids = [qids]

    for qid in qids:
        # --- 1. 获取数据 ---
        answers, qtype = survey.get_answers_by_qid(qid, return_qtype=True)
        # --- 2. 题型检查 & 分析 ---
        subtitle_map = survey.qinfo.set_index('raw_col')['short_name'].to_dict()

        if analysis_type == 'nps':
            check_question_type(qtype, 'S', qid)
            nps_df = nps_table(answers) 
            table = {}
            table[qid] = nps_df
            print(f'{qid} NPS 分析完成!')


        elif analysis_type == 'nss':
            check_question_type(qtype, 'S', qid)
            nss_df = calc_nss_table(answers, short_names=subtitle_map)
            table = {}
            table[qid] = nss_df
            print(f'{qid} NSS 分析完成!')

        elif analysis_type == 'nss_detail':
            check_question_type(qtype, 'M', qid)
            options_cols, txt_cols, option_names, _ = preprocess_multi_choice(survey.qinfo, qid)
            multi_df = calc_nss_detail(survey.df, options_cols, option_names)
            table = {}
            table[qid] = multi_df
            print(f'{qid} NSS 分析完成!')

            
            multi_text = collect_openended_texts(survey.df, txt_cols)
            table['others'] = pd.DataFrame({'others补充': multi_text})
            print(f'{qid} NSS细节 导出完成!')

        elif analysis_type == 'rank':
            check_question_type(qtype, 'R', qid)
            # max_rank可根据survey.qinfo动态获取，也可固定写5
            options_cols, txt_cols, option_names, _ = preprocess_multi_choice(survey.qinfo, qid)
            max_rank = 5
            rank_df = rank_table(answers, max_rank, options_cols, short_names=subtitle_map)
            table = {}
            table[qid] = rank_df

            rank_text = collect_openended_texts(survey.df, txt_cols)
            table['others'] = pd.DataFrame({'others补充': rank_text})

            print(f'{qid} 排序题分析完成!')
        else:
            print(f'不支持的分析类型: {analysis_type}')
    return table


survey = SurveyData('D:/1NPS_projector/survey_data/UK/UK_2425_2426.xlsx')
survey.df = drop_invalid_samples(survey.df)  # 只保留有效样本
survey.qinfo = pd.concat([
    survey.qinfo, 
    pd.DataFrame([{
        'raw_col': 'g1 income group from S68',
        'original_qid': 'g1',
        'question_id': 'g1',
        'qtype': 'S',
        'short_name': 'income group'
    }])
], ignore_index=True)
# 处理收入分组
income_col = survey.qinfo[survey.qinfo['original_qid'] == 'S68']['raw_col'].iloc[0]
income_group_mapping = {
    'a低收入': ['Less than £20,000','£20,000 - £34,999'],
    'b中收入': ['£35,000 - £54,999', '£55,000 - £79,999','£80,000 - £119,999'],
    'c高收入': ['£120,000 or more'],
    'dPrefer not to say': ['Prefer not to say']
}
survey.df['g1 income group from S68'] = map_income_group(survey.df[income_col], income_group_mapping)
survey.qinfo.loc[survey.qinfo['original_qid'] == 'S68', 'g1'] = '收入分组'



cross_all_tab = batch_analysis_and_export(survey, 
                          qids=[], 
                          analysis_type='cross', 
                          excel_out_dir='D:/1NPS_projector/survey_data/UK/nps_result'
                          ,
                          cross_args={
                                "row_col": 'S69',  # NPS分数题
                                "col_col": 'S70',  # 场景题
                                "row_labels": 'S69',  # 可选行标签
                                "col_labels": 'S70',  # 可选列标签
                                "stat_row_name": 'count'  # 统计行名
                            }
                        )       


# for label, cross_tab in cross_all_tab.items():
#     cross_tab = add_total_column_by_percent_sum(cross_tab)
#     cross_all_tab[label] = cross_tab
# save_multi_tables_to_excel(cross_all_tab, 'M11_g1', 'cross', 'D:/1NPS_projector/survey_data/UK/nps_result')
# print('cross分析结果已保存!')
print(cross_all_tab)
save_multi_tables_to_excel(cross_all_tab, "S69_S70", 'cross', 'D:/1NPS_projector/survey_data/UK/nps_result')