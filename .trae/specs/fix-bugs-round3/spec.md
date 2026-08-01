# 持续 Bug 排查与修复（第三轮）Spec

## Why

前两轮已修复大量后端逻辑、支付安全、前端类型安全与并发竞态问题。本次按「发现 → 修复 → 验证」的循环对三端源码（backend / admin-web / uniapp）做持续复审与实测，目标是消除剩余明显 Bug，确保核心业务流程、边界条件、异常处理、资源释放、并发安全、权限校验等均无缺陷。

## What Changes

### 后端 backend（Python / FastAPI）

- 运行测试套件与静态检查，确认当前基线状态。
- 复审核心 API（admin/client 的 auth、category、dish、order、cart、pay、upload）与 services（wechat、order_state、storage）。
- 重点检查：空值/undefined、边界条件、异常处理、事务一致性、权限校验、并发安全、资源释放、除零/越界、类型转换。
- 修复所有新确认的 Bug，仅做最小改动并保留原有风格。

### 管理端 admin-web（Vue 3）

- 运行 build / lint，确认基线。
- 复审 views、api、router、layouts，重点检查：响应体空值、金额/分页逻辑、401/权限跳转、上传校验、表单提交防抖。
- 修复新确认的 Bug。

### 用户端 uniapp（UniApp）

- 运行 build（H5）确认基线。
- 复审 pages、utils、store、config，重点检查：环境变量、请求拦截、登录并发、下单/购物车、金额显示、页面参数。
- 修复新确认的 Bug。

### 验证

- 后端：`backend/smoke_test.py` 全部通过；新增/修改的定向测试通过。
- 管理端：生产构建成功，浏览器实测无报错。
- 用户端：H5 dev 构建成功，完整下单链路实测通过。

## Impact

- **Affected specs**: `fix-bugs-round2`、`BUG_FIX_REPORT.md`
- **Affected code**: 视本轮实际发现的 Bug 而定，可能涉及 backend/app、admin-web/src、uniapp/src
- **Breaking changes**: 无预期破坏性变更；若有会在对应任务中单独标注

## ADDED Requirements

### Requirement: 持续 Bug 发现

#### Scenario: 测试与静态检查基线
- **WHEN** 项目测试套件或静态检查工具运行
- **THEN** 失败/告警项作为首轮待修复 Bug 来源

#### Scenario: 源码复审发现新 Bug
- **WHEN** 阅读核心业务流程、边界条件、异常处理、并发安全等代码
- **THEN** 确认根因后纳入修复列表

### Requirement: 持续 Bug 修复

#### Scenario: 修复已确认 Bug
- **WHEN** 已定位某个 Bug 的根因
- **THEN** 只修改该 Bug 相关文件，改动最小，保留原有风格，并添加必要注释

### Requirement: 持续 Bug 验证

#### Scenario: 验证单个修复
- **WHEN** 修复某个 Bug 后
- **THEN** 重新运行相关测试或手动验证，确认 Bug 已修复且无回归

#### Scenario: 结束循环
- **WHEN** 测试全部通过且连续两轮未发现新 Bug，或已完整审查主要代码路径
- **THEN** 停止循环并输出最终报告

## MODIFIED Requirements

无

## REMOVED Requirements

无
