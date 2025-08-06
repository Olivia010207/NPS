import unittest
import pandas as pd
import numpy as np
from metrics_cal import (
    calc_nps_from_series,
    nps_table,
    calc_nss_table,
    rank_table,
    calc_nss_detail,
    collect_openended_texts,
    cross_analysis
)
from ultis import to_numeric_series


class TestMetricsCal(unittest.TestCase):
    def setUp(self):
        # 创建测试数据
        self.nps_series = pd.Series([10, 9, 8, 7, 6, 5, 10, 9, 8, 7])
        self.empty_series = pd.Series([np.nan, np.nan])
        self.satisfaction_df = pd.DataFrame({
            'Q1': [5, 4, 3, 2, 1, 5, 4, 3],
            'Q2': [5, 5, 4, 4, 3, 2, 1, 5]
        })
        self.rank_df = pd.DataFrame({
            'Option1': [1, 2, 3, np.nan, 1],
            'Option2': [2, 1, 1, 2, np.nan],
            'Option3': [3, 3, 2, 1, 2]
        })
        self.openended_df = pd.DataFrame({
            'Comment1': ['Good', '', 'Excellent', np.nan],
            'Comment2': ['Bad', 'Poor', np.nan, 'Terrible']
        })
        self.cross_row_series = pd.Series([10, 9, 8, 7, 6, 5, 10, 9, 8, 7])
        self.cross_col_series = pd.Series(['A', 'A', 'A', 'B', 'B', 'B', 'C', 'C', 'C', 'C'])

    def test_calc_nps_from_series(self):
        # 测试正常情况
        nps, score_pct, pct_recommend, pct_passive, pct_detractor = calc_nps_from_series(self.nps_series)
        self.assertAlmostEqual(nps, 20.0)
        self.assertEqual(pct_recommend, 40.0)
        self.assertEqual(pct_passive, 40.0)
        self.assertEqual(pct_detractor, 20.0)
        self.assertEqual(len(score_pct), 11)

        # 测试空序列
        result = calc_nps_from_series(self.empty_series)
        # 函数应该返回5个值，即使是空序列
        self.assertEqual(len(result), 5)
        self.assertEqual(result[0], 0)
        self.assertEqual(result[1], 0)
        self.assertEqual(result[2], 0)
        self.assertEqual(result[3], 0)
        # 第五个值可能是缺失的，根据函数实现

    def test_nps_table(self):
        df = nps_table(self.nps_series)
        self.assertIsInstance(df, pd.DataFrame)
        self.assertEqual(df.shape, (16, 2))  # 11个分数 + 4个分类 + 1个NPS + 1个Base
        self.assertEqual(df.iloc[0, 1], 10)  # Base样本数
        self.assertEqual(df.iloc[-1, 0], 'NPS')  # 最后一行是NPS

    def test_calc_nss_table(self):
        # 测试Series输入 (提供short_names字典)
        short_names_series = {'Q1': '问题1'}
        df = calc_nss_table(self.satisfaction_df['Q1'], short_names_series)
        self.assertIsInstance(df, pd.DataFrame)
        self.assertEqual(df.shape, (1, 10))
        self.assertEqual(df.iloc[0, 0], '问题1')

        # 测试DataFrame输入 (提供short_names字典)
        short_names_df = {'Q1': '问题1', 'Q2': '问题2'}
        df = calc_nss_table(self.satisfaction_df, short_names_df)
        self.assertIsInstance(df, pd.DataFrame)
        self.assertEqual(df.shape, (2, 10))

        # 测试带有short_names (使用字典形式)
        short_names = {'Q1': '问题1', 'Q2': '问题2'}
        df = calc_nss_table(self.satisfaction_df, short_names)
        self.assertEqual(df.iloc[0, 0], '问题1')
        self.assertEqual(df.iloc[1, 0], '问题2')

    def test_rank_table(self):
        option_cols = ['Option1', 'Option2', 'Option3']
        df = rank_table(self.rank_df, 5, option_cols)
        self.assertIsInstance(df, pd.DataFrame)
        self.assertEqual(df.shape, (3, 9))  # 3个选项 × (2 + 5 + 2)列

        # 测试带有short_names
        short_names = {'Option1': '选项1', 'Option2': '选项2', 'Option3': '选项3'}
        df = rank_table(self.rank_df, 5, option_cols, short_names)
        self.assertEqual(df.iloc[0, 0], '选项1')
        self.assertEqual(df.iloc[1, 0], '选项2')
        self.assertEqual(df.iloc[2, 0], '选项3')

    def test_calc_nss_detail(self):
        option_cols = ['Q1', 'Q2']
        df = calc_nss_detail(self.satisfaction_df, option_cols)
        self.assertIsInstance(df, pd.DataFrame)
        self.assertEqual(df.shape, (3, 3))  # Base + 2个选项
        self.assertEqual(df.iloc[0, 0], 'Base')
        self.assertEqual(df.iloc[1, 0], 'Q1')
        self.assertEqual(df.iloc[2, 0], 'Q2')

        # 测试带有option_names
        option_names = {'Q1': '问题1', 'Q2': '问题2'}
        df = calc_nss_detail(self.satisfaction_df, option_cols, option_names)
        self.assertEqual(df.iloc[1, 0], '问题1')
        self.assertEqual(df.iloc[2, 0], '问题2')

    def test_collect_openended_texts(self):
        txt_cols = ['Comment1', 'Comment2']
        comments = collect_openended_texts(self.openended_df, txt_cols)
        self.assertIsInstance(comments, list)
        self.assertEqual(len(comments), 5)  # Good, Excellent, Bad, Poor, Terrible
        self.assertIn('Good', comments)
        self.assertIn('Excellent', comments)
        self.assertIn('Bad', comments)
        self.assertIn('Poor', comments)
        self.assertIn('Terrible', comments)

    def test_cross_analysis(self):
        # 测试基本交叉表
        df = cross_analysis(self.cross_row_series, self.cross_col_series)
        self.assertIsInstance(df, pd.DataFrame)
        # 实际行数取决于不同分数的数量 + 1个Base行
        self.assertEqual(df.shape[1], 3)  # 3列: A, B, C
        self.assertIn('Base', df.index)

        # 测试带有stat_func
        df = cross_analysis(
            self.cross_row_series, 
            self.cross_col_series, 
            stat_func=calc_nps_from_series, 
            stat_row_name='NPS'
        )
        self.assertIsInstance(df, pd.DataFrame)
        self.assertEqual(df.shape[1], 3)  # 3列: A, B, C
        self.assertEqual(df.index[-1], 'NPS')


if __name__ == '__main__':
    unittest.main()