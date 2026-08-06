"""无需外部服务的关键回归测试。"""
import hashlib
import hmac
import os
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from contextlib import closing
from datetime import datetime
from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import Mock, patch

from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.api.admin import auth as admin_auth
from app.api.client import order as client_order
from app.database import Base
from app.models.order import Order
from app.models.user import User
from app.services import wechat
from app.services.order_state import mark_cancelled, mark_paid
from app.utils.time import format_utc, today_utc_range, utc_now
from seed import DISHES, SEED_IMAGE_DIR


class ConfigTests(unittest.TestCase):
    def test_explicit_production_mode_never_falls_back_to_dev(self):
        environment = os.environ.copy()
        environment.update({
            "DEV_MODE": "false",
            "SECRET_KEY": "test-only-strong-secret",
            "WX_APPID": "",
            "WX_SECRET": "",
            "WX_MCH_ID": "",
            "WX_API_KEY": "",
        })
        result = subprocess.run(
            [sys.executable, "-c", "import app.config"],
            cwd=os.path.dirname(__file__),
            env=environment,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Production mode requires", result.stderr)


class WechatTests(unittest.TestCase):
    def test_hmac_signature_matches_wechat_v2_algorithm(self):
        params = {"b": 2, "a": 1, "empty": "", "sign": "ignored"}
        raw = "a=1&b=2&key=secret"
        expected = hmac.new(b"secret", raw.encode(), hashlib.sha256).hexdigest().upper()
        self.assertEqual(wechat._sign(params, "secret"), expected)

    def test_production_pay_params_use_hmac_sha256(self):
        response = Mock()
        response.text = (
            "<xml><return_code>SUCCESS</return_code><result_code>SUCCESS</result_code>"
            "<prepay_id>prepay-123</prepay_id></xml>"
        )
        order = SimpleNamespace(order_no="SW-TEST", total_amount=Decimal("12.34"))
        with (
            patch.object(wechat, "DEV_MODE", False),
            patch.object(wechat, "WX_APPID", "app-id"),
            patch.object(wechat, "WX_MCH_ID", "merchant-id"),
            patch.object(wechat, "WX_API_KEY", "secret"),
            patch.object(wechat.httpx, "post", return_value=response) as post,
        ):
            params = wechat.build_pay_params(order, "openid")

        self.assertEqual(params["signType"], "HMAC-SHA256")
        self.assertTrue(params["paySign"])
        request_xml = post.call_args.kwargs["content"].decode("utf-8")
        self.assertIn("<sign_type>HMAC-SHA256</sign_type>", request_xml)
        self.assertIn("<total_fee>1234</total_fee>", request_xml)

    def test_notify_rejects_tampered_signature(self):
        data = {
            "appid": "app-id",
            "mch_id": "merchant-id",
            "out_trade_no": "SW-TEST",
            "result_code": "SUCCESS",
            "sign_type": "HMAC-SHA256",
            "total_fee": "1234",
        }
        with (
            patch.object(wechat, "DEV_MODE", False),
            patch.object(wechat, "WX_APPID", "app-id"),
            patch.object(wechat, "WX_MCH_ID", "merchant-id"),
            patch.object(wechat, "WX_API_KEY", "secret"),
        ):
            data["sign"] = wechat._sign(data, "secret")
            xml = "<xml>" + "".join(f"<{key}>{value}</{key}>" for key, value in data.items()) + "</xml>"
            self.assertEqual(wechat.verify_notify(xml)["out_trade_no"], "SW-TEST")
            tampered = xml.replace("<total_fee>1234</total_fee>", "<total_fee>1</total_fee>")
            with self.assertRaisesRegex(RuntimeError, "签名校验失败"):
                wechat.verify_notify(tampered)

    def test_close_order_treats_missing_or_closed_as_closed(self):
        order = SimpleNamespace(order_no="SW-MISSING")
        for err_code in ("ORDERNOTEXIST", "ORDERCLOSED"):
            response = Mock()
            response.text = (
                "<xml><return_code>SUCCESS</return_code><result_code>FAIL</result_code>"
                f"<err_code>{err_code}</err_code></xml>"
            )
            with (
                patch.object(wechat, "DEV_MODE", False),
                patch.object(wechat, "WX_APPID", "app-id"),
                patch.object(wechat, "WX_MCH_ID", "merchant-id"),
                patch.object(wechat, "WX_API_KEY", "secret"),
                patch.object(wechat.httpx, "post", return_value=response),
            ):
                self.assertEqual(wechat.close_order(order), "closed")


class TimeTests(unittest.TestCase):
    def test_utc_created_at_is_formatted_in_store_timezone(self):
        self.assertEqual(format_utc(datetime(2026, 8, 2, 15, 0, 0)), "2026-08-02 23:00:00")

    def test_utc_now_and_today_range_are_naive_utc(self):
        stamp = utc_now()
        self.assertIsNone(stamp.tzinfo)
        start, end = today_utc_range()
        self.assertIsNone(start.tzinfo)
        self.assertLess(start, end)
        # 应用层写入的 UTC 时间经 format_utc 转为门店时区
        self.assertEqual(format_utc(datetime(2026, 8, 2, 15, 0, 0)), "2026-08-02 23:00:00")


class RateLimitTests(unittest.TestCase):
    def tearDown(self):
        with admin_auth._login_failures_lock:
            admin_auth._login_failures.clear()

    def test_only_failures_trigger_limit_and_success_can_clear_them(self):
        ip = "test-client"
        for _ in range(admin_auth.RATE_LIMIT_MAX):
            admin_auth._record_login_failure(ip)
        with self.assertRaises(HTTPException) as raised:
            admin_auth._check_rate_limit(ip)
        self.assertEqual(raised.exception.status_code, 429)
        admin_auth._clear_login_failures(ip)
        admin_auth._check_rate_limit(ip)


class SeedAssetsTests(unittest.TestCase):
    def test_every_seed_dish_has_a_versioned_image(self):
        missing = [
            filename
            for _, _, _, _, filename in DISHES
            if not (SEED_IMAGE_DIR / filename).is_file()
        ]
        self.assertEqual(missing, [])

    def test_seed_restores_a_missing_local_image_path(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            database_path = os.path.join(temp_dir, "seed.db")
            upload_dir = os.path.join(temp_dir, "uploads")
            environment = os.environ.copy()
            environment.update({
                "DATABASE_URL": f"sqlite:///{database_path.replace(os.sep, '/')}",
                "UPLOAD_DIR": upload_dir,
                "STATIC_URL_PREFIX": "/static",
                "DEV_MODE": "true",
            })

            for attempt in range(2):
                result = subprocess.run(
                    [sys.executable, "seed.py"],
                    cwd=os.path.dirname(__file__),
                    env=environment,
                    capture_output=True,
                    text=True,
                    check=False,
                )
                self.assertEqual(result.returncode, 0, result.stderr)
                if attempt == 0:
                    with closing(sqlite3.connect(database_path)) as connection:
                        connection.execute(
                            "UPDATE dishes SET image = ? WHERE name = ?",
                            ("/static/dishes/2099/01/hongshao-rou.jpg", "秘制红烧肉"),
                        )
                        connection.commit()

            with closing(sqlite3.connect(database_path)) as connection:
                image = connection.execute(
                    "SELECT image FROM dishes WHERE name = ?",
                    ("秘制红烧肉",),
                ).fetchone()[0]
            self.assertEqual(image, "/static/dishes/seed/hongshao-rou.jpg")
            restored_image = os.path.join(upload_dir, "dishes", "seed", "hongshao-rou.jpg")
            self.assertTrue(os.path.isfile(restored_image))


class OrderStateTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        database_path = os.path.join(self.temp_dir.name, "state.db")
        self.engine = create_engine(f"sqlite:///{database_path}", connect_args={"check_same_thread": False})
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        session = self.Session()
        user = User(openid="state-test-user")
        session.add(user)
        session.flush()
        session.add_all([
            Order(order_no="STATE-CANCEL-FIRST", user_id=user.id, total_amount=1, dining_mode=1, status=1, pay_status=0),
            Order(order_no="STATE-PAY-FIRST", user_id=user.id, total_amount=1, dining_mode=1, status=1, pay_status=0),
            Order(order_no="STATE-CANCEL-PAID", user_id=user.id, total_amount=1, dining_mode=1, status=1, pay_status=0),
        ])
        session.commit()
        self.user_id = user.id
        session.close()

    def tearDown(self):
        self.engine.dispose()
        self.temp_dir.cleanup()

    def test_cancel_and_payment_updates_are_atomic(self):
        cancel_session = self.Session()
        pay_session = self.Session()
        cancel_order = cancel_session.query(Order).filter_by(order_no="STATE-CANCEL-FIRST").one()
        stale_for_pay = pay_session.query(Order).filter_by(order_no="STATE-CANCEL-FIRST").one()

        self.assertTrue(mark_cancelled(cancel_session, cancel_order))
        self.assertFalse(mark_paid(pay_session, stale_for_pay))
        self.assertEqual((stale_for_pay.status, stale_for_pay.pay_status), (4, 0))
        cancel_session.close()
        pay_session.close()

        pay_session = self.Session()
        cancel_session = self.Session()
        pay_order = pay_session.query(Order).filter_by(order_no="STATE-PAY-FIRST").one()
        stale_for_cancel = cancel_session.query(Order).filter_by(order_no="STATE-PAY-FIRST").one()

        self.assertTrue(mark_paid(pay_session, pay_order))
        self.assertFalse(mark_cancelled(cancel_session, stale_for_cancel))
        self.assertEqual((stale_for_cancel.status, stale_for_cancel.pay_status), (2, 1))
        pay_session.close()
        cancel_session.close()

    def test_cancel_when_wechat_reports_paid_syncs_order(self):
        session = self.Session()
        order = session.query(Order).filter_by(order_no="STATE-CANCEL-PAID").one()
        with (
            patch.object(wechat, "DEV_MODE", False),
            patch.object(wechat, "close_order", return_value="paid"),
        ):
            with self.assertRaises(HTTPException) as raised:
                client_order.cancel_order(order.id, self.user_id, session)
        self.assertEqual(raised.exception.status_code, 409)
        self.assertIn("已支付", raised.exception.detail)
        session.refresh(order)
        self.assertEqual((order.status, order.pay_status), (2, 1))
        self.assertIsNotNone(order.paid_at)
        session.close()


if __name__ == "__main__":
    unittest.main()
