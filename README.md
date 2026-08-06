# 拾味堂 · 餐厅堂食与打包点餐系统

一套完整的三端点餐项目：uni-app 用户端（微信小程序 + H5）、FastAPI 后端和 Vue 3 管理后台。支持首页推荐、分类点餐、购物车、堂食/打包带走、微信支付、订单流转、菜品管理与经营看板。

## 目录结构

```text
.
├── backend/      FastAPI 后端（SQLAlchemy 2.0，默认 SQLite，可切 MySQL）
├── uniapp/       uni-app Vue 3 用户端（微信小程序 + H5）
├── admin-web/    Vue 3 + Vite + Element Plus 管理后台
├── prototypes/   原型图
└── PRD_餐厅堂食外卖小程序.md
```

## 本地启动

### 1. 后端（8000）

```bash
cd backend
pip install -r requirements.txt
python seed.py
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

- Swagger：http://127.0.0.1:8000/docs
- 健康检查：http://127.0.0.1:8000/health
- 默认使用 SQLite 和开发支付模拟，无需微信凭证。

### 2. 管理后台（5173）

```bash
cd admin-web
npm install
npm run dev
```

访问 http://127.0.0.1:5173，默认账号为 `admin / admin123`。

### 3. 用户端（5174）

```bash
cd uniapp
npm install
npm run dev:h5 -- --host 127.0.0.1 --port 5174
```

访问 http://127.0.0.1:5174。微信小程序开发构建：

```bash
npm run dev:mp-weixin
```

将 `uniapp/dist/dev/mp-weixin` 导入微信开发者工具。

## 用户端 API 配置

- H5 开发环境默认使用同源 `/api/v1`，Vite 代理到 `http://localhost:8000`。
- 小程序模拟器开发默认使用 `http://127.0.0.1:8000/api/v1`。
- 真机和生产小程序必须通过 `VITE_API_BASE` 配置完整 HTTPS 合法域名；图片独立域名可通过 `VITE_IMG_BASE` 配置。

例如在 `uniapp/.env.local` 中配置：

```dotenv
VITE_API_BASE=https://api.your-domain.com/api/v1
VITE_IMG_BASE=https://api.your-domain.com
```

管理端生产环境默认请求同源 `/api`。前后端分域部署时，通过 `admin-web/.env.production` 的 `VITE_API_BASE` 指向后端 `/api` 前缀。

## 默认数据

| 项目 | 值 |
| --- | --- |
| 管理后台 | `admin / admin123` |
| 用户登录 | 开发模式自动注册；H5 每个浏览器使用独立开发 OpenID |
| 种子数据 | 6 个分类、14 道菜品、14 张版本化菜品图 |

`python seed.py` 会将 `backend/seed_assets/dishes` 中的图片复制到固定的 `/static/dishes/seed/` 路径。重复执行是幂等的。

## 核心业务链路

```text
浏览与分类点餐 → 购物车 → 选择堂食/打包带走 → 创建订单 → 微信预支付
  → 支付回调 → 待出餐 → 管理端标记完成 → 已完成
```

打包为到店带走，不要求填写地址。待支付订单默认 15 分钟后过期关闭。

| 状态 | 含义 | 允许流转 |
| --- | --- | --- |
| 1 | 待支付 | → 2（支付成功）、→ 4（取消/超时） |
| 2 | 待出餐 | → 3（管理端标记完成） |
| 3 | 已完成 | 终态 |
| 4 | 已取消 | 终态 |

## 生产配置

生产环境必须在 `backend/.env` 中显式设置 `DEV_MODE=false`，并配置：

- `WX_APPID`、`WX_SECRET`、`WX_MCH_ID`、`WX_API_KEY`
- 强随机 `SECRET_KEY`
- 公网可访问的 HTTPS `NOTIFY_URL`
- 有效的 `PAYMENT_CLIENT_IP`
- 按部署域名收敛 `CORS_ORIGINS`

数据库可继续使用 SQLite，生产部署通常建议改为 MySQL 8.0。示例和完整字段见 `backend/.env.example`。

## 质量验证

```bash
cd backend
python -m compileall -q app seed.py smoke_test.py test_regressions.py
python -m unittest -v test_regressions.py
python smoke_test.py
python -m pip check

cd ../admin-web
npm run build

cd ../uniapp
npm run build:h5
npm run build:mp-weixin
```

当前验证基线：后端独立回归测试 `9/9`、接口冒烟检查 `62/62`，管理端/H5/微信小程序构建通过。完整修复与浏览器验收范围见 `BUG_FIX_REPORT.md`。
