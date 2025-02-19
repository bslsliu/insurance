from backtest_util import *


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
        self.year_ma_line = bt.indicators.MovingAverageSimple(period=250)
        self.crossover = bt.indicators.CrossOver(self.macd.macd, self.macd.signal)  # MACD线与Signal线的交叉信号

    def next(self):
        # 检查是否需要止损
        if self.position.size > 0 and self.params.stop_loss_pct > 0:
            if self.data.close[0] < self.buy_price * (1 - self.params.stop_loss_pct):
                self.close()  # 卖出止损
                return

        # 根据MACD信号做买入或卖出操作
        if self.crossover > 0 and self.data.close[0] > self.year_ma_line:  # 如果MACD线穿越Signal线向上 并且站上年线
            if self.position.size <= 0:  # 如果当前没有持仓
                self.buy(size=get_buy_size_while_use_next_day_open(self))  # 买入
        elif self.crossover < 0 or self.data.close[0] < self.year_ma_line:  # 如果MACD线穿越Signal线向下
            if self.position.size > 0:  # 如果当前有持仓
                self.close()  # 卖出

    def notify_order(self, order):
        if order.status == bt.Order.Canceled:
            print(f"订单取消: {order.ref}")
        elif order.status == bt.Order.Margin:
            print(f"保证金不足: {order.ref}")
        elif order.status == bt.Order.Rejected:
            print(f"订单拒绝: {order.ref}")


def run_macd_strategy():
    cerebro = bt.Cerebro()
    cerebro.adddata(
        get_stock_history_sina(report_code="sh600570", start_date_str="20050105", end_date_str="20251231"))
    cerebro.addstrategy(MACDStrategy)
    cerebro.addanalyzer(bt.analyzers.PyFolio)
    cerebro.broker.setcash(100000.0)  # 设置投资金额100000.0
    cerebro.broker.setcommission(commission=0.0)
    results = cerebro.run()
    strat = results[0]
    generate_qs_report(strat, "恒生电子")


def opt_macd_strategy():
    cerebro = bt.Cerebro()
    cerebro.adddata(
        get_stock_history_sina(report_code="sh600570", start_date_str="20050105", end_date_str="20251231"))
    cerebro.optstrategy(MACDStrategy, macd1=range(5, 14), macd2=range(20, 30), signal=range(3, 10))
    cerebro.addanalyzer(bt.analyzers.PyFolio)
    cerebro.broker.setcash(100000.0)  # 设置投资金额100000.0
    cerebro.broker.setcommission(commission=0.0)
    results = cerebro.run()
    rank_strategy_navs(results)


if __name__ == "__main__":
    run_macd_strategy()
