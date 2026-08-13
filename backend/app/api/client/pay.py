"""小程序端：微信支付预下单与异步回调。"""
import json
import logging
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import Response
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user_id
from app.models.order import Order
from app.models.user import User
from app.schemas.common import R
from app.services import wechat
from app.services.order_state import STATUS_PENDING, expire_pending_orders, mark_paid
from app.utils.time import is_expired

logger = logging.getLogger(__name__)

router = APIRouter()

# 微信要求的 XML 成功响应
def _wx_success() -> Response:
    return Response(
        content='<xml><return_code>SUCCESS</return_code><return_msg>OK</return_msg></xml>',
        media_type="application/xml",
    )


def _wx_fail(message: str = "FAIL") -> Response:
    return Response(
        content=f"<xml><return_code>FAIL</return_code><return_msg>{message}</return_msg></xml>",
        media_type="application/xml",
    )


class PrepayRequest(BaseModel):
    order_id: int = Field(gt=0)


@router.post("/pay/prepay")
def prepay(
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
        expire_pending_orders(db, user_id)
        db.refresh(order)
        if order.status == STATUS_PENDING:
            raise HTTPException(status_code=502, detail="订单关闭失败，请稍后重试")
        return R.fail(2002, "订单已超时取消")
    user = db.query(User).filter(User.id == order.user_id).first()
    if user is None:
        raise HTTPException(status_code=400, detail="用户不存在")
    openid = user.openid
    try:
        pay_params = wechat.build_pay_params(order, openid)
    except Exception as exc:
        logger.exception("微信预下单失败: order_no=%s", order.order_no)
        raise HTTPException(status_code=502, detail="支付服务暂不可用，请稍后重试") from exc
    return R.ok(pay_params)


async def _get_raw_body(request: Request) -> bytes:
    """异步读取请求体，供同步路由使用。"""
    return await request.body()


@router.post("/pay/notify")
def pay_notify(
    request: Request,
    raw: bytes = Depends(_get_raw_body),
    db: Session = Depends(get_db),
):
    """微信支付异步回调。

    - 生产模式：解析 XML，校验微信签名，幂等更新订单为待出餐。
    - 开发模式（DEV_MODE）：接受 JSON {"order_no": ...} 用于本地联调模拟回调。

    注意：微信要求回调接口始终返回 XML 格式的 SUCCESS，否则会持续重试（最多 24 小时）。
    """
    content_type = request.headers.get("content-type", "")
    if len(raw) > 64 * 1024:
        logger.warning("支付回调请求体过大")
        return R.fail(2003, "回调数据无效") if wechat.DEV_MODE else _wx_fail("INVALID")

    try:
        if wechat.DEV_MODE and "application/json" in content_type:
            data = json.loads(raw or b"{}")
            order_no = data.get("order_no")
        else:
            data = wechat.verify_notify(raw.decode("utf-8"))
            order_no = data.get("out_trade_no")
    except Exception as e:
        logger.exception("回调校验失败")
        return R.fail(2003, "回调校验失败") if wechat.DEV_MODE else _wx_fail("INVALID")

    if not order_no:
        logger.error("回调缺少订单号")
        return R.fail(2003, "回调缺少订单号") if wechat.DEV_MODE else _wx_fail("INVALID")

    order = db.query(Order).filter(Order.order_no == order_no).first()
    if not order:
        logger.error("回调订单不存在: %s", order_no)
        return R.fail(2004, "订单不存在") if wechat.DEV_MODE else _wx_fail("ORDER NOT FOUND")

    # 幂等：已处理过直接返回成功；开发模式需返回 JSON 以便测试解析
    if order.status != STATUS_PENDING:
        if order.status == 4:
            logger.error("已取消订单收到支付成功通知: order_no=%s", order_no)
            if wechat.DEV_MODE:
                return R.fail(2005, "已取消订单不能确认支付")
            return _wx_fail("CANCELLED ORDER")
        if wechat.DEV_MODE:
            return R.ok(msg="success")
        return _wx_success()

    # 生产模式校验 result_code 和金额一致性
    if not wechat.DEV_MODE:
        if data.get("return_code") != "SUCCESS":
            logger.warning("支付通信失败回调: order_no=%s", order_no)
            return _wx_success()
        if data.get("result_code") != "SUCCESS":
            logger.warning("支付失败回调: order_no=%s, result_code=%s", order_no, data.get("result_code"))
            return _wx_success()  # 支付失败，返回 SUCCESS 防止重试

        try:
            total_fee = int(data.get("total_fee", 0))
        except (TypeError, ValueError):
            logger.error("支付回调金额格式无效: order_no=%s", order_no)
            return _wx_fail("INVALID AMOUNT")
        expected = int(Decimal(str(order.total_amount)) * 100)
        if total_fee != expected:
            logger.error("金额不一致: order_no=%s, expected=%d, actual=%d", order_no, expected, total_fee)
            return _wx_fail("AMOUNT MISMATCH")

    if mark_paid(db, order):
        logger.info("支付成功: order_no=%s", order_no)
    else:
        logger.warning("支付回调到达时订单已变更: order_no=%s, status=%s", order_no, order.status)

    if wechat.DEV_MODE:
        return R.ok(msg="success")
    return _wx_success()
