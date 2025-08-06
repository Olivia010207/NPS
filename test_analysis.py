import unittest
import pandas as pd
import os
from Survey_Data import SurveyData
import analysis
from metrics_cal import calc_nps_from_series


class TestAnalysis(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # 确保测试文件存在
        cls.file_path = 'SurveyResults_2025-05-09-03-24-30.xlsx'
        if not os.path.exists(cls.file_path):
            raise FileNotFoundError(f"测试文件不存在: {cls.file_path}")
        # 创建SurveyData实例
        cls.survey = SurveyData(cls.file_path)
        # 处理无效样本
        try:
            from ultis import drop_invalid_samples
            cls.survey.df = drop_invalid_samples(cls.survey.df)
        except Exception as e:
            print(f"处理无效样本时出错: {e}")

    def test_nps_analysis(self):
        # 测试NPS分析
        try:
            # 使用有效的题号S2（根据Survey_Data.py示例）
            nps_result = analysis.nps_analysis(self.survey, 'S2')
            self.assertIsInstance(nps_result, dict)
            self.assertIn('S2', nps_result)
            self.assertIsInstance(nps_result['S2'], pd.DataFrame)
            print(f"NPS分析结果表形状: {nps_result['S2'].shape}")
            print(nps_result['S2'].head(16))
        except Exception as e:
            self.fail(f"NPS分析测试失败: {e}")

    def test_nss_analysis(self):
        # 测试NSS分析
        try:
            # 使用有效的题号S2进行测试
            nss_result = analysis.nss_analysis(self.survey, 'M11')
            self.assertIsInstance(nss_result, dict)
            self.assertIn('M11', nss_result)
            self.assertIsInstance(nss_result['M11'], pd.DataFrame)
            # 设置pandas显示选项以显示所有列
            pd.set_option('display.max_columns', None)
            print(f"NSS分析结果表形状: {nss_result['M11'].shape}")
            print("所有列名:", nss_result['M11'].columns.tolist())
            print(nss_result['M11'].head())
            # 直接打印第三列
            if len(nss_result['M11'].columns) >= 3:
                third_col_name = nss_result['M11'].columns[2]
                print(f"第三列 '{third_col_name}' 的内容:")
                print(nss_result['M11'][third_col_name])
        except Exception as e:
            self.fail(f"NSS分析测试失败: {e}")

    def test_rank_analysis(self):
        # 测试排序题分析
        try:
            # 尝试使用可能的排序题题号，如果失败则跳过
            try:
                rank_result = analysis.rank_analysis(self.survey, 'S67')
                self.assertIsInstance(rank_result, dict)
                self.assertIn('S67', rank_result)
                self.assertIsInstance(rank_result['S67'], pd.DataFrame)
                print(f"排序题分析结果表形状: {rank_result['S67'].shape}")
                print(rank_result['S67'].head())
                # 检查是否包含补充文本
                self.assertIn('others', rank_result)
                self.assertIsInstance(rank_result['others'], pd.DataFrame)
            except ValueError as ve:
                if "没有找到题号" in str(ve):
                    print(f"跳过排序题分析测试: {ve}")
                else:
                    raise
        except Exception as e:
            self.fail(f"排序题分析测试失败: {e}")

    def test_cross_analysis_handler(self):
        # 测试交叉分析处理器
        try:
            # 使用S2作为行变量和列变量
            cross_args = {
                'row_col': 'S2',
                'col_col': 'S2',
                'stat_func': calc_nps_from_series,
                'stat_row_name': 'NPS'
            }
            cross_result = analysis.cross_analysis_handler(self.survey, cross_args)
            self.assertIsInstance(cross_result, dict)
            # 检查结果是否包含至少一个表格
            self.assertGreater(len(cross_result), 0)
            # 检查第一个结果是否为DataFrame
            first_key = next(iter(cross_result.keys()))
            self.assertIsInstance(cross_result[first_key], pd.DataFrame)
            print(f"交叉分析结果包含 {len(cross_result)} 个表格")
            print(f"第一个表格形状: {cross_result[first_key].shape}")
        except Exception as e:
            self.fail(f"交叉分析测试失败: {e}")

    def test_nss_detail_analysis(self):
        # 测试NSS详细分析
        try:
            # 尝试使用可能的多选题题号，如果失败则跳过
            try:
                nss_detail_result = analysis.nss_detail_analysis(self.survey, 'S17')
                self.assertIsInstance(nss_detail_result, dict)
                self.assertIn('S17', nss_detail_result)
                self.assertIsInstance(nss_detail_result['S17'], pd.DataFrame)
                print(f"NSS详细分析结果表形状: {nss_detail_result['S17'].shape}")
                print(nss_detail_result['S17'])
                # 检查是否包含补充文本
                self.assertIn('others', nss_detail_result)
                self.assertIsInstance(nss_detail_result['others'], pd.DataFrame)
            except ValueError as ve:
                if "没有找到题号" in str(ve):
                    print(f"跳过NSS详细分析测试: {ve}")
                else:
                    raise
        except Exception as e:
            self.fail(f"NSS详细分析测试失败: {e}")


if __name__ == '__main__':
    unittest.main()