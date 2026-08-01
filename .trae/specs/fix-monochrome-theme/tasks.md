# Tasks
- [x] Task 1: 管理后台暖色调重配
  - [x] SubTask 1.1: 修改 `variables.scss` 中 `--sidebar-bg` 从 `#1e1e2d` 改为暖色调深棕色渐变
  - [x] SubTask 1.2: 调整全局背景、边框、阴影等中性色为暖色系（米白/奶油/浅棕）
  - [x] SubTask 1.3: 调整 DefaultLayout 侧边栏样式适配新配色
  - [x] SubTask 1.4: 确认 Dashboard、分类、菜品、订单页面视觉协调
- [x] Task 2: 用户端暖色调重配
  - [x] SubTask 2.1: 修改 `App.vue` 全局变量，购物车栏从纯黑改为品牌橙渐变
  - [x] SubTask 2.2: 调整首页、购物车、下单、订单页面的底栏和重点元素配色
- [x] Task 3: 构建验证
  - [x] SubTask 3.1: `admin-web` 执行 `npm run build` 通过
  - [x] SubTask 3.2: `uniapp` 执行 `npm run build:h5` 通过

# Task Dependencies
- Task 2 可与 Task 1 并行
- Task 3 依赖 Task 1 和 Task 2 完成