# 拾味堂 后端服务（FastAPI）

餐厅堂食 + 外卖小程序的统一后端，提供小程序端（client）与管理后台（admin）两套接口，
所有接口统一返回结构 `{ code, msg, data }`，`code != 0` 表示业务失败。

## 技术栈
- FastAPI + SQLAlchemy 2.0
- 鉴权：自定义 HMAC-SHA256 token（用户端 / 管理端分离角色）
- 存储：默认 SQLite（开箱即跑），可切换 MySQL 8.0
- 支付：微信支付预下单 / 异步回调（开发模式退化为本地模拟）

## 快速开始

```bash
cd backend
pip install -r requirements.txt

# 初始化数据库并写入种子数据（管理员 / 分类 / 菜品 / 图片）
python seed.py

# 启动（默认 8000 端口）
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

启动后访问：
- API 文档（Swagger）：http://localhost:8000/docs
- 健康检查：http://localhost:8000/health

## 默认账号
- 管理后台：`admin` / `admin123`
- 小程序端：微信 code 登录（开发模式自动用 dev code 注册，无需真实微信）

## 配置（.env）
复制 `.env.example` 为 `.env` 修改。关键项：
- `DATABASE_URL`：默认 `sqlite:///./restaurant.db`；MySQL 改为
  `mysql+pymysql://root:password@127.0.0.1:3306/restaurant_db`
- `WX_APPID` / `WX_SECRET` / `WX_MCH_ID` / `WX_API_KEY`：配置后自动切换为真实微信逻辑；
  留空则为开发模式（`DEV_MODE=true`），登录 code 直接当作 openid、支付走本地模拟。
- `SECRET_KEY`：生产务必修改。

## 接口一览
- 小程序端（`/api/v1/client`）：`auth/login`、`categories`、`dishes`、`dishes/hot`、
  `cart`、`cart/add`、`cart/update`、`cart/clear`、`orders`、`orders/{id}`、
  `orders/{id}/cancel`、`orders/{id}/repay`、`pay/prepay`、`pay/notify`
- 管理端（`/api/v1/admin`）：`auth/login`、`categories`(增删改)、`dishes`(增删改/上下架/上传)、
  `orders`、`orders/{id}/status`、`dashboard`、`upload`

> 关于支付回调：生产环境由微信服务器 POST XML 到 `/api/v1/client/pay/notify` 并校验签名；
> 开发模式可通过 `POST /api/v1/client/pay/notify` 传入 `{"order_no":"..."}` 模拟回调完成下单，
> 便于前后端本地联调。

## 接口自测
后端启动后执行全链路冒烟测试（覆盖登录鉴权、菜品分类 CRUD、购物车累加、
下单支付、状态流转、越权拦截等 46 项断言）：

```bash
python smoke_test.py
```

## MySQL 建库
见 `sql/init.sql`，在 MySQL 8.0 执行即可创建 `restaurant_db` 与全部表。
切换方式：在 `.env` 中把 `DATABASE_URL` 指向 MySQL，再执行一次 `python seed.py`。
模型主键在 MySQL 下为 `BIGINT AUTO_INCREMENT`，SQLite 下自动退化为 `INTEGER`，两端均可直接运行。
