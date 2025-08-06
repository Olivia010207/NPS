import pandas as pd
import numpy as np
import os

from metrics_cal import calc_nps_from_series
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
            'row_col': single_question,
            'col_col': mutiple_question,
            'is_numeric': True,
        }
        result1 = cross_analysis_handler(survey, cross_args1)
        for key, df in result1.items():
            print(f"交叉表 - {key}:")
            print(df)
            print()

        # 场景2: NPS题 vs 多选题
        print("=== 场景2: NPS题(Q3) vs 多选题(Q2) ===")
        cross_args2 = {
            'row_col': NPS_question,
            'col_col': mutiple_question,
            'is_numeric': True,
            'stat_func': calc_nps_from_series,
            'stat_row_name': 'nps'
        }
        result2 = cross_analysis_handler(survey, cross_args2)
        for key, df in result2.items():
            print(f"交叉表 - {key}:")
            print(df)
            print()

        # 场景3: 多选题 vs 单选题
        print("=== 场景3: 多选题(Q2) vs 单选题(Q4) ===")
        cross_args3 = {
            'row_col': mutiple_question,
            'col_col': single_question,
            'is_numeric': False
        }
        result3 = cross_analysis_handler(survey, cross_args3)
        for key, df in result3.items():
            print(f"交叉表 - {key}:")
            print(df)
            print()

    finally:
        pass  # 真实数据文件无需删除


if __name__ == '__main__':
    test_cross_analysis()