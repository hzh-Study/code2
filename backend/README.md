# 拾味堂后端服务（FastAPI）

餐厅堂食与打包点餐系统的统一后端，提供用户端（client）和管理端（admin）两组 API。普通 JSON 接口统一返回 `{ code, msg, data }`；生产环境的微信支付通知接口按微信协议返回 XML。

## 技术栈

- FastAPI + SQLAlchemy 2.0
- 默认 SQLite，可切换 MySQL 8.0
- 用户端与管理端分角色 HMAC-SHA256 token
- 微信登录、JSAPI 支付、支付通知验签和关单
- 本地上传目录经 `/static` 提供静态资源

## 快速开始

```bash
cd backend
pip install -r requirements.txt
python seed.py
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

- Swagger：http://127.0.0.1:8000/docs
- 健康检查：http://127.0.0.1:8000/health
- 默认管理员：`admin / admin123`

`seed.py` 会幂等创建管理员、6 个分类和 14 道菜品，并将 `seed_assets/dishes` 中的版本化图片复制到 `uploads/dishes/seed`。

## 配置

复制 `.env.example` 为 `.env` 后按环境修改。

| 配置 | 说明 |
| --- | --- |
| `DATABASE_URL` | 默认 `sqlite:///./restaurant.db`；可改 MySQL 连接串 |
| `APP_TIMEZONE` | 业务时区，默认 `Asia/Shanghai` |
| `ORDER_EXPIRE_MINUTES` | 待支付订单超时分钟数，默认 15 |
| `UPLOAD_DIR` | 上传文件目录 |
| `STATIC_URL_PREFIX` | 上传文件 URL 前缀，默认 `/static` |
| `CORS_ORIGINS` | 允许的前端来源，生产应收敛到实际域名 |

开发模式默认允许无微信凭证启动：登录 code 作为开发 OpenID，支付使用本地模拟。生产必须显式设置 `DEV_MODE=false`，并同时提供：

- `WX_APPID`、`WX_SECRET`、`WX_MCH_ID`、`WX_API_KEY`
- 非默认强随机 `SECRET_KEY`
- 公网 HTTPS `NOTIFY_URL`
- 有效 `PAYMENT_CLIENT_IP`

缺少任一生产必填项时服务会拒绝启动，不会静默退回模拟支付。

## 主要接口

- 用户端 `/api/v1/client`：登录、分类、菜品、热门菜、购物车、订单、取消、重新支付和支付通知。
- 管理端 `/api/v1/admin`：登录、分类、菜品、图片上传、订单流转和经营看板。

开发模式可向 `/api/v1/client/pay/notify` 发送 `{"order_no":"..."}` 模拟支付通知。生产模式只接受通过微信配置、商户号、金额和 HMAC-SHA256 签名校验的 XML 通知。

## 数据库

SQLite 连接会主动启用外键，并在初始化时补齐兼容旧数据库所需的唯一索引。MySQL 建库脚本位于 `sql/init.sql`。

```dotenv
DATABASE_URL=mysql+pymysql://root:password@127.0.0.1:3306/restaurant_db
```

订单时间在数据库中统一按 UTC 存储，接口展示、日期筛选和“今日”统计按 `APP_TIMEZONE` 转换。

## 验证

先启动后端的 8000 端口，再执行：

```bash
python -m compileall -q app seed.py smoke_test.py test_regressions.py
python -m unittest -v test_regressions.py
python smoke_test.py
python -m pip check
```

当前基线为独立回归测试 `9/9`、接口冒烟检查 `62/62`。回归范围包括生产配置、微信签名与通知验签、业务时区、登录限流、订单状态竞争和版本化种子图片。
