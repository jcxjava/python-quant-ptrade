import numpy as np


def initialize(context):
    """初始化——tick级别策略"""
    # 股票池
    g.security = '600570.SS'
    set_universe(g.security)

    # 自定义参数
    g.tick_count = 0
    g.stop_loss = -0.02

    # 回测配置
    set_benchmark('000300.XBHS')
    set_commission(commission_ratio=0.0003, min_commission=5.0)
    set_slippage(slippage=0.002)

    # tick策略二选一：
    #   方式一: run_interval(context, interval_handle, seconds=10) — 自定义间隔
    #   方式二: tick_data(context, data) — 固定每3秒


def before_trading_start(context, data):
    """盘前处理  运行时间: 9:10"""
    g.tick_count = 0


def handle_data(context, data):
    """盘中主逻辑  tick策略中可留空"""
    pass


# 方式一: run_interval 回调函数
def interval_handle(context):
    security = g.security
    g.tick_count += 1

    snapshot = get_snapshot(security)
    if snapshot is None:
        return

    price = snapshot[security]['last_px']
    position = get_position(security)

    log.info("[Tick:%d] %s 最新价: %.2f 持仓: %.0f股" % (
        g.tick_count, security, price, position.amount
    ))


# 方式二: tick_data 回调函数
def tick_data(context, data):
    security = g.security
    g.tick_count += 1

    bar = data[security]
    price = bar.price
    position = get_position(security)

    log.info("[Tick:%d] %s 最新价: %.2f 持仓: %.0f股" % (
        g.tick_count, security, price, position.amount
    ))


def after_trading_end(context, data):
    """盘后处理  运行时间: 15:30"""
    log.info("当日结束, tick总数: %d" % (g.tick_count))
