# 导入backtrader框架
import backtrader as bt
from flights.hq.uhq_akshare import *


# 创建策略继承bt.Strategy
class SmaStrategy(bt.Strategy):
    params = (
        # 均线参数设置15天，15日均线
        ("maperiod", 15),
        ("printlog", False),
    )

    def log(self, txt, dt=None, doprint=False):
        # 记录策略的执行日志
        if self.params.printlog or doprint:
            dt = dt or self.datas[0].datetime.date(0)
            print("%s, %s" % (dt.isoformat(), txt))

    def __init__(self):
        # 保存收盘价的引用
        self.dataclose = self.datas[0].close
        # 跟踪挂单
        self.order = None
        # 买入价格和手续费
        self.buyprice = None
        self.buycomm = None
        # 加入均线指标
        self.sma = bt.indicators.SimpleMovingAverage(
            self.datas[0], period=self.params.maperiod
        )
        # 订单状态通知，买入卖出都是下单

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # broker 提交/接受了，买/卖订单则什么都不做
            return

        # 检查一个订单是否完成
        # 注意: 当资金不足时，broker会拒绝订单
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(
                    "已买入, 价格: %.2f, 费用: %.2f, 佣金 %.2f"
                    % (order.executed.price, order.executed.value, order.executed.comm)
                )
                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm
            elif order.issell():
                self.log(
                    "已卖出, 价格: %.2f, 费用: %.2f, 佣金 %.2f"
                    % (order.executed.price, order.executed.value, order.executed.comm)
                )
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

    def next(self):
        # 记录收盘价
        self.log("Close, %.2f" % self.dataclose[0])

        # 如果有订单正在挂起，不操作
        if self.order:
            return

        # 如果没有持仓则买入
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
                # 测略结束时，多用于参数调优

    def stop(self):
        self.log(
            "(均线周期 %2d) 期末资金 %.2f"
            % (self.params.maperiod, self.broker.getvalue()),
            doprint=True,
        )

class SmaCrossStrategy(bt.Strategy):
    params = (
        # 均线参数设置15天，15日均线
        ("fperiod", 50),
        ("speriod", 200),
        ("printlog", False),
    )

    def log(self, txt, dt=None, doprint=False):
        # 记录策略的执行日志
        if self.params.printlog or doprint:
            dt = dt or self.datas[0].datetime.date(0)
            print("%s, %s" % (dt.isoformat(), txt))

    def __init__(self):
        # 保存收盘价的引用
        self.dataclose = self.datas[0].close
        # 跟踪挂单
        self.order = None
        # 买入价格和手续费
        self.buyprice = None
        self.buycomm = None
        # 加入均线指标
        self.fsma = bt.indicators.SimpleMovingAverage(
            self.datas[0], period=self.params.fperiod
        )
        self.ssma = bt.indicators.SimpleMovingAverage(
            self.datas[0], period=self.params.speriod
        )
        # 订单状态通知，买入卖出都是下单

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # broker 提交/接受了，买/卖订单则什么都不做
            return

        # 检查一个订单是否完成
        # 注意: 当资金不足时，broker会拒绝订单
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(
                    "已买入, 价格: %.2f, 费用: %.2f, 佣金 %.2f"
                    % (order.executed.price, order.executed.value, order.executed.comm)
                )
                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm
            elif order.issell():
                self.log(
                    "已卖出, 价格: %.2f, 费用: %.2f, 佣金 %.2f"
                    % (order.executed.price, order.executed.value, order.executed.comm)
                )
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

    def next(self):
        # 记录收盘价
        self.log("Close, %.2f" % self.dataclose[0])

        # 如果有订单正在挂起，不操作
        if self.order:
            return

        # 如果没有持仓则买入
        if not self.position:
            # 今天的收盘价在均线价格之上
            if self.fsma[0] > self.ssma[0]:
                # 买入
                self.log("买入单, %.2f" % self.dataclose[0])
                # 跟踪订单避免重复
                self.order = self.buy()
        else:
            # 如果已经持仓，收盘价在均线价格之下
            if self.fsma[0] < self.ssma[0]:
                # 全部卖出
                self.log("卖出单, %.2f" % self.dataclose[0])
                # 跟踪订单避免重复
                self.order = self.sell()
                # 测略结束时，多用于参数调优

    def stop(self):
        self.log(
            "(均线周期 %2d,%2d) 期末资金 %.2f"
            % (self.params.fperiod,self.params.speriod, self.broker.get_value()),
            doprint=True,
        )

cerebro = bt.Cerebro()  # 创建Cerebro引擎
# 参数调优，看具体哪根均线的效果好。
# cerebro.optstrategy(SmaStrategy, maperiod=range(2, 50))
cerebro.optstrategy(SmaCrossStrategy, fperiod=range(2, 50))
cerebro.adddata(get_stock_history_sina(report_code="sh600570",start_date_str="20010101", end_date_str="20251231"))  # 加载交易数据
cerebro.broker.setcash(100000.0)  # 设置投资金额100000.0
# 每笔交易使用固定交易量
cerebro.addsizer(bt.sizers.FixedSize, stake=10)
# 设置佣金为0.0
cerebro.broker.setcommission(commission=0.0)
# cerebro.broker.setcommission(commission=0.001) # 设置交易手续费为 0.1%
# 引擎运行前打印期出资金
# print("组合期初资金: %.2f" % cerebro.broker.getvalue())
cerebro.run(maxcpus=1)

# cerebro.plot(style='candlestick')