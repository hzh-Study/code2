"""SQLAlchemy engine / SessionLocal / Base 与建表入口。"""
from sqlalchemy import BigInteger, Integer, Numeric, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.config import DATABASE_URL

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args, pool_pre_ping=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# 主键类型：MySQL 用 BIGINT AUTO_INCREMENT；SQLite 仅 INTEGER PRIMARY KEY 才自增，
# 故在 sqlite 方言下回退为 Integer，保证两端均可自动自增。
BigIntPK = BigInteger().with_variant(Integer, "sqlite")

# 外键/普通大整数列：SQLite 同样用 Integer，保证与主键类型一致
BigIntCol = BigInteger().with_variant(Integer, "sqlite")

# 金额类型：DECIMAL(10,2)，跨方言通用
Money = Numeric(10, 2)


def get_db():
    """依赖注入：请求级数据库会话。"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """创建全部数据表（若尚不存在）。"""
    import app.models  # noqa: F401 确保模型注册到 Base
    Base.metadata.create_all(bind=engine)
