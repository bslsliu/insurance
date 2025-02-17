from flights.hq.uhq_akshare import *
from datetime import datetime
import quantstats as qs


# 创建MACD策略类
class MACDStrategy(bt.Strategy):
    # 定义MACD参数
    params = (
        ('macd1', 5),  # 短期EMA的周期
        ('macd2', 27),  # 长期EMA的周期
        ('signal', 7),  # Signal线的周期
        ('stop_loss_pct', 0),  # 不设置止损
    )

    def __init__(self):
        # 初始化MACD指标
        self.macd = bt.indicators.MACD(self.data.close,
                                       period_me1=self.params.macd1,
                                       period_me2=self.params.macd2,
                                       period_signal=self.params.signal)
        self.crossover = bt.indicators.CrossOver(self.macd.macd, self.macd.signal)  # MACD线与Signal线的交叉信号
        # 用于追踪买入价格
        self.buy_price = None
        self.trade_log = []  # 存储交易记录

    def get_buy_size(self):
        try :
            expected_buy_price = max(self.data.open[1], self.data.close[0])
        except IndexError:
            expected_buy_price = self.data.close[0]
        # 当前市场价格
        if expected_buy_price > 0:  # 避免除以零
            buy_size = int (self.broker.get_cash() / expected_buy_price / 100) * 100
        return buy_size

    def next(self):
        # 检查是否需要止损
        if self.position.size > 0 and self.params.stop_loss_pct > 0:
            if self.data.close[0] < self.buy_price * (1 - self.params.stop_loss_pct):
                self.close()  # 卖出止损
                return

        # 根据MACD信号做买入或卖出操作
        if self.crossover > 0:  # 如果MACD线穿越Signal线向上
            if self.position.size <= 0:  # 如果当前没有持仓
                self.buy(size=self.get_buy_size())  # 买入
        elif self.crossover < 0:  # 如果MACD线穿越Signal线向下
            if self.position.size > 0:  # 如果当前有持仓
                self.close()  # 卖出

    def notify_order(self, order):

        if order.status == bt.Order.Completed:
            trade_date = self.data.datetime.date(0)  # 交易日期
            if order.isbuy():
                self.buy_price = order.executed.price  # 记录买入价格
                self.trade_log.append({
                    "日期": trade_date,
                    "类型": "买入",
                    "价格": order.executed.price,
                    "头寸": self.position.size,
                    "利润": None,  # 买入时利润未知
                    "净值": self.broker.get_value()
                })
            elif order.issell():
                profit = (order.executed.price - self.buy_price) * abs(order.executed.size)
                self.trade_log.append({
                    "日期": trade_date,
                    "类型": "卖出",
                    "价格": order.executed.price,
                    "头寸": self.position.size,
                    "利润": profit,
                    "净值": self.broker.get_value()
                })
        elif order.status == bt.Order.Canceled:
            print(f"订单取消: {order.ref}")
        elif order.status == bt.Order.Margin:
            print(f"保证金不足: {order.ref}")
        elif order.status == bt.Order.Rejected:
            print(f"订单拒绝: {order.ref}")

    def notify_trade(self, trade):
        # 一个trade结束的时候输出信息
        if trade.isclosed:
            pass
        if trade.isopen:
            pass

    def stop(self):
        """ 在回测结束时，保存交易数据到 CSV """
        # df = pd.DataFrame(self.trade_log)
        # df.to_csv("result/trade_log_{}.csv".format(datetime.now().strftime("%m%d%H%M%S")), index=False,
        #           encoding='utf-8-sig')
        print(f" 参数 {vars(self.params)}，"
              f" 总资产 {round(self.broker.get_value(),2)}")


def run_macd_strategy():
    cerebro = bt.Cerebro()
    cerebro.adddata(
        get_stock_history_sina(report_code="sh600570", start_date_str="20010101", end_date_str="20251231"))
    # cerebro.optstrategy(MACDStrategy, macd1 = range(5,14), macd2=range(20,30),signal = range(3,10))
    cerebro.addstrategy(MACDStrategy)
    cerebro.addanalyzer(bt.analyzers.PyFolio)

    cerebro.broker.setcash(100000.0)  # 设置投资金额100000.0
    # 改成allin，而不是固定的持仓量
    cerebro.broker.setcommission(commission=0.0)
    results = cerebro.run()
    strat = results[0]
    pyfoliozer = strat.analyzers.getbyname('pyfolio')
    returns, positions, transactions, gross_lev = pyfoliozer.get_pf_items()
    returns = returns.dropna()
    returns.index = returns.index.tz_convert(None)
    qs.reports.html(returns, output='stats.html',
                    download_filename='result/backtest-600570.html', title='Stock Sentiment')


if __name__ == "__main__":
    run_macd_strategy()
