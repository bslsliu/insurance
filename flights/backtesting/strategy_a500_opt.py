from flights.hq.uhq_akshare import *
from datetime import datetime


# 创建策略类
class MACDStrategy(bt.Strategy):
    # 定义MACD参数
    params = (
        ('macd1', 12),  # 短期EMA的周期
        ('macd2', 26),  # 长期EMA的周期
        ('signal', 9),  # Signal线的周期
        ('stop_loss_pct', 0.1),  # 止损百分比（10%）
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
        self.last_date = self.data.datetime.date(-1)

    def get_buy_size(self):
        cash = self.broker.get_cash()  # 当前现金余额
        if self.data.datetime.date() < self.last_date:
            buy_price = self.data.open[1]  # 当前市场价格
            if buy_price > 0:  # 避免除以零
                buy_size = int(cash / buy_price)  # 计算可以买入的数量，向下取整
        else:
            buy_size = int(cash / self.data.open[0])
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
                profit = (order.executed.price - self.buy_price) * order.executed.size * -1
                self.trade_log.append({
                    "日期": trade_date,
                    "类型": "卖出",
                    "价格": order.executed.price,
                    "头寸": self.position.size,
                    "利润": profit,
                    "净值": self.broker.get_value()
                })

    def stop(self):
        """ 在回测结束时，保存交易数据到 CSV """
        df = pd.DataFrame(self.trade_log)
        df.to_csv("result/trade_log_{}.csv".format(datetime.now().strftime("%m%d%H%M%S")), index=False,
                  encoding='utf-8-sig')
        print(f" 参数 {vars(self.params)}，"
              f" 总资产 {self.broker.get_value()}")


def run_macd_strategy():
    cerebro = bt.Cerebro()
    cerebro.adddata(
        get_stock_history_sina(report_code="sh600570", start_date_str="20010101", end_date_str="20251231"))
    cerebro.optstrategy(MACDStrategy, stop_loss_pct=[0, 0.1])
    # cerebro.addstrategy(MACDStrategy)
    cerebro.broker.setcash(100000.0)  # 设置投资金额100000.0
    # 改成allin，而不是固定的持仓量
    cerebro.broker.setcommission(commission=0.0)
    cerebro.run(maxcpus=1)
    # cerebro.plot()


if __name__ == "__main__":
    run_macd_strategy()
