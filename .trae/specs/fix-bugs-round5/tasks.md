# Tasks

## 后端修复
- [ ] Task 1: 修复 admin/category.py update_category 查重（R1）
  - 改名时查询同名分类（排除自身），冲突返回 400
- [ ] Task 2: 修复 client/order.py 重试路径用 Decimal（R2）
  - 重试路径 subtotal 改用 Decimal(str(dish.price)) * ci.quantity
- [ ] Task 3: 修复 client/order.py 重试路径 db.flush 保护（R7）
  - 将 flush 及后续逻辑放入 try/except
- [ ] Task 4: 修复 client/order.py _prepay 失败友好处理（R8）
  - _prepay 失败时返回 {order_id, order_no, pay_params: null} 而非 500
- [ ] Task 5: 修复 client/order.py 菜品 None vs 下架提示（N27）
  - dish 为 None 提示"菜品不存在"，否则"已下架"
- [ ] Task 6: 优化 client/order.py _serialize_order N+1 查询（R10）
  - list_orders 批量预加载 OrderItem 与 Dish
- [ ] Task 7: 清理 client/order.py 重复导入（N21）
  - 顶部统一导入 STATUS_CANCELLED, STATUS_PENDING
- [ ] Task 8: 修复 admin/dish.py 删除菜品保护购物车（N25）
  - 删除前检查 Cart 引用，有引用则拒绝或仅允许下架
- [ ] Task 9: 修复 client/cart.py update_cart 校验在售（R14）
  - 更新时查询 dish.status，下架返回 400
- [ ] Task 10: 限制 order address 长度（R15）
  - schemas/order.py address 加 max_length=255
- [ ] Task 11: 迁移 wechat.py MD5 到 HMAC-SHA256（N15）
  - 使用 hmac.new(key, raw, hashlib.sha256)
  - signType 改为 "HMAC-SHA256"
- [ ] Task 12: 修复 wechat.py 内联 __import__（N22）
  - 顶部 import time，用 time.time()
- [ ] Task 13: 修复 pay.py WX_SUCCESS 单例（R9）
  - 改为工厂函数，每次返回新 Response
- [ ] Task 14: 强化 config.py SECRET_KEY 生产校验（R11）
  - 生产环境默认值时 raise RuntimeError
- [ ] Task 15: 修复 config.py DEV_MODE 隐式推断（N26）
  - 增加 DEV_MODE 环境变量显式控制
- [ ] Task 16: admin/auth.py 登录频率限制（R12）
  - 简单内存限流，单 IP 60 秒 5 次
- [ ] Task 17: 清理 main.py UPLOAD_DIR 重复 makedirs（N30）
  - 删除 lifespan 中冗余创建（保留模块级）

## 前端修复(admin-web)
- [ ] Task 18: 修复 request.js 401 跳转用 router（N18）
  - 用 router.replace('/login') 替代 window.location.hash
- [ ] Task 19: 修复 dish/Manage.vue toggleDish 多余参数（N19）
  - 删除第二参数
- [ ] Task 20: 修复 order.js completeOrder body 契约（N20）
  - 后端接受 body 或前端不发 body
- [ ] Task 21: 修复 admin-web 多处 load() 未 await（R16）
  - dish/Manage.vue、category/Manage.vue、order/Manage.vue 的 load() 加 await 或 catch
- [ ] Task 22: 修复 dish/Manage.vue resolveImg 生产配置（R13）
  - .env.production 增加 VITE_STATIC_BASE

## 前端修复(uniapp)
- [ ] Task 23: 修复 .env.production 绝对 URL（R3）
  - VITE_API_BASE、VITE_IMG_BASE 改为示例绝对地址
- [ ] Task 24: 修复 detail.vue onLoad 缺 catch（R4）
  - 加 catch 设 error.value = true
- [ ] Task 25: 修复 cart.vue onShow 缺 error（R5）
  - catch 中加 error.value = true
- [ ] Task 26: 修复 orders.vue onShow 缺 error（R6）
  - catch 中加 error.value = true
- [ ] Task 27: 修复 detail.vue dining_mode fallback（N23）
  - 非 1 非 2 时显示"未知"
- [ ] Task 28: 修复 orders.vue activeLabel 重复 find（N24）
  - 提取变量避免重复调用
- [ ] Task 29: 修复 uniapp 多处 async 无 catch（N28）
  - order.vue submit、index.vue changeDish 加 catch

# Task Dependencies
- Task 2、3、4、5、6、7 都在 client/order.py，需顺序或合并执行
- Task 11、12 都在 wechat.py，合并执行
- Task 18 与 Task 21 都涉及 admin-web，但不同文件可并行
- 其余任务无依赖，可并行
