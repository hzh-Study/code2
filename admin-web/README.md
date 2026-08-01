# 拾味堂 管理后台（Vue3 + Vite + Element Plus）

## 启动

```bash
npm install
npm run dev      # http://localhost:5173
npm run build    # 产物 dist/
```

默认账号：**admin / admin123**

## 说明

- 开发环境通过 vite 代理把 `/api` 与 `/static` 转发到 `http://localhost:8000`，
  无需处理跨域；生产环境用 `.env.production` 里的 `VITE_API_BASE`。
- `src/api/request.js` 统一处理 `{code,msg,data}` 响应：`code!==0` 弹错误提示，
  401 自动清 token 并跳登录页。
- 路由守卫在 `src/router/index.js`，未登录访问受限页会重定向到 `/login`。

## 功能

| 页面 | 路径 | 能力 |
| --- | --- | --- |
| 数据看板 | `/dashboard` | 今日订单数/营业额、待出餐数、菜品总数、最近订单 |
| 分类管理 | `/categories` | 新增、编辑、排序、删除（分类下有菜品时禁止删除） |
| 菜品管理 | `/dishes` | 分页、按分类/名称筛选、增删改、上下架、图片上传 |
| 订单管理 | `/orders` | 分页、按状态/订单号筛选、订单详情、标记完成 |
