# NPS分析工具

这是一个用于分析问卷调查数据的Python程序，支持NPS、NSS、排序题和交叉分析等多种分析类型，并提供了直观的用户界面。

## 项目功能
- NPS分析：计算净推荐值
- NSS分析：计算净满意度得分
- 排序题分析：分析排序题数据
- 交叉分析：分析不同变量之间的关系
- 数据可视化：直观展示分析结果
- 结果导出：将分析结果导出到Excel文件

## 项目结构
```
NPS_analysis_program/
├── .gitignore
├── README.md
├── requirements.txt       # 项目依赖
├── app.py                 # 主UI界面
├── Survey_Data.py         # 问卷调查数据处理类
├── main.py                # 分析主函数
├── metrics_cal.py         # 指标计算函数
├── nps_factor.py          # NPS因子分析
├── test.py                # 测试代码
├── ultis.py               # 工具函数
└── 因子均分表.xlsx
```

## 安装说明
1. 确保已安装Python 3.8或更高版本
2. 克隆或下载此项目
3. 安装依赖包：
   ```
   pip install -r requirements.txt
   ```

## 使用方法
### 运行UI界面
```
streamlit run app.py
```

### 使用步骤
1. 运行UI界面后，在浏览器中打开显示的URL
2. 上传Excel格式的问卷调查数据
3. 选择分析类型和相关参数
4. 点击"运行分析"按钮
5. 查看分析结果
6. 可选：导出结果到Excel文件

## 数据格式要求
- Excel文件应包含问卷调查数据
- 第一行应为列名
- 应包含"样本状态"列，标记样本是否有效

## 联系方式
如有问题或建议，请联系开发者。