# Tasks
- [x] Task 1: Admin-web 主题与全局基础升级
  - [x] SubTask 1.1: 定义色板、字体层级、间距与圆角变量（基于 Element Plus 主题）
  - [x] SubTask 1.2: 优化全局 reset/基础样式、容器背景、卡片阴影与边框风格
  - [x] SubTask 1.3: 统一按钮、输入框、弹窗等高频组件的视觉权重与交互反馈
- [x] Task 2: Admin-web 页面重构（登录、侧边栏、看板、管理页）
  - [x] SubTask 2.1: 重构登录页布局与品牌感
  - [x] SubTask 2.2: 重构 DefaultLayout 的侧边栏与顶部栏样式
  - [x] SubTask 2.3: 优化 Dashboard 卡片与数据展示层次
  - [x] SubTask 2.4: 优化菜品/分类/订单管理页的表格密度、筛选区与操作按钮
- [x] Task 3: UniApp 用户端主题与交互提升
  - [x] SubTask 3.1: 建立移动端视觉变量与基础排版规则
  - [x] SubTask 3.2: 优化首页商品卡片、分类导航与图片比例
  - [x] SubTask 3.3: 提升购物车与下单页的触控热区、按钮层级与空状态
  - [x] SubTask 3.4: 优化订单列表/详情的状态流转与可读性
- [x] Task 4: 一致性与回归验证
  - [x] SubTask 4.1: 走通管理后台功能流程，确认样式改动不影响功能
  - [x] SubTask 4.2: 走通用户端功能流程，确认样式改动不影响功能

# Task Dependencies
- Task 2 依赖 Task 1（管理员端主题基础）
- Task 3 可与 Task 1/2 并行，但需最终与整体品牌一致
- Task 4 依赖 Task 1~3 完成