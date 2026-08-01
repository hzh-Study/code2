# 餐厅堂食+外卖小程序系统 — 全栈开发任务 Prompt

> 本文档为交付给自主开发 Agent 的完整任务指令。请严格按照本文档执行，不增不减需求。
> PRD 原文：`PRD_餐厅堂食外卖小程序.md`
> 原型图参考：`prototypes/` 目录下 9 张图

---

## 0. 总体执行原则

1. **一口气完成全部三端**：uni-app + Vue3 用户端、FastAPI 后端、Vue3 管理后台。中途不暂停询问，遇到决策点按本文档默认方案执行。
2. **严格遵守技术栈约束**：不可替换框架/库，不可引入云存储，不可脑补需求外功能。
3. **先读 PRD 再开工**：开工前必须完整阅读 `PRD_餐厅堂食外卖小程序.md`，所有字段、状态码、业务规则以 PRD 为准。
4. **参考原型图**：UI 还原 `prototypes/` 目录下 9 张原型图的布局、配色、信息层级。配色与风格规范见第 11 节。
5. **可运行优先**：每个端必须能本地启动并通过基础功能验证，不要只交付代码片段。
6. **代码注释用中文**，变量/函数命名用英文。

---

## 1. 项目结构（强制目录布局）

在 `d:\axm\test2026730` 下创建以下三端独立目录：

```
d:\axm\test2026730\
├── PRD_餐厅堂食外卖小程序.md          # 已存在
├── AGENT_DEV_PROMPT.md                # 本文件
├── prototypes/                        # 已存在，9 张原型图
├── backend/                           # FastAPI 后端（你要创建）
├── uniapp/                            # uni-app + Vue3 用户端（小程序/H5，你要创建）
└── admin-web/                         # Vue3 管理后台（你要创建）
```

### 1.1 backend 目录
```
backend/
├── app/
│   ├── main.py                        # FastAPI 入口，挂载路由、CORS、静态文件
│   ├── config.py                      # 配置读取（env / .env）
│   ├── database.py                    # SQLAlchemy engine + SessionLocal
│   ├── deps.py                        # 依赖注入（get_db / 用户鉴权 / 管理员鉴权）
│   ├── models/                        # SQLAlchemy 模型
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── category.py
│   │   ├── dish.py
│   │   ├── cart.py
│   │   ├── order.py
│   │   └── order_item.py
│   ├── schemas/                       # Pydantic 模型（请求/响应）
│   │   ├── __init__.py
│   │   ├── common.py                  # 统一响应 R<T>
│   │   ├── user.py
│   │   ├── category.py
│   │   ├── dish.py
│   │   ├── cart.py
│   │   └── order.py
│   ├── api/
│   │   ├── __init__.py
│   │   ├── client/                    # 小程序端路由
│   │   │   ├── __init__.py
│   │   │   ├── auth.py
│   │   │   ├── category.py
│   │   │   ├── dish.py
│   │   │   ├── cart.py
│   │   │   ├── order.py
│   │   │   └── pay.py
│   │   └── admin/                     # 管理后台路由
│   │       ├── __init__.py
│   │       ├── auth.py
│   │       ├── category.py
│   │       ├── dish.py
│   │       ├── order.py
│   │       ├── upload.py
│   │       └── dashboard.py
│   ├── services/                      # 业务层
│   │   ├── __init__.py
│   │   ├── wechat.py                  # 微信 code2session + 支付预下单 + 回调验签
│   │   ├── order_state.py             # 订单状态机
│   │   └── storage.py                 # 本地图片存储
│   └── utils/
│       ├── __init__.py
│       ├── security.py                # token 生成/校验
│       └── time.py                    # 超时关闭等时间工具
├── uploads/                           # 本地图片存储目录（按日期子目录）
├── alembic/                           # 可选迁移
├── alembic.ini
├── requirements.txt
├── .env.example
└── README.md
```

### 1.2 uniapp 目录
```
uniapp/
├── pages.json                         # 页面路由 + tabBar 配置
├── manifest.json                      # 应用配置（小程序 AppID 等）
├── App.vue
├── main.js
├── uni.scss                           # 全局样式变量
├── pages/
│   ├── home/index.vue                 # 首页
│   ├── ordering/index.vue             # 菜品分类与列表页
│   ├── cart/index.vue                 # 购物车
│   ├── order-confirm/index.vue        # 下单确认
│   ├── my-orders/index.vue            # 我的订单
│   ├── order-detail/index.vue         # 订单详情
│   └── profile/index.vue              # 个人中心
├── components/
│   ├── dish-card.vue
│   ├── quantity-stepper.vue
│   └── empty-state.vue
├── api/
│   ├── request.js                     # 封装 uni.request，带 token 拦截器
│   ├── auth.js                        # 登录态管理
│   ├── format.js                      # 价格/时间格式化
│   └── config.js                      # API base url
├── store/                             # Pinia（如需要全局状态）
│   └── index.js
├── static/                            # 本地图标资源
└── uni_modules/                       # uni-app 内置组件
```

> 使用 HBuilderX 或 `vue-cli` + `@dcloudio/uni-preset-vue`（Vue3 版）创建项目。
> `pages.json` 中配置 tabBar：首页 / 订单 / 我的（三个 tab），iconPath 用 `static/` 下图标。

### 1.3 admin-web 目录
```
admin-web/
├── package.json
├── vite.config.js
├── index.html
├── .env.development
├── .env.production
└── src/
    ├── main.js
    ├── App.vue
    ├── router/
    │   └── index.js
    ├── stores/                        # Pinia
    │   ├── auth.js
    │   └── dish.js
    ├── api/
    │   ├── request.js                 # axios 封装，带 token 拦截器
    │   ├── auth.js
    │   ├── category.js
    │   ├── dish.js
    │   ├── order.js
    │   ├── upload.js
    │   └── dashboard.js
    ├── layouts/
    │   └── DefaultLayout.vue          # 左侧栏 + 主内容区
    ├── views/
    │   ├── Login.vue
    │   ├── Dashboard.vue
    │   ├── category/Manage.vue
    │   ├── dish/Manage.vue
    │   └── order/Manage.vue
    ├── components/
    │   ├── DishFormDialog.vue
    │   ├── CategoryFormDialog.vue
    │   └── OrderDetailDialog.vue
    └── styles/
        └── variables.scss
```

---

## 2. 技术栈（强制约束，严格遵守）

| 层级 | 选型 | 约束 |
|------|------|------|
| 用户端 | uni-app + Vue3（Composition API）+ Pinia | 编译到微信小程序为主，兼容 H5 |
| 后端 | Python 3.10+ / FastAPI / SQLAlchemy 2.0 | 异步 |
| 数据库 | MySQL 8.0（utf8mb4 / InnoDB） | 金额用 DECIMAL(10,2) |
| 管理后台 | Vue3 + Vite + Pinia + Vue Router + Element Plus | |
| HTTP | axios（后台）/ uni.request（uni-app 端） | |
| 图片存储 | FastAPI 本地 `uploads/` 目录 | 禁用 OSS/COS/七牛/任何云存储 |
| 支付 | 微信小程序 JSAPI 支付 | 商户号 + AppID |
| 鉴权 | 自定义 token（uni-app 端）+ JWT 或自定义 token（后台） | 二选一，PRD 约定自定义 token |

### 后端依赖（requirements.txt 至少包含）
```
fastapi
uvicorn[standard]
sqlalchemy>=2.0
pymysql
cryptography
python-dotenv
pydantic
python-multipart
httpx
```

微信支付签名可自行实现（HMAC-SHA256 / MD5），不强制引第三方 SDK。

---

## 3. 数据库设计（完整建表 SQL）

执行以下 SQL 初始化数据库 `restaurant_db`：

```sql
CREATE DATABASE IF NOT EXISTS restaurant_db
  DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE restaurant_db;

-- 用户表
CREATE TABLE users (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  openid VARCHAR(64) NOT NULL UNIQUE,
  nickname VARCHAR(64) NULL,
  avatar VARCHAR(255) NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NULL ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- 分类表
CREATE TABLE categories (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  name VARCHAR(64) NOT NULL,
  sort_order INT NOT NULL DEFAULT 0,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- 菜品表
CREATE TABLE dishes (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  name VARCHAR(128) NOT NULL,
  price DECIMAL(10,2) NOT NULL,
  description VARCHAR(512) NULL,
  image VARCHAR(255) NULL,
  category_id BIGINT NOT NULL,
  status TINYINT NOT NULL DEFAULT 1 COMMENT '1=在售,0=下架',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NULL ON UPDATE CURRENT_TIMESTAMP,
  CONSTRAINT fk_dish_category FOREIGN KEY (category_id) REFERENCES categories(id)
) ENGINE=InnoDB;
CREATE INDEX idx_dishes_cat_status ON dishes(category_id, status);

-- 购物车表
CREATE TABLE cart (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  user_id BIGINT NOT NULL,
  dish_id BIGINT NOT NULL,
  quantity INT NOT NULL DEFAULT 1,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NULL ON UPDATE CURRENT_TIMESTAMP,
  CONSTRAINT fk_cart_user FOREIGN KEY (user_id) REFERENCES users(id),
  CONSTRAINT fk_cart_dish FOREIGN KEY (dish_id) REFERENCES dishes(id),
  UNIQUE KEY uk_user_dish (user_id, dish_id)
) ENGINE=InnoDB;

-- 订单表
CREATE TABLE orders (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  order_no VARCHAR(64) NOT NULL UNIQUE,
  user_id BIGINT NOT NULL,
  total_amount DECIMAL(10,2) NOT NULL,
  dining_mode TINYINT NOT NULL COMMENT '1=堂食,2=打包',
  status TINYINT NOT NULL DEFAULT 1 COMMENT '1=待支付,2=待出餐,3=已完成,4=已取消',
  pay_status TINYINT NOT NULL DEFAULT 0 COMMENT '0=未付,1=已付',
  address VARCHAR(255) NULL,
  expire_at DATETIME NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  paid_at DATETIME NULL,
  updated_at DATETIME NULL ON UPDATE CURRENT_TIMESTAMP,
  CONSTRAINT fk_order_user FOREIGN KEY (user_id) REFERENCES users(id)
) ENGINE=InnoDB;
CREATE INDEX idx_orders_user_status ON orders(user_id, status);

-- 订单详情表
CREATE TABLE order_items (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  order_id BIGINT NOT NULL,
  dish_id BIGINT NOT NULL,
  dish_name VARCHAR(128) NOT NULL,
  price DECIMAL(10,2) NOT NULL,
  quantity INT NOT NULL,
  subtotal DECIMAL(10,2) NOT NULL,
  CONSTRAINT fk_item_order FOREIGN KEY (order_id) REFERENCES orders(id)
) ENGINE=InnoDB;
CREATE INDEX idx_order_items_order ON order_items(order_id);

-- 管理员表（PRD 未列出，但后台登录必需，按最小实现补充）
CREATE TABLE admins (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  username VARCHAR(64) NOT NULL UNIQUE,
  password_hash VARCHAR(255) NOT NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;
-- 默认账号 admin / admin123（密码用 sha256 或 bcrypt，二选一）
```

> 初始化时插入 1 条管理员记录、6 条示例分类、若干示例菜品，便于联调。

---

## 4. 后端实现要求

### 4.1 统一响应结构
所有接口必须返回：
```json
{ "code": 0, "msg": "success", "data": {} }
```
`code != 0` 表示业务失败。封装 `R.ok(data)` / `R.fail(code, msg)` 工具函数。

### 4.2 配置项（.env.example）
```
DB_HOST=127.0.0.1
DB_PORT=3306
DB_USER=root
DB_PASSWORD=
DB_NAME=restaurant_db
UPLOAD_DIR=uploads
STATIC_URL_PREFIX=/static
WX_APPID=
WX_SECRET=
WX_MCH_ID=
WX_API_KEY=
NOTIFY_URL=https://your.domain/api/v1/client/pay/notify
TOKEN_EXPIRE_HOURS=72
ADMIN_TOKEN_EXPIRE_HOURS=24
ORDER_EXPIRE_MINUTES=15
```

### 4.3 接口清单（全部实现，路径不可变）

基础前缀：`/api/v1`。小程序端 `/api/v1/client`，后台 `/api/v1/admin`。
鉴权：`Authorization: Bearer <token>`（登录与支付回调豁免）。

#### 小程序端
| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /api/v1/client/auth/login | 微信 code 换 OpenID，自动注册/登录，返回 token+用户信息 |
| GET | /api/v1/client/categories | 全部分类（按 sort_order） |
| GET | /api/v1/client/dishes/hot | 热门/在售菜品（首页用，取若干条） |
| GET | /api/v1/client/dishes | 按分类获取在售菜品（query: category_id） |
| GET | /api/v1/client/dishes/{id} | 菜品详情 |
| GET | /api/v1/client/cart | 当前用户购物车 |
| POST | /api/v1/client/cart/add | body: { dish_id, quantity } |
| POST | /api/v1/client/cart/update | body: { dish_id, quantity }（quantity=0 移除） |
| POST | /api/v1/client/cart/clear | 清空购物车 |
| GET | /api/v1/client/orders | query: status（可选） |
| GET | /api/v1/client/orders/{id} | 订单详情（含 items） |
| POST | /api/v1/client/orders | body: { dining_mode: 1\|2 }，返回 order_id + 支付参数 |
| POST | /api/v1/client/orders/{id}/cancel | 仅待支付本人订单 |
| POST | /api/v1/client/orders/{id}/repay | 重新支付预下单 |
| POST | /api/v1/client/pay/prepay | 微信支付预下单 |
| POST | /api/v1/client/pay/notify | 微信异步回调，校验签名，幂等更新订单状态为待出餐 |

#### 管理后台
| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /api/v1/admin/auth/login | 账号密码登录，返回 token |
| GET/POST | /api/v1/admin/categories | 列表 / 新增 |
| PUT/DELETE | /api/v1/admin/categories/{id} | 编辑 / 删除（有菜品时禁止并返回提示） |
| GET/POST | /api/v1/admin/dishes | 列表（含下架）/ 新增 |
| PUT/DELETE | /api/v1/admin/dishes/{id} | 编辑 / 删除 |
| POST | /api/v1/admin/dishes/{id}/toggle | 上下架切换 |
| POST | /api/v1/admin/upload | 图片上传，保存到 uploads/，返回访问路径 |
| GET | /api/v1/admin/orders | 列表（status、时间范围筛选、分页） |
| GET | /api/v1/admin/orders/{id} | 详情 |
| POST | /api/v1/admin/orders/{id}/status | 修改状态（待出餐→已完成） |
| GET | /api/v1/admin/dashboard | 今日订单数、今日销售额、在售菜品数 |

#### 静态资源
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /static/{path} | 访问 uploads 下的图片 |

用 `app.mount("/static", StaticFiles(directory="uploads"))` 挂载。

### 4.4 关键业务实现要点

1. **微信登录**：`wx.login` 拿 code → 后端用 `code2session` 换 openid/session_key → 查/建用户 → 签发 token。昵称头像由小程序端用新版头像昵称组件获取后调用接口更新（或登录时一并提交）。
2. **购物车**：以 `(user_id, dish_id)` 唯一；加购前校验菜品在售；quantity=0 删除。
3. **下单**：
   - 从购物车快照生成 order_items（dish_name、price 落快照）。
   - 计算 total_amount。
   - 必传 dining_mode（1 堂食 / 2 打包），堂食不写 address。
   - 设置 expire_at = now + ORDER_EXPIRE_MINUTES。
   - 清空已下单的购物车项。
   - 返回 order_id 与微信支付预下单参数。
4. **支付回调**：
   - 校验微信签名。
   - 幂等：已处理过的订单直接返回 success。
   - 校验金额一致后更新 status=2(待出餐)、pay_status=1、paid_at=now。
5. **超时关闭**：可在访问订单/列表时懒校验 expire_at，或用 APScheduler 定时任务，超时未支付置 status=4。
6. **权限**：客户端 token 中间件解析 user_id；后台 token 中间件解析 admin。两套独立。
7. **图片上传**：限制 jpg/png，单文件 < 2MB；按 `uploads/dishes/YYYY/MM/uuid.ext` 存储；返回 `/static/dishes/YYYY/MM/uuid.ext`。
8. **分页**：列表接口默认 page=1, page_size=20，返回 `{ list, total, page, page_size }`。

### 4.5 启动
`uvicorn app.main:app --reload --port 8000`
Swagger 文档：`http://localhost:8000/docs`。

---

## 5. uni-app 用户端实现（8 大模块）

### 5.1 全局约定
- `pages.json` 配置 tabBar：首页 / 订单 / 我的（三个 tab），使用 `static/` 下图标。
- `api/request.js` 封装 `uni.request`，自动注入 `Authorization: Bearer <token>`，401 时触发重新登录。
- `api/auth.js` 管理 token 缓存（`uni.setStorageSync`）与 `uni.login` 流程。
- 页面统一用 `<view>`/`<text>`/`<image>`/`<scroll-view>` 等 uni-app 内置组件，不写平台专属 API。
- 全局配色与原型图一致（见第 10 节），在 `uni.scss` 定义变量。
- 支付统一用 `uni.requestPayment`。

### 5.2 微信登录（6.1）
- `App.vue` 的 `onLaunch` 中自动 `uni.login` → 调 `/client/auth/login` → 缓存 token。
- 首次需要头像昵称时，使用微信新版「头像昵称填写组件」（`<button open-type="chooseAvatar">` + `<input type="nickname">`）获取后调用更新接口。
- 登录失败 `uni.showToast` 提示并允许重试。

### 5.3 首页（6.2）→ 参考原型图 `01_home.jpg`
- 顶部：店铺名称「拾味堂」大标题 + 副标题「本味家常 · 堂食打包」。
- 中部：横向滚动的分类圆形图标（6 个：招牌硬菜、家常小炒、时蔬、主食、汤羹、凉菜），点击跳转点餐页并定位分类。
- 下部：热门菜品横向卡片（3 个），含真实图片、名称、价格、橙色「+」加购按钮。
- 底部 tabBar 高亮「首页」。

### 5.4 点餐页（6.3）→ 参考原型图 `02_ordering.jpg`
- 左侧竖向分类栏（约 25% 宽），选中态橙色左边框 + 白底加粗。
- 右侧菜品列表（75% 宽），每个菜品：左侧方形图片、右侧名称+一行简介+价格+数量步进器（− 数量 +，+ 按钮橙色圆形）。
- 顶部搜索框占位「搜索菜品」+ 购物车图标（带红色角标数量）。
- 点击 + 调加购接口；下架菜品不展示。
- 购物车角标实时更新。

### 5.5 购物车（6.4）→ 参考原型图 `03_cart.jpg`
- 顶部标题「购物车」+ 右侧「清空」文字按钮。
- 菜品列表：图片、名称、单价、数量步进器、小计。薄分割线分隔。
- 进入页面时若菜品已下架，提示并移除。
- 底部固定结算栏：左侧「合计 ¥158.00」（橙色），右侧橙色大按钮「去结算」。
- 清空需二次确认弹窗。

### 5.6 下单确认（6.5）→ 参考原型图 `04_order_confirm.jpg`
- 顶部标题「确认订单」。
- 「订单商品」清单：名称、数量、小计。
- 「用餐方式」两个并排可选卡片：堂食（盘子图标）/ 打包带走（袋子图标），单选，选中态橙色边框+浅橙底+橙色对勾。
- 订单汇总：商品小计、合计（橙色大字）。
- 底部固定「提交订单」橙色按钮。
- 提交前校验用餐模式，未选 Toast「请选择堂食或打包」。

### 5.7 微信支付（6.6）
- 下单成功拿到支付参数 → `uni.requestPayment` 唤起收银台。
- 成功：跳转「我的订单」并 `uni.showToast` 提示支付成功。
- 失败/取消：保留待支付订单，可重新支付。

### 5.8 我的订单（6.7）→ 参考原型图 `05_my_orders.jpg`
- 顶部 4 个 Tab：待支付、待出餐、已完成、已取消。
- 每条订单：订单号 + 状态标签（橙色 pill）+ 缩略菜品图 3 张 + 菜品名摘要 + 用餐方式标签（堂食/打包）+ 总价。
- 点击进入订单详情页。
- 详情页：菜品清单、下单时间、用餐方式、状态、总价。
- 待支付订单提供「重新支付」「取消订单」按钮。

### 5.9 个人中心（6.8）→ 参考原型图 `06_profile.jpg`
- 顶部头像区（圆形头像 + 昵称 + 微信用户副标题），背景为暖色调实色（非渐变）。
- 「全部订单」入口行。
- 4 个状态快捷入口：待支付、待出餐、已完成、已取消（带线性图标）。
- 菜单列表：店铺信息、联系商家、关于我们。
- 底部 tabBar 高亮「我的」。

---

## 6. Vue3 管理后台实现（5 大模块）

### 6.1 全局约定
- `DefaultLayout.vue`：左侧深色 `#2B2B2B` 侧栏 + 右侧主内容区。
- 侧栏菜单：数据看板、分类管理、菜品管理、订单管理。顶部 logo「拾味堂后台」。
- 路由守卫：未登录跳转 `/login`。
- axios 拦截器自动注入 token，401 跳登录。
- 配色与原型图一致（见第 11 节）。

### 6.2 登录页（7.1）
- 账号、密码输入框 + 登录按钮。
- 成功存 token 跳看板；失败 Element Plus message 提示。

### 6.3 数据看板（7.5）→ 参考原型图 `07_admin_dashboard.jpg`
- 页面标题「数据看板」+ 今日日期。
- 三个 KPI 大字横向排列（非卡片，薄分割线分隔）：今日订单数、今日销售额、在售菜品数。每个带小说明文字。
- 「近期订单」数据表格：订单号、用户、金额、用餐方式、状态、时间。状态用彩色 pill（待出餐橙、已完成绿、待支付灰）。

### 6.4 分类管理（7.2）
- 表格：名称、排序值、操作（编辑、删除）。
- 新增/编辑用 `CategoryFormDialog.vue` 弹窗。
- 删除二次确认；有菜品时后端返回提示，前端 message 显示。

### 6.5 菜品管理（7.3）→ 参考原型图 `08_admin_dishes.jpg`
- 顶部：标题「菜品管理」+ 橙色「新增菜品」按钮 + 搜索框 + 分类筛选下拉。
- 表格列：图片缩略图、名称、价格、分类、状态、操作（编辑、上架/下架、删除）。
- 状态 pill：在售绿、下架灰。
- `DishFormDialog.vue`：图片上传（调 `/admin/upload`）+ 名称 + 价格 + 简介 + 分类下拉。
- 上下架调 `/dishes/{id}/toggle`。
- 删除二次确认。

### 6.6 订单管理（7.4）→ 参考原型图 `09_admin_orders.jpg`
- 顶部：标题「订单管理」+ 状态 Tab（全部、待支付、待出餐、已完成、已取消）+ 日期范围选择器。
- 表格列：订单号、用户、菜品明细、用餐方式、金额、状态、下单时间、操作。
- 用餐方式标签：堂食（盘图标）、打包（袋图标）。
- 状态 pill 彩色。
- 操作：详情（弹窗 `OrderDetailDialog.vue`）、标记完成（仅待出餐行）。
- 底部分页「共 N 条」+ 页码。

---

## 7. 业务规则（必须全部落地）

1. 下架菜品（status=0）小程序端不可见、不可加购；后台可见可管理。
2. 每个订单 dining_mode 必为 1 或 2；堂食不存 address；后台列表与详情标注用餐方式。
3. 未支付订单超时（expire_at，默认 15 分钟）自动关闭为已取消。
4. 图片一律本地存储，数据库只存访问路径。
5. 权限隔离：仅管理员可操作商品与订单状态；用户仅可管理本人订单。
6. 订单状态机：
   - 待支付(1) →（支付成功）→ 待出餐(2)
   - 待支付(1) →（用户取消/超时）→ 已取消(4)
   - 待出餐(2) →（商家操作）→ 已完成(3)
   - 已完成(3)、已取消(4) 为终态。
7. 微信支付回调幂等。
8. 结算下单时若菜品已下架，提示并阻止。

---

## 8. 非功能要求

- 小程序首页/分类页接口 P95 < 500ms。
- 列表分页默认 20 条。
- 图片上传限制 jpg/png，单图 < 2MB。
- token 有效期管理：小程序 72h，后台 24h。
- 微信支付回调必须验签。
- 配置走 .env，不硬编码。

---

## 9. 原型图参考说明

`prototypes/` 目录下 9 张图，UI 必须**高度还原**其布局、配色、信息层级、组件样式：

| 文件 | 还原目标 |
|------|----------|
| 01_home.jpg | uni-app 首页 |
| 02_ordering.jpg | uni-app 点餐页 |
| 03_cart.jpg | uni-app 购物车 |
| 04_order_confirm.jpg | uni-app 下单确认页 |
| 05_my_orders.jpg | uni-app 我的订单 |
| 06_profile.jpg | uni-app 个人中心 |
| 07_admin_dashboard.jpg | 后台数据看板 |
| 08_admin_dishes.jpg | 后台菜品管理 |
| 09_admin_orders.jpg | 后台订单管理 |

开发每个页面/视图前，先用 Read 工具查看对应原型图，确认布局后再编码。原型图中的示例数据（店名「拾味堂」、菜品名、价格、订单号格式）应作为初始 seed 数据。

---

## 10. 视觉规范（严格遵守，避免 AI 味）

应用 `frontend-skill` 克制美学原则：

- **主色**：暖橙红 `#E85D2C`（单一强调色，用于主按钮、选中态、价格、状态 pill）
- **背景**：暖米白 `#FAF7F2`
- **文字**：深炭灰 `#2B2B2B`（主）/ `#888`（次）
- **侧栏**（后台）：深炭灰 `#2B2B2B` 底 + 白字
- **禁用**：紫蓝渐变、玻璃拟态、3D 塑料感、dashboard 卡片马赛克、装饰性阴影、AI 通用插画
- **布局**：cardless 优先，用分割线/留白/列布局代替卡片堆叠；后台 KPI 用大字排版而非卡片
- **字体**：最多两个字族；中文用系统默认或思源黑体
- **图标**：线性极简图标，不使用彩色拟物图标
- **图片**：菜品图用真实食物摄影感（暖光、陶瓷餐具），可用 `https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt={prompt}&image_size={image_size}` 生成占位菜品图（prompt 写真实中式菜品摄影）

---

## 11. 执行步骤建议

1. 创建三端目录结构。
2. 后端：建库建表 → 模型 → schemas → 路由 → 业务层 → 静态文件挂载 → 启动验证 Swagger。
3. 插入 seed 数据（1 管理员、6 分类、若干菜品）。
4. 管理后台：脚手架 → 登录 → 布局 → 5 个模块页面 → 联调后端。
5. uni-app 用户端：pages.json 配置 → request 封装 → 8 个页面（.vue）→ 联调后端。
6. 全链路验证：登录 → 浏览 → 加购 → 下单 → 支付（沙箱或 mock）→ 订单流转 → 后台管理。

---

## 12. 验收标准（全部满足）

- [ ] `backend/` 可 `uvicorn` 启动，Swagger 所有接口可调通。
- [ ] `admin-web/` 可 `npm run dev` 启动，5 大模块功能完整。
- [ ] `uniapp/` 可在 HBuilderX 运行到微信小程序模拟器，8 大模块功能完整。
- [ ] 数据库 7 张表（含 admins）按第 3 节建表。
- [ ] 所有接口返回统一 `{ code, msg, data }`。
- [ ] 图片本地存储 + `/static/` 访问正常。
- [ ] 业务规则 1~8 全部落地。
- [ ] UI 高度还原 `prototypes/` 9 张原型图。
- [ ] 配色与第 10 节一致，无 AI 味。
- [ ] 配置走 .env，无硬编码密钥。

---

## 13. 禁止事项

- 禁止引入 OSS/COS/七牛/任何云存储。
- 禁止用原生 WXML/WXSS 或 Taro 替代 uni-app（用户端统一 uni-app + Vue3）。
- 禁止脑补 PRD 之外的功能（配送、骑手、优惠券、会员、评价、多门店等）。
- 禁止只交付片段代码，必须可运行。
- 禁止使用紫蓝渐变、玻璃拟态等 AI 味视觉。
- 禁止硬编码数据库密码、微信密钥。

---

完成全部三端开发并验证可运行后，输出每个端的启动方式与默认账号。
