"""配置读取：从 .env 加载，所有密钥/连接信息均走环境变量，不硬编码。"""
import logging
import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

logger = logging.getLogger(__name__)


def _env(name: str, default: str = "") -> str:
    return os.getenv(name, default)


# 数据库：默认使用 SQLite 以便开箱即跑；生产可改为 MySQL 连接串
# MySQL 示例：mysql+pymysql://root:password@127.0.0.1:3306/restaurant_db
DATABASE_URL = _env("DATABASE_URL", f"sqlite:///{os.path.join(BASE_DIR, 'restaurant.db')}")

UPLOAD_DIR = _env("UPLOAD_DIR", os.path.join(BASE_DIR, "uploads"))
STATIC_URL_PREFIX = _env("STATIC_URL_PREFIX", "/static")

# 微信小程序
WX_APPID = _env("WX_APPID", "")
WX_SECRET = _env("WX_SECRET", "")
WX_MCH_ID = _env("WX_MCH_ID", "")
WX_API_KEY = _env("WX_API_KEY", "")
NOTIFY_URL = _env("NOTIFY_URL", "http://localhost:8000/api/v1/client/pay/notify")

# token 有效期
TOKEN_EXPIRE_HOURS = int(_env("TOKEN_EXPIRE_HOURS", "72"))
ADMIN_TOKEN_EXPIRE_HOURS = int(_env("ADMIN_TOKEN_EXPIRE_HOURS", "24"))

# 订单超时（分钟）
ORDER_EXPIRE_MINUTES = int(_env("ORDER_EXPIRE_MINUTES", "15"))

# token 签名密钥
SECRET_KEY = _env("SECRET_KEY", "change-me-please-use-strong-secret-in-prod")

# 调试/开发模式：无微信凭证时把 login code 当作 openid 直接返回
DEV_MODE = not (WX_APPID and WX_SECRET)

if DEV_MODE:
    logger.warning("DEV_MODE 已启用：未配置 WX_APPID/WX_SECRET，微信登录/支付退化为本地实现，请勿用于生产")

CORS_ORIGINS = _env("CORS_ORIGINS", "*").split(",")
