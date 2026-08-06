# Tasks

## 后端修复
- [x] Task 1: 修复 pay.py prepay 端点 openid 空值（N1）
  - user 为 None 时抛 HTTPException(400, "用户不存在")，与 order.py _prepay 保持一致
- [x] Task 2: 为 categories.name 添加 UNIQUE 约束（N3，B9 未修）
  - init.sql 添加 UNIQUE KEY uk_name
  - models/category.py 添加 unique=True 索引
  - admin/category.py create 校验重名返回 400
- [x] Task 3: 修复 CORS 通配符+凭据反模式（N4）
  - main.py 中当 CORS_ORIGINS 为 ["*"] 时设 allow_credentials=False
- [x] Task 4: 统一 admin/dish.py category_id 类型标注（N6）
  - 改为 int | None = Query(None)
- [x] Task 5: 订单金额计算改用 Decimal（N5，B7 完成意图）
  - client/order.py create_order 用 Decimal 累加
- [x] Task 6: _serialize_order 增加 item_count 字段（N11，U3 根因）
  - client/order.py 序列化返回 item_count 整数
- [x] Task 7: create_order 回滚重试路径加二次异常处理（N12）
  - 第二次提交 try/except，失败返回 500 友好错误
- [x] Task 8: seed.py 图片路径改为动态年月（N13，B10 根因）
  - 使用 datetime.now().strftime("/static/dishes/%Y/%m")
- [x] Task 9: smoke_test.py 图片路径与 seed.py 对齐（N14）
  - 改为动态路径或与 seed BASE_IMG 一致
- [x] Task 10: main.py 迁移 on_event 到 lifespan（N16）
  - 用 async def lifespan 替代 @app.on_event("startup")
- [x] Task 11: storage.py 文件读取改用 bytearray（N17）
  - 用 bytearray 替代 bytes 拼接

## 前端修复(admin-web)
- [x] Task 12: 修复 DefaultLayout.vue username 非 ref（N8，F5 未修）
  - 改为 ref，avatarLetter computed 响应式更新
- [x] Task 13: 修复 dish/Manage.vue listCategories 空 catch（N9）
  - catch 中加 ElMessage.error('分类加载失败')

## 前端修复(uniapp)
- [x] Task 14: 移除 config.js IMG_BASE 的 localhost 兜底（N2，U1 根因）
  - ?? 'http://localhost:8000' 改为 ?? ''
- [x] Task 15: 修复支付 operatingId 提前重置（N10）
  - orders.vue 和 detail.vue 的 operatingId 重置移到 success/fail 回调
- [x] Task 16: orders.vue itemCount 改用后端 item_count 字段（N11，U3 完成）
  - 移除正则解析，直接读取 order.item_count

# Task Dependencies
- Task 6 与 Task 16 配合（后端字段+前端使用）
- Task 8 与 Task 9 配合（统一图片路径）
- 其余任务无依赖，可并行
