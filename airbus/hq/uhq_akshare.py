import pandas as pd
import backtrader as bt
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
    return bt.feeds.PandasData(dataname=stock_hfq_df)  # 加载数据


# 数据源：新浪财经
def get_stock_history_sina(
        report_code: str = "sh600570",
        start_date_str: str = "20000101",
        end_date_str: str = "20251231"):
    stock_hfq_df = ak.stock_zh_a_daily(symbol=report_code, start_date=start_date_str, end_date=end_date_str,
                                       adjust="hfq")
    # 把 date 作为日期索引，以符合 Backtrader 的要求
    stock_hfq_df.index = pd.to_datetime(stock_hfq_df["date"])
    # stock_hfq_df.to_csv("sh600570.csv")
    return bt.feeds.PandasData(dataname=stock_hfq_df)  # 加载数据


# 获取指数的历史行情
def get_index_history_em(
        symbol: str = "sh000300",
        start_date: str = "19900101",
        end_date: str = "20500101",
) -> pd.DataFrame:
    index_df = ak.stock_zh_index_daily_em(symbol="sh000300")
    index_df.index = pd.to_datetime(index_df['date'], format='%Y-%m-%d')
    return index_df


if __name__ == "__main__":
    ods_hq_300 = get_index_history_em(symbol="sh000300")
    ods_hq_300["ret"] = ods_hq_300["close"].pct_change()
    # ods_hq_300.dropna(subset=["return"],inplace=True)
    ods_hq_300_return = ods_hq_300["ret"].dropna()
    ods_hq_300.to_csv("csv/sh000300.csv")

    print((1+ods_hq_300_return).cumprod()[-1])
