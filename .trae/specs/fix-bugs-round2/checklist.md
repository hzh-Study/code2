# Checklist

## 后端 backend

### 支付与安全
- [x] 微信 `_sign` 已改为 MD5，与 `verify_notify` 一致
- [x] `verify_notify` 使用 `hmac.compare_digest` 常量时间比较
- [x] 构造微信 XML 报文对值做了 `escape` 转义
- [x] 下单 `total_fee` 使用 `Decimal` 计算避免浮点精度
- [x] 支付回调生产模式校验 `total_fee` 与订单金额一致
- [x] 支付回调生产模式返回 XML `<return_code>SUCCESS</return_code>`
- [x] 支付回调 dev 模式仍返回 R.ok
- [x] `DEV_MODE` 缺失微信凭证时启动日志有告警

### 订单状态机
- [x] `mark_cancelled` 仅当 `STATUS_PENDING` 时才置为取消
- [x] `mark_done` 仅当 `STATUS_COOKING` 时才置为完成
- [x] `repay` 检查 `expire_at`，过期则 `mark_cancelled` 并返回 400
- [x] `prepay` 检查 `expire_at`，过期则 `mark_cancelled` 并返回 400

### 数据正确性
- [x] `_gen_order_no` 包含随机后缀，`create_order` 捕获 `IntegrityError` 重试
- [x] `admin/dish.py` 更新逻辑移除 `if value is not None`，可空字段可被 null 清空
- [x] `admin/dashboard.py` 今日销售额按 `paid_at` 过滤并排除已取消订单
- [x] `admin/order.py` `_serialize` 的 `username` 与 dashboard 一致（`user.nickname if user and user.nickname else "微信用户"`）
- [x] `client/order.py` 打包订单校验 `address` 非空

### 并发与输入校验
- [x] `client/auth.py` 登录捕获 `IntegrityError` 回滚后重新查询
- [x] `client/cart.py` 加购捕获 `IntegrityError` 回滚后改为更新数量
- [x] `admin/order.py` 日期筛选捕获 `ValueError` 返回 400
- [x] `schemas/dish.py` `price` 有 `ge=0`，`status` 有 `ge=0, le=1`
- [x] `schemas/cart.py` `CartAdd.quantity` 有 `gt=0`，`CartUpdate.quantity` 有 `ge=0`
- [x] `schemas/order.py` `dining_mode` 为 `Literal[1, 2]`

### 文件上传
- [x] `storage.py` 分块读取累计大小，超 2MB 立即终止
- [x] `storage.py` 校验 `file.content_type`
- [x] `storage.py` 校验文件头魔数（JPEG/PNG）

### 代码质量
- [x] `admin/order.py` 移除未使用的 `mark_cancelled` 导入
- [x] `admin/upload.py` 移除未使用的 `db=Depends(get_db)`
- [x] `deps.py` 从 `database.py` 重导出 `get_db`
- [x] `order_state.build_items_summary` 死代码已删除

### 后端验证
- [x] `backend/smoke_test.py` 全部 52 项通过（含 6 项新增过期检查）
- [x] 新增的金额校验、状态守卫、过期检查有定向验证
- [x] 后端进程重启后无运行期报错

## 管理端 admin-web

### 类型安全与响应处理
- [x] `request.js` 响应拦截器对非 `{code, msg, data}` 结构原样返回，不抛 TypeError
- [x] `request.js` 401 处理有 `isRedirecting` 防抖，不重复弹窗/跳转
- [x] `dish/Manage.vue` 列表价格用 `Number(d.price || 0).toFixed(2)`
- [x] `order/Manage.vue` 列表金额用 `Number(row.total_amount || 0).toFixed(2)`
- [x] `Dashboard.vue` 销售额与订单金额用 `Number(x || 0).toFixed(2)`
- [x] `dish/Manage.vue` 列表解构有 `|| []` / `|| 0` 兜底
- [x] `order/Manage.vue` 列表解构有 `|| []` / `|| 0` 兜底
- [x] `Dashboard.vue` 解构有 `|| {}` / `|| []` / `|| 0` 兜底

### 分页与功能逻辑
- [x] `dish/Manage.vue` 筛选变化时 `filters.page = 1`
- [x] `order/Manage.vue` 筛选变化时 `filters.page = 1`
- [x] `api/order.js` `completeOrder` 传递 `{ status: 3 }`
- [x] `order/Manage.vue` 模板状态比较用 `Number(row.status) === 2`

### 错误处理与上传校验
- [x] `category/Manage.vue` `onDelete` 有 try/catch
- [x] `dish/Manage.vue` `onToggle`/`onDelete` 有 try/catch 与防重复
- [x] `dish/Manage.vue` `onUpload` 有大小/类型校验与 loading
- [x] `order/Manage.vue` `onComplete` 有确认对话框与 try/catch

### 安全与路由
- [x] `Login.vue` 默认凭据提示仅 dev 显示
- [x] `router/index.js` 跳转登录带 `redirect` query
- [x] `Login.vue` 登录成功后跳 `route.query.redirect || '/'`
- [x] `api/dish.js` `uploadImage` 移除手动 Content-Type header

### 管理端验证
- [x] 生产构建 `npm run build` 成功，登录页不显示默认凭据
- [x] 管理端浏览器实测：登录页正常加载，控制台无错误
- [x] 筛选重置分页逻辑已通过源码核验
- [x] 当前页面控制台无 unhandled rejection

## 用户端 uniapp

### 配置与认证
- [x] `config.js` 生产环境 API 地址来自 `import.meta.env.VITE_API_BASE` / `VITE_IMG_BASE`
- [x] 新增 `.env.production` 示例文件
- [x] `request.js` 401 自动登出并跳首页
- [x] `store/user.js` `loginIfNeeded` 有单例 promise 锁
- [x] `request.js` `getToken()` 只调用一次
- [x] `request.js` 未登录时不发送空 Authorization 头
- [x] `request.js` 有 `timeout: 15000`

### 下单与购物车逻辑
- [x] `order.vue` `submit` 有 `submitting` 防抖锁
- [x] `order.vue` `simulatePay` 失败时提示并跳订单列表
- [x] `cart.vue` `change` 当 qty < 1 时移除菜品
- [x] `cart.vue` `change` 有 try/catch

### 类型安全与 UX
- [x] `detail.vue` 金额用 `Number(x || 0).toFixed(2)`
- [x] `orders.vue` 金额用 `Number(x || 0).toFixed(2)`
- [x] `index.vue` `cartCount` 为总件数而非种类数
- [x] `config.js` `imgUrl` 处理无前导斜杠路径
- [x] `detail.vue` 校验 `opts.id` 存在
- [x] `orders.vue` `cancel` 有二次确认
- [x] `orders.vue` `pay` 有空值校验
- [x] `orders.vue` `load` 有序号防竞态

### 用户端验证
- [x] H5 dev 模式 `npm run dev:h5` 启动正常
- [ ] 完整下单链路跑通：浏览 → 加购 → 结算 → 支付 → 订单详情
- [ ] 购物车角标显示总件数
- [ ] 连续点击提交只创建一个订单
- [ ] 控制台无 unhandled rejection
