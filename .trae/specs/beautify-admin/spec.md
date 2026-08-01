# 管理后台全页面美化 Spec

## Why
当前管理后台已有基础的 CSS 变量体系和品牌色（橙 #e85d2c），但整体视觉层次平淡、空间利用保守、卡片与表格缺乏视觉冲击力。登录页虽有动画但背景单调，看板统计卡信息密度低，管理页面的表格和弹窗设计偏常规。需要全面提升视觉品质，打造有辨识度的餐饮管理后台。

## What Changes
- **设计系统增强**：扩展 CSS 变量（渐变色、玻璃态、装饰性图案），新增全局工具类
- **登录页**：增加品牌装饰图案、优化卡片布局与输入框交互
- **侧边栏/头部**：增加品牌装饰线、优化菜单项图标与文字间距
- **看板页**：统计卡片增加趋势指示、背景装饰；订单表格优化行悬停与状态展示
- **分类管理**：表格增加行操作区美化、空状态引导
- **菜品管理**：卡片增加图片遮罩渐变、价格标签美化、筛选区增加视觉分组
- **订单管理**：订单号可点击跳详情、状态筛选标签化、详情弹窗美化

## Impact
- Affected code: `admin-web/src/styles/variables.scss`, `admin-web/src/views/Login.vue`, `admin-web/src/layouts/DefaultLayout.vue`, `admin-web/src/views/Dashboard.vue`, `admin-web/src/views/category/Manage.vue`, `admin-web/src/views/dish/Manage.vue`, `admin-web/src/views/order/Manage.vue`
- 不修改任何 API 调用、路由、权限、数据模型

## Requirements

### Requirement: 视觉层次提升
- 系统 SHALL 通过阴影、间距、圆角的层次化使用建立清晰的视觉层级
- 统计卡片 SHALL 具有品牌色渐变背景装饰
- 表格行悬停 SHALL 有流畅的过渡效果

### Requirement: 交互反馈增强
- 所有可操作元素 SHALL 有明确的悬停/点击状态
- 空状态 SHALL 有引导性提示
- 加载态 SHALL 有骨架屏或动画

### Requirement: 品牌一致性
- 品牌橙 #e85d2c SHALL 作为主色调贯穿所有页面
- 侧边栏暖棕渐变 SHALL 与品牌色协调
- 所有页面 SHALL 使用统一的 CSS 变量体系

## Acceptance Criteria
- 登录页视觉吸引力提升
- 看板页数据展示层次分明
- 管理页面表格美观易读
- 所有弹窗设计统一精致
- `npm run build` 构建通过
- 功能路径完整可用（登录、看板、分类/菜品/订单 CRUD）
