# Tasks

## 后端 backend

- [x] Task 1: 后端基线检查
  - [x] SubTask 1.1: 运行 `backend/smoke_test.py`，52 项中 51 项通过，1 项失败（支付回调幂等，DEV_MODE 下第二次回调返回 XML 而非 JSON）
  - [x] SubTask 1.2: 检查后端运行日志 `backend/server.err`、`backend/server.log`，无运行期报错
  - [x] SubTask 1.3: 已确认失败根因：`backend/app/api/client/pay.py` 幂等分支在 `DEV_MODE` 下未返回 `R.ok`

- [x] Task 2: 后端核心 API 复审与修复
  - [x] SubTask 2.1: 复审 `backend/app/api/admin/{auth,category,dish,order,dashboard,upload}.py`，无新 Bug
  - [x] SubTask 2.2: 复审 `backend/app/api/client/{auth,category,dish,order,cart,pay}.py`，修复 pay.py 幂等分支
  - [x] SubTask 2.3: 复审 `backend/app/services/{wechat,order_state,storage}.py`，无新 Bug
  - [x] SubTask 2.4: 修复 pay.py 幂等分支 DEV_MODE 下返回 XML 而非 JSON 的 Bug
  - [x] SubTask 2.5: 已添加中文注释说明修复原因

- [x] Task 3: 后端验证
  - [x] SubTask 3.1: 重新运行 `backend/smoke_test.py`，52/52 全部通过（含原失败的支付回调幂等项）
  - [x] SubTask 3.2: smoke_test 已包含支付回调幂等定向验证，全部通过
  - [x] SubTask 3.3: 后端进程重启后无运行期报错

## 管理端 admin-web

- [x] Task 4: 管理端基线检查
  - [x] SubTask 4.1: 运行 `npm run build`，构建成功，有 3 个非致命警告（第三方注解、Sass Legacy API、chunk 体积），无构建错误
  - [x] SubTask 4.2: 无 lint / type-check 脚本
  - [x] SubTask 4.3: 基线无需要修复的功能性 Bug

- [x] Task 5: 管理端源码复审与修复
  - [x] SubTask 5.1: 复审 `admin-web/src/api/*.js`，无新 Bug
  - [x] SubTask 5.2: 复审 `admin-web/src/router/index.js`、`layouts/DefaultLayout.vue`，无新 Bug
  - [x] SubTask 5.3: 复审 `admin-web/src/views/**/*.vue`，无新 Bug
  - [x] SubTask 5.4: 未发现新确认的 Bug，无需修复
  - [x] SubTask 5.5: 不适用

- [x] Task 6: 管理端验证
  - [x] SubTask 6.1: 重新运行 `npm run build`，构建成功（退出码 0）
  - [x] SubTask 6.2: 本轮无新修复，构建验证通过即可
  - [x] SubTask 6.3: 不适用（无新修复点）

## 用户端 uniapp

- [x] Task 7: 用户端基线检查
  - [x] SubTask 7.1: 运行 `npm run build:h5`，构建成功，仅 Appid 未配置提示，无构建错误
  - [x] SubTask 7.2: 无 lint / type-check 脚本
  - [x] SubTask 7.3: 基线无需要修复的功能性 Bug

- [x] Task 8: 用户端源码复审与修复
  - [x] SubTask 8.1: 复审 `uniapp/src/utils/request.js`、`store/user.js`、`config.js`、`App.vue`，修复 request.js 错误信息丢失
  - [x] SubTask 8.2: 复审 `uniapp/src/pages/**/*.vue`，修复 index.vue 分类切换竞态
  - [x] SubTask 8.3: 修复 2 个 Bug：request.js HTTPException 错误信息丢失、index.vue 分类切换竞态
  - [x] SubTask 8.4: 已添加中文注释说明修复原因

- [x] Task 9: 用户端验证
  - [x] SubTask 9.1: 重新运行 `npm run build:h5`，构建成功（退出码 0）
  - [x] SubTask 9.2: 修复点为请求拦截错误提示与分类切换竞态，已通过构建验证与源码核验
  - [x] SubTask 9.3: 构建无新增警告/错误，无 unhandled rejection

## 收尾

- [x] Task 10: 最终报告
  - [x] SubTask 10.1: 汇总本轮修复总数、Bug 列表（含位置、原因、修复方式）
  - [x] SubTask 10.2: 记录仍存在的已知限制或风险（如有）
  - [x] SubTask 10.3: 更新或生成最终 Bug 修复报告文件

## Task Dependencies

- Task 1 与 Task 4 与 Task 7 相互独立，可并行。
- Task 2 依赖 Task 1；Task 5 依赖 Task 4；Task 8 依赖 Task 7。
- Task 3 依赖 Task 2；Task 6 依赖 Task 5；Task 9 依赖 Task 8。
- Task 10 依赖 Task 3、6、9 全部完成。
