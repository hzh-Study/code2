# Tasks

## 后端 backend

- [x] Task 1: 修复微信支付与签名相关 Bug（`backend/app/services/wechat.py`、`backend/app/api/client/pay.py`）
  - [x] SubTask 1.1: `_sign` 统一改为 MD5，更新文档注释；`verify_notify` 已用 MD5 保持不变，但改用 `hmac.compare_digest` 常量时间比较。
  - [x] SubTask 1.2: 构造微信 XML 报文时对值做 `xml.sax.saxutils.escape` 转义。
  - [x] SubTask 1.3: 下单 `total_fee` 改用 `int(Decimal(str(order.total_amount)) * 100)` 避免浮点精度。
  - [x] SubTask 1.4: 支付回调 `notify` 在 `DEV_MODE=False` 时校验 `total_fee` 与订单应付金额一致；生产模式返回 XML `<return_code>SUCCESS</return_code>`，dev 模式仍返回 R.ok。
  - [x] SubTask 1.5: `DEV_MODE` 缺失微信凭证时在启动日志中显式告警（`main.py` 或 `config.py`）。
  - [x] 验证：`backend/smoke_test.py` 全部通过；dev 模式支付回调仍可走通；新增金额一致性校验单测。

- [x] Task 2: 修复订单状态机防御（`backend/app/services/order_state.py`、`backend/app/api/client/order.py`、`backend/app/api/client/pay.py`）
  - [x] SubTask 2.1: `mark_cancelled` 加守卫：仅 `STATUS_PENDING` 才置为取消，否则直接返回 order。
  - [x] SubTask 2.2: `mark_done` 加守卫：仅 `STATUS_COOKING` 才置为完成，否则直接返回 order。
  - [x] SubTask 2.3: `repay`（client/order.py）与 `prepay`（client/pay.py）在调用 `_prepay` 前先检查 `is_expired(order.expire_at)`，过期则 `mark_cancelled` 并返回 400。
  - [x] 验证：冒烟测试「取消订单后调用 mark_done 不变化」「过期订单 repay 返回 400」。

- [x] Task 3: 修复数据正确性问题（`backend/app/api/admin/{order,dish}.py`、`backend/app/api/admin/dashboard.py`、`backend/app/api/client/order.py`）
  - [x] SubTask 3.1: `_gen_order_no` 追加 6 位随机 hex：`f"SW{...}{uuid.uuid4().hex[:6].upper()}"`；`create_order` 用 `try/except IntegrityError` 重试一次（重新生成订单号）。
  - [x] SubTask 3.2: `admin/dish.py` 更新逻辑移除 `if value is not None`，仅靠 `exclude_unset=True` 决定是否更新（允许显式传 null 清空）。
  - [x] SubTask 3.3: `admin/dashboard.py` 今日销售额过滤改为 `Order.paid_at >= today_start` 且 `pay_status == 1` 且 `status != 4`。
  - [x] SubTask 3.4: `admin/order.py` `_serialize` 中 `username` 改为 `user.nickname if user and user.nickname else "微信用户"`。
  - [x] SubTask 3.5: `client/order.py` `create_order` 当 `dining_mode == PACKING` 且 `address` 为空时返回 400。
  - [x] 验证：菜品 image 可清空；打包订单无地址返回 400；看板销售额按支付时间。

- [x] Task 4: 修复并发竞态与输入校验（`backend/app/api/client/{auth,cart}.py`、`backend/app/api/admin/order.py`、`backend/app/schemas/{dish,cart,order}.py`）
  - [x] SubTask 4.1: `client/auth.py` 登录：`try/except IntegrityError` 回滚后重新查询 user。
  - [x] SubTask 4.2: `client/cart.py` 加购：`try/except IntegrityError` 回滚后改为 `item.quantity += body.quantity` 更新。
  - [x] SubTask 4.3: `admin/order.py` 日期筛选 `try/except ValueError` 返回 `R.fail(3007, "日期格式错误，应为 YYYY-MM-DD")`。
  - [x] SubTask 4.4: `schemas/dish.py` `DishCreate.price` 加 `ge=0`，`status` 加 `ge=0, le=1`；`DishUpdate` 同理。
  - [x] SubTask 4.5: `schemas/cart.py` `CartAdd.quantity` 加 `gt=0`，`CartUpdate.quantity` 加 `ge=0`。
  - [x] SubTask 4.6: `schemas/order.py` `dining_mode` 改为 `Literal[1, 2]`。
  - [x] 验证：并发登录/加购不返回 500；非法日期返回 400；负价格/负数量被 schema 拒绝。

- [x] Task 5: 修复文件上传安全（`backend/app/services/storage.py`）
  - [x] SubTask 5.1: 分块读取累计大小，超 2MB 立即终止并返回 400，不再先 `read()` 全量。
  - [x] SubTask 5.2: 校验 `file.content_type in ("image/jpeg", "image/png")`。
  - [x] SubTask 5.3: 校验文件头魔数：JPEG `b'\xff\xd8'` 或 PNG `b'\x89PNG'`，否则返回 400「文件内容非有效图片」。
  - [x] 验证：上传超过 2MB 文件被拒；上传伪装 .jpg 的文本文件被拒。

- [x] Task 6: 后端代码质量清理（`backend/app/api/admin/{order,upload}.py`、`backend/app/deps.py`、`backend/app/services/order_state.py`）
  - [x] SubTask 6.1: 移除 `admin/order.py` 未使用的 `mark_cancelled` 导入。
  - [x] SubTask 6.2: 移除 `admin/upload.py` 未使用的 `db=Depends(get_db)` 参数。
  - [x] SubTask 6.3: `deps.py` 改为 `from app.database import get_db` 重导出，删除重复定义。
  - [x] SubTask 6.4: 删除 `order_state.build_items_summary` 死代码。
  - [x] 验证：后端可正常启动；冒烟测试全部通过。

## 管理端 admin-web

- [x] Task 7: 修复类型安全与响应处理（`admin-web/src/api/request.js`、`admin-web/src/views/{Dashboard,dish/Manage,order/Manage}.vue`）
  - [x] SubTask 7.1: `request.js` 响应拦截器：仅当 `res` 为对象且含 `code` 字段才走业务分支；否则原样返回 `res`。
  - [x] SubTask 7.2: `request.js` 401 处理加 `isRedirecting` 标志位防抖，避免多次弹窗与路由跳转。
  - [x] SubTask 7.3: `dish/Manage.vue` 列表 `d.price.toFixed(2)` → `Number(d.price || 0).toFixed(2)`。
  - [x] SubTask 7.4: `order/Manage.vue` 列表 `row.total_amount.toFixed(2)` → `Number(row.total_amount || 0).toFixed(2)`。
  - [x] SubTask 7.5: `Dashboard.vue` `stats.today_sales.toFixed(2)` 与 `row.total_amount.toFixed(2)` → `Number(x || 0).toFixed(2)`。
  - [x] SubTask 7.6: `dish/Manage.vue` `data.list || []`、`data.total || 0`；`order/Manage.vue` 同理；`Dashboard.vue` `data || {}` 并对每个字段兜底。
  - [x] 验证：后端返回字符串金额/null 时不白屏。

- [x] Task 8: 修复分页与功能逻辑（`admin-web/src/views/{dish,order}/Manage.vue`、`admin-web/src/api/order.js`）
  - [x] SubTask 8.1: `dish/Manage.vue` 分类 `@change`、关键词 `@clear`、查询按钮 `@click` 统一改为调用 `resetAndLoad`（先 `filters.page = 1` 再 `load()`）。
  - [x] SubTask 8.2: `order/Manage.vue` 状态 `@change`、日期、查询按钮同理加 `resetAndLoad`。
  - [x] SubTask 8.3: `api/order.js` `completeOrder` 改为 `request.post(\`/v1/admin/orders/${id}/status\`, { status: 3 })`。
  - [x] SubTask 8.4: `order/Manage.vue` 模板 `v-if="row.status === 2"` → `v-if="Number(row.status) === 2"`。
  - [x] 验证：第 3 页改筛选后回到第 1 页；标记完成按钮在状态为字符串 '2' 时也显示。

- [x] Task 9: 修复错误处理与上传校验（`admin-web/src/views/{category,dish,order}/Manage.vue`）
  - [x] SubTask 9.1: `category/Manage.vue` `onDelete` 加 try/catch（用户取消与 API 失败分别处理）。
  - [x] SubTask 9.2: `dish/Manage.vue` `onToggle`、`onDelete` 加 try/catch 与 `_toggling`/`_deleting` 防重复。
  - [x] SubTask 9.3: `dish/Manage.vue` `onUpload` 加大小（≤2MB）、类型（image/*）校验与 `uploading` loading；加 try/catch。
  - [x] SubTask 9.4: `order/Manage.vue` `onComplete` 加确认对话框 + try/catch。
  - [x] 验证：取消删除不报 unhandled rejection；上传超大文件被前端拒绝。

- [x] Task 10: 修复安全与路由（`admin-web/src/views/Login.vue`、`admin-web/src/router/index.js`、`admin-web/src/api/dish.js`）
  - [x] SubTask 10.1: `Login.vue` 默认凭据提示用 dev 环境变量控制，仅 dev 显示。
  - [x] SubTask 10.2: `router/index.js` 未登录跳转带 redirect；已登录访问 /login 跳 /。
  - [x] SubTask 10.3: `Login.vue` 登录成功后回跳 `route.query.redirect || '/'`。
  - [x] SubTask 10.4: `api/dish.js` `uploadImage` 移除手动 Content-Type header。
  - [x] 验证：生产构建成功，登录页不显示默认凭据。

## 用户端 uniapp

- [x] Task 11: 修复配置与认证（`uniapp/src/config.js`、`uniapp/src/utils/request.js`、`uniapp/src/store/user.js`、`uniapp/src/App.vue`）
  - [x] SubTask 11.1: `config.js` 生产环境 `API_BASE` / `IMG_BASE` 改为读 `import.meta.env.VITE_API_BASE` / `VITE_IMG_BASE`，保留 dev 默认；新增 `.env.production` 示例（占位变量）。
  - [x] SubTask 11.2: `request.js` 检测 `res.statusCode === 401` → 调用 `logout()` 清 token 并 `uni.reLaunch` 到 /pages/index/index。
  - [x] SubTask 11.3: `store/user.js` `loginIfNeeded` 加单例 promise 锁（`loginPromise`），并发调用复用同一 promise。
  - [x] SubTask 11.4: `request.js` `getToken()` 只调用一次，未登录时不发送空 Authorization 头；加 `timeout: 15000`。
  - [x] 验证：并发 `loginIfNeeded` 只发一次登录请求；401 后自动登出。

- [x] Task 12: 修复下单与购物车逻辑（`uniapp/src/pages/order/order.vue`、`uniapp/src/pages/cart/cart.vue`）
  - [x] SubTask 12.1: `order.vue` `submit` 加 `submitting` ref 锁，`try/finally` 释放；`simulatePay` 失败时 toast「支付失败」并跳订单列表。
  - [x] SubTask 12.2: `cart.vue` `change` 函数：当 `qty < 1` 时调用 `updateCart(dish_id, 0)` 移除该菜品；加 try/catch，失败时 toast。
  - [x] 验证：连续点击提交只创建一个订单；购物车数量不能为负。

- [x] Task 13: 修复类型安全与 UX（`uniapp/src/pages/orders/{detail,orders}.vue`、`uniapp/src/pages/index/index.vue`、`uniapp/src/config.js`）
  - [x] SubTask 13.1: `detail.vue` `it.subtotal.toFixed(2)` → `Number(it.subtotal || 0).toFixed(2)`；`order.total_amount.toFixed(2)` 同理。
  - [x] SubTask 13.2: `orders.vue` `o.total_amount.toFixed(2)` → `Number(o.total_amount || 0).toFixed(2)`。
  - [x] SubTask 13.3: `index.vue` `cartCount` 改为 `items.reduce((s, it) => s + Number(it.quantity || 0), 0)`。
  - [x] SubTask 13.4: `config.js` `imgUrl` 当 path 不以 `/` 开头时补 `/`。
  - [x] SubTask 13.5: `detail.vue` `onLoad` 校验 `opts.id` 存在，无则 toast 并返回。
  - [x] SubTask 13.6: `orders.vue` `cancel` 加 `uni.showModal` 二次确认；`pay` 加 `res.pay_params` 空值校验；`load` 加序号防竞态。
  - [x] 验证：金额为字符串时不白屏；购物车角标显示总件数；取消订单有确认框。

- [x] Task 14: 补充过期订单定向冒烟测试（`backend/smoke_test.py`）
  - [x] SubTask 14.1: 在 `smoke_test.py` 中新增测试：创建订单后手动将 `expire_at` 改为过去时间，调用 `repay` 与 `prepay`，断言返回 400/失败且订单状态变为已取消。
  - [x] 验证：`smoke_test.py` 全部通过（含新增项）。

## Task Dependencies

- Task 1, 5, 6, 7, 10, 11 相互独立，可并行。
- Task 2 依赖 Task 1（共用 order_state / pay 上下文，但改不同函数，可并行；验证时需一起跑）。
- Task 3, 4 依赖后端基础结构，独立于 Task 1/2，可并行。
- Task 8, 9 依赖 Task 7（同文件，需顺序避免冲突）。
- Task 12, 13 依赖 Task 11（同文件，需顺序避免冲突）。
- 验证阶段：所有任务完成后统一运行 `backend/smoke_test.py` 与三端 Playwright 实测。
