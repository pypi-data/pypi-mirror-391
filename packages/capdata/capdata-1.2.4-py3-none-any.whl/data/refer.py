import request.request as rq
from typing import List

"""
获取指定日历下的假期数据
参数:
  calendar -- 日历 CFETS
"""


def get_holidays(calendar: str):
    return rq.post_token("/capdata/get/holidays/" + calendar, None)


"""
获取基准利率列表
参数:
  ccy -- 基准利率编码列表 ['CNY']
"""


def get_ir_index(ccy: List[str]):
    return rq.post_token("/capdata/get/ir/index/list", ccy)


"""
获取基准利率定义数据
参数:
  ir_index -- 产品编码列表 ['FR_001','FR_007']
"""


def get_ir_index_definition(ir_index: List[str]):
    return rq.post_token("/capdata/get/ir/index/definition", ir_index)


"""
获取利率收益率曲线列表
参数:
  ccy -- 货币列表 ['CNY']
  ir_index -- 基准利率列表 ['FR_007']
"""


def get_ir_curve_list(ccy: List[str], ir_index: List[str]):
    param = {'ccy': ccy, 'irIndex': ir_index}
    return rq.post_token("/capdata/get/ir/yield/curve/list", param)


"""
获取利率收益率曲线定义
参数:
  curve_codes -- 曲线编码列表 ['CNY_FR_007'] 
"""


def get_ir_curve_definition(curve_codes: List[str]):
    return rq.post_token("/capdata/get/ir/yield/curve/definition", curve_codes)


"""
获取债券收益率曲线列表
参数:
  ccy -- 货币列表 ['CNY']
  ir_index -- 基准利率列表 []
  curve_class -- 曲线类别 MKT STD
"""


def get_bond_yield_curve_list(ccy: List[str], ir_index: List[str], curve_class: str):
    param = {'ccy': ccy, 'irIndex': ir_index, 'curveClass': curve_class}
    return rq.post_token("/capdata/get/bond/yield/curve/list", param)


"""
获取债券收益率曲线定义
参数:
  curve_codes -- 曲线编码列表 ['CN_RAILWAY_MKT'，'CN_CLO_LEASE_ABS_AA_STD'] 
"""


def get_bond_yield_curve_definition(curve_codes: List[str]):
    return rq.post_token("/capdata/get/bond/yield/curve/definition", curve_codes)


"""
获取债券信用利差曲线列表
参数:
  ccy -- 货币列表 ['CNY']
  ir_index -- 基准利率列表 []
  curve_class -- 曲线类别 MKT STD
"""


def get_bond_credit_curve_list(ccy: List[str], ir_index: List[str], curve_class: str):
    param = {'ccy': ccy, 'irIndex': ir_index, 'curveClass': curve_class}
    return rq.post_token("/capdata/get/bond/sprd/curve/list", param)


"""
获取债券信用利差曲线定义
参数:
  curve_codes -- 曲线编码列表 ['CN_SP_MTN_AA+_SPRD_STD'，'CN_CORP_AAA-_SPRD_STD'] 
"""


def get_bond_credit_curve_definition(curve_codes: List[str]):
    return rq.post_token("/capdata/get/bond/sprd/curve/definition", curve_codes)


def get_bond(inst_type: List[str], bond_type: list[str], currency: List[str], coupon_type: List[str],
             maturity_type: List[str]):
    """
    获取债券编码列表
    :param inst_type: 产品类型列表
    :param bond_type:债券类型列表
    :param currency: 货币列表
    :param coupon_type:票息类型列表
    :param maturity_type:期限类型列表
    :return:   债券编码列表
    """
    param = {'instType': inst_type, 'bondType': bond_type, 'currency': currency, 'couponType': coupon_type,
             'maturityType': maturity_type}
    return rq.post_token("/capdata/get/bond", param)


def get_bond_definition(bond_codes: List[str]):
    """
     获取债券定义信息列表
    :param bond_codes: 债券编码列表
    :return: 债券定义信息列表
    """
    return rq.post_token("/capdata/get/bond/definition", bond_codes)


def get_bond_credit_info(bond_codes: List[str]):
    """
     获取债券信用信息列表
    :param bond_codes: 债券编码列表
    :return: 债券信用信息列表
    """
    return rq.post_token("/capdata/get/bond/credit/info", bond_codes)


def get_bond_issue_info(bond_codes: List[str]):
    """
     获取债券发行信息列表
    :param bond_codes: 债券编码列表
    :return: 债券发行信息列表
    """
    return rq.post_token("/capdata/get/bond/issue/info", bond_codes)


def get_bond_mkt_info(bond_codes: List[str]):
    """
     获取债券市场信息列表
    :param bond_codes: 债券编码列表
    :return: 获取债券市场信息列表
    """
    return rq.post_token("/capdata/get/bond/mkt/info", bond_codes)


def get_bond_class_info(bond_codes: List[str]):
    """
     获取债券分类信息列表
    :param bond_codes: 债券编码列表
    :return: 获取债券分类信息列表
    """
    return rq.post_token("/capdata/get/bond/class/info", bond_codes)


def get_bond_fee_info(bond_codes: List[str]):
    """
     获取债券税费信息列表
    :param bond_codes: 债券编码列表
    :return: 获取债券分类信息列表
    """
    return rq.post_token("/capdata/get/bond/fee/info", bond_codes)


"""
获取风险因子定义
参数:
  risk_factor_code -- 风险因子编码列表 ['RF_CN_TREAS_ZERO_1M'] 
"""


def get_risk_factor_definition(risk_factor_code: List[str]):
    return rq.post_token("/capdata/get/risk/factor/definition", risk_factor_code)


"""
获取风险因子组定义
参数:
  risk_factor_group -- 风险因子组编码列表 ['FI_BOND_IR_CN_IB_HIST_SIM_SCN_GROUP'] 
"""


def get_risk_factor_group_definition(risk_factor_group: List[str]):
    return rq.post_token("/capdata/get/risk/factor/group/definition", risk_factor_group)


"""
获取利率产品定义
参数： 
  inst_type  -- 产品类型列表,必填，可选 SWAP, CROSS, DEPO
  inst_codes -- 产品编码
  ccy       -- 货币
  ir_index   -- 基准利率列表
"""


def get_ir_vanilla_instrument_definition(inst_type: [str], ccy: [str], inst_codes: [str], ir_index: [str]):
    param = {'instType': inst_type, 'ccy': ccy, 'instCodes': inst_codes, 'irIndex': ir_index}
    return rq.post_token("/capdata/get/ir/vanilla/instrument/definition", param)


"""
获取利率互换列表
参数：
   swap_type  -- 互换类型列表,预留字段
   ccy       -- 货币
   ir_index   -- 基准利率列表
"""


def get_ir_vanilla_swap_list(ccy: [] = None, ir_index: [] = None, swap_type: [] = None):
    param = {'ccy': ccy, 'swapType': swap_type, 'irIndex': ir_index}
    return rq.post_token("/capdata/get/ir/vanilla/swap/list", param)


"""
获取同业拆借列表
参数： 
   ccy  -- 货币 
"""


def get_ir_depo_list(ccy: [] = None):
    return rq.post_token("/capdata/get/ir/depo/list", ccy)


"""
获取交叉货币列表
参数： 
   ccy       -- 货币
   ir_index   -- 基准利率列表
"""


def get_xccy_swap_list(ccy: [] = None, ir_index: [] = None):
    param = {'ccy': ccy, 'irIndex': ir_index}
    return rq.post_token("/capdata/get/xccy/swap/list", param)
