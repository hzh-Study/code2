# Checklist

## 后端
- [x] pay.py 的 prepay 和 pay_notify 不再是 async 函数
- [x] config.py 中 SECRET_KEY 使用默认值时输出强警告
- [x] order.py 中 user 为 None 时抛出 HTTPException 而非传空 openid
- [x] order.py 过期订单取消后查询仍能返回已取消订单
- [x] cart.py IntegrityError 回退路径有 None 安全检查
- [x] dish.py category_id 类型标注为 Optional[int]
- [x] schema 金额字段统一使用 round 或 Decimal

## 前端(admin-web)
- [x] dish/Manage.vue 使用 togglingId ref 而非 _toggling 属性
- [x] Login.vue 登录失败有用户可见的错误提示
- [x] dish/Manage.vue 上传和删除失败有错误提示
- [x] Dashboard.vue 使用 status 数字值而非中文字符串匹配

## 前端(uniapp)
- [x] config.js 生产环境 IMG_BASE 不回退到 localhost
- [x] cart.vue 下架菜品清理使用 Promise.allSettled
- [x] orders/detail.vue pay/cancel 有 catch 错误处理
- [x] orders.vue diningLabel 对未知值有 fallback