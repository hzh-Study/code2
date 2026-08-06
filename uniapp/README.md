# 拾味堂用户端（uni-app + Vue 3）

同一套源码构建微信小程序和 H5，覆盖首页推荐、分类点餐、购物车、堂食/打包带走、支付、订单和个人中心。

## 启动与构建

```bash
npm install

# H5 开发预览
npm run dev:h5 -- --host 127.0.0.1 --port 5174

# 微信小程序开发产物：dist/dev/mp-weixin
npm run dev:mp-weixin

# 生产构建
npm run build:h5
npm run build:mp-weixin
```

## 后端地址

地址由 Vite 环境变量读取，不需要修改源码中的常量。

| 场景 | 默认行为 |
| --- | --- |
| H5 开发 | 同源 `/api/v1`，Vite 代理至 `http://localhost:8000` |
| 小程序开发 | `http://127.0.0.1:8000/api/v1`，仅适合开发者工具模拟器 |
| H5 生产 | 未配置时使用部署站点同源 `/api/v1` |
| 小程序生产 | 必须配置完整的 HTTPS API 地址，否则界面会明确提示未配置 |

真机或生产配置示例（`uniapp/.env.local` 或部署环境变量）：

```dotenv
VITE_API_BASE=https://api.your-domain.com/api/v1
VITE_IMG_BASE=https://api.your-domain.com
```

微信公众平台还需配置 request 合法域名。真机不能使用 `127.0.0.1` 访问电脑上的后端。

## 页面

| 页面 | 路径 | 说明 |
| --- | --- | --- |
| 首页 | `pages/home/home` | 品牌、分类入口和真实热门菜图片 |
| 点餐 | `pages/index/index` | 分类切换、菜品列表与加购 |
| 购物车 | `pages/cart/cart` | 数量调整、删除、清空与结算 |
| 确认订单 | `pages/order/order` | 选择堂食或打包带走并发起支付 |
| 我的订单 | `pages/orders/orders` | 状态筛选、取消和重新支付 |
| 订单详情 | `pages/orders/detail` | 菜品快照、金额、状态与支付操作 |
| 个人中心 | `pages/profile/profile` | 用户信息、订单和点餐入口 |

打包为到店带走，不要求填写地址。

## 登录

应用按需调用 `uni.login` 换取 token。接口返回 401 时只自动重新登录并重放原请求一次，避免无限重试。

H5 开发环境会为每个浏览器生成独立开发 OpenID，避免不同浏览器共享购物车和订单。生产 H5 不会使用该开发回退。

## 支付

- 开发模式：后端返回 `dev: true`，前端调用模拟支付通知并刷新订单。
- 微信环境：调用 `uni.requestPayment`，成功后轮询后端订单状态，避免支付通知尚未落库时误报。
- 订单已创建但预支付参数暂不可用时，前端会跳转订单列表并提示稍后继续支付。

## 发布前检查

- 设置 DCloud Appid 和微信小程序 Appid。
- 设置生产 `VITE_API_BASE`，并配置微信合法域名与 HTTPS 证书。
- 执行 `npm run build:h5` 和 `npm run build:mp-weixin`。
- 使用真实微信支付沙箱/商户环境验证支付通知公网可达。
