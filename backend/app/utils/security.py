"""自定义 token：HMAC-SHA256 签名，含角色/主体/过期时间，不依赖第三方库。"""
import base64
import hashlib
import hmac
import time

from app.config import SECRET_KEY

_ROLE_USER = "u"
_ROLE_ADMIN = "a"


def _b64e(raw: str) -> str:
    return base64.urlsafe_b64encode(raw.encode("utf-8")).decode("ascii").rstrip("=")


def _b64d(raw: str) -> str:
    raw += "=" * (-len(raw) % 4)
    return base64.urlsafe_b64decode(raw).decode("utf-8")


def generate_token(sub: int, hours: int, role: str = _ROLE_USER) -> str:
    """签发 token。role 区分用户端与管理端。"""
    exp = int(time.time()) + int(hours * 3600)
    payload = f"{role}:{sub}:{exp}"
    sig = hmac.new(SECRET_KEY.encode("utf-8"), payload.encode("utf-8"), hashlib.sha256).hexdigest()
    return f"{_b64e(payload)}.{sig}"


def verify_token(token: str, role: str) -> int | None:
    """校验 token，返回主体 id；无效/过期/角色不符返回 None。"""
    if not token or "." not in token:
        return None
    try:
        payload_b64, sig = token.rsplit(".", 1)
        payload = _b64d(payload_b64)
        expected = hmac.new(SECRET_KEY.encode("utf-8"), payload.encode("utf-8"), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(expected, sig):
            return None
        r, sub, exp = payload.split(":")
        if r != role:
            return None
        if int(exp) < int(time.time()):
            return None
        return int(sub)
    except Exception:
        return None


def hash_password(password: str) -> str:
    """管理员密码哈希（PBKDF2-SHA256，带盐值）。"""
    import os
    salt = os.urandom(16)
    dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 100000)
    return salt.hex() + ":" + dk.hex()


def verify_password(password: str, stored: str) -> bool:
    """校验密码，兼容旧的 SHA256 格式。"""
    if ":" in stored:
        salt_hex, dk_hex = stored.split(":", 1)
        salt = bytes.fromhex(salt_hex)
        dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 100000)
        # 使用恒定时间比较，防止时序攻击泄露密码信息
        return hmac.compare_digest(dk.hex(), dk_hex)
    # 兼容旧格式
    expected = hashlib.sha256(password.encode("utf-8")).hexdigest()
    return hmac.compare_digest(expected, stored)
