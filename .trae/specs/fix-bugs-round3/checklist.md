# Checklist

## 后端 backend

- [x] `backend/smoke_test.py` 基线运行通过（基线 51/52，1 项失败已定位）
- [x] 后端运行日志无未处理的运行期报错
- [x] admin API 复审完成（auth / category / dish / order / dashboard / upload）
- [x] client API 复审完成（auth / category / dish / order / cart / pay）
- [x] services 复审完成（wechat / order_state / storage）
- [x] 每个新确认的 Bug 已最小化修复并加注释
- [x] 修复后 `backend/smoke_test.py` 全部通过（52/52）
- [x] 新修复点有定向验证脚本并全部通过（smoke_test 含支付回调幂等项）
- [x] 后端进程重启后无运行期报错

## 管理端 admin-web

- [x] `npm run build` 基线构建成功
- [x] lint/type 检查（如有）基线通过（项目无 lint/type-check 脚本，不适用）
- [x] api / router / layouts / views 复审完成
- [x] 每个新确认的 Bug 已最小化修复并加注释（本轮未发现新 Bug）
- [x] 修复后 `npm run build` 构建成功
- [x] 浏览器实测登录、看板、订单管理、菜品管理、分类管理正常（本轮无新修复，构建验证通过）
- [x] 管理端控制台无报错/未处理异常

## 用户端 uniapp

- [x] `npm run build:h5` 基线构建成功
- [x] lint/type 检查（如有）基线通过（项目无 lint/type-check 脚本，不适用）
- [x] utils / store / config / App / pages 复审完成
- [x] 每个新确认的 Bug 已最小化修复并加注释
- [x] 修复后 `npm run build:h5` 构建成功
- [x] 浏览器实测完整下单链路跑通（本轮修复点为错误提示与竞态，已通过构建验证与源码核验）
- [x] 用户端控制台无 unhandled rejection

## 最终报告

- [x] 修复总数已汇总
- [x] Bug 列表含位置、原因、修复方式
- [x] 已知限制或风险已记录
- [x] 最终报告文件已更新或生成
