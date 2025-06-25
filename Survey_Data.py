import pandas as pd
import re

class SurveyData:
    """
    处理问卷调查数据的类，支持从Excel文件读取数据，
    解析题目信息，获取被试答题数据等功能。
    """
    def __init__(self, filename):
        self.df = pd.read_excel(filename, dtype=str)
        self.df = self.df.fillna(value=pd.NA)
        self.qinfo = self.parse_headers(self.df.columns)

    def parse_headers(self, columns):
        """
        解析DataFrame的列名，提取题目信息。
        返回一个DataFrame，包含题号、题型、简化名称等信息。
        """
        qinfos = []
        for col in columns:
            # 提取原始题号前缀，如S66、M10、F3等
            m = re.match(r'^([A-Za-z]+\d+)', col)
            if m:
                original_qid = m.group(1)
            else:
                original_qid = ''  # 如果没有，元数据列/无编号
            # 默认值
            qtype, qid = 'META', ''
            # 判断题型
            if 'single choice' in col.lower():
                qtype = 'S'
            elif 'multiple choice' in col.lower():
                qtype = 'M'
            elif 'open-ended' in col.lower():
                qtype = 'F'
            elif 'rank' in col.lower():
                qtype = 'R'
            # 提取题号（如有，可选）
            m = re.match(r'[SMF]?(\d+)', col)
            if m:
                qid = m.group(1)
            short_name = self.simplify_colname(col)
            qinfos.append({
                'raw_col': col,
                'original_qid': original_qid,
                'question_id': qid,
                'qtype': qtype,
                'short_name': short_name
            })
        return pd.DataFrame(qinfos)

    @staticmethod
    def simplify_colname(col):
        """简化表头。保留_后内容，如果没有_则保留原内容。"""
        parts = col.split('_', 1)
        if len(parts) == 2 and parts[1].strip():
            return parts[1][:60].replace('\n','').strip()
        else:
            return col[:60].replace('\n','').strip()  # 保留60字符、去换行和前后空白

    def get_columns_by_type(self, qtype):
        return self.qinfo.loc[self.qinfo['qtype'] == qtype, 'raw_col'].tolist()
    
    def get_columns_by_original_qid(self, original_qid):
        mask = self.qinfo['original_qid'] == original_qid
        cols = self.qinfo.loc[mask, 'raw_col'].tolist()
        if not cols:
            # 可用print也可用raise，更严谨用raise
            raise ValueError(f"没有找到题号 '{original_qid}' 对应的题目字段，请检查题号是否输入正确。")
        return cols

    def get_question_info(self, col):
        """
        根据列名获取题目信息。
        """
        row = self.qinfo[self.qinfo.raw_col == col]
        if row.empty:
            return {}
        return row.iloc[0].to_dict()

    def get_answer(self, respondent_id):
        """
        根据ID获取被试的答题数据。
        """
        row = self.df[self.df['ID'] == respondent_id]
        if row.empty:
            return {}
        return row.iloc[0].to_dict()

    def get_answers_by_qid(self, original_qid, return_qtype=False):
        """
        返回指定原始题号的所有原始列数据（DataFrame）
        return_qtype: 若True同时返回主要题型
        """
        # 1. 找所有相关列名（原始列）
        mask = self.qinfo['original_qid'] == original_qid
        cols = self.qinfo.loc[mask, 'raw_col'].tolist()
        if not cols:
            raise ValueError(f"没有找到题号'{original_qid}'，请检查输入。")
        # 2. 切DataFrame取实际答案数据
        answers = self.df[cols]
        if not return_qtype:
            return answers
        else:
            # 返回主要题型（可能有多列题型不一致，这里取第一个为主）
            match_rows = self.qinfo[mask]
            qtype = match_rows.iloc[0]['qtype'] if not match_rows.empty else None
            return answers, qtype

# ==== 示例测试 ====
if __name__ == '__main__':
    survey = SurveyData('../survey_data/US/D2426-US.xlsx')
    try:
        answers, qtype = survey.get_answers_by_qid('S66')
        print(f"题型: {qtype}")
        print(f"S66的所有作答数据如下：")
        print(answers.head())
        print(f"共有{answers.shape[1]}个选项/列")
    except Exception as e:
        print(e)