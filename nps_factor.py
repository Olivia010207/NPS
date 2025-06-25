from metrics_cal import *
from Survey_Data import SurveyData
from ultis import *

#读入
#音箱
#survey = SurveyData('D:/1NPS_projector/survey_data/SurveyResults_2025-05-09-03-24-30.xlsx')
#投影仪-英国
survey = SurveyData('D:/1NPS_projector/survey_data/UK/UK_2425_2426.xlsx')
#投影仪-美国
#survey = SurveyData('D:/1NPS_projector/survey_data/US/2425_2426-US.xlsx')
survey.df = drop_invalid_samples(survey.df)  # 只保留有效样本

nss_qid1 = 'M10'  # nss题号
nss_qid2 = 'M11'  # nss题号

nps_qid = 'S2'  # nps题号
nps_series = survey.get_answers_by_qid(nps_qid, return_qtype=False)
nps_series = to_numeric_series(nps_series).dropna()
# 推荐者切片（得分9或10）
recommender_idx = nps_series[(nps_series >= 9) & (nps_series <= 10)].index
recommender_df = survey.df.loc[recommender_idx]


# 贬损者切片（得分0~6）
detractor_idx = nps_series[(nps_series >= 0) & (nps_series <= 8)].index
detractor_df = survey.df.loc[detractor_idx]


option_cols, _, option_names, _ = preprocess_multi_choice(survey.qinfo, nss_qid1)
option_cols2, _, option_names2, _ = preprocess_multi_choice(survey.qinfo, nss_qid2)
# 合并两个nss题的选项列
option_cols.extend(option_cols2)
option_names.update(option_names2)

results = []
for col in option_cols:
    # 推荐者
    recommender_ser = to_numeric_series(recommender_df[col]).dropna()
    recommender_mean = recommender_ser.mean() if len(recommender_ser) > 0 else 0
    recommender_count = len(recommender_ser)
    # 贬损者
    detractor_ser = to_numeric_series(detractor_df[col]).dropna()
    detractor_mean = detractor_ser.mean() if len(detractor_ser) > 0 else 0
    detractor_count = len(detractor_ser)
    
    # 保存结果
    results.append({
        '因子': option_names[col],
        '推荐者均分': recommender_mean,
        '推荐者样本量': recommender_count,
        '贬损者均分': detractor_mean,
        '贬损者样本量': detractor_count,
        '总样本量': recommender_count + detractor_count
    })
# 列表转DataFrame
df = pd.DataFrame(results)

# 可选：调整列顺序
df = df[['因子', '推荐者均分', '贬损者均分','总样本量', '推荐者样本量', '贬损者样本量']]

print(df)

# 如果需要导出Excel
#df.to_excel('因子均分表.xlsx', index=False)

#标签映射-投影仪
label_map = {
    'Product packaging': '产品包装',
    'Unboxing': '开箱体验',
    'Product appearance': '投影仪的外观',
    'Product instructions': '产品使用指引',
    'Installation and screen angle adjustment': '安装与画面角度调节',
    'Powering on the projector':'投影仪开机',
    'Connection with other devices via Bluetooth':'通过蓝牙连接',
    'Non-Bluetooth connection with other devices (cables, USB dri':'通过非蓝牙的方式连接',
    'Remote control':'遥控器交互控制',
    'App controls and interactivity': 'App交互控制',
    'Screen brightness': '画面亮度',
    'Image quality': '画质',
    'Focus and intelligent correction': '画面智能矫正',
    'Sound quality and performance': '音质与音效',
    'Content playback and availablity': '软件内容播放以及丰富度',
    'Karaoke experience': '使用投影仪进行K歌',
    'Storage and portability': '收纳与便携',
    'Durability and ease of maintenance': '耐用性和保养/清洁',
    'Updating the projector': '投影仪的更新/升级',
    'Power efficiency and battery performance': '供电与续航',

}

#标签映射-音箱
# label_map = {
#     'Product packaging': '产品包装',
#     'Unboxing': '开箱体验',
#     'Appearance of the speaker': '音箱的外观',
#     'Product instructions': '产品使用指引',
#     'Powering on the speaker': '音箱开机',
#     'Connection with other devices via Bluetooth': '通过蓝牙连接',
#     'Connection with other soundcore speakers via PartyCast': '通过PatryCast连接',
#     'Connection with other devices via cables': '通过数据传输线连接',
#     'Button controls': '按键交互控制',
#     'App controls and interactivity': 'App交互控制',
#     'Sound quality and performance indoors (e.g. home, gym, etc.)': '室内场景音质与音效',
#     'Sound quality and performance outdoors (e.g. backyard, park,': '户外场景音质与音效',
#     'Sound quality and performance in vehicles (e.g. car, truck,': '交通场景音质与音效',
#     'Sound quality and performance on water (e.g. boat, yacht, cr': '水上场景音质与音效',
#     'BassUp technology': 'BassUp功能',
#     'Light effects on both sides of the speaker': '音箱两侧的灯效',
#     'Power supply and battery life': '供电与续航',
#     'Carrying by the handle': '通过把手携带音箱',
#     'Carrying by the shoulder strap': '通过肩带携带音箱',
#     'Durability and ease of maintenance': '耐用性和保养/清洁',
#     'Updating the speaker': '音箱的更新/升级'

# }

df['因子'] = df['因子'].map(label_map)
# df = df[df['因子'] != '通过PatryCast连接'].reset_index(drop=True)
# df = df[df['因子'] != '音箱两侧的灯效'].reset_index(drop=True)
df = df[df['因子'] != '使用投影仪进行K歌'].reset_index(drop=True)
print(df)

#---------------------------------画图----------------------------------
import matplotlib.pyplot as plt
import textwrap
from adjustText import adjust_text


plt.rcParams['font.sans-serif'] = ['SimHei']     # 用黑体显示中文（Windows适用）
plt.rcParams['axes.unicode_minus'] = False       # 解决负号'-'显示为方块的问题

# 读取你刚刚组装好的DataFrame df

# X轴是“贬损者均分” （激怒用户可能性）
x = df['贬损者均分']
# Y轴是“推荐者均分” （愉悦用户可能性）
y = df['推荐者均分']
# 气泡大小可随意，比如都设为300；或者用两个均分的标准差、样本数等（如需自定义请补充）
sizes = df['总样本量'] * 50  # 缩放系数可自行调整


#气泡颜色
x_split = x.median()  # 或x.mean()
y_split = y.median()  # 或y.mean()
# 顺序依次为四个象限，从图上来看，左上（黄色），右上（红），右下（蓝），左下（灰）
def get_quadrant_color(xi, yi, x_split, y_split):
    if xi < x_split and yi >= y_split:
        return 'gold'
    elif xi >= x_split and yi >= y_split:
        return 'red'
    elif xi >= x_split and yi < y_split:
        return 'dodgerblue'
    else:
        return 'gray'
colors = [get_quadrant_color(xi, yi, x_split, y_split) for xi, yi in zip(x, y)]

# 画布
fig, ax = plt.subplots(figsize=(10,10))

#错开重合气泡（美国）
# x.iloc[4] += 0.02
# y.iloc[12] -= 0.03
# x.iloc[0] += 0.04
# y.iloc[1] += 0.01
# x.iloc[15] -= 0.04
# y.iloc[15] -= 0.03

#错开重合气泡（音箱）
# y.iloc[14] += 0.02
# y.iloc[8] -= 0.02
# x.iloc[16] += 0.02
# y.loc[6] += 0.25
# x.iloc[6] += 0.2
# x.iloc[15] += 0.2
# y.iloc[15] += 0.2



sc = ax.scatter(x, y, s=sizes, alpha=0.4, c=colors, edgecolors='w')



# 象限分割线（可取均值，或指定某个阈值）

ax.axhline(y=y_split, color='gray', linestyle='--')
ax.axvline(x=x_split, color='gray', linestyle='--')

# 标签和标题
ax.set_xlabel('激怒用户的可能性')
ax.set_ylabel('愉悦用户的可能性')
ax.set_title('影响因子分析四象限')

# 可选：微调坐标范围
ax.set_xlim(x.min() - 0.05, x.max() + 0.1)
ax.set_ylim(y.min() - 0.05, y.max() + 0.05)
# 等画完scatter和分割线后
xlim = ax.get_xlim()
ylim = ax.get_ylim()
ax.set_xticks([])   # x轴去掉刻度
ax.set_yticks([])   # y轴去掉刻度

offset_x = 0.03 * (xlim[1] - xlim[0])  # 距离边缘百分比，可调
offset_y = 0.03 * (ylim[1] - ylim[0])
# 获取边界
xlim = ax.get_xlim()
ylim = ax.get_ylim()
offx = 0.03 * (xlim[1] - xlim[0])
offy = 0.03 * (ylim[1] - ylim[0])

# 愉悦因子（左上角）
ax.text(xlim[0] + offx, ylim[1] - offy, '愉悦因子', 
        color='gold', fontsize=18, fontweight='bold', ha='left', va='top')

# 必备因子（右上角）
ax.text(xlim[1] - offx, ylim[1] - offy, '必备因子', 
        color='red', fontsize=18, fontweight='bold', ha='right', va='top')

# 激怒因子（右下角）
ax.text(xlim[1] - offx, ylim[0] + offy, '激怒因子', 
        color='dodgerblue', fontsize=18, fontweight='bold', ha='right', va='bottom')


# 坐标轴端点“强/弱”文字
# Y轴 “强/弱”
ax.text(xlim[0] - 0.03*(xlim[1] - xlim[0]), ylim[1], '强', fontsize=14, color='grey', va='bottom', ha='left', rotation=0)
ax.text(xlim[0] - 0.03*(xlim[1] - xlim[0]), ylim[0], '弱', fontsize=14, color='grey', va='top', ha='left', rotation=0)

# X轴 “强/弱”
ax.text(xlim[1], ylim[0] - 0.04*(ylim[1] - ylim[0]), '强', fontsize=14, color='grey', va='top', ha='center', rotation=0)
ax.text(xlim[0], ylim[0] - 0.04*(ylim[1] - ylim[0]), '弱', fontsize=14, color='grey', va='top', ha='center', rotation=0)

# 调整文本位置以避免重叠
# 因子名
labels = df['因子']
def wrap_label(label, width=5):
    return '\n'.join(textwrap.wrap(label, width))

labels_wrapped = labels.apply(wrap_label)
texts = []

#字体大小自适应
def get_fontsize(labels_wrapped):
    length = len(labels_wrapped.replace('\n',''))
    if length <= 4:
        return 10
    elif length <= 7:
        return 9
    elif length <= 10:
        return 8
    else:
        return 7

for i, txt in enumerate(labels_wrapped):
    texts.append(ax.annotate(txt, (x.iloc[i], y.iloc[i]), fontsize=get_fontsize(txt), ha='center', va='center'))



plt.tight_layout()
plt.show()
