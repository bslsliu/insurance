from airbus.hq.uhq_akshare import *
import quantstats as qs
from datetime import datetime


def generate_qs_report(strat, stock_name):
    portfolio = strat.analyzers.getbyname('pyfolio')
    returns, positions, transactions, gross_lev = portfolio.get_pf_items()
    nav = returns.add(1).prod()
    returns = returns.dropna()
    returns.index = returns.index.tz_convert(None)
    # 获取基准沪深300的收益
    ods_hq300 = get_index_history_em(symbol="sh000300")
    ods_hq300["ret"] = ods_hq300["close"].pct_change()
    benchmark = ods_hq300["ret"].dropna()
    # quantstats输出报告
    qs.reports.html(returns, benchmark=benchmark, benchmark_title="sh000300",
                    output='stats.html', rf=0.03, download_filename=f'result/backtest-{stock_name}.html')
    cagr = qs.stats.cagr(returns)
    print(f"参数-> {vars(strat.params)}, 产品净值-> {round(nav,2)}, 年复增长率-> {round(cagr*100,2)}%, 总资产-> {round(strat.broker.get_value(),2)}")
    transactions.loc[1::2, 'profit'] = (transactions['value'] +
                                        transactions['value'].shift(1))
    transactions.to_csv("result/transactions_{}.csv".format(datetime.now().strftime("%m%d%H%M%S")))
    win_trades = (transactions['profit'] > 0).sum()  # 盈
    loss_trades = (transactions['profit'] < 0).sum()  # 亏
    all_trades = transactions['profit'].notna().sum()
    print(f"all_trades:{all_trades}")
    print(f"win_trades:{win_trades}, win_rate:{round(float(win_trades * 100 / all_trades), 2)}%")
    print(f"loss_trades:{loss_trades}, loss_rate:{round(float(loss_trades * 100 / all_trades), 2)}%")


def rank_strategy_navs(results):
    def get_my_analyzer(result):
        analyzer = {}
        analyzer.update(vars(result.params))
        portfolio = result.analyzers.getbyname('pyfolio')
        returns, positions, transactions, gross_lev = portfolio.get_pf_items()
        analyzer["cagr"] = qs.stats.cagr(returns)
        analyzer["nav"] = returns.add(1).prod()
        return analyzer

    ret = []
    for i in results:
        ret.append(get_my_analyzer(i[0]))
    dw_rets = pd.DataFrame(ret)
    dw_rets_sorted = dw_rets.sort_values(by='nav', ascending=False)
    dw_rets_sorted.to_excel("result/navs_rank_{}.xlsx".format(datetime.now().strftime("%m%d%H%M%S")))
    print(dw_rets_sorted.head())

def get_buy_size_while_use_next_day_open(self):
    try:
        expected_buy_price = max(self.data.open[1], self.data.close[0])
    except IndexError:
        expected_buy_price = self.data.close[0]
    # 当前市场价格
    if expected_buy_price > 0:  # 避免除以零
        buy_size = int(self.broker.get_cash() / expected_buy_price / 100) * 100
    return buy_size