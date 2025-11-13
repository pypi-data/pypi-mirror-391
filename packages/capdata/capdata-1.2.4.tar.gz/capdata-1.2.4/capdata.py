import request.request as rq

import data.curve
import data.market
import data.pricing
import data.refer
import data.risk
from typing import List


def init(name, pwd):
    """
    capdata 认证
    :param name: 用户名
    :param pwd: 密码
    :return:
    """
    auth_json = {'account': name, 'pwd': pwd}
    token = rq.post_no_token("/capdata/auth", auth_json)
    rq.save_token(token)
    print('登录成功')


def get_bond_yield_curve(curve, start, end, freq='d', parse_proto=True, window=None):
    """
    获取债券收益率曲线
    :param curve: 曲线编码
    :param start: 开始时间
    :param end: 结束时间
    :param freq: 频率(1m, d, w)
    :param parse_proto: 是否转化曲线,默认True
    :param window: 时间窗口 ['10:00:00','10:30:00']
    :return:
    """
    return data.curve.get_bond_yield_curve(curve, start, end, freq, window, parse_proto)


def get_bond_spread_curve(curve, start, end, freq='d', parse_proto=True, window=None):
    """
    获取信用利差曲线
    :param curve: 曲线编码
    :param start: 开始时间
    :param end: 结束时间
    :param freq: 频率(1m, d, w)
    :param parse_proto: 是否转化曲线,默认True
    :param window: 时间窗口 ['10:00:00','10:30:00']
    :return:
    """
    return data.curve.get_bond_spread_curve(curve, start, end, freq, window, parse_proto)


def get_ir_yield_curve(curve, start, end, freq='d', parse_proto=True, window=None):
    """
    获取利率收益率曲线
    :param curve: 曲线编码
    :param start: 开始时间
    :param end: 结束时间
    :param freq: 频率(1m, d, w)
    :param parse_proto: 是否转化曲线,默认True
    :param window: 时间窗口 ['10:00:00','10:30:00']
    :return:
    """
    return data.curve.get_ir_yield_curve(curve, start, end, freq, window, parse_proto)


def get_dividend_curve(curve, start, end, freq='d', parse_proto=True, window=None):
    """
    获取股息分红率曲线
    :param curve: 曲线编码
    :param start: 开始时间
    :param end: 结束时间
    :param freq: 频率(1m, d, w)
    :param parse_proto: 是否转化曲线,默认True
    :param window: 时间窗口 ['10:00:00','10:30:00']
    :return:
    """
    return data.curve.get_dividend_curve(curve, start, end, freq, window, parse_proto)


def get_vol_surface(surface, start, end, freq='d', window=None):
    """
    获取波动率曲面数据
    :param surface: 波动率曲面编码
    :param start: 开始时间
    :param end: 结束时间
    :param freq: 频率(1m, d, w)
    :param window: 时间窗口 ['10:00:00','10:30:00']
    :return:
    """
    return data.curve.get_vol_surface(surface, start, end, freq, window)


def get_hist_mkt(inst, start, end, fields, window=None, mkt=None, freq="d", clazz: str = None):
    """
    获取历史行情数据
    :param inst: 产品编码列表 ['200310.IB', '190008.IB']
    :param start: 开始时间  2024-05-09
    :param end: 结束时间  2024-05-10
    :param fields: 需要返回的字段(open、close、high、low、open_ytm、close_ytm、high_ytm、low_ytm、adv_5d、adv_10d、adv_20d、pre_adj_close、post_adj_close、volume、turnover、num_trades、settlement、vwap、open_interest、bid、ask、bid_size、ask_size、trade、trade_size、level1、level2、level2_5、level2_10、lix、'bid','ask')
    :param window: 时间窗口 ['10:00:00','10:30:00']
    :param mkt: 市场
    :param freq: 频率( 1m,1h, d, w)
    :param clazz: 产品类别
    :return:
    """
    return data.market.get_hist_mkt(inst, start, end, fields, window, mkt, freq, clazz)


def get_live_mkt(inst, fields, mkt=""):
    """
    获取日内实时行情数据
    :param inst: 产品编码列表 ['200310.IB', '190008.IB']
    :param fields: 需要返回的字段(bid、ask、level1、level2、level2_5、level2_10、lix)  ['bid','ask']
    :param mkt: 市场
    :return:
    """
    return data.market.get_live_mkt(inst, fields, mkt)


def get_pricing(inst, start, end, fields, window=None, mkt=None, freq="d"):
    """
    获取产品定价数据
    :param inst: 产品编码列表 ['2292030.IB', '2292012.IB']
    :param start: 开始时间  2024-05-26
    :param end: 结束时间  2024-05-29
    :param fields: 需要返回的字段(price、duration、modified_duration、macaulay_duration、convexity、z_spread、dv01、bucket_dv01、cs01、bucket_cs01、delta、gamma、vega、term_bucket_vega、term_strike_bucket_vega、volga、term_bucket_volga、term_strike_bucket_volga、vanna、term_bucket_vanna、term_strike_bucket_vanna、rho)  ['duration','modified_duration']
    :param window:  时间窗口 ['10:00:00','10:30:00']
    :param mkt: 市场
    :param freq: 频率( 1m, d, w)
    :return:
    """
    return data.pricing.get_pricing(inst, start, end, fields, window, mkt, freq)


def get_valuation(inst, start, end, fields, window=None, mkt=None, freq="d"):
    """
    获取产品估值数据
    :param inst: 产品编码列表 ['2292030.IB', '2292012.IB']
    :param start: 开始时间  2024-05-26
    :param end: 结束时间  2024-05-29
    :param fields: 需要返回的字段(present_value、dv01、bucket_dv01、frtb_bucket_dv01、cs01、bucket_cs01、frtb_bucket_cs01、delta、frtb_delta、 gamma、frtb_curvature、vega、term_bucket_vega、term_strike_bucket_vega、frtb_vega、volga、term_bucket_volga、term_strike_bucket_volga、vanna、term_bucket_vanna、term_strike_bucket_vanna、rho)  ['dv01','cs01']
    :param window: 时间窗口 ['10:00:00','10:30:00']
    :param mkt: 市场
    :param freq: 频率( 1m, d, w)
    :return:
    """
    return data.pricing.get_valuation(inst, start, end, fields, window, mkt, freq)


def get_sim_bond_yield_curve(curve, sim_date, base_date, num_start=0, num_end=500, parse_proto=False):
    """
    获取债券收益率曲线情景模拟数据
    :param curve: 曲线编码  CN_TREAS_STD_SIM
    :param sim_date: 情景时间  2024-01-05
    :param base_date: 基础时间 2024-01-04
    :param num_start: 情景开始数   0
    :param num_end: 情景结束数   500
    :param parse_proto: 是否转化proto  False
    :return:
    """
    return data.risk.get_sim_bond_yield_curve(curve, sim_date, base_date, num_start, num_end, parse_proto)


def get_hist_sim_ir_curve(curve, sim_date, base_date, num_sims=200):
    """
    获取历史模拟的利率收益率曲线数据
    :param curve: 曲线编码  CN_TREAS_STD
    :param sim_date: 情景时间  2024-05-28
    :param base_date:  情景数   200
    :param num_sims: 基础时间 2024-05-27
    :return:
    """
    return data.risk.get_hist_sim_ir_curve(curve, sim_date, base_date, num_sims)


def get_hist_sim_credit_curve(curve, sim_date, base_date, num_sims=200):
    """
    获取历史模拟的信用利差曲线数据
    :param curve: 曲线编码  CN_CORP_AAA_SPRD_STD
    :param sim_date: 情景时间  2024-05-28
    :param base_date: 情景数   200
    :param num_sims: 基础时间 2024-05-27
    :return:
    """
    return data.risk.get_hist_sim_credit_curve(curve, sim_date, base_date, num_sims)


def get_hist_stressed_ir_curve(curve, sim_date, base_date, num_sims=200):
    """
    获取历史压力情景下利率收益率曲线数据
    :param curve: 曲线编码  CN_TREAS_STD
    :param sim_date:  情景时间  2024-05-28
    :param base_date:  情景数   200
    :param num_sims: 基础时间 2024-05-27
    :return:
    """
    return data.risk.get_hist_stressed_ir_curve(curve, sim_date, base_date, num_sims)


def get_hist_stressed_credit_curve(curve, sim_date, base_date, num_sims=200):
    """
    获取历史压力情景下信用利差曲线数据
    :param curve: 曲线编码  CN_CORP_AAA_SPRD_STD
    :param sim_date: 情景时间  2024-05-28
    :param base_date: 情景数   200
    :param num_sims: 基础时间 2024-05-27
    :return:
    """
    return data.risk.get_hist_sim_credit_curve(curve, sim_date, base_date, num_sims)


def get_inst_sim_pnl(inst, sim_date, base_date, num_sims=200):
    """
    获取产品模拟情景下损益数据
    :param inst: 产品编码  ['2171035.IB','2105288.IB']
    :param sim_date:  情景时间  2024-05-28
    :param base_date: 基础时间 2024-05-27
    :param num_sims: 情景数   200
    :return:
    """
    return data.risk.get_inst_sim_pnl(inst, sim_date, base_date, num_sims)


def get_inst_stressed_pnl(inst, sim_date, base_date, num_sims=200):
    """
    获取产品压力情景下损益数据
    :param inst: 产品编码  ['2171035.IB','2105288.IB']
    :param sim_date: 情景时间  2024-05-28
    :param base_date: 基础时间 2024-05-27
    :param num_sims: 情景数   200
    :return:
    """
    return data.risk.get_inst_stressed_pnl(inst, sim_date, base_date, num_sims)


def get_inst_var(inst, sim_date, base_date, fields, confidence_interval=0.95):
    """
    获取产品Value-at-Risk数据
    :param inst: 产品编码  2171035.IB
    :param sim_date:  情景时间  2024-05-28
    :param base_date: 基础时间 2024-05-27
    :param fields: 响应字段 (var, mirror_var, stressed_var, mirror_stressed_var, es, mirror_es, stressed_es, mirror_stressed_es) ['var','es']
    :param confidence_interval: 置信区间 0.95
    :return:
    """
    return data.risk.get_inst_var(inst, sim_date, base_date, fields, confidence_interval)


def get_holidays(calendar: str):
    """
    获取指定日历下的假期数据
    :param calendar:  日历 CFETS
    :return:
    """
    return data.refer.get_holidays(calendar)


def get_ir_index(ccy: List[str]):
    """
    获取基准利率列表
    :param ccy: 基准利率编码列表 ['CNY']
    :return:
    """
    return data.refer.get_ir_index(ccy)


def get_ir_index_definition(ir_index: List[str]):
    """
    获取基准利率定义数据
    :param ir_index: 产品编码列表 ['FR_001','FR_007']
    :return:
    """
    return data.refer.get_ir_index_definition(ir_index)


def get_ir_curve_list(ccy: List[str], ir_index: List[str]):
    """
    获取利率收益率曲线列表
    :param ccy: 货币列表 ['CNY']
    :param ir_index: 基准利率列表 ['FR_007']
    :return:
    """
    return data.refer.get_ir_curve_list(ccy, ir_index)


def get_ir_curve_definition(curve_codes: List[str]):
    """
    获取利率收益率曲线定义
    :param curve_codes: 曲线编码列表 ['CNY_FR_007']
    :return:
    """
    return data.refer.get_ir_curve_definition(curve_codes)


def get_bond_yield_curve_list(ccy: List[str], ir_index: List[str]):
    """
    获取债券收益率曲线列表
    :param ccy: 货币列表 ['CNY']
    :param ir_index: 基准利率列表 []
    :return:
    """
    return data.refer.get_bond_yield_curve_list(ccy, ir_index, 'MKT')


def get_std_bond_yield_curve_list(ccy: List[str], ir_index: List[str]):
    """
    获取标准债券收益率曲线列表
    :param ccy: 货币列表 ['CNY']
    :param ir_index: 基准利率列表 []
    :return:
    """
    return data.refer.get_bond_yield_curve_list(ccy, ir_index, 'STD')


def get_bond_yield_curve_definition(curve_codes: List[str]):
    """
    获取债券收益率曲线定义
    :param curve_codes: 曲线编码列表 ['CN_RAILWAY_MKT'，'CN_CLO_LEASE_ABS_AA_STD']
    :return:
    """
    return data.refer.get_bond_yield_curve_definition(curve_codes)


def get_bond_credit_curve_list(ccy: List[str], ir_index: List[str]):
    """
    获取债券信用利差曲线列表
    :param ccy: 货币列表 ['CNY']
    :param ir_index: 基准利率列表 []
    :return:
    """
    return data.refer.get_bond_credit_curve_list(ccy, ir_index, 'MKT')


def get_std_bond_credit_curve_list(ccy: List[str], ir_index: List[str]):
    """
    获取标准债券信用利差曲线列表
    :param ccy: 货币列表 ['CNY']
    :param ir_index: 基准利率列表 []
    :return:
    """
    return data.refer.get_bond_credit_curve_list(ccy, ir_index, 'STD')


def get_bond_credit_curve_definition(curve_codes: List[str]):
    """
    获取债券信用利差曲线定义
    :param curve_codes: 曲线编码列表 ['CN_SP_MTN_AA+_SPRD_STD'，'CN_CORP_AAA-_SPRD_STD']
    :return:
    """
    return data.refer.get_bond_credit_curve_definition(curve_codes)


def get_bond(inst_type: List[str], bond_type: list[str], currency: List[str], coupon_type: List[str],
             maturity_type: List[str]):
    """
      获取债券编码列表
      :param inst_type: 产品类型列表 VANILLA_BOND AMORTIZING_BOND CALLABLE_BOND CONVERTIBLE_BOND
      :param bond_type:债券类型列表 SUPRANATIONAL SOVEREIGN AGENCY LOCALAUTHORITY CORPORATE
      :param currency: 货币列表
      :param coupon_type:票息类型列表 ZERO FIXED FLOATING STRUCTURED
      :param maturity_type:期限类型列表 NORMAL PERPETUAL
      :return:   债券编码列表
      """
    return data.refer.get_bond(inst_type, bond_type, currency, coupon_type, maturity_type)


def get_bond_definition(bond_codes: List[str]):
    """
    获取债券定义列表
    :param bond_codes:
    :return:券定义列表
    """
    return data.refer.get_bond_definition(bond_codes)


def get_bond_credit_info(bond_codes: List[str]):
    """
    获取债券信用信息列表
    :param bond_codes:
    :return: 债券信用信息列表
    """
    return data.refer.get_bond_credit_info(bond_codes)


def get_bond_issue_info(bond_codes: List[str]):
    """
    获取债券发行信息列表
    :param bond_codes: 债券编码列表
    :return: 债券发行信息列表
    """
    return data.refer.get_bond_issue_info(bond_codes)


def get_bond_mkt_info(bond_codes: List[str]):
    """
     获取债券市场信息列表
    :param bond_codes: 债券编码列表
    :return: 获取债券市场信息列表
    """
    return data.refer.get_bond_mkt_info(bond_codes)


def get_bond_class_info(bond_codes: List[str]):
    """
     获取债券分类信息列表
    :param bond_codes: 债券编码列表
    :return: 获取债券分类信息列表
    """
    return data.refer.get_bond_class_info(bond_codes)


def get_bond_fee_info(bond_codes: List[str]):
    """
     获取债券税费信息列表
    :param bond_codes: 债券编码列表
    :return: 获取债券分类信息列表
    """
    return data.refer.get_bond_fee_info(bond_codes)


def get_risk_factor_definition(risk_factor_code: List[str]):
    """
    获取风险因子定义
    :param risk_factor_code: 风险因子编码列表 ['RF_CN_TREAS_ZERO_1M']
    :return:
    """
    return data.refer.get_risk_factor_definition(risk_factor_code)


def get_risk_factor_group_definition(risk_factor_group: List[str]):
    """
    获取风险因子组定义
    :param risk_factor_group: 风险因子组编码列表 ['FI_BOND_IR_CN_IB_HIST_SIM_SCN_GROUP']
    :return:
    """
    return data.refer.get_risk_factor_group_definition(risk_factor_group)


"""
获取利率产品定义
参数： 
  inst_type  -- 产品类型列表,必填，可选 SWAP, CROSS, DEPO  ['DEPO']
  inst_codes -- 产品编码  []
  ccy       -- 货币 ['CNY']
  ir_index   -- 基准利率列表 []
"""


def get_ir_vanilla_instrument_definition(inst_type: [str], ccy: [str], inst_codes: [str], ir_index: [str]):
    """
    获取利率产品定义
    :param inst_type: 产品类型列表,必填，可选 SWAP, CROSS, DEPO  ['DEPO']
    :param ccy:  产品编码  []
    :param inst_codes:  货币 ['CNY']
    :param ir_index: 基准利率列表 []
    :return:
    """
    if (inst_codes is None or len(inst_codes) == 0):
        raise ValueError(f'inst_codes 值不能空')
    return data.refer.get_ir_vanilla_instrument_definition(inst_type, ccy, inst_codes, ir_index)


def get_ir_vanilla_swap_list(ccy: [] = None, ir_index: [] = None, swap_type: [] = None):
    """
    获取利率互换列表
    :param ccy: 货币 ['CNY']
    :param ir_index: 基准利率列表 []
    :param swap_type: 互换类型列表,预留字段 []
    :return:
    """
    return data.refer.get_ir_vanilla_swap_list(ccy, ir_index, swap_type)


def get_ir_depo_list(ccy: [] = None):
    """
    获取同业拆借列表
    :param ccy: 货币 ['CNY']
    :return:
    """
    return data.refer.get_ir_depo_list(ccy)


def get_xccy_swap_list(ccy: [] = None, ir_index: [] = None):
    """
    获取交叉货币列表
    :param ccy: 货币 ['CNY']
    :param ir_index: 基准利率列表 []
    :return:
    """
    return data.refer.get_xccy_swap_list(ccy, ir_index)
