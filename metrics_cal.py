
from ultis import *
def calc_nps_from_series(ser):
    """
    输入
        ser: Series (必须为0-10分数，非数字或缺失会被自动忽略)
    返回
        (nps, score_pct, pct_recommend, pct_passive, pct_detractor)
        nps: NPS分数(float)
        score_pct: 分数分布（index为0~10，值为百分比，合计100%）
        pct_recommend: 推荐者百分比
        pct_passive: 中立者百分比
        pct_detractor: 贬损者百分比
    """
    # 增强数据清洗：处理带空格的字符串分数
    if ser.dtype == object:
        ser = ser.str.strip()  # 去除字符串前后空格
    # 转换为整数类型确保索引匹配
    ser = pd.to_numeric(ser, errors='coerce').fillna(-1).astype(int)
    ser = ser[ser != -1]  # 移除转换失败的数据
    total = ser.dropna().count()
    if total == 0:
        return 0, 0, 0, 0, 0
    score_pct = ser.value_counts(normalize=True).reindex(range(0,11), fill_value=0).sort_index() * 100
    # 调试分数分布
    print("分数分布百分比:", {i: f'{v:.2f}%' for i, v in score_pct.items()})
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

    # 计算NPS相关百分比
    nps,score_pct, pct_recommend, pct_passive, pct_detractor = calc_nps_from_series(ser)

    # 输出表构造 - 使用列表推导式简化代码
    rows = [
        ('Base: 实际样本', ser.count()),
        *[(str(i), f"{score_pct.loc[i]:.2f}%") for i in range(0, 11)],
        ("推荐者", f"{pct_recommend:.2f}%"),
        ("中立者", f"{pct_passive:.2f}%"),
        ("贬损者", f"{pct_detractor:.2f}%"),
        ("NPS", f"{nps:.2f}%")
    ]

    df_result = pd.DataFrame(rows, columns=[ '整体调研用户', '占比/百分比'])
    return df_result


def calc_nss_from_series(ser):
    """
    输入
        ser: Series (必须为1-5分数，非数字或缺失会被自动忽略)
    返回
        (nss, score_pct, t2b, mean_v)
        nss: 净满意度分数(float)
        score_pct: 分数分布（index为1~5，值为百分比，合计100%）
        t2b: T2B百分比(4/5分%)
        mean_v: 满意度平均分
    """
    # 转换为数字型Series并删除缺失值
    ser = to_numeric_series(ser).dropna()
    total = len(ser)
    if total == 0:
        return 0, pd.Series([0]*5, index=[1,2,3,4,5]), 0, 0

    # 计算各分数的百分比
    score_pct = ser.value_counts(normalize=True).reindex(range(1,6), fill_value=0).sort_index() * 100

    # 计算T2B (4/5分%)
    t2b = score_pct.loc[4] + score_pct.loc[5]

    # 计算平均分
    mean_v = ser.mean()

    # 计算NSS (T2B - 1~3分%)
    nss = t2b - score_pct.loc[1:3].sum()

    return nss, score_pct, t2b, mean_v

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
        # 将列名映射到自身作为默认短名
        short_names = {col: col for col in cols}
    # 如果传入列表，则转换为字典映射
    elif isinstance(short_names, list):
        short_names = {col: short_names[i] for i, col in enumerate(cols)}

    result = []
    for col in cols:
        # 使用calc_nss_from_series函数计算NSS相关值
        ser = to_numeric_series(df[col])
        nss, score_pct, t2b, mean_v = calc_nss_from_series(ser)
        total = ser.dropna().count()
        pct = [score_pct.loc[i] for i in [1,2,3,4,5]]
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


