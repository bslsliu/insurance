import datetime
import pandas as pd
import backtrader as bt
from datetime import datetime
import warnings
warnings.filterwarnings("ignore")

import akshare as ak

# 数据源：东方财富
# 获取个股的日线级别的历史行情
# report_code ,eg "000001"
# start_date 回测开始时间
# end_date 回测结束时间
def get_stock_history(report_code, start_date_str="20240101", end_date_str="20241231"):

    stock_hfq_df = ak.stock_zh_a_hist(symbol=report_code, start_date=start_date_str
                                      , end_date=end_date_str, adjust="hfq").iloc[:, :6]
    # 处理字段命名，以符合 Backtrader 的要求
    stock_hfq_df.columns = [
        "date",
        "open",
        "close",
        "high",
        "low",
        "volume",
    ]
    # 把 date 作为日期索引，以符合 Backtrader 的要求
    stock_hfq_df.index = pd.to_datetime(stock_hfq_df["date"])
    start_date_obj = datetime.strptime(start_date_str, "%Y%m%d")
    end_date_obj = datetime.strptime(end_date_str, "%Y%m%d")
    data = bt.feeds.PandasData(dataname=stock_hfq_df, fromdate=start_date_obj, todate=end_date_obj)  # 加载数据
    return data

# 数据源：新浪财经
def get_stock_history_sina(report_code="sh600570", start_date_str="20240101", end_date_str="20241231"):

    stock_hfq_df = ak.stock_zh_a_daily(symbol=report_code, start_date=start_date_str, end_date=end_date_str, adjust="hfq")
    # 把 date 作为日期索引，以符合 Backtrader 的要求
    stock_hfq_df.index = pd.to_datetime(stock_hfq_df["date"])
    start_date_obj = datetime.strptime(start_date_str, "%Y%m%d")
    end_date_obj = datetime.strptime(end_date_str, "%Y%m%d")
    # stock_hfq_df.to_csv("sh600570.csv")
    data = bt.feeds.PandasData(dataname=stock_hfq_df, fromdate=start_date_obj, todate=end_date_obj)  # 加载数据
    return data

if __name__ == "__main__":
    data = get_stock_history_sina(report_code="sh600570")
    print(type(data))
