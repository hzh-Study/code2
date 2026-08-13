"""配置读取：从 .env 加载，所有密钥/连接信息均走环境变量，不硬编码。"""
import logging
import os
from urllib.parse import urlparse
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_DIR = os.path.dirname(BASE_DIR)

logger = logging.getLogger(__name__)


def _env(name: str, default: str = "") -> str:
    return os.getenv(name, default)


def _parse_bool(name: str, value: str) -> bool:
    normalized = value.strip().lower()
    if normalized in {"1", "true", "yes", "on"}:
        return True
    if normalized in {"0", "false", "no", "off"}:
        return False
    raise RuntimeError(f"{name} must be true or false")


# 数据库：默认使用 SQLite 以便开箱即跑；生产可改为 MySQL 连接串
# MySQL 示例：mysql+pymysql://root:password@127.0.0.1:3306/restaurant_db
DATABASE_URL = _env("DATABASE_URL", f"sqlite:///{os.path.join(BASE_DIR, 'restaurant.db')}")

UPLOAD_DIR = _env("UPLOAD_DIR", os.path.join(BASE_DIR, "uploads"))
IMAGE_DIR = _env("IMAGE_DIR", os.path.join(PROJECT_DIR, "images"))
STATIC_URL_PREFIX = _env("STATIC_URL_PREFIX", "/static")
IMAGE_URL_PREFIX = _env("IMAGE_URL_PREFIX", "/images")

# 微信小程序
WX_APPID = _env("WX_APPID", "")
WX_SECRET = _env("WX_SECRET", "")
WX_MCH_ID = _env("WX_MCH_ID", "")
WX_API_KEY = _env("WX_API_KEY", "")
NOTIFY_URL = _env("NOTIFY_URL", "http://localhost:8000/api/v1/client/pay/notify")
PAYMENT_CLIENT_IP = _env("PAYMENT_CLIENT_IP", "")

# token 有效期
TOKEN_EXPIRE_HOURS = int(_env("TOKEN_EXPIRE_HOURS", "72"))
ADMIN_TOKEN_EXPIRE_HOURS = int(_env("ADMIN_TOKEN_EXPIRE_HOURS", "24"))

# 订单超时（分钟）
ORDER_EXPIRE_MINUTES = int(_env("ORDER_EXPIRE_MINUTES", "15"))
APP_TIMEZONE = _env("APP_TIMEZONE", "Asia/Shanghai")

# token 签名密钥
DEFAULT_SECRET_KEY = "change-me-please-use-strong-secret-in-prod"
SECRET_KEY = _env("SECRET_KEY", DEFAULT_SECRET_KEY)

# 未显式设置时，未配置微信凭证则自动启用开发模式（开箱即用）；
# 显式 DEV_MODE=false 时绝不静默退回模拟，必须提供完整微信凭证。
_dev_mode_value = _env("DEV_MODE", "")
DEV_MODE = _parse_bool("DEV_MODE", _dev_mode_value) if _dev_mode_value.strip() else not (WX_APPID and WX_SECRET)

if not DEV_MODE:
    missing_wechat_settings = [
        name
        for name, value in {
            "WX_APPID": WX_APPID,
            "WX_SECRET": WX_SECRET,
            "WX_MCH_ID": WX_MCH_ID,
            "WX_API_KEY": WX_API_KEY,
        }.items()
        if not value
    ]
    if missing_wechat_settings:
        raise RuntimeError(f"Production mode requires: {', '.join(missing_wechat_settings)}")
    if SECRET_KEY == DEFAULT_SECRET_KEY:
        raise RuntimeError("SECRET_KEY must be set in production (do not use the default value)")
    notify_url = urlparse(NOTIFY_URL)
    if notify_url.scheme != "https" or notify_url.hostname in {"localhost", "127.0.0.1", "::1"}:
        raise RuntimeError("Production NOTIFY_URL must be a public HTTPS URL")
    if not PAYMENT_CLIENT_IP:
        raise RuntimeError("Production PAYMENT_CLIENT_IP must be configured")

if DEV_MODE:
    logger.warning("DEV_MODE 已启用：未配置 WX_APPID/WX_SECRET，微信登录/支付退化为本地实现，请勿用于生产")

CORS_ORIGINS = [origin.strip() for origin in _env("CORS_ORIGINS", "*").split(",") if origin.strip()]
if not CORS_ORIGINS:
    raise RuntimeError("CORS_ORIGINS must contain at least one origin")

if SECRET_KEY == DEFAULT_SECRET_KEY:
    logger.warning("SECRET_KEY 使用了默认弱值，请在 .env 中设置强密钥；当前配置不安全")
