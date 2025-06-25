
from ultis import *
def calc_nps_from_series(ser):
    """
    输入
        ser: Series (必须为0-10分数，非数字或缺失会被自动忽略)
    返回
        (nps, pct_recommend, pct_passive, pct_detractor)
        nps: NPS分数(float)
        score_pct: 分数分布（index为0~10，值为百分比，合计100%）
        pct_recommend: 推荐者百分比
        pct_passive: 中立者百分比
        pct_detractor: 贬损者百分比
    """
    total = ser.count()
    if total == 0:
        return 0, 0, 0, 0
    score_pct = ser.value_counts(normalize=True).reindex(range(0,11), fill_value=0).sort_index() * 100
    # 推荐者/中立/贬损者定义
    pct_recommend = score_pct.loc[9] + score_pct.loc[10]
    pct_passive = score_pct.loc[7] + score_pct.loc[8]
    pct_detractor = score_pct.loc[0:6].sum()
    #NPS
    nps = pct_recommend - pct_detractor
    return nps, score_pct, pct_recommend, pct_passive, pct_detractor

def nps_table(ser):
    """
    输入
        ser: 单选题分数Series
    
    返回
       NPS表(pd.DataFrame)
    """

    # 只要有效数字分数
    ser = to_numeric_series(ser)
    total = int(ser.count())

    
    # 计算NPS相关百分比
    nps,score_pct, pct_recommend, pct_passive, pct_detractor = calc_nps_from_series(ser)

    # 输出表构造
    rows = []
    rows.append(('Base: 实际样本', total))
    for i in range(0, 11):
        rows.append((str(i),  f"{score_pct.loc[i]:.2f}%"))
    rows.append(("推荐者",  f"{pct_recommend:.2f}%"))
    rows.append(("中立者",  f"{pct_passive:.2f}%"))
    rows.append(("贬损者",  f"{pct_detractor:.2f}%"))
    rows.append(("NPS",  f"{nps:.2f}%"))

    df_result = pd.DataFrame(rows, columns=[ '整体调研用户', '占比/百分比'])
    return df_result


def calc_nss_table(df_satisfaction, short_names=None):
    """
    输入
        df_satisfaction: DataFrame/Series，每列或唯一列为满意度分值（通常1~5）
        short_names: 可选，字典或列表，列名映射到题目短名（如果没有提供则使用列名）
    返回
        NSS表DataFrame
        
    """
    
    # 自动判断：多维还是1列
    if isinstance(df_satisfaction, pd.Series):
        cols = [df_satisfaction.name]
        df = df_satisfaction.to_frame()
    else:
        df = df_satisfaction
        cols = df.columns
    
    # short_names: 题目短名，没给就用列名
    if short_names is None:
        short_names = list(cols)

    result = []
    for col in cols:
        # 这里略，只举例一题的处理
        ser = to_numeric_series(df[col]).dropna()
        total = len(ser)
        pct = [(ser == i).sum() / total * 100 if total>0 else 0 for i in [1,2,3,4,5]]
        t2b = pct[3] + pct[4]
        mean_v = ser.mean() if total>0 else 0
        nss = t2b - sum(pct[:3])  # 4/5分%-1~3分%
        row = [short_names.get(col, col), total] + [f"{i:.2f}%" for i in pct] + [f"{t2b:.2f}%", f"{mean_v:.2f}", f"{nss:.2f}%"]
        result.append(row)
    
    nss_df = pd.DataFrame(result, columns=[
        '题名', '样本量', '满意度1分','满意度2分','满意度3分','满意度4分','满意度5分',
        'T2B (4/5分%)', '满意度平均分', '净满意度(%)'
    ])
    return nss_df


def rank_table(df_rank,max_rank, option_cols, short_names=None):
    """
    输入
        df_rank: DataFrame，columns为排序选项，每列为排名，未选为nan
        max_rank: int 需要统计的最大排名数，通常为5
        short_names: dict 可选，{原列名:短名}
    返回按照指定表格格式统计的DataFrame
    
    """
    df_rank = df_rank[option_cols] if option_cols else df_rank
    cols = df_rank.columns
    # 最大排名
    
    max_rank = 5

    result = []
    for col in cols:
        ser = to_numeric_series(df_rank[col])
        # 每一名的计数, index从1累到max_rank
        rank_counts = [(ser == i).sum() for i in range(1, max_rank + 1)]
        n_selected = ser.notna().sum()
        pct_selected = n_selected / len(df_rank) * 100 if len(df_rank) > 0 else 0
        # 按权重5~1依次分配赋值后重要性
        index_value = sum(c * (max_rank - i) for i, c in enumerate(rank_counts)) / len(df_rank) * 100 if len(df_rank) > 0 else 0
        row = [
            short_names[col] if short_names and col in short_names else col,
            n_selected
        ] + rank_counts + [
            f"{pct_selected:.2f}%", f"{index_value:.2f}%"
        ]
        result.append(row)

    columns = [
        "Dimension/维度（主任务/子任务）", "计数样本(排序前5)"
    ] + [f"重要性排序第{i}/计数" for i in range(1, max_rank+1)] \
      + ["被选定影响决策的比例%", "赋值后重要性index"]

    return pd.DataFrame(result, columns=columns)

def calc_nss_detail(df, option_cols, option_names=None):
    """
    输入
        df: survey.df/切片
        option_cols: 可选项列名（不含填空）
        option_names: {col: name}
    返回
        DataFrame, 行为选项，列为Base/n/百分比
    """
    sub_df = df[option_cols]
    # base为: 至少勾选了该题一道选项的受访者数
    is_answered = sub_df.notna().any(axis=1)
    base = is_answered.sum()
    result = []
    for col in option_cols:
        n = df[col].notna().sum()  # 被选人数
        pct = n/base*100 if base else 0
        name = option_names[col] if option_names and col in option_names else col
        result.append([name, n, f"{pct:.2f}%"])
    # 按选中率排序
    df_out = pd.DataFrame(result, columns=['选项','计数','百分比'])
    # 最前加一行 Base
    df_out = pd.concat([pd.DataFrame([['Base', base, '']], columns=df_out.columns), df_out], ignore_index=True)
    return df_out

def collect_openended_texts(df, txt_cols):
    """
    收集所有填空列的非空内容合并为一个list
    """
    comments = []
    for col in txt_cols:
        values = df[col].dropna().astype(str)
        values = values[values.str.strip() != '']     # 去空白
        comments.extend(list(values))
    return comments


def cross_analysis(
    row_s, col_s, row_labels=None, col_labels=None, 
    stat_func=None, stat_row_name=None,
):
    """
    输入
        row_s: series,行变量（如分数、满意度等）
        col_s: series,列变量（如分组变量）
        row_labels: 行变量label映射 dict
        col_labels: 列变量label映射 dict
        stat_func: 可选，传入统计函数(如calc_nps_from_series)。会对每列用df[df[col_col]==场景][row_col]做一次统计。
        stat_row_name: 统计行名称（如'NPS','均值'等）

    返回
        二元交叉表DataFrame
    """

    row_s= to_numeric_series(row_s).dropna()  # 确保是数值型Series
    col_s = merge_others(col_s).dropna()  # 合并其他选项

    # 交叉表计算
    cross_tab = pd.crosstab(row_s, col_s, dropna=False)

    # Base行（每个分组样本量）
    base = cross_tab.sum(axis=0)
    cross_tab = pd.concat(
        [pd.DataFrame([base], columns=cross_tab.columns, index=['Base']), cross_tab]
    )

    # 行列名称处理
    if col_labels:
        cross_tab.columns = [col_labels.get(x,x) for x in cross_tab.columns]
    if row_labels:
        cross_tab.index = [row_labels.get(y,y) if y!='Base' else y for y in cross_tab.index]


    # 可选统计分析行
    if stat_func is not None:
        stat_row = []
        for group_val in cross_tab.columns:
            # 注意此时group_val可能已做了标签转化，如果这样需要准备一个逆映射;这里假设原值和labels一致
            # 取分组的原始值
            col_val = group_val
            if col_labels:
                #逆向查原值
                col_val = next((k for k,v in col_labels.items() if v==group_val), group_val)
            group_series = row_s[col_s == col_val]
            # 计算指标
            v = stat_func(group_series)
            if isinstance(v, tuple):
                v = v[0]  # 只取第1个输出，适合NPS返回多值情况
            stat_row.append(f"{v:.0f}%" if isinstance(v, float) or isinstance(v,int) else v)
        stat_name = stat_row_name if stat_row_name else stat_func.__name__
        stat_df = pd.DataFrame([ [stat_name] + stat_row ], columns=['stat'] + list(cross_tab.columns))
        stat_df = stat_df.set_index('stat')
        cross_tab = pd.concat([cross_tab, stat_df])
    
    return cross_tab
