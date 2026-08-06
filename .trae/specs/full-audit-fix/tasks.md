# Tasks

## 后端修复
- [x] Task 1: 修复 pay.py async 阻塞问题(B1)
  - 将 prepay 改为同步；pay_notify 通过依赖注入异步读取body，路由本身同步
- [x] Task 2: 添加 SECRET_KEY 安全检查(B2)
  - 在 config.py 中检测默认 SECRET_KEY 并输出警告
- [x] Task 3: 修复 order.py openid 空值和过期订单查询(B3,B4)
  - user为None时抛出业务错误
  - 过期订单取消后查询包含已取消订单
- [x] Task 4: 修复 cart.py IntegrityError 回退的 None 检查(B5)
  - 在回退查询后加 None 判断
- [x] Task 5: 修复 dish.py 类型标注(B6)
  - category_id 改为 int | None
- [x] Task 6: 修复 schema 金额类型(B7)
  - 金额字段改用 Decimal

## 前端修复(admin-web)
- [x] Task 7: 修复 dish Manage _toggling 响应性问题(F1)
  - 改用独立 ref 管理 togglingId
- [x] Task 8: 修复多处静默吞错(F2,F3)
  - Login/dish/category/order 的 catch 中添加错误提示
- [x] Task 9: 修复 Dashboard 状态分类(F4)
  - 改用 status 数字枚举值判断

## 前端修复(uniapp)
- [x] Task 10: 修复 config.js IMG_BASE 回退问题(U1)
  - || 改为 ??，空字符串不触发 fallback
- [x] Task 11: 修复 cart 菜品清理和 detail 错误处理(U2,U4)
  - 串行改并行，添加 catch 处理
- [x] Task 12: 修复 orders.vue itemCount 和 diningLabel(U3,U5)
  - 增强字符串解析容错

# Task Dependencies
- Task 3 依赖 Task 1（同文件 order.py）
- Task 4-6 与 Task 1-3 无依赖，可并行
- Task 7-12 前端任务之间无依赖，可并行