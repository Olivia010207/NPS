import unittest
import pandas as pd
import os
from Survey_Data import SurveyData
import metrics_cal
from ultis import drop_invalid_samples


class TestMetricsWithRealData(unittest.TestCase):
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
            cls.survey.df = drop_invalid_samples(cls.survey.df)
        except Exception as e:
            print(f"处理无效样本时出错: {e}")
        # 获取NPS相关问题的数据
        try:
            cls.nps_data, _ = cls.survey.get_answers_by_qid('S2', return_qtype=True)
            # 提取第一列数据作为测试NPS的序列
            cls.nps_series = pd.to_numeric(cls.nps_data.iloc[:, 0], errors='coerce')
        except Exception as e:
            print(f"获取NPS数据时出错: {e}")
            cls.nps_series = pd.Series([5, 4, 3, 2, 1, 5, 4, 3])  # 备用测试数据

        # 获取其他问题数据用于测试
        try:
            # 获取单选题数据
            cls.single_choice_data, _ = cls.survey.get_answers_by_qid('M11', return_qtype=True)
            # 获取多选题数据
            cls.multiple_choice_data, _ = cls.survey.get_answers_by_qid('S66', return_qtype=True)
            # 获取开放题数据
            cls.open_ended_data, _ = cls.survey.get_answers_by_qid('F3', return_qtype=True)
        except Exception as e:
            print(f"获取其他问题数据时出错: {e}")

    def test_calc_nps_from_series(self):
        # 测试使用真实NPS数据计算NPS
        nps, score_pct, pct_recommend, pct_passive, pct_detractor = metrics_cal.calc_nps_from_series(self.nps_series)
        self.assertIsInstance(nps, float)
        self.assertIsInstance(score_pct, pd.Series)
        self.assertIsInstance(pct_recommend, float)
        self.assertIsInstance(pct_passive, float)
        self.assertIsInstance(pct_detractor, float)
        print(f"真实数据NPS计算结果: NPS值{nps:.2f}%, 推荐者{pct_recommend:.2f}%, 中立者{pct_passive:.2f}%, 贬损者{pct_detractor:.2f}%")

    def test_nps_table(self):
        # 测试生成NPS表格
        nps_table = metrics_cal.nps_table(self.nps_series)
        self.assertIsInstance(nps_table, pd.DataFrame)
        print(f"NPS表格形状: {nps_table.shape}")
        print(nps_table.head())

    def test_calc_nss_table(self):
        # 测试计算NSS表格
        if hasattr(self, 'single_choice_data') and not self.single_choice_data.empty:
            # 转换为数值型
            numeric_data = pd.to_numeric(self.single_choice_data.iloc[:, 0], errors='coerce')
            # 假设题目名称映射
            short_names = {'S3': '满意度问题'}
            nss_table = metrics_cal.calc_nss_table(numeric_data.to_frame(), short_names)
            self.assertIsInstance(nss_table, pd.DataFrame)
            print(f"NSS表格形状: {nss_table.shape}")
            print(nss_table.head())

    def test_cross_analysis(self):
        # 测试交叉分析
        if hasattr(self, 'single_choice_data') and hasattr(self, 'multiple_choice_data') and not self.single_choice_data.empty and not self.multiple_choice_data.empty:
            # 使用单选题作为行，多选题作为列
            row_data = self.single_choice_data.iloc[:, 0]
            col_data = self.multiple_choice_data.iloc[:, 0]
            cross_table = metrics_cal.cross_analysis(row_data, col_data)
            self.assertIsInstance(cross_table, pd.DataFrame)
            print(f"交叉分析表格形状: {cross_table.shape}")
            print(cross_table.head())

    def test_collect_openended_texts(self):
        # 测试收集开放题文本
        if hasattr(self, 'open_ended_data') and not self.open_ended_data.empty:
            # 使用开放题数据的所有列作为文本列
            txt_cols = self.open_ended_data.columns.tolist()
            open_texts = metrics_cal.collect_openended_texts(self.open_ended_data, txt_cols)
            self.assertIsInstance(open_texts, list)
            print(f"收集到的开放题文本数量: {len(open_texts)}")
            if open_texts:
                print(f"第一个开放题文本示例: {open_texts[0][:100]}...")


if __name__ == '__main__':
    unittest.main()