from futu import *
import time
quote_ctx = OpenQuoteContext(host='localhost', port=11111)  # 创建行情对象
# ret, data = quote_ctx.get_market_snapshot('HK.00700')
# if ret == RET_OK:
#     print(data.columns)
#     print(data.index)
#     data.to_csv('code.csv')
# quote_ctx.close() # 关闭对象，防止连接条数用尽

report_code = 'US.MRVL'
# 获取期权的到期日期
ret, ods_option_expiration_date = quote_ctx.get_option_expiration_date(code=report_code)
# strike_time到期日期，例 2025-01-31
# option_expiry_date_distance，剩余天数，例7
print(ods_option_expiration_date)
data_filter = OptionDataFilter()
# data_filter.implied_volatility_min = 80
data_filter.delta_min = 0
data_filter.delta_max = 0.1

# 拿满足条件的期权列表
if ret == RET_OK:
    expiration_date_list = ods_option_expiration_date['strike_time'].values.tolist()
    for expiration_date in expiration_date_list:
        # 接口限制：每 30 秒内最多请求 10 次获取期权链接口，传入的时间跨度上限为 30 天
        ret2, option_chain = quote_ctx.get_option_chain(code=report_code, option_type=OptionType.PUT,
                                                        start=expiration_date, end=expiration_date, data_filter=data_filter)
        if ret2 == RET_OK:
            print(option_chain)
            print(option_chain['code'][0])  # 取第一条的股票代码
            print(option_chain['code'].values.tolist())  # 转为 list
        else:
            print('error:', option_chain)
        time.sleep(3)
else:
    print('error:', ods_option_expiration_date)


quote_ctx.close() # 结束后记得关闭当条连接，防止连接条数用尽
