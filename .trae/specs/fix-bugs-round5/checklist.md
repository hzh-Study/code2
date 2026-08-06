# Checklist

## 后端
- [ ] admin/category.py update_category 改名时查重，冲突返回 400
- [ ] client/order.py 重试路径 subtotal 用 Decimal
- [ ] client/order.py 重试路径 db.flush 在 try/except 内
- [ ] client/order.py _prepay 失败返回 pay_params: null 而非 500
- [ ] client/order.py dish 为 None 提示"菜品不存在"
- [ ] client/order.py list_orders 批量预加载避免 N+1
- [ ] client/order.py 顶部统一导入 STATUS_CANCELLED, STATUS_PENDING
- [ ] admin/dish.py 删除菜品时检查购物车引用
- [ ] client/cart.py update_cart 校验菜品在售状态
- [ ] schemas/order.py address 有 max_length=255
- [ ] wechat.py 签名用 HMAC-SHA256
- [ ] wechat.py signType 为 "HMAC-SHA256"
- [ ] wechat.py 顶部 import time，无内联 __import__
- [ ] pay.py WX_SUCCESS 为工厂函数
- [ ] config.py 生产环境默认 SECRET_KEY 时 raise RuntimeError
- [ ] config.py DEV_MODE 支持环境变量显式控制
- [ ] admin/auth.py 登录有频率限制
- [ ] main.py lifespan 无冗余 UPLOAD_DIR makedirs

## 前端(admin-web)
- [ ] request.js 401 用 router.replace 跳转
- [ ] dish/Manage.vue toggleDish 无多余第二参数
- [ ] order.js completeOrder 与后端 body 契约一致
- [ ] dish/Manage.vue、category/Manage.vue、order/Manage.vue load() 有 await 或 catch
- [ ] .env.production 有 VITE_STATIC_BASE
- [ ] dish/Manage.vue resolveImg 生产环境用 VITE_STATIC_BASE

## 前端(uniapp)
- [ ] .env.production VITE_API_BASE 为绝对 URL
- [ ] .env.production VITE_IMG_BASE 为绝对 URL
- [ ] orders/detail.vue onLoad 有 catch 设 error
- [ ] cart.vue onShow catch 设 error.value = true
- [ ] orders.vue onShow catch 设 error.value = true
- [ ] orders/detail.vue dining_mode 非 1 非 2 显示"未知"
- [ ] orders.vue activeLabel 不重复调用 find
- [ ] order.vue submit 有 catch
- [ ] index.vue changeDish 有 catch
