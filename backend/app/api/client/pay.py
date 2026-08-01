"""小程序端：微信支付预下单与异步回调。"""
import json
import logging
from decimal import Decimal

from fastapi import APIRouter, Depends, Request
from fastapi.responses import Response
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user_id
from app.models.order import Order
from app.models.user import User
from app.schemas.common import R
from app.services import wechat
from app.services.order_state import STATUS_PENDING, mark_cancelled, mark_paid
from app.utils.time import is_expired

logger = logging.getLogger(__name__)

router = APIRouter()

# 微信要求的 XML 成功响应
WX_SUCCESS = Response(
    content='<xml><return_code>SUCCESS</return_code><return_msg>OK</return_msg></xml>',
    media_type="application/xml",
)


class PrepayRequest(BaseModel):
    order_id: int


@router.post("/pay/prepay")
async def prepay(
    body: PrepayRequest,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """微信支付预下单，返回 uni.requestPayment 所需参数。"""
    order = db.query(Order).filter(Order.id == body.order_id, Order.user_id == user_id).first()
    if not order:
        return R.fail(2001, "订单不存在")
    if order.status != STATUS_PENDING:
        return R.fail(2002, "订单状态不可支付")
    if is_expired(order.expire_at):
        mark_cancelled(db, order)
        return R.fail(2002, "订单已超时取消")
    user = db.query(User).filter(User.id == order.user_id).first()
    openid = user.openid if user else ""
    pay_params = wechat.build_pay_params(order, openid)
    return R.ok(pay_params)


@router.post("/pay/notify")
async def pay_notify(request: Request, db: Session = Depends(get_db)):
    """微信支付异步回调。

    - 生产模式：解析 XML，校验微信签名，幂等更新订单为待出餐。
    - 开发模式（DEV_MODE）：接受 JSON {"order_no": ...} 用于本地联调模拟回调。

    注意：微信要求回调接口始终返回 XML 格式的 SUCCESS，否则会持续重试（最多 24 小时）。
    """
    content_type = request.headers.get("content-type", "")
    raw = await request.body()

    try:
        if wechat.DEV_MODE and "application/json" in content_type:
            data = json.loads(raw or b"{}")
            order_no = data.get("order_no")
        else:
            data = wechat.verify_notify(raw.decode("utf-8"))
            order_no = data.get("out_trade_no")
    except Exception as e:
        logger.exception("回调校验失败")
        return WX_SUCCESS  # 返回 SUCCESS 防止微信重试，通过日志排查

    if not order_no:
        logger.error("回调缺少订单号")
        return WX_SUCCESS

    order = db.query(Order).filter(Order.order_no == order_no).first()
    if not order:
        logger.error("回调订单不存在: %s", order_no)
        return WX_SUCCESS

    # 幂等：已处理过直接返回成功；开发模式需返回 JSON 以便测试解析
    if order.status != STATUS_PENDING:
        if wechat.DEV_MODE:
            return R.ok(msg="success")
        return WX_SUCCESS

    # 生产模式校验 result_code 和金额一致性
    if not wechat.DEV_MODE:
        if data.get("result_code") != "SUCCESS":
            logger.warning("支付失败回调: order_no=%s, result_code=%s", order_no, data.get("result_code"))
            return WX_SUCCESS  # 支付失败，返回 SUCCESS 防止重试

        total_fee = int(data.get("total_fee", 0))
        expected = int(Decimal(str(order.total_amount)) * 100)
        if total_fee != expected:
            logger.error("金额不一致: order_no=%s, expected=%d, actual=%d", order_no, expected, total_fee)
            return WX_SUCCESS  # 金额异常，返回 SUCCESS 防止重试，通过日志排查

    mark_paid(db, order)
    logger.info("支付成功: order_no=%s", order_no)

    if wechat.DEV_MODE:
        return R.ok(msg="success")
    return WX_SUCCESS
