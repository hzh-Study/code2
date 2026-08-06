# 全面代码审查修复 Spec

## Why
对餐厅堂食外卖系统进行全面审查后发现多处 bug、安全漏洞和代码质量问题，需系统性修复以确保项目能正常运行。

## What Changes
- 修复 pay.py 中 async 声明与同步 DB 操作冲突（去掉 async）
- 修复 SECRET_KEY 弱默认值安全漏洞
- 修复后端运行时 bug（openid 空值、过期订单丢数据、cart 并发安全）
- 修复前端生产环境 IMG_BASE 回退到 localhost
- 修复前端静默吞错（登录失败无提示等）
- 修复前端代码质量问题
- 清理死代码和未使用的配置

## Impact
- 后端 API、管理后台、客户端小程序均受影响

## 完整问题清单

### 后端问题
- B1 [严重] backend/app/api/client/pay.py:36,56 — async+同步DB阻塞事件循环
- B2 [严重] backend/app/utils/security.py:7 — SECRET_KEY 弱默认值安全漏洞
- B3 [中高] backend/app/api/client/order.py:69-72 — user为None传空openid给微信
- B4 [中高] backend/app/api/client/order.py:90-102 — 过期订单取消后重查丢数据
- B5 [中高] backend/app/api/client/cart.py:52-56 — IntegrityError回退无None检查
- B6 [中] backend/app/api/client/dish.py:34 — category_id类型标注矛盾
- B7 [中] backend/app/schemas/ — 金额字段用float而非Decimal，精度风险
- B8 [低] backend/app/api/admin/upload.py:16 — 未校验上传文件是否为空
- B9 [低] backend/sql/init.sql — categories.name无唯一约束
- B10 [低] backend/seed.py:11 — 图片路径硬编码为2026/07

### 前端问题(admin-web)
- F1 [高] admin-web/src/views/dish/Manage.vue:170-177 — _toggling直接挂载到行数据，响应性反模式
- F2 [中] admin-web/src/views/Login.vue:68 — 登录失败catch为空，无用户反馈
- F3 [中] admin-web/src/views/dish/Manage.vue:150,192 — 上传/删除失败catch为空
- F4 [中] admin-web/src/views/Dashboard.vue:103-109 — 状态分类依赖中文字符串匹配
- F5 [低] admin-web/src/layouts/DefaultLayout.vue:75 — username非ref，computed不会更新

### 前端问题(uniapp)
- U1 [高] uniapp/src/config.js:5 — IMG_BASE生产环境回退到localhost
- U2 [中] uniapp/src/pages/cart/cart.vue:68-69 — 下架菜品串行删除且错误未处理
- U3 [中] uniapp/src/pages/orders/orders.vue:76-78 — itemCount依赖字符串解析
- U4 [中] uniapp/src/pages/orders/detail.vue:85-126 — pay/cancel错误未catch
- U5 [低] uniapp/src/pages/orders/orders.vue:72-74 — diningLabel默认值不严谨
- U6 [低] uniapp/src/components/QuantityStepper.vue — modelValue与change事件不匹配