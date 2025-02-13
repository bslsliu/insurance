import backtrader as bt
from flights.hq.uhq_akshare import *


class TestStrategy(bt.Strategy):
    params = (
        ("maperiod", 15),
        ("exitbars", 5),
    )

    def log(self, txt, dt=None):
        # 记录策略的执行日志
        dt = dt or self.datas[0].datetime.date(0)
        print(f"{dt.isoformat()}, {txt}")

    def __init__(self):
        # 保存收盘价的引用
        self.dataclose = self.datas[0].close
        # 跟踪挂单
        self.order = None
        self.buyprice = None
        self.buycomm = None
        self.sma = bt.indicators.MovingAverageSimple(
            self.datas[0], period=self.params.maperiod
        )
        self.trade_result = []

    def next(self):
        # 记录收盘价
        self.log(f"Close, {self.dataclose[0]}")
        # 如果有订单正在挂起，不操作
        if self.order:
            return
        self.trade_by_sma()

    def notify_order(self, order):
        self.log(f"order change {order.status}")
        if order.status in [order.Submitted, order.Accepted]:
            # broker 提交/接受了，买/卖订单则什么都不做
            return
        # 检查一个订单是否完成
        # 注意: 当资金不足时，broker会拒绝订单
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log("已买入, %.2f" % order.executed.price)
                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm
            elif order.issell():
                self.log("已卖出, %.2f" % order.executed.price)

            # 记录当前交易数量
            self.bar_executed = len(self)

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log("订单取消/保证金不足/拒绝")

        # 其他状态记录为：无挂起订单
        self.order = None

    # 交易状态通知，一买一卖算交易
    def notify_trade(self, trade):
        if not trade.isclosed:
            return
        self.log("交易利润, 毛利润 %.2f, 净利润 %.2f" % (trade.pnl, trade.pnlcomm))
        self.trade_result.append(
            [
                self.datas[0].datetime.date(-1 * trade.barlen).isoformat(),
                trade.data.open[-1 * trade.barlen],
                self.datas[0].datetime.date(0).isoformat(),
                trade.data.open[0],
                trade.size,
                trade.pnl,
                trade.pnlcomm,
            ]
        )

    def stop(self):
        self.log(
            "(均线周期 %2d)期末资金 %.2f"
            % (self.params.maperiod, self.broker.getvalue()),
        )
        print(self.trade_result)

    # 如果K线收盘价出现三连跌，则买入。
    def trade_simple(self):
        if not self.position:
            # 今天的收盘价在均线价格之上
            if len(self) >= (self.bar_executed + self.params.exitbars):
                # 全部卖出
                self.log(f"order sale")
                # 跟踪订单避免重复
                self.order = self.sell()
        else:
            # 卖出逻辑也很简单： 5个K线柱后（第6个K线柱）不管涨跌都卖。
            if self.dataclose[0] < self.dataclose[-1]:
                if self.dataclose[-1] < self.dataclose[-2]:
                    self.log(f"order buy")
                    self.buy()

    def trade_by_sma(self):
        if not self.position:
            # 今天的收盘价在均线价格之上
            if self.dataclose[0] > self.sma[0]:
                # 买入
                self.log("买入单, %.2f" % self.dataclose[0])
                # 跟踪订单避免重复
                self.order = self.buy()
        else:
            # 如果已经持仓，收盘价在均线价格之下
            if self.dataclose[0] < self.sma[0]:
                # 全部卖出
                self.log("卖出单, %.2f" % self.dataclose[0])
                # 跟踪订单避免重复
                self.order = self.sell()

cerebro = bt.Cerebro()  # 创建Cerebro引擎
cerebro.addstrategy(TestStrategy, maperiod=20, exitbars=5)  # 为Cerebro引擎添加策略
cerebro.adddata(get_stock_history_sina(report_code="sh600570"))  # 加载交易数据
cerebro.broker.setcash(100000.0)  # 设置投资金额100000.0
# 每笔交易使用固定交易量
cerebro.addsizer(bt.sizers.FixedSize, stake=10)
# 设置佣金为0.0
cerebro.broker.setcommission(commission=0.0)
# 引擎运行前打印期出资金
# print("组合期初资金: %.2f" % cerebro.broker.getvalue())
cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name="mysharpe")
thestrats = cerebro.run(maxcpus=1)
print("夏普比率:", thestrats[0].analyzers.mysharpe.get_analysis())

cerebro.plot(style="candlestick")
