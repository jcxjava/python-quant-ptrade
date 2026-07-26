import numpy as np


def initialize(context):
    """初始化——分钟策略启动时间默认 09:30"""
    # 股票池
    g.security = ['600570.SS', '000001.SZ']
    set_universe(g.security)

    # 自定义参数
    g.bar_period = 5
    g.hold_bars = 10
    g.stop_loss = -0.05

    # 回测配置
    set_benchmark('000300.XBHS')
    set_commission(commission_ratio=0.0003, min_commission=5.0)
    set_slippage(slippage=0.002)

    # 状态变量
    g.entry_price = None
    g.hold_count = 0


def before_trading_start(context, data):
    """盘前处理  运行时间: 9:10"""
    pass


def handle_data(context, data):
    """盘中主逻辑  每分钟运行一次(09:30~15:00)"""
    current_time = context.blotter.current_dt.time()

    # 每隔N分钟执行一次（如需每分钟执行，删除此判断）
    if current_time.minute % g.bar_period != 0:
        return

    security = g.security[0] if isinstance(g.security, list) else g.security

    # 获取数据
    df = get_history(g.hold_bars + 10, '1m', ['close', 'volume'], security, fq=None, include=False)
    if df is None or len(df) < 2:
        return

    # 计算指标
    close_series = df['close']

    # 生成信号 & 执行交易
    price = close_series.iloc[-1]
    cash = context.portfolio.cash
    position = get_position(security)

    # [★ 在此编写你的买卖逻辑]

    log.info("[%s] %s 价格: %.2f 持仓: %.0f股" % (
        current_time.strftime('%H:%M'), security, price, position.amount
    ))


def after_trading_end(context, data):
    """盘后处理  运行时间: 15:30"""
    log.info("当日结束, 总资产: %.2f" % (context.portfolio.portfolio_value))
