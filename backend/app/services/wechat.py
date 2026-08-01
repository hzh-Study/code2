"""微信相关：code2session、支付预下单、回调验签。

生产模式（配置了 WX_APPID/WX_SECRET）走真实微信接口与 MD5 验签；
开发模式（DEV_MODE，未配置微信凭证）退化为本地可运行实现，便于联调验证。
"""
import hashlib
import hmac
import random
import string
import xml.etree.ElementTree as ET
from decimal import Decimal
from xml.sax.saxutils import escape

import httpx

from app.config import (
    DEV_MODE,
    NOTIFY_URL,
    WX_API_KEY,
    WX_APPID,
    WX_MCH_ID,
    WX_SECRET,
)


def code2session(code: str) -> str:
    """微信 code 换 openid。开发模式直接把 code 当作 openid。"""
    if DEV_MODE:
        return code
    url = "https://api.weixin.qq.com/sns/jscode2session"
    params = {
        "appid": WX_APPID,
        "secret": WX_SECRET,
        "js_code": code,
        "grant_type": "authorization_code",
    }
    resp = httpx.get(url, params=params, timeout=10)
    data = resp.json()
    if "openid" not in data:
        raise RuntimeError(data.get("errmsg", "code2session 失败"))
    return data["openid"]


def _nonce_str(length: int = 32) -> str:
    return "".join(random.choices(string.ascii_letters + string.digits, k=length))


def _sign(params: dict, key: str) -> str:
    """微信支付签名（MD5）。"""
    items = sorted([(k, v) for k, v in params.items() if v not in (None, "")])
    raw = "&".join(f"{k}={v}" for k, v in items) + f"&key={key}"
    return hashlib.md5(raw.encode("utf-8")).hexdigest().upper()


def build_pay_params(order, openid: str) -> dict:
    """生成微信支付 JSAPI 预下单参数。

    返回可直接用于 uni.requestPayment / wx.requestPayment 的参数字典。
    """
    if DEV_MODE:
        # 开发模式返回可识别的占位参数，前端据此走模拟支付流程
        return {
            "dev": True,
            "order_no": order.order_no,
            "timeStamp": "",
            "nonceStr": "",
            "package": "",
            "signType": "MD5",
            "paySign": "",
        }

    params = {
        "appid": WX_APPID,
        "mch_id": WX_MCH_ID,
        "nonce_str": _nonce_str(),
        "body": "拾味堂订单",
        "out_trade_no": order.order_no,
        "total_fee": int(Decimal(str(order.total_amount)) * 100),
        "spbill_create_ip": "127.0.0.1",
        "notify_url": NOTIFY_URL,
        "trade_type": "JSAPI",
        "openid": openid,
    }
    params["sign"] = _sign(params, WX_API_KEY)
    xml_body = "<xml>" + "".join(f"<{k}>{escape(str(v))}</{k}>" for k, v in params.items()) + "</xml>"
    resp = httpx.post(
        "https://api.mch.weixin.qq.com/pay/unifiedorder",
        content=xml_body.encode("utf-8"),
        timeout=10,
    )
    root = ET.fromstring(resp.text)
    prepay_id = root.findtext("prepay_id")
    if not prepay_id:
        raise RuntimeError("微信预下单失败")

    # 组装前端支付参数
    pay_sign_params = {
        "appId": WX_APPID,
        "timeStamp": str(int(__import__("time").time())),
        "nonceStr": _nonce_str(),
        "package": f"prepay_id={prepay_id}",
        "signType": "MD5",
    }
    pay_sign_params["paySign"] = _sign(pay_sign_params, WX_API_KEY)
    return pay_sign_params


def verify_notify(xml_text: str) -> dict:
    """校验微信支付回调签名，返回解析后的字典。

    开发模式（无 API KEY）信任本地构造的回调，便于联调。
    """
    root = ET.fromstring(xml_text)
    data = {child.tag: (child.text or "") for child in root}
    if DEV_MODE:
        return data
    sign = data.pop("sign", "")
    items = sorted([(k, v) for k, v in data.items() if v != ""])
    raw = "&".join(f"{k}={v}" for k, v in items) + f"&key={WX_API_KEY}"
    expected = hashlib.md5(raw.encode("utf-8")).hexdigest().upper()
    if not hmac.compare_digest(expected, sign):
        raise RuntimeError("微信回调签名校验失败")
    return data
