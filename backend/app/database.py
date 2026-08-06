"""SQLAlchemy engine / SessionLocal / Base 与建表入口。"""
from sqlalchemy import BigInteger, Integer, Numeric, create_engine, event, inspect
from sqlalchemy.orm import declarative_base, sessionmaker

from app.config import DATABASE_URL

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args, pool_pre_ping=True)


if engine.dialect.name == "sqlite":
    @event.listens_for(engine, "connect")
    def _enable_sqlite_foreign_keys(dbapi_connection, _connection_record):
        cursor = dbapi_connection.cursor()
        try:
            cursor.execute("PRAGMA foreign_keys=ON")
        finally:
            cursor.close()


if engine.dialect.name == "mysql":
    @event.listens_for(engine, "connect")
    def _set_mysql_utc(dbapi_connection, _connection_record):
        cursor = dbapi_connection.cursor()
        try:
            cursor.execute("SET time_zone = '+00:00'")
        finally:
            cursor.close()

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
    _ensure_schema_constraints()


def _ensure_schema_constraints() -> None:
    """为 create_all 无法更新的旧数据库补齐关键唯一约束。"""
    with engine.begin() as connection:
        unique_columns = {
            tuple(constraint.get("column_names") or [])
            for constraint in inspect(connection).get_unique_constraints("categories")
        }
        index_columns = {
            tuple(index.get("column_names") or [])
            for index in inspect(connection).get_indexes("categories")
            if index.get("unique")
        }
        if ("name",) in unique_columns | index_columns:
            return
        if connection.dialect.name == "sqlite":
            connection.exec_driver_sql(
                "CREATE UNIQUE INDEX uq_categories_name ON categories (name)"
            )
        elif connection.dialect.name == "mysql":
            connection.exec_driver_sql(
                "ALTER TABLE categories ADD CONSTRAINT uq_categories_name UNIQUE (name)"
            )
