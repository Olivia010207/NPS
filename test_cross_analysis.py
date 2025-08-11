import pandas as pd
import numpy as np
import os

from metrics_cal import nps_table
# 用户可配置的分析列 - 请替换为实际存在的列名
NPS_question = 'S2'#nps(修正为实际存在的NPS列名)
mutiple_question = 'S64'#多选
single_question = 'S61'#单选
import tempfile
from Survey_Data import SurveyData
from analysis import cross_analysis_handler


def create_test_data():
    # 使用SurveyData类加载真实数据
    real_data_path = os.path.join(os.path.dirname(__file__), 'SurveyResults_2025-05-09-03-24-30.xlsx')
    survey = SurveyData(real_data_path)
    
    # 打印可用列信息供用户参考
    print("\n=== 可用分析列 ===")
    #print("原始列名:", survey.df.columns.tolist())
    print("问题ID列表:", survey.qinfo['original_qid'].unique().tolist())
    print("==================\n")
    
    return survey


def test_cross_analysis():
    # 加载真实数据
    survey = create_test_data()
    try:
        # 场景1: 单选题 vs 多选题
        print("=== 场景1: 单选题(Q1) vs 多选题(Q2) ===")
        cross_args1 = {
            'row_qid': single_question,
            'col_qid': mutiple_question,

        }
        result1 = cross_analysis_handler(survey, cross_args1)
        print("交叉表:")
        print(result1)
        print()

        # 场景2: NPS题 vs 多选题
        print("=== 场景2: NPS题(Q3) vs 多选题(Q2) ===")
        cross_args2 = {
            'row_qid': NPS_question,
            'col_qid': mutiple_question,
            'is_nps': True
        }
        result2 = cross_analysis_handler(survey, cross_args2)
        print("交叉表:")
        print(result2)
        print()

        # 场景3: 多选题 vs 单选题
        print("=== 场景3: 多选题(Q2) vs 单选题(Q4) ===")
        cross_args3 = {
            'row_qid': mutiple_question,
            'col_qid': single_question,

        }
        result3 = cross_analysis_handler(survey, cross_args3)
        print("交叉表:")
        print(result3)
        print()

        print("=== 场景4: 多选题(Q2) vs 单选题(Q4) ===")
        cross_args4 = {
            'row_qid': mutiple_question,
            'col_qid': 'S28',

        }
        result4 = cross_analysis_handler(survey, cross_args4)
        print("交叉表:")
        print(result4)
        print()

    finally:
        pass  # 真实数据文件无需删除


if __name__ == '__main__':
    test_cross_analysis()