# 第5轮 Bug 修复 Spec

## Why
对项目再次全面审计后发现 29 处问题，含第4轮 N5 未彻底修复的残留、3 项高危问题（分类改名 500、订单重试精度不一致、小程序生产配置不可用），以及大量中低优先级问题。本轮系统性修复全部问题。

## What Changes
- 修复 admin/category.py update_category 未查重导致 500（R1）
- 修复 client/order.py 重试路径 subtotal 用 float（R2，N5 彻底完成）
- 修复 uniapp .env.production 相对路径在小程序不可用（R3）
- 修复 detail.vue/cart.vue/orders.vue 缺 catch 导致空白页或误导提示（R4-R6）
- 修复 client/order.py 重试路径 db.flush() 未被 try/except 保护（R7）
- 修复 client/order.py _prepay 失败后用户陷入死局（R8）
- 修复 admin/dish.py 删除菜品静默清空购物车（N25）
- 修复 client/order.py 菜品被删除提示"已下架"误导（N27）
- 迁移 wechat.py MD5 签名到 HMAC-SHA256（N15）
- 修复 admin-web request.js 401 用 window.location.hash 跳转（N18）
- 修复 dish/Manage.vue toggleDish 传无用第二参数（N19）
- 修复 order.js completeOrder 与后端 body 契约不一致（N20）
- 清理 client/order.py 函数内重复导入（N21）
- 修复 wechat.py 内联 __import__("time")（N22）
- 修复 detail.vue dining_mode 无 fallback（N23）
- 修复 orders.vue activeLabel 重复 find（N24）
- 修复 config.py DEV_MODE 隐式推断（N26）
- 修复 uniapp 多处 async 无 catch（N28）
- 清理 main.py UPLOAD_DIR 重复 makedirs（N30）
- 修复 pay.py WX_SUCCESS 单例 Response 竞态（R9）
- 优化 client/order.py _serialize_order N+1 查询（R10）
- 强化 config.py SECRET_KEY 生产环境强制校验（R11）
- admin/auth.py 登录增加简单频率限制（R12）
- admin-web resolveImg 生产环境配置（R13）
- client/cart.py update_cart 校验菜品在售状态（R14）
- 限制 order address 长度（R15）
- 修复 admin-web 多处 load() 未 await（R16）
- **BREAKING** wechat.py 签名算法 MD5→HMAC-SHA256

## Impact
- 后端 API、管理后台、客户端小程序均受影响
- 涉及微信支付签名算法变更

## ADDED Requirements

### Requirement: 分类改名查重
系统 SHALL 在 update_category 时检查新名称是否与其他分类冲突，冲突时返回 400。

#### Scenario: 改名为已存在名称
- **WHEN** 管理员将分类 A 改名为已存在的分类 B 的名称
- **THEN** 返回 400，detail 为"分类名已存在"

### Requirement: 订单重试路径精度一致
系统 SHALL 在 IntegrityError 重试路径中使用与主路径相同的 Decimal 计算方式。

#### Scenario: order_no 碰撞重试
- **WHEN** 创建订单时 order_no 碰撞触发 IntegrityError 重试
- **THEN** 重试路径的 subtotal 与 total 使用 Decimal 计算

### Requirement: 小程序生产环境绝对 URL
系统 SHALL 在 uniapp 生产环境配置绝对 API_BASE 与 IMG_BASE。

#### Scenario: 生产构建
- **WHEN** 执行生产构建
- **THEN** API_BASE 与 IMG_BASE 均为 https 开头的绝对 URL

### Requirement: 微信支付 HMAC-SHA256 签名
系统 SHALL 使用 HMAC-SHA256 算法对微信支付请求签名。

#### Scenario: 签名生成
- **WHEN** 调用 build_pay_params 生成支付参数
- **THEN** signType 为 "HMAC-SHA256"

### Requirement: 预下单失败友好处理
系统 SHALL 在订单创建后预下单失败时返回订单信息与 null pay_params。

#### Scenario: 微信接口超时
- **WHEN** 订单已创建但 _prepay 调用微信接口超时
- **THEN** 返回 200 与 {order_id, order_no, pay_params: null}

### Requirement: 登录频率限制
系统 SHALL 对管理员登录接口增加频率限制，单 IP 60 秒内最多 5 次失败尝试。

#### Scenario: 暴力破解防护
- **WHEN** 同一 IP 在 60 秒内第 6 次尝试登录
- **THEN** 返回 429

### Requirement: 购物车更新校验菜品在售
系统 SHALL 在 update_cart 时检查菜品在售状态，下架菜品返回 400。

#### Scenario: 修改下架菜品数量
- **WHEN** 用户尝试修改已下架菜品的购物车数量
- **THEN** 返回 400

## MODIFIED Requirements

### Requirement: 订单地址长度
CreateOrderRequest.address SHALL 限制最大 255 字符。

### Requirement: SECRET_KEY 生产环境校验
生产环境检测到默认 SECRET_KEY 时 SHALL 抛 RuntimeError。

### Requirement: 订单列表查询性能
list_orders SHALL 批量预加载 OrderItem 与 Dish。

### Requirement: 错误状态显示
uniapp 各页面 onLoad/onShow 失败时 SHALL 设置 error 状态。

## REMOVED Requirements
无
