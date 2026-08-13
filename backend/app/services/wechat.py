"""微信登录和微信支付 v2 适配。"""
import hashlib
import hmac
import secrets
import time
import xml.etree.ElementTree as ET
from decimal import Decimal
from xml.sax.saxutils import escape

import httpx

from app.config import (
    DEV_MODE,
    NOTIFY_URL,
    PAYMENT_CLIENT_IP,
    WX_API_KEY,
    WX_APPID,
    WX_MCH_ID,
    WX_SECRET,
)
from app.utils.time import LOCAL_TIMEZONE

SIGN_TYPE = "HMAC-SHA256"


def code2session(code: str) -> str:
    """用小程序登录 code 换取 openid；开发模式直接使用 code。"""
    if DEV_MODE:
        return code

    try:
        response = httpx.get(
            "https://api.weixin.qq.com/sns/jscode2session",
            params={
                "appid": WX_APPID,
                "secret": WX_SECRET,
                "js_code": code,
                "grant_type": "authorization_code",
            },
            timeout=10,
        )
        response.raise_for_status()
    except httpx.HTTPError:
        # 不传播 HTTPStatusError，避免完整请求 URL（含 WX_SECRET）进入上层日志。
        raise RuntimeError("微信登录服务请求失败") from None
    data = response.json()
    openid = data.get("openid")
    if not openid:
        raise RuntimeError(data.get("errmsg") or "code2session 失败")
    return str(openid)


def _nonce_str() -> str:
    return secrets.token_hex(16)


def _sign(params: dict, key: str) -> str:
    """生成微信支付 v2 的 HMAC-SHA256 签名。"""
    values = sorted(
        (name, value)
        for name, value in params.items()
        if name != "sign" and value not in (None, "")
    )
    raw = "&".join(f"{name}={value}" for name, value in values) + f"&key={key}"
    return hmac.new(key.encode("utf-8"), raw.encode("utf-8"), hashlib.sha256).hexdigest().upper()


def _parse_xml(xml_text: str) -> dict[str, str]:
    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError as exc:
        raise RuntimeError("微信返回了无效 XML") from exc
    if root.tag != "xml":
        raise RuntimeError("微信 XML 根节点无效")
    return {child.tag: child.text or "" for child in root}


def _xml_body(params: dict) -> bytes:
    fields = "".join(f"<{name}>{escape(str(value))}</{name}>" for name, value in params.items())
    return f"<xml>{fields}</xml>".encode("utf-8")


def build_pay_params(order, openid: str) -> dict:
    """生成可传给 ``uni.requestPayment`` 的 JSAPI 支付参数。"""
    if DEV_MODE:
        return {
            "dev": True,
            "order_no": order.order_no,
            "timeStamp": "",
            "nonceStr": "",
            "package": "",
            "signType": SIGN_TYPE,
            "paySign": "",
        }

    params = {
        "appid": WX_APPID,
        "mch_id": WX_MCH_ID,
        "nonce_str": _nonce_str(),
        "body": "拾味堂订单",
        "out_trade_no": order.order_no,
        "total_fee": int(Decimal(str(order.total_amount)) * 100),
        "spbill_create_ip": PAYMENT_CLIENT_IP,
        "notify_url": NOTIFY_URL,
        "trade_type": "JSAPI",
        "openid": openid,
        "sign_type": SIGN_TYPE,
    }
    if getattr(order, "expire_at", None):
        # 数据库存储的是无时区的 UTC 时间，微信要求北京时间 (UTC+8)
        from datetime import timezone as _tz
        local_expire = order.expire_at.replace(tzinfo=_tz.utc).astimezone(LOCAL_TIMEZONE)
        params["time_expire"] = local_expire.strftime("%Y%m%d%H%M%S")
    params["sign"] = _sign(params, WX_API_KEY)

    response = httpx.post(
        "https://api.mch.weixin.qq.com/pay/unifiedorder",
        content=_xml_body(params),
        headers={"Content-Type": "application/xml; charset=utf-8"},
        timeout=10,
    )
    response.raise_for_status()
    result = _parse_xml(response.text)
    if result.get("return_code") != "SUCCESS":
        raise RuntimeError(result.get("return_msg") or "微信预下单通信失败")
    if result.get("result_code") != "SUCCESS":
        raise RuntimeError(result.get("err_code_des") or result.get("err_code") or "微信预下单失败")
    if result.get("sign") and not hmac.compare_digest(_sign(result, WX_API_KEY), result["sign"].upper()):
        raise RuntimeError("微信预下单响应签名校验失败")
    prepay_id = result.get("prepay_id")
    if not prepay_id:
        raise RuntimeError("微信预下单响应缺少 prepay_id")

    pay_params = {
        "appId": WX_APPID,
        "timeStamp": str(int(time.time())),
        "nonceStr": _nonce_str(),
        "package": f"prepay_id={prepay_id}",
        "signType": SIGN_TYPE,
    }
    pay_params["paySign"] = _sign(pay_params, WX_API_KEY)
    return pay_params


def close_order(order) -> str:
    """关闭尚未支付的微信订单；若微信已收款则返回 ``paid``。"""
    if DEV_MODE:
        return "closed"

    params = {
        "appid": WX_APPID,
        "mch_id": WX_MCH_ID,
        "out_trade_no": order.order_no,
        "nonce_str": _nonce_str(),
        "sign_type": SIGN_TYPE,
    }
    params["sign"] = _sign(params, WX_API_KEY)
    response = httpx.post(
        "https://api.mch.weixin.qq.com/pay/closeorder",
        content=_xml_body(params),
        headers={"Content-Type": "application/xml; charset=utf-8"},
        timeout=10,
    )
    response.raise_for_status()
    result = _parse_xml(response.text)
    if result.get("sign") and not hmac.compare_digest(_sign(result, WX_API_KEY), result["sign"].upper()):
        raise RuntimeError("微信关单响应签名校验失败")
    if result.get("return_code") != "SUCCESS":
        raise RuntimeError(result.get("return_msg") or "微信关单通信失败")
    if result.get("result_code") == "SUCCESS":
        return "closed"
    err_code = (result.get("err_code") or "").upper()
    if err_code == "ORDERPAID":
        return "paid"
    # 微信侧已无此单或已关闭，本地可安全取消
    if err_code in {"ORDERNOTEXIST", "ORDERCLOSED"}:
        return "closed"
    raise RuntimeError(result.get("err_code_des") or result.get("err_code") or "微信关单失败")


def verify_notify(xml_text: str) -> dict[str, str]:
    """解析支付通知，并在生产模式验证 HMAC-SHA256 签名。"""
    data = _parse_xml(xml_text)
    if DEV_MODE:
        return data

    received_sign = data.get("sign", "")
    if not received_sign:
        raise RuntimeError("微信回调缺少签名")
    if data.get("sign_type", SIGN_TYPE).upper() != SIGN_TYPE:
        raise RuntimeError("微信回调签名类型不受支持")
    expected_sign = _sign(data, WX_API_KEY)
    if not hmac.compare_digest(expected_sign, received_sign.upper()):
        raise RuntimeError("微信回调签名校验失败")
    if data.get("appid") != WX_APPID or data.get("mch_id") != WX_MCH_ID:
        raise RuntimeError("微信回调商户信息不匹配")
    return data
