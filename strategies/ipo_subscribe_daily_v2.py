"""
新股/新可转债自动申购策略 v2。
每交易日 9:31 批量申购当日全部 IPO，盘后 15:30 查询中签结果。
"""


def initialize(context):
    g.black_stocks = []
    g.enable_lucky_check = True

    run_daily(context, ipo_subscribe, time='09:31')

    # 占位股票池，满足平台要求
    g.security = '600570.SS'
    set_universe(security_list=g.security)


def ipo_subscribe(context):
    ipo_dict = get_ipo_stocks()
    log.info("[IPO申购] %s" % ipo_dict)
    if ipo_dict is None:
        return

    result = ipo_stocks_order(submarket_type=None, black_stocks=g.black_stocks)
    log.info("[IPO申购] 结果: %s" % result)

    if result is None:
        log.info("[IPO申购] 委托返回为空")
        return

    if not isinstance(result, dict):
        log.info("[IPO申购] 委托结果异常: %s" % result)
        return

    success_count = 0
    fail_count = 0

    for stock_code, detail in result.items():
        if not isinstance(detail, dict):
            continue

        status = detail.get('entrust_status', -1)
        entrust_no = detail.get('entrust_no', '')
        amount = detail.get('redemption_amount', '')

        if status == 1:
            success_count += 1
            log.info("[IPO申购] 成功 %s, 委托编号=%s, 数量=%s" % (stock_code, entrust_no, amount))
        elif status == 0:
            fail_count += 1
            log.info("[IPO申购] 失败 %s, 委托编号=%s" % (stock_code, entrust_no))

    log.info("[IPO申购] 完成, 成功=%d, 失败=%d" % (success_count, fail_count))


def handle_data(context, data):
    pass


def after_trading_end(context, data):
    if not g.enable_lucky_check:
        return

    pre_date = str(get_trading_day(-1)).replace("-", "")
    current_date = context.blotter.current_dt.strftime("%Y%m%d")

    lucky_info = get_lucky_info(pre_date, current_date)
    log.info("[中签查询] 原始返回: %s" % lucky_info)

    if lucky_info is None or len(lucky_info) == 0:
        return

    log.info("[中签查询] %s ~ %s 期间中签结果:" % (pre_date, current_date))
    for info in lucky_info:
        log.info("[中签查询] %s" % info)
