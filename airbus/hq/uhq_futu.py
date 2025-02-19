# 计算多个品种的相关性
# print(pow(1.2343,2025-2004))
#
# print(pow(1.071,20))
params = (
        ('macd1', 5),  # 短期EMA的周期
        ('macd2', 27),  # 长期EMA的周期
        ('signal', 7),  # Signal线的周期
        ('stop_loss_pct', 0),  # 不设置止损
    )
analyzer = dict()
analyzer["ad"]=2
analyzer["ret"]=1
analyzer.update(params)
print(analyzer)