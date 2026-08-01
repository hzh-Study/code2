# 餐厅点餐系统 Bug 修复（第二轮）Spec

## Why

第一轮已修复 4 个后端逻辑缺陷（见 `BUG_FIX_REPORT.md`）。本次对三端源码（backend / admin-web / uniapp）做全量复审，又发现一批影响功能正确性、安全性、用户体验的 Bug。本 spec 用于系统性修复这些问题，使三端在「dev 模式」与「生产模式」下均能稳定、安全运行。

## What Changes

### 后端 backend（Python / FastAPI）

#### 支付与安全（严重）
- **BREAKING** 修复微信支付签名算法不一致：`_sign` 统一改为 MD5（微信 V2 默认），与 `verify_notify` 保持一致；移除错误的「HMAC-SHA256」注释。
- 修复支付回调未校验金额：生产模式下必须比对 `total_fee` 与订单应付金额（用 Decimal 计算，避免浮点精度）。
- 修复支付金额浮点精度：`total_fee = int(Decimal(str(order.total_amount)) * 100)`，避免 `int(float(...) * 100)` 少收 1 分。
- 修复微信回调返回格式：生产模式返回微信要求的 XML `<return_code>SUCCESS</return_code>`，dev 模式仍返回 R.ok。
- 修复 `mark_cancelled` / `mark_done` 不校验当前状态（与已修复的 `mark_paid` 同类问题），加防御性守卫。
- 修复 `repay` / `prepay` 未校验订单是否已过期，过期订单先 `mark_cancelled` 再拒绝。
- 加固 `DEV_MODE`：当 `WX_APPID`/`WX_SECRET` 缺失时仍允许 dev，但日志显式告警；不在生产部署文档中隐瞒。
- 微信回调验签改用 `hmac.compare_digest` 常量时间比较。
- 构造微信 XML 报文时对值做 `xml.sax.saxutils.escape` 转义。

#### 数据正确性（高）
- 修复订单号碰撞风险：`_gen_order_no` 追加 6 位随机 hex，并在 `create_order` 捕获 `IntegrityError` 重试一次。
- 修复菜品更新无法清空可空字段：移除 `if value is not None` 与 `exclude_unset=True` 叠加导致的 null 被跳过问题。
- 修复看板「今日销售额」按 `created_at` 统计：改为按 `paid_at` 过滤，并排除已取消订单。
- 修复管理端订单列表 `username` 显示 null：与 dashboard 一致，`user.nickname if user and user.nickname else "微信用户"`。
- 修复打包订单未校验收货地址：`dining_mode == PACKING` 时 `address` 必填。

#### 并发与输入校验（中）
- 修复用户注册并发竞态：捕获 `IntegrityError` 后回滚并重新查询。
- 修复购物车添加并发竞态：捕获 `IntegrityError` 后回滚改为更新数量。
- 修复订单日期筛选未处理格式异常：`try/except ValueError` 返回 400。
- `schemas/dish.py`：`price` 加 `ge=0`，`status` 加 `ge=0, le=1`。
- `schemas/cart.py`：`CartAdd.quantity` 加 `gt=0`，`CartUpdate.quantity` 加 `ge=0`。
- `schemas/order.py`：`dining_mode` 改为 `Literal[1, 2]`。

#### 文件上传（中）
- 修复上传先全量读入内存再校验大小：改为分块读取累计，超限立即终止。
- 加固上传内容校验：除扩展名外，校验 `content_type` 与文件头魔数（JPEG `FF D8`、PNG `89 50 4E 47`）。

#### 代码质量（低）
- 移除 `admin/order.py` 未使用的 `mark_cancelled` 导入。
- 移除 `admin/upload.py` 未使用的 `db=Depends(get_db)` 参数。
- `deps.py` 改为从 `database.py` 重导出 `get_db`，删除重复定义。
- 删除 `order_state.build_items_summary` 死代码。

### 管理端 admin-web（Vue 3）

#### 类型安全与稳定性（严重）
- 修复 `.toFixed(2)` 类型不安全：`dish/Manage.vue`、`order/Manage.vue` 列表、`Dashboard.vue` 全部改为 `Number(x || 0).toFixed(2)`。
- 修复列表数据解构无空值防御：`dish/Manage.vue`、`order/Manage.vue`、`Dashboard.vue` 加 `|| {}` / `|| []` / `|| 0`。
- 修复 401 重复弹窗与路由抖动：`request.js` 加 `isRedirecting` 标志位防抖。
- 修复响应拦截器对非标准响应体崩溃：判断 `res` 为对象且含 `code` 字段才走业务分支，否则原样返回。

#### 功能与 UX（高）
- 修复筛选条件变化未重置分页：`dish/Manage.vue`、`order/Manage.vue` 所有查询触发处先 `filters.page = 1`。
- 修复 `completeOrder` 未传目标状态值：`api/order.js` 改为 `request.post(..., { status: 3 })`。
- 修复订单状态严格比较：`order/Manage.vue` 模板 `Number(row.status) === 2`。
- 删除/完成操作加 `try/catch`：`category/Manage.vue`、`dish/Manage.vue`、`order/Manage.vue`。
- 图片上传加大小/类型校验与 loading：`dish/Manage.vue`。

#### 安全（中）
- 登录页默认凭据仅在 dev 模式显示：`Login.vue` 用 `import.meta.env.DEV` 控制。
- 路由守卫传递 `redirect` 参数，登录后回到原页面。
- `dish.js uploadImage` 移除手动 `Content-Type: multipart/form-data`，让浏览器自动补 boundary。

### 用户端 uniapp（UniApp）

#### 配置与认证（严重）
- **BREAKING** 修复生产环境 API 硬编码 localhost：`config.js` 改为通过 `import.meta.env.VITE_API_BASE` / `VITE_IMG_BASE` 注入，保留 dev 默认值。
- 修复 401 未自动登出：`request.js` 检测 401 后清 token 并跳首页。
- 修复 `loginIfNeeded` 无锁并发：加单例 promise 锁，避免重复创建用户。
- 修复 `submit` 无防抖可重复下单：加 `submitting` 锁。

#### 类型安全与逻辑（高）
- 修复 `detail.vue` / `orders.vue` `.toFixed(2)` 未包 `Number()`，金额为字符串时白屏。
- 修复购物车数量可减到 0/负数：`cart.vue` `change` 函数 qty < 1 时直接移除该菜品。
- 修复首页购物车角标显示种类数而非总件数：`index.vue` `cartCount` 改为 `reduce(quantity)`。
- 修复 `imgUrl` 未处理无前导斜杠的相对路径。
- `orders.vue` 取消订单加二次确认；`pay` 加空值校验。
- `detail.vue` 校验 `opts.id` 存在性。

#### 错误处理（中）
- `request.js`：`getToken()` 只调用一次；未登录时不发送空 Authorization 头；加 15s timeout。
- `cart.vue` `change` 加 try/catch。
- `orders.vue` `load` 加序号防竞态。

## Impact

- **Affected specs**: 第一轮 `BUG_FIX_REPORT.md` 中已修复的 4 项不在本次范围。
- **Affected code**:
  - 后端：`backend/app/api/admin/{order,upload}.py`、`backend/app/api/client/{order,pay,auth,cart}.py`、`backend/app/services/{wechat,order_state,storage}.py`、`backend/app/schemas/{dish,cart,order}.py`、`backend/app/utils/security.py`、`backend/app/{deps,main}.py`
  - 管理端：`admin-web/src/api/{request,dish,order}.js`、`admin-web/src/router/index.js`、`admin-web/src/views/{Login,Dashboard}.vue`、`admin-web/src/views/{category,dish,order}/Manage.vue`
  - 用户端：`uniapp/src/{config.js,utils/request.js,store/user.js,App.vue}`、`uniapp/src/pages/{cart,index,order,orders}/*.vue`
  - 配置：`uniapp/.env*`（新增生产环境变量示例）
- **Breaking changes**:
  - 微信支付签名算法改为 MD5（仅影响生产微信支付，dev 模式不变）。
  - uniapp 生产 API 地址改为环境变量注入，部署时需配置 `VITE_API_BASE` / `VITE_IMG_BASE`。
- **不在本次范围**（保留为后续改进）：
  - 管理员密码改 bcrypt（需迁移现有哈希，单独 spec 处理）。
  - `SECRET_KEY` 默认值告警（需配合部署文档，单独处理）。
  - CORS `allow_origins=["*"]` 收敛（需明确生产域名清单）。
  - N+1 查询性能优化（不影响正确性）。
  - 客户端订单列表分页（不影响正确性）。
  - `manifest.json` 真实 appid（需业务方提供）。
  - JWT token 主动失效 / refresh token 机制（架构性改造）。

## ADDED Requirements

### Requirement: 支付安全

#### Scenario: 支付回调金额校验
- **WHEN** 微信回调到达且 `DEV_MODE=False`
- **THEN** 系统比对 `total_fee` 与 `Decimal(order.total_amount)*100`，不一致则拒绝标记已支付并返回失败。

#### Scenario: 支付金额精度
- **WHEN** 订单金额为 `19.99`
- **THEN** 微信下单 `total_fee` 为 `1999`（而非 `1998`）。

#### Scenario: 微信回调返回格式
- **WHEN** 支付回调处理成功且 `DEV_MODE=False`
- **THEN** 返回 `Content-Type: application/xml` 的 `<xml><return_code>SUCCESS</return_code></xml>`。

#### Scenario: 微信签名算法一致
- **WHEN** 调用统一下单或校验回调
- **THEN** 签名与验签均使用 MD5 算法。

### Requirement: 订单状态机防御

#### Scenario: 已支付订单不可被取消
- **WHEN** 调用 `mark_cancelled` 且订单状态非「待支付」
- **THEN** 订单状态保持不变，函数直接返回。

#### Scenario: 已取消订单不可被完成
- **WHEN** 调用 `mark_done` 且订单状态非「待出餐」
- **THEN** 订单状态保持不变。

#### Scenario: 过期订单不可支付
- **WHEN** 调用 `repay` 或 `prepay` 且订单 `expire_at` 已过期
- **THEN** 系统先 `mark_cancelled` 再返回 400「订单已超时取消」。

### Requirement: 数据正确性

#### Scenario: 订单号不碰撞
- **WHEN** 同一毫秒并发创建两个订单
- **THEN** 订单号不同；若仍触发唯一约束冲突，捕获 `IntegrityError` 重试一次。

#### Scenario: 菜品可空字段可清空
- **WHEN** 管理员提交 `{"image": null}` 更新菜品
- **THEN** 菜品 `image` 字段被清空为 NULL。

#### Scenario: 看板销售额按支付时间
- **WHEN** 查询今日销售额
- **THEN** 过滤条件为 `paid_at >= today_start` 且 `pay_status == 1` 且 `status != 4`。

#### Scenario: 打包订单必填地址
- **WHEN** 创建 `dining_mode=2` 订单且 `address` 为空
- **THEN** 返回 400「打包订单需填写收货地址」。

### Requirement: 并发安全

#### Scenario: 用户注册并发
- **WHEN** 两个相同 openid 的登录请求并发到达
- **THEN** 第二个请求捕获 `IntegrityError` 后回滚并重新查询，不返回 500。

#### Scenario: 购物车并发添加
- **WHEN** 两个相同 user_id + dish_id 的加购请求并发到达
- **THEN** 第二个请求捕获 `IntegrityError` 后改为更新数量，不返回 500。

### Requirement: 文件上传安全

#### Scenario: 上传超大文件
- **WHEN** 上传文件超过 2MB
- **THEN** 在读取过程中（而非读完后）即拒绝，不占用完整内存。

#### Scenario: 上传伪装文件
- **WHEN** 上传扩展名为 `.jpg` 但文件头非 JPEG/PNG 魔数
- **THEN** 返回 400「文件内容非有效图片」。

### Requirement: 管理端类型安全

#### Scenario: 金额字段为字符串
- **WHEN** 后端返回 `total_amount: "19.99"`（字符串）
- **THEN** 前端 `Number(row.total_amount || 0).toFixed(2)` 正常渲染，不白屏。

#### Scenario: 列表数据为 null
- **WHEN** 后端返回 `data: null`
- **THEN** 前端解构不抛 `Cannot read properties of null`。

### Requirement: 用户端配置与认证

#### Scenario: 生产环境 API 地址
- **WHEN** 构建生产包
- **THEN** API 地址来自 `import.meta.env.VITE_API_BASE`，不硬编码 localhost。

#### Scenario: 401 自动登出
- **WHEN** 后端返回 401
- **THEN** 前端清空 token 并跳转首页触发重新登录。

#### Scenario: 重复登录请求合并
- **WHEN** 应用启动时多处并发调用 `loginIfNeeded`
- **THEN** 只发起一次 `/client/auth/login` 请求。

#### Scenario: 防重复下单
- **WHEN** 用户在 `createOrder` 未返回前再次点击提交
- **THEN** 第二次点击被忽略。

## MODIFIED Requirements

### Requirement: 前端金额展示
所有金额展示统一使用 `Number(value || 0).toFixed(2)`，兼容 number / string / null / undefined。

### Requirement: 分页查询
筛选条件（分类、关键词、状态、日期）变化时，`page` 必须重置为 1。
