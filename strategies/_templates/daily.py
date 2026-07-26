import numpy as np


def initialize(context):
    """初始化——日线策略启动时间默认 14:50"""
    # 股票池
    g.security = ['600570.SS', '000001.SZ']
    set_universe(g.security)

    # 自定义参数
    g.ma_short = 5
    g.ma_long = 20

    # 回测配置
    set_benchmark('000300.XBHS')
    set_commission(commission_ratio=0.0003, min_commission=5.0)
    set_slippage(slippage=0.002)


def before_trading_start(context, data):
    """盘前处理  运行时间: 9:10"""
    pass


def handle_data(context, data):
    """盘中主逻辑  运行时间: 14:50"""
    # 获取数据
    security = g.security[0] if isinstance(g.security, list) else g.security
    df = get_history(g.ma_long + 1, '1d', 'close', security, fq=None, include=False)
    if df is None or len(df) < g.ma_long:
        return

    # 计算指标
    close_series = df['close']

    # 生成信号 & 执行交易
    price = data[security]['close']
    cash = context.portfolio.cash
    position = get_position(security)

    # [★ 在此编写你的买卖逻辑]

    log.info("当前持仓 %s: %.0f股, 可用资金: %.2f" % (security, position.amount, cash))


def after_trading_end(context, data):
    """盘后处理  运行时间: 15:30"""
    log.info("当日结束, 总资产: %.2f, 持仓市值: %.2f" % (
        context.portfolio.portfolio_value,
        context.portfolio.positions_value
    ))
