from metrics_cal import *
from ultis import *
from Survey_Data import SurveyData

def cross_analysis(survey, row_qid, col_qid, is_nps=False, row_labels=None, col_labels=None):
    # 确保标签参数不为None
    row_labels = row_labels or {}
    col_labels = col_labels or {}
    """
    交叉分析入口函数：根据是否为NPS计算自动路由分析类型
    输入
        survey: SurveyData对象
        row_qid: 行变量题号
        col_qid: 列变量题号
        row_labels: 行变量label映射 dict
        col_labels: 列变量label映射 dict
        is_nps: 是否进行NPS计算
    返回
        交叉分析结果DataFrame
    """

    # 获取行变量题型
    _, row_qtype = survey.get_answers_by_qid(row_qid, return_qtype=True)
    # 获取列变量题型
    _, col_qtype = survey.get_answers_by_qid(col_qid, return_qtype=True)

    # 处理多选题与多选题的交叉分析
    if row_qtype == 'M' and col_qtype == 'M':
        return count_cross_analysis_multiple(survey, row_qid, col_qid, row_labels, col_labels)

    # 处理行变量为多选题的情况
    if row_qtype == 'M':
        return process_multiple_choice_analysis(survey, row_qid, col_qid, row_labels, col_labels, 'row', is_nps=is_nps)

    # 处理列变量为多选题的情况
    if col_qtype == 'M':
        return process_multiple_choice_analysis(survey, row_qid, col_qid, row_labels, col_labels, 'col', is_nps=is_nps)

    # 处理非多选题之间的交叉分析
    row_s = survey.get_answers_by_qid(row_qid, return_qtype=False).iloc[:, 0]
    col_s = survey.get_answers_by_qid(col_qid, return_qtype=False).iloc[:, 0]
    return count_cross_analysis(row_s, col_s, row_labels, col_labels)


def compute_cross_analysis(
    row_s, col_s, group_val, row_labels=None
):
    """
    NPS计算型交叉分析：对每个分组应用NPS计算
    返回每个选项的单列统计结果DataFrame
    """
    # 确保row_s和col_s索引对齐
    combined = pd.DataFrame({'row': row_s, 'col': col_s}).dropna()
    row_s = combined['row']
    col_s = combined['col']

    # 筛选当前分组数据
    group_data = row_s[col_s == group_val]
    if not group_data.empty:
        # 应用NPS计算函数
        stat_result = nps_table(group_data)
        # 添加分组名称前缀
        stat_result.columns = [f'{group_val}_{col}' for col in stat_result.columns]
        return stat_result
    return pd.DataFrame()


def count_cross_analysis(
    row_s, col_s, row_labels=None, col_labels=None
):
    """
    非计算型交叉分析：仅计算选项间频次分布
    返回标准交叉表DataFrame
    """
    # 确保row_s和col_s索引对齐
    combined = pd.DataFrame({'row': row_s, 'col': col_s}).dropna()
    row_s = combined['row']
    col_s = combined['col']

    # 基础频次交叉表
    cross_tab = pd.crosstab(row_s, col_s, dropna=False)

    # 应用标签映射
    if row_labels:
        cross_tab.index = [row_labels.get(idx, idx) if idx != 'Base' else idx for idx in cross_tab.index]
    if col_labels:
        cross_tab.columns = [col_labels.get(col, col) for col in cross_tab.columns]

    return cross_tab


def multiple_choice_dummy(survey, qid):
    """
    处理多选题数据，返回每个选项的虚拟变量矩阵
    输入
        survey: SurveyData对象
        qid: 多选题题号
    返回
        包含每个选项虚拟变量的DataFrame
    """
    options_cols, _, option_names, _ = preprocess_multi_choice(survey.qinfo, qid)
    
    # 创建虚拟变量矩阵
    dummy_df = pd.DataFrame()
    for col in options_cols:
        # 将非空值设为1，空值设为0
        dummy_df[option_names.get(col, col)] = survey.df[col].notna().astype(int)
    
    return dummy_df

def count_cross_analysis_multiple(survey, row_qid, col_qid, row_labels=None, col_labels=None):
    """
    多选题×多选题的非计算型交叉分析
    """
    row_dummy_df = multiple_choice_dummy(survey, row_qid)
    col_dummy_df = multiple_choice_dummy(survey, col_qid)

    # 计算选项间的共现频率
    result = pd.DataFrame()
    for row_col in row_dummy_df.columns:
        row_result = []
        for col_col in col_dummy_df.columns:
            count = (row_dummy_df[row_col] & col_dummy_df[col_col]).sum()
            row_result.append(count)
        result[row_col] = row_result

    result.index = col_dummy_df.columns
    base = row_dummy_df.sum()
    result = pd.concat([pd.DataFrame([base], columns=result.columns, index=['Base']), result])

    # 添加Total列：使用列变量选项的原始计数并通过索引映射
    result['Total'] = result.index.map(col_dummy_df.sum().to_dict())

    # 调整列顺序，将Total放在第二列
    cols = result.columns.tolist()
    if len(cols) > 1:
        cols.insert(0, cols.pop())
        result = result[cols]

    if row_labels:
        result.columns = [row_labels.get(x, x) for x in result.columns]
    if col_labels:
        result.index = [col_labels.get(x, x) if x != 'Base' else x for x in result.index]

    return result


def process_multiple_choice_analysis(survey, row_qid, col_qid, row_labels, col_labels, multiple_type, is_nps=False):
    """
    多选题交叉分析通用处理函数
    multiple_type: 'row'表示多选题作为行变量, 'col'表示作为列变量
    """
    # 根据类型获取对应的虚拟变量矩阵和数据系列
    if multiple_type == 'row':
        dummy_df = multiple_choice_dummy(survey, row_qid)
        data_s = survey.get_answers_by_qid(col_qid, return_qtype=False).iloc[:, 0]
    else:  # 'col'
        dummy_df = multiple_choice_dummy(survey, col_qid)
        data_s = survey.get_answers_by_qid(row_qid, return_qtype=False).iloc[:, 0]

    dfs_to_merge = []
    for col in dummy_df.columns:
        mask = dummy_df[col] == 1
        if multiple_type == 'row':
            # 多选题作为行变量: 过滤列数据
            filtered_row_s = pd.Series(col, index=data_s[mask].index)
            filtered_col_s = data_s[mask]
            current_row_labels = {str(col): f"{row_labels.get(col, col)}"}
            current_col_labels = col_labels
        else:
            # 多选题作为列变量: 过滤行数据
            filtered_row_s = data_s[mask]
            filtered_col_s = pd.Series(col, index=data_s[mask].index)
            current_row_labels = row_labels
            current_col_labels = {str(col): f"{col_labels.get(col, col)}"}

        if is_nps:
            # 计算型分析
            # 处理所有分组
            group_results = []
            for group_val in filtered_col_s.unique():
                group_df = compute_cross_analysis(
                    filtered_row_s, filtered_col_s, group_val,
                    row_labels=current_row_labels if multiple_type == 'row' else row_labels
                )
                # 保留非空结果
                if not group_df.empty:
                    group_results.append(group_df)
            cross_df = pd.concat(group_results, axis=1) if group_results else pd.DataFrame()

        else:
            if multiple_type == 'col':
                 cross_df = count_cross_analysis(
                     filtered_row_s, filtered_col_s,
                     row_labels=current_row_labels,
                     col_labels=current_col_labels
                 )
                 # 添加Total列（每行选项的总人数）

            else: #行和列反过来处理
                cross_df = count_cross_analysis(
                     filtered_col_s, filtered_row_s,
                     col_labels=current_col_labels,
                     row_labels=current_row_labels
                 )
 
            sample_size = mask.sum()

            # 添加Base行：当前多选题选项的样本量
            base_row = pd.DataFrame([[sample_size]*len(cross_df.columns)], columns=cross_df.columns, index=['Base'])
            cross_df = pd.concat([base_row, cross_df])
        dfs_to_merge.append(cross_df)

    # 按行合并并重组为列形式
    result = pd.concat(dfs_to_merge, axis=1) if dfs_to_merge else pd.DataFrame()

    #计算total列并添加到第一列



    if is_nps:
        #删除第3、5、7等奇数列（0-based索引2、4、6...）
        columns_to_drop = list(range(2, result.shape[1], 2))
        result = result.drop(columns=result.columns[columns_to_drop])

    return result if multiple_type == 'col' else result.T


