# 导入
from metrics_cal import *
from Survey_Data import SurveyData
# 获取数据 answers, qtype
survey = SurveyData('D:/1NPS_projector/survey_data/UK/UK_2425_2426.xlsx')
survey.df = drop_invalid_samples(survey.df)  # 只保留有效样本


    # check_question_type(qtype, 'S', 'S2')
    # nps_df = nps_table(answers)
    # print(nps_df)

    # answers, qtype = survey.get_answers_by_qid('M9',return_qtype=True)  # 例如S2是NPS单选分数题
    # check_question_type(qtype, 'S', 'M9')
    # subtitle_map = survey.qinfo.set_index('raw_col')['short_name'].to_dict()
    # nss_df = calc_nss_table(answers,short_names = subtitle_map)
    # print(nss_df)

    # answers, qtype = survey.get_answers_by_qid('S67',return_qtype=True)  # 例如S2是NPS单选分数题
    # check_question_type(qtype, 'R', 'S67')
    # subtitle_map = survey.qinfo.set_index('raw_col')['short_name'].to_dict()
    # rank = rank_table(answers, 5, short_names = subtitle_map)
    # print(rank)
    # answers, qtype = survey.get_answers_by_qid('S27',return_qtype=True)
    # check_question_type(qtype, 'M', 'S27')
    # options_cols, txt_cols, option_names, txt_names = preprocess_multi_choice(
    # qinfo=survey.qinfo, original_qid='S27')
    # multi_df = calc_nss_detail(survey.df, options_cols, option_names)
    # print(multi_df)


    # multi_text = collect_openended_texts(survey.df, txt_cols)
    # print("细节的评论明细：")
    # for x in multi_text:
    #     print(x)

scene_col = survey.get_answers_by_qid('S57',return_qtype=False)

nps_col = survey.get_answers_by_qid('S2',return_qtype=False)

nps_table = cross_analysis( nps_col, scene_col,stat_func=calc_nps_from_series, stat_row_name='NPS')
print(nps_table)

