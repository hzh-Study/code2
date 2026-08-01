# 修复黑白单调主题 Spec

## Why
上一轮美化后管理后台侧边栏过深（`#1e1e2d` 近乎纯黑）、用户端底部栏也是深黑（`#2b2b2b`），整体呈现"黑白灰"冷淡风格，与餐厅"拾味堂"温暖、食欲感的品牌调性不符。需要换用暖色调、有层次感的配色，让页面更有温度和辨识度。

## What Changes
- **管理后台**：侧边栏从深黑改为暖色调深棕色/深橙色渐变，保持与品牌色 `#e85d2c` 的协调；全局背景、卡片、表格等恢复温暖的米白/奶油色系。
- **用户端**：购物车底部栏从纯黑改为品牌色渐变或暖色深底；整体色调更贴近餐饮暖色系。
- **两套前端**：确保品牌色（橙红 `#e85d2c`）作为主色调贯穿，辅以米白、奶油、浅棕等暖色中性色，避免大面积黑白灰。
- 不修改任何业务逻辑、路由、API 调用。

## Impact
- Affected specs: 前端视觉主题
- Affected code: `admin-web/src/styles/variables.scss`、`admin-web/src/layouts/DefaultLayout.vue`、`uniapp/src/App.vue`、`uniapp/src/pages/index/index.vue`、`uniapp/src/pages/cart/cart.vue`、`uniapp/src/pages/order/order.vue`、`uniapp/src/pages/orders/orders.vue`

## ADDED Requirements
（无，属于视觉修正）

## MODIFIED Requirements
### Requirement: 餐厅品牌视觉调性
管理后台与用户端的整体配色 SHALL 符合中式餐厅温暖、有食欲感的品牌调性，侧边栏和底部栏不再使用纯黑/深黑。

## REMOVED Requirements
（无）

## Acceptance Criteria
- 管理后台侧边栏为暖色调（棕色/深橙渐变），不再接近纯黑。
- 用户端购物车栏/底部操作栏为品牌橙色或暖色，不再使用纯黑。
- 两套前端均可构建通过。
- 功能完整可用。