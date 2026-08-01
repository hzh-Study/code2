# 餐厅点餐项目 · Bug 排查与修复报告

排查范围：后端 FastAPI、用户端 uniapp(H5)、管理端 admin-web 三端全量源码 + 运行态实测。
验证方式：后端冒烟测试(46 项) + 定向接口验证 + Playwright 浏览器实测三端 UI。

## 一、已修复的 Bug（4 项，全部为后端逻辑缺陷）

### 1. 管理端订单「结束日期」筛选漏掉当天订单（off-by-one）
- 文件：`backend/app/api/admin/order.py`
- 问题：`created_at < datetime.strptime(end, "%Y-%m-%d")` 把结束日期当作次日 0 点前，导致**结束日期当天的订单被整批排除**，筛选「今天~今天」看不到今天的订单。
- 修复：`created_at < datetime.strptime(end, "%Y-%m-%d") + timedelta(days=1)`，结束日期改为包含当天（需 `from datetime import datetime, timedelta`）。
- 验证：创建当日订单后，筛选 `start=end=今天`，订单正确返回；UI 订单管理页日期筛选正常。

### 2. 管理端看板「用户」列永远显示「微信用户」
- 文件：`backend/app/api/admin/dashboard.py`
- 问题：`recent_orders` 的 `username` 被**硬编码为 "微信用户"**，后台真实用户昵称不显示。
- 修复：按 `user_id` 关联查询真实昵称，无昵称时回退 "微信用户"（并引入 `app.models.user.User`）。
- 验证：看板首行实际显示真实昵称「测试用户A」；UI 看板确认。

### 3. 下单事务非原子，可能产生「无明细的孤儿订单」
- 文件：`backend/app/api/client/order.py`
- 问题：先 `db.commit()` 落订单，再逐个添加订单项；若中途异常，会留下**没有菜品明细的订单**。
- 修复：用 `db.flush()` 先分配 `order.id`（不提交），订单项 + 清空购物车一次性 `db.commit()`，保证原子性。
- 验证：冒烟测试「订单含菜品快照 / 下单后购物车清空」仍全部通过。

### 4. 支付回调可重新激活「已取消」订单
- 文件：`backend/app/services/order_state.py`
- 问题：`mark_paid` 未校验当前状态，已取消（状态 4）的订单被支付回调重新置为待出餐。
- 修复：`mark_paid` 仅当订单处于待支付（状态 1）时生效，幂等且不会复活已取消订单。
- 验证：取消订单后调用支付回调，订单状态保持「已取消」。

## 二、实测验证结果

### 后端
- 冒烟测试 46/46 通过（重启服务回归通过）。
- 定向验证全部 PASS：日期筛选包含当天、看板真实昵称、取消订单支付回调幂等、管理端标记完成写路径。
- 新进程 `server.err` 仅启动日志，无运行期报错。

### 管理端 admin-web（http://127.0.0.1:5173）
- 登录(admin/admin123)、看板、订单管理、菜品管理、分类管理 5 个页面均正常渲染。
- 「标记完成」仅对「待出餐」订单出现，点击后状态变「已完成」正确。
- 控制台除 `favicon.ico 404`（无害，非功能问题）外无报错。

### 用户端 uniapp H5（http://127.0.0.1:5174）
- 完整下单链路跑通：浏览菜品 → 加入购物车（角标+金额更新）→ 去结算 → 提交订单（dev 模式模拟支付）→ 订单显示「待出餐」→ 订单详情页正确渲染。
- 控制台除 favicon 404 外无报错。

## 三、结论
- 共发现并修复 **4 个真实 Bug**（均为后端逻辑/数据正确性缺陷），三端前端代码与后端接口契约一致，无路径/字段错位。
- 三端功能在运行态实测中均正常，可交付你验收。
- 已知非问题：`favicon.ico 404` 为浏览器自动请求缺失图标所致，不影响功能，如需可后续补一个图标。

> 说明：后端进程已用修复后代码重启（uvicorn，端口 8000），验证均基于修复后运行实例。

---

# 第三轮 Bug 排查与修复报告

排查范围：后端 FastAPI、用户端 uniapp(H5)、管理端 admin-web 三端全量源码复审。
验证方式：后端冒烟测试(52 项) + 三端生产构建 + 源码交叉核验。

## 一、本轮修复的 Bug（3 项）

### 5. 支付回调幂等分支在 DEV_MODE 下返回 XML 导致测试失败
- **文件**：[pay.py](file:///d:/axm/test2026730/backend/app/api/client/pay.py#L88-L92)
- **根因**：幂等分支 `if order.status != STATUS_PENDING` 在 `DEV_MODE=True` 时仍返回 `WX_SUCCESS`（XML 格式），导致冒烟测试 `json.loads` 解析失败。前两轮修复支付回调时，生产模式返回 XML 是正确的，但遗漏了 dev 模式需返回 JSON 的场景。
- **修复方式**：幂等分支增加 `DEV_MODE` 判断，开发模式返回 `R.ok(msg="success")`（JSON），生产模式才返回 `WX_SUCCESS`（XML）。
- **验证**：smoke_test 52/52 全部通过，含「支付回调幂等」项。

### 6. 用户端请求拦截器丢失后端 HTTPException 错误信息
- **文件**：[request.js](file:///d:/axm/test2026730/uniapp/src/utils/request.js#L27-L28)
- **根因**：后端客户端 API 对业务错误混用两种返回：`R.fail()` 返回 `{code, msg, data}`（HTTP 200），`HTTPException` 返回 `{detail: "..."}`（HTTP 4xx，无 `msg` 字段）。前端失败分支只读取 `body.msg`，对 HTTPException 响应 `body.msg` 为 `undefined`，统一回退为"请求失败"，导致"购物车为空""菜品不存在或已下架""打包订单需填写收货地址""订单不存在""仅待支付订单可取消"等真实原因全部对用户隐藏。后端客户端 cart/order/dish 模块共 14 处 `HTTPException` 均受影响。
- **修复方式**：失败 toast 取标题时优先 `body.msg`，回退 `body.detail`，再回退"请求失败"。
- **验证**：`npm run build:h5` 构建成功。

### 7. 首页分类快速切换导致菜品列表错位
- **文件**：[index.vue](file:///d:/axm/test2026730/uniapp/src/pages/index/index.vue#L74-L80)
- **根因**：`loadDishes()` 直接赋值 `dishes.value = await getDishes(activeCat.value)`，无竞态保护。用户快速切换分类 A→B 时，若 A 的响应晚于 B 到达，会把 A 的菜品写入已高亮为 B 的页面，造成分类标签与菜品不一致。同项目 `orders.vue` 已用 `loadSeq` 解决同类问题，但 `index.vue` 漏处理。
- **修复方式**：引入 `dishSeq` 序号，请求前自增并记录，响应返回后比对，过期响应直接丢弃（与 `orders.vue` 的 `loadSeq` 同模式）。
- **验证**：`npm run build:h5` 构建成功。

## 二、验证结果

### 后端
- 冒烟测试 **52/52 全部通过**（含原失败的支付回调幂等项）。
- 后端进程重启后无运行期报错。
- 全量复审 admin/client API、services、schemas、models、utils，未发现新 Bug。

### 管理端 admin-web
- `npm run build` 构建成功（退出码 0）。
- 全量复审 api/router/layouts/views，**未发现新 Bug**。
- 3 个非致命警告（第三方注解、Sass Legacy API、chunk 体积）与基线一致。

### 用户端 uniapp
- `npm run build:h5` 构建成功（退出码 0）。
- 全量复审 utils/store/config/App/pages，修复 2 个 Bug。
- 构建无新增警告/错误。

## 三、结论
- 本轮共发现并修复 **3 个 Bug**（后端 1 个、用户端 2 个），管理端无新 Bug。
- 累计三轮共修复 **7 个 Bug**（第一轮 4 个 + 第三轮 3 个）。
- 三端构建与测试均通过，代码库主要路径已完整审查，未发现新的明显问题。

## 四、仍存在的已知限制或风险

1. **时区一致性**：`Order.created_at` 使用 `server_default=func.now()`（SQLite 下返回 UTC），而 `dashboard.py` 的 `today_start` 使用 `datetime.now()`（本地时间）。在 UTC+8 环境下凌晨 0-8 点可能导致看板「今日销售额」统计偏差。此为设计层面问题，修复需统一时区策略，超出最小改动范围。
2. **管理端 chunk 体积**：`index-*.js` 超过 500 kB，首屏加载可优化（`manualChunks` 拆分），但不影响功能正确性。
3. **Sass Legacy API 弃用**：Dart Sass 2.0 将移除 Legacy API，未来升级 Sass 后构建可能失败，需迁移到 Modern API。
4. **uniapp Appid 未配置**：`manifest.json` 中 `appid` 为空，不影响 H5 部署，但发布到 DCloud 平台时需补充。
5. **管理员密码仍用 MD5**：未迁移到 bcrypt（需迁移现有哈希，留作后续单独 spec 处理）。
6. **CORS `allow_origins=["*"]`**：生产部署时需收敛到具体域名清单。
7. **无 lint/type-check 脚本**：admin-web 与 uniapp 均未配置 ESLint/TypeScript 检查，建议基线稳定后补充。
