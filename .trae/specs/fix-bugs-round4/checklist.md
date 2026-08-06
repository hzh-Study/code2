# Checklist

## 后端
- [x] pay.py prepay 端点 user 为 None 时抛 HTTPException(400) 而非传空 openid
- [x] init.sql 中 categories.name 有 UNIQUE 约束
- [x] models/category.py name 字段 unique=True
- [x] admin/category.py 创建重名分类返回 400
- [x] main.py CORS_ORIGINS 为 ["*"] 时 allow_credentials=False
- [x] admin/dish.py category_id 类型标注为 int | None
- [x] client/order.py create_order 金额用 Decimal 累加
- [x] client/order.py _serialize_order 返回 item_count 字段
- [x] client/order.py create_order 回滚重试有二次异常处理
- [x] seed.py 图片路径为动态年月（非硬编码）
- [x] smoke_test.py 图片路径与 seed.py 一致
- [x] main.py 使用 lifespan 而非 on_event("startup")
- [x] storage.py 文件读取使用 bytearray

## 前端(admin-web)
- [x] DefaultLayout.vue username 为 ref
- [x] dish/Manage.vue listCategories 失败有 ElMessage.error 提示

## 前端(uniapp)
- [x] config.js IMG_BASE 无 localhost 兜底
- [x] orders.vue pay 的 operatingId 在 success/fail 回调中重置
- [x] orders/detail.vue pay 的 operatingId 在 success/fail 回调中重置
- [x] orders.vue itemCount 直接读取 order.item_count 而非字符串解析
