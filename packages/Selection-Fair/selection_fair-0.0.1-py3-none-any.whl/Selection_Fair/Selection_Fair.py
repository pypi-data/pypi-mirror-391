import pandas as pd


class TableProcessor:
    """
    表格数据处理器，用于处理销售数据并生成选货排位等信息
    """

    def processing_table_data_v1(self, data_h):
        """
        版本1：原始数据处理逻辑，包含7个数据分片的合并

        参数:
            data_h: 原始数据DataFrame，需包含以下列：
                ['在售量', '分车方式', '成交量', '是否新员工分车', '平均在售天数', 
                 '成交让价效果', '成交总收益', '让价总金额', '销售', '经理']

        返回:
            处理后的DataFrame，包含选货排位和指定列
        """
        columns = ['销售', '经理', '在售量', '平均在售天数', '成交让价效果',
                   '成交总收益', '让价总金额', '选货方式']

        # 数据分片处理
        df1 = data_h[(data_h['在售量'] < 6)
                     & (data_h['分车方式'] == '新员工')
                     & (data_h['成交量'] > 0)]
        df1 = df1.sort_values(by=['成交让价效果'], ascending=[False])
        df1['选货方式'] = '新手选车'

        df2 = data_h[(data_h['在售量'] < 6)
                     & (data_h['分车方式'] == '新员工')
                     & (data_h['成交量'] == 0)
                     & (data_h['是否新员工分车'] == 1)]
        df2 = df2.sort_values(by=['平均在售天数'], ascending=[True])
        df2['选货方式'] = '新手选车'

        df3 = data_h[(data_h['在售量'] < 25)
                     & (data_h['成交量'] > 0)
                     & (data_h['分车方式'] == '正常')]
        df3 = df3.sort_values(by=['成交让价效果'], ascending=[False])
        df3['选货方式'] = '成交选车'

        df4 = data_h[(data_h['在售量'] < 25)
                     & (data_h['成交量'] == 0)
                     & (data_h['分车方式'] == '正常')]
        df4 = df4.sort_values(by=['平均在售天数'], ascending=[True])
        df4['选货方式'] = '等待选车'

        df5 = data_h[(data_h['在售量'] >= 10)
                     & (data_h['在售量'] < 25)
                     & (data_h['分车方式'] == '新手保护')]
        df5 = df5.sort_values(by=['平均在售天数'], ascending=[True])
        df5['选货方式'] = '新人候补'

        df6 = data_h[(data_h['在售量'] >= 25)
                     & (data_h['分车方式'] == '精力保护')]
        df6 = df6.sort_values(by=['平均在售天数'], ascending=[True])
        df6['选货方式'] = '精力候补'

        df7 = data_h[(data_h['在售量'] < 6)
                     & (data_h['分车方式'] == '新员工')
                     & (data_h['成交量'] == 0)
                     & (data_h['是否新员工分车'] == 0)]
        df7 = df7.sort_values(by=['平均在售天数'], ascending=[True])
        df7['选货方式'] = '新手选车'

        # 合并数据并添加选货排位
        df_combined = pd.concat(
            [df1, df2, df3, df4, df5, df6, df7],
            ignore_index=False
        ).reset_index(drop=True)
        df_combined = df_combined[columns]
        df_combined.insert(0, '选货排位', range(1, 1 + len(df_combined)))

        # 长度校验（如果需要微信通知，需确保uxin_wx函数可用）
        if len(data_h) != len(df_combined):
            print('今日分车表前后长度不一致')
            print(f'原始表长度：{len(data_h)}')
            print(f'新表长度：{len(df_combined)}')
            # 注意：uxin_wx需要额外实现或导入，这里仅保留原逻辑
            # uxin_wx('dongyang', f'今日分车表前后长度不一致 \n原始表长度：{len(data_h)} \n新表长度：{len(df_combined)}')
        else:
            print('长度一致')

        return df_combined

    def processing_table_data_v2(self, data_h):
        """
        版本2：简化版数据处理逻辑，包含3个数据分片的合并

        参数:
            data_h: 原始数据DataFrame，需包含以下列：
                ['分车方式', '成交量', '是否新员工分车', '平均在售天数', 
                 '成交让价效果', '成交总收益', '让价总金额', '销售', '经理', '级别', '车辆上限']

        返回:
            处理后的DataFrame，包含选货排位和指定列
        """
        columns = ['销售', '经理', '级别', '车辆上限', '在售量', '平均在售天数',
                   '成交量', '成交让价效果', '成交总收益', '让价总金额', '选货方式']

        # 数据分片处理
        df1 = data_h[(data_h['分车方式'] == '新员工') & (data_h['成交量'] > 0)]
        df1 = df1.sort_values(by=['成交让价效果'], ascending=[False])
        df1['选货方式'] = '新手选车'

        df2 = data_h[(data_h['分车方式'] == '新员工')
                     & (data_h['成交量'] == 0)
                     & (data_h['是否新员工分车'] == 1)]
        df2 = df2.sort_values(by=['平均在售天数'], ascending=[True])
        df2['选货方式'] = '新手选车'

        df3 = data_h[(data_h['成交量'] > 0) & (data_h['分车方式'] == '正常')]
        df3 = df3.sort_values(by=['成交让价效果'], ascending=[False])
        df3['选货方式'] = '成交选车'

        # 合并数据并添加选货排位
        df_combined = pd.concat(
            [df1, df2, df3],
            ignore_index=False
        ).reset_index(drop=True)
        df_combined = df_combined[columns]
        df_combined.insert(0, '选货排位', range(1, 1 + len(df_combined)))

        return df_combined

    def processing_table_data_weichengjiao(self, data_h):
        """
        未成交名单处理逻辑

        参数:
            data_h: 原始数据DataFrame，需包含以下列：
                ['分车方式', '成交量', '是否新员工分车', '销售', '经理']

        返回:
            处理后的未成交名单DataFrame
        """
        columns = ['销售', '经理']

        df = data_h[
            ((data_h['分车方式'] == '新员工')
             & (data_h['成交量'] == 0)
             & (data_h['是否新员工分车'] == 0))
            | (data_h['成交量'] == 0)
            ]
        df = df.sort_values(by=['销售'], ascending=[True])
        df = df[columns]

        return df