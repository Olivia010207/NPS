from metrics_cal import *
from Survey_Data import SurveyData
from ultis import *
from analysis import cross_analysis_handler, nps_analysis, nss_analysis, nss_detail_analysis, rank_analysis


def batch_analysis_and_export(survey, qids, analysis_type,
                              cross_args=None):
    """
    批量分析与导出入口函数
    输入
        survey:      SurveyData对象
        qids=[]:        单个题号（str）或题号list
        analysis_type:  'nps', 'nss', 'nss_detail', 'rank', 'cross'
        cross_args: dict，cross分析专用参数
    """
    if analysis_type == 'cross':
        return cross_analysis_handler(survey, cross_args)

    if isinstance(qids, str):
        qids = [qids]

    # 只处理单个qid的情况，多个qid的循环调用逻辑可以在外部实现
    if len(qids) > 1:
        print("警告: 当前只处理单个qid的分析，将使用第一个qid")
    qid = qids[0]

    if analysis_type == 'nps':
        return nps_analysis(survey, qid)
    elif analysis_type == 'nss':
        return nss_analysis(survey, qid)
    elif analysis_type == 'nss_detail':
        return nss_detail_analysis(survey, qid)
    elif analysis_type == 'rank':
        return rank_analysis(survey, qid)
    else:
        print(f'不支持的分析类型: {analysis_type}')
        return {}


survey = SurveyData("D:/3概念测试/0626/SurveyResults_2025-07-30-09-39-59.xlsx")
survey.df = drop_invalid_samples(survey.df)  # 只保留有效样本
# 使用工具函数处理收入分组
#process_income_group(survey)



cross_all_tab = batch_analysis_and_export(survey, 
                          qids=[], 
                          analysis_type='cross', 
                          cross_args={
                                "row_col": 'S19', 
                                "col_col": 'S13',  
                                "row_labels": {},  # 行标签映射字典
                                "col_labels": {},  # 列标签映射字典
                                "is_numeric": False  # S19是分类变量
                            }
                        )       


# for label, cross_tab in cross_all_tab.items():
#     cross_tab = add_total_column_by_percent_sum(cross_tab)
#     cross_all_tab[label] = cross_tab
# save_multi_tables_to_excel(cross_all_tab, 'M11_g1', 'cross', 'D:/1NPS_projector/survey_data/UK/nps_result')
# print('cross分析结果已保存!')
print(cross_all_tab)
#save_multi_tables_to_excel(cross_all_tab, "S69_S70", 'cross', 'D:/1NPS_projector/survey_data/UK/nps_result')