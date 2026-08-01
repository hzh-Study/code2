# 拾味堂 · 餐厅堂食 + 外卖点餐系统

一套完整的三端项目：**微信小程序点餐端（uni-app）+ FastAPI 后端 + Vue3 管理后台**。
扫码点餐、堂食/打包、购物车、微信支付、订单流转、后台菜品与订单管理、数据看板全链路打通。

## 目录结构

```
.
├── backend/      FastAPI 后端（SQLAlchemy 2.0 / SQLite 默认，可切 MySQL）
├── uniapp/       uni-app Vue3 用户端（微信小程序 + H5）
├── admin-web/    Vue3 + Vite + Element Plus 管理后台
├── prototypes/   原型图
└── PRD_餐厅堂食外卖小程序.md
```

## 一键启动（三个终端）

### 1. 后端（端口 8000）

```bash
cd backend
pip install -r requirements.txt
python seed.py                                    # 建表 + 种子数据（仅首次）
python -m uvicorn app.main:app --reload --port 8000
```

- Swagger 文档：http://localhost:8000/docs
- 默认无需任何数据库/微信配置，开箱即跑（SQLite + 支付模拟）

### 2. 管理后台（端口 5173）

```bash
cd admin-web
npm install
npm run dev
```

访问 http://localhost:5173 ，账号 **admin / admin123**

### 3. 用户端

```bash
cd uniapp
npm install

npm run dev:h5           # 浏览器预览（手机尺寸），默认 5173 被占用时用 -- --port 5174
npm run dev:mp-weixin    # 微信小程序，产物在 dist/dev/mp-weixin，用微信开发者工具导入
```

> 小程序端需在 `uniapp/src/config.js` 中把 `BASE_URL` 改为你的后端地址
> （小程序不支持 vite 代理，必须填完整域名/IP）。

## 默认账号与数据

| 项目 | 值 |
| --- | --- |
| 管理后台 | `admin` / `admin123` |
| 小程序登录 | 开发模式免配置，`wx.login` 的 code 直接作为 openid 自动注册 |
| 种子数据 | 6 个分类、14 道菜品（含 AI 生成实拍风格配图） |

## 核心业务链路

```
选菜加购 → 购物车调整 → 确认订单(堂食/打包+地址) → 微信支付预下单
   → 支付回调 → 订单状态 待支付→待出餐 → 后台标记完成 → 已完成
```

订单状态机（`backend/app/services/order_state.py`）：

| 状态 | 含义 | 允许流转 |
| --- | --- | --- |
| 1 | 待支付 | → 2（支付成功）、→ 4（用户取消/超时） |
| 2 | 待出餐 | → 3（后台标记完成） |
| 3 | 已完成 | 终态 |
| 4 | 已取消 | 终态 |

待支付订单 15 分钟未支付自动过期取消。

## 生产切换

| 能力 | 开发模式（默认） | 生产配置 |
| --- | --- | --- |
| 数据库 | SQLite `restaurant.db` | `.env` 里 `DATABASE_URL` 指向 MySQL 8.0，执行 `backend/sql/init.sql` |
| 微信登录 | code 直接当 openid | 配置 `WX_APPID` / `WX_SECRET` |
| 微信支付 | 本地模拟，返回 `dev:true` | 配置 `WX_MCH_ID` / `WX_API_KEY`，回调走真实签名校验 |
| 图片存储 | 本地 `backend/uploads`，经 `/static` 暴露 | 可换 OSS/COS，改 `app/services/storage.py` |

只要在 `backend/.env` 填入微信参数，`DEV_MODE` 自动关闭，无需改动任何代码。

## 质量验证

- 后端：`cd backend && python smoke_test.py` —— 46 项接口断言全通过
- 管理后台：`npm run build` 构建通过，登录/看板/分类/菜品/订单流转已浏览器实测
- 用户端：`npm run build:h5`、`npm run build:mp-weixin` 均构建通过，H5 下单支付全流程已实测
