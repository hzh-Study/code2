# 拾味堂 用户端（uni-app + Vue3）

一套代码同时输出 **微信小程序** 与 **H5**。

## 启动

```bash
npm install

# H5 预览（推荐用浏览器手机模式查看）
npm run dev:h5 -- --port 5174

# 微信小程序：产物在 dist/dev/mp-weixin，用微信开发者工具「导入项目」打开
npm run dev:mp-weixin
```

构建：`npm run build:h5` / `npm run build:mp-weixin`

## 后端地址配置

`src/config.js`：

```js
export const BASE_URL = ''   // H5 留空走 vite 代理
```

- **H5**：留空即可，vite 会把 `/api`、`/static` 代理到 `http://localhost:8000`
- **微信小程序**：必须改成完整地址，例如 `http://192.168.1.100:8000`
  （小程序无代理能力；真机调试需用局域网 IP，正式发布需 HTTPS 域名并在
  微信公众平台配置 request 合法域名）

## 页面

| 页面 | 路径 | 说明 |
| --- | --- | --- |
| 点餐 | `pages/index/index` | 左侧分类 + 右侧菜品，加购、底部购物车悬浮条 |
| 购物车 | `pages/cart/cart` | 增减数量、删除、清空、去结算 |
| 确认订单 | `pages/order/order` | 堂食/打包切换、打包填地址、提交并拉起支付 |
| 我的订单 | `pages/orders/orders` | 全部/待支付/待出餐/已完成 分类查看 |
| 订单详情 | `pages/orders/detail` | 菜品快照、金额、状态、继续支付/取消 |

## 登录

App 启动时自动调用 `uni.login` 拿 code 换取 token 并存本地。
后端开发模式下 code 直接作为 openid，无需真实微信环境即可在 H5 调试全流程。

## 支付

调用 `/client/pay/prepay` 拿参数：
- 生产：调 `uni.requestPayment` 拉起微信支付
- 开发模式（后端返回 `dev:true`）：直接调用 `/client/pay/notify` 模拟支付成功，
  便于在浏览器里跑通「下单 → 支付 → 待出餐」完整链路
