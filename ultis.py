import pandas as pd
import re
def drop_invalid_samples(df, status_col='样本状态', valid_value='有效'):
    """
    输入
        去除“样本状态”列不等于指定值（如“有效”）的行
        df:          原始DataFrame
        status_col:  样本状态列名，默认为“样本状态”
        valid_value: 有效标记字符串，默认为“有效”
    返回:        仅保留有效样本的数据表
    """
    # 只保留状态为“有效”的行
    df_valid = df[df[status_col] == valid_value].copy()
    return df_valid

def check_question_type(qtype, expected_types, qid=None):
    """
    检查一个或一组题型qtype是否全部都在expected_types内，否则抛出异常。
    - qtype: 可以是str，也可以是list/Series
    - expected_types: str 或 str列表
    """
    if isinstance(expected_types, str):
        expected_types = [expected_types]
    # 统一转为list处理
    if isinstance(qtype, (str, type(None))):
        qtypes = [qtype]
    else:
        # Series, list, array 等
        qtypes = list(qtype)
    qtypes_set = set(qtypes)
    valid_set = set(expected_types)
    difference = qtypes_set - valid_set

    if difference:
        raise ValueError(
            f"题型为 {qtypes_set}，但本指标只适用于 {'/'.join(expected_types)} 题型。"
            + (f"（你的题号：{qid}）" if qid else '')
        )


def to_numeric_series(answers_df):
    """
    将单列DataFrame或Series转换成数字型Series，自动剔除非数字（转为NaN）
    """
    if isinstance(answers_df, pd.DataFrame):
        if answers_df.shape[1] != 1:
            raise ValueError("to_numeric_series只适用于单列数据。")
        ser = answers_df.iloc[:, 0]
    else:
        ser = answers_df
    return pd.to_numeric(ser, errors='coerce')

def preprocess_multi_choice(qinfo, original_qid):
    """
    输入
        qinfo:   survey.qinfo
        original_qid: 例如'S27'
    返回
        tuple (选择项列名list, 填空型列名list, 选项短名dict)
    """
    # 拿到所有相关列
    mask = (qinfo['original_qid'] == original_qid)
    rows = qinfo[mask]
    # 选择“非填空”的定量选项（常见命名为 包含"填空"的列不要）
    option_mask = ~rows['short_name'].str.contains('填空', na=False)
    options_cols = rows[option_mask]['raw_col'].tolist()
    option_names = rows[option_mask].set_index('raw_col')['short_name'].to_dict()

    # 提取“填空xx”专用列（可被当做开放题明细）
    txt_mask  = rows['short_name'].str.contains('填空', na=False)
    txt_cols  = rows[txt_mask]['raw_col'].tolist()
    txt_names = rows[txt_mask].set_index('raw_col')['short_name'].to_dict()
    return options_cols, txt_cols, option_names, txt_names

# def save_result_to_excel(df, original_qid, analysis_name, out_dir='.'):
#     """
#     输入
#         df:          要保存的DataFrame
#         original_qid: 题号（S27、M10等）
#         analysis_name: 分析名称（如'NSS分析','多选题统计','排序题统计'等，不要带.）
#         out_dir:     输出目录，默认当前目录
#     """
#     # 构造文件名
#     file_name = f"{original_qid}_{analysis_name}.xlsx"
#     file_path = f"{out_dir}/{file_name}".replace('//','/')
#     # 写入excel
#     df.to_excel(file_path, index=True)
#     print(f"已保存到: {file_path}")

def save_multi_tables_to_excel(tables: dict, original_qid, analysis_name, out_dir='.', show_print=True):
    """
    输入：
        tables: dict {sheet名: DataFrame}，每个表保存为一个sheet
        original_qid: 题号（S27、M10等）
        analysis_name: 分析名称（如'NSS分析','多选题统计','排序题统计'等，不要带.）
        out_dir:     输出目录，默认当前目录
    """
    # 构造文件名
    file_name = f"{original_qid}_{analysis_name}.xlsx"
    file_path = f"{out_dir}/{file_name}".replace('//','/')

    with pd.ExcelWriter(file_path) as ew:
        for label, table in tables.items():
            # Excel sheet名不能大于31字符
            sheetn = str(label)[:31]
            table.to_excel(ew, sheet_name=sheetn)
            if show_print:
                print(f"已写入: {sheetn}")
    if show_print:
        print(f"全部结果已保存到: {file_path}")

def map_income_group(series, mapping, unknown_val=pd.NA):
    """
    输入
        series: 需要分组的一列（Series）
        mapping: dict，key为新分组名，value为list(原选项)
        unknown_val: 未能匹配的值的替代（如np.nan、pd.NA、'未知'等）

    返回: Series，分组后新标签
    """
    lookup = {}
    for group, origin_list in mapping.items():
        for raw in origin_list:
            lookup[raw] = group
    return series.map(lambda x: lookup.get(x, unknown_val))

def process_income_group(survey, original_qid='S68', group_col_name='g1 income group from S68'):
    """
    处理收入分组并添加到survey对象中
    参数:
        survey: SurveyData对象
        original_qid: 收入题的原始题号，默认为'S68'
        group_col_name: 新生成的分组列名
    """
    # 定义收入分组映射
    income_group_mapping = {
        'a低收入': ['Less than £20,000','£20,000 - £34,999'],
        'b中收入': ['£35,000 - £54,999', '£55,000 - £79,999','£80,000 - £119,999'],
        'c高收入': ['£120,000 or more'],
        'dPrefer not to say': ['Prefer not to say']
    }
    
    # 获取收入列
    income_col = survey.qinfo[survey.qinfo['original_qid'] == original_qid]['raw_col'].iloc[0]
    
    # 应用分组映射
    survey.df[group_col_name] = map_income_group(survey.df[income_col], income_group_mapping)
    
    # 更新qinfo
    if group_col_name not in survey.qinfo['raw_col'].values:
        survey.qinfo = pd.concat([
            survey.qinfo,
            pd.DataFrame([{
                'raw_col': group_col_name,
                'original_qid': 'g1',
                'question_id': 'g1',
                'qtype': 'S',
                'short_name': 'income group'
            }])
        ], ignore_index=True)
    
    # 设置g1列
    survey.qinfo.loc[survey.qinfo['original_qid'] == original_qid, 'g1'] = '收入分组'

def merge_others(series, keywords=('other', '其他')):
    """
    把Series中所有包含指定关键词的选项全部归为'其他'，其余保持原样。
    - series: pandas.Series（原选项结果）
    - keywords: 匹配的关键字元组，不分大小写（默认支持'other'和'其他'）
    返回：新Series
    """

    pattern = '|'.join([re.escape(k) for k in keywords])
    pattern_re = re.compile(pattern, flags=re.IGNORECASE)
    def map_func(x):
        if pd.isnull(x):
            return x
        if pattern_re.search(str(x)):
            return '其他'
        return x
    return series.map(map_func)

def add_total_column_by_percent_sum(cross_tab, group_cols=None, total_colname='总计'):
    """
    输入
        cross_tab: crosstab结果，频数表（Base第一行，其余行为分数频次）
        group_cols: 用于求总计列的分组列list，默认全非总计非Base列
        total_colname: 新增列名
    """
    # 如果没指定group_cols，自动检测
    if group_cols is None:
        group_cols = [c for c in cross_tab.columns if c != total_colname]
    # 1. 先取分组Base
    base_row = cross_tab.loc['Base', group_cols].astype(float)
    base_sum = base_row.sum()
    # 2. 其它行转百分比并算总计
    for idx in cross_tab.index:
        if idx == 'Base':
            cross_tab.loc[idx, total_colname] = int(base_sum)
        else:
            # 各组分数人数
            scale = cross_tab.loc[idx, group_cols].astype(float)
            # 列内百分比
            cross_tab.loc[idx, group_cols] = [
                f"{(scale[c]/base_row[c]*100 if base_row[c] else 0):.2f}%" for c in group_cols
            ]
            # 行总计 — 当前分数的所有分组计数之和 / base_sum
            cnt_sum = scale.sum()
            pct = cnt_sum / base_sum * 100 if base_sum else 0
            cross_tab.loc[idx, total_colname] = f"{pct:.2f}%"
    return cross_tab