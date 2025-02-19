from futu import *
quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)
# US.AAPL270115P300000
# 拿期权名称拿期权的行情价，option_delta，option_implied_volatility，option_premium，安全边际，
ret, data = quote_ctx.get_market_snapshot(['US.AAPL'])
if ret == RET_OK:
    data.to_excel('US-AAPLquote_snapshot.xlsx')
else:
    print('error:', data)
quote_ctx.close() # 结束后记得关闭当条连接，防止连接条数用尽
