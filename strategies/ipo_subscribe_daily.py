"""
[已弃用] 新股/新可转债自动申购策略 v1。
请使用 ipo_subscribe_daily_v2.py（批量申购版）。
每交易日 9:31 自动获取当日 IPO 清单，按市场分批申购，
盘后 15:30 查询近期中签结果。
"""
import time


def initialize(context):
    # 申购市场: 0=上证普通 1=科创板(需权限) 2=深圳普通 3=创业板 4=可转债
    g.sub_market_types = [0, 2, 3, 4]

    # get_ipo_stocks() 返回字典中各市场对应的 key，首次运行后可先 log.info 确认再回填
    g.ipo_dict_keys = {
        0: '上证普通代码',
        1: '上证科创板代码',
        2: '深证普通代码',
        3: '深证创业板代码',
        4: '可转债代码',
    }

    g.sub_interval = 5
    g.black_stocks = []
    g.enable_lucky_check = True

    # 每日 9:31 触发申购
    run_daily(context, ipo_subscribe, time='09:31')

    # 占位股票池，满足平台要求
    g.security = '600570.SS'
    set_universe(security_list=g.security)


def ipo_subscribe(context):
    # 获取当日 IPO 清单
    ipo_dict = get_ipo_stocks()
    log.info("[IPO申购] 当日IPO清单: %s" % ipo_dict)
    if ipo_dict is None:
        log.info("[IPO申购] 获取当日IPO清单为空")
        return

    sub_market_names = {
        0: "上证普通",
        1: "上证科创板",
        2: "深证普通",
        3: "深证创业板",
        4: "可转债",
    }

    has_any_stock = False

    for market_type in g.sub_market_types:
        market_name = sub_market_names.get(market_type, "未知类型(%d)" % market_type)

        dict_key = g.ipo_dict_keys.get(market_type)
        if dict_key is None:
            log.info("[IPO申购] %s: 未配置字典key，跳过" % market_name)
            continue

        # 检查该市场当日是否有申购标的
        ipo_list = ipo_dict.get(dict_key, [])
        if ipo_list is None or (isinstance(ipo_list, (list, tuple)) and len(ipo_list) == 0):
            log.info("[IPO申购] [无新股] %s: 当日无申购标的" % market_name)
            continue

        stock_count = len(ipo_list) if isinstance(ipo_list, (list, tuple)) else 1
        log.info("[IPO申购] [待申购] %s: %d 支, %s" % (market_name, stock_count, ipo_list))
        has_any_stock = True

        # 调用申购接口
        result = ipo_stocks_order(
            submarket_type=market_type,
            black_stocks=g.black_stocks
        )

        _log_subscription_result(market_name, result)

        if len(g.sub_market_types) > 1:
            time.sleep(g.sub_interval)

    if not has_any_stock:
        log.info("[IPO申购] 当日所有关注市场均无申购标的")
    else:
        log.info("[IPO申购] 申购流程结束")


def _log_subscription_result(market_name, result):
    if result is None:
        log.info("[IPO申购] %s: 委托返回为空" % market_name)
        return

    if not isinstance(result, dict):
        log.info("[IPO申购] %s: 委托结果异常: %s" % (market_name, result))
        return

    success_count = 0
    fail_count = 0

    for stock_code, detail in result.items():
        if not isinstance(detail, dict):
            log.info("[IPO申购] %s %s: 结果格式异常" % (market_name, stock_code))
            continue

        # 委托状态: 0=失败, 1=成功
        status = detail.get('委托状态', detail.get('entrust_status', 0))
        entrust_no = detail.get('委托编号', detail.get('entrust_no', ''))
        amount = detail.get('委托数量', detail.get('entrust_amount', ''))
        msg = detail.get('委托信息', detail.get('entrust_msg', ''))

        if status == 1:
            success_count += 1
            log.info("[IPO申购] [委托成功] %s %s, 委托编号=%s, 数量=%s" % (
                market_name, stock_code, entrust_no, amount))
        else:
            fail_count += 1
            log.info("[IPO申购] [委托拒绝] %s %s, 原因=%s" % (
                market_name, stock_code, msg))

    log.info("[IPO申购] %s: 成功=%d, 失败=%d" % (market_name, success_count, fail_count))


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
