import { getOrderDetail, simulatePay } from '../api'

function delay(milliseconds) {
  return new Promise((resolve) => setTimeout(resolve, milliseconds))
}

export async function waitForPayment(orderId, attempts = 8) {
  let order = null
  for (let attempt = 0; attempt < attempts; attempt += 1) {
    order = await getOrderDetail(orderId)
    if (Number(order?.status) !== 1) return order
    if (attempt < attempts - 1) await delay(500 + attempt * 150)
  }
  return order
}

/**
 * 根据后端返回的 pay_params 完成支付（含开发模式模拟回调）。
 * @returns {'paid'|'submitted'|'missing'|'failed'}
 */
export function payWithParams({ orderId, orderNo, payParams, onPaid }) {
  return new Promise((resolve) => {
    if (!payParams) {
      resolve('missing')
      return
    }
    if (payParams.dev) {
      simulatePay(orderNo)
        .then(async () => {
          if (onPaid) await onPaid()
          uni.showToast({ title: '支付成功', icon: 'success' })
          resolve('paid')
        })
        .catch(() => {
          resolve('failed')
        })
      return
    }
    uni.requestPayment({
      ...payParams,
      success: async () => {
        try {
          const latestOrder = await waitForPayment(orderId)
          const paid = [2, 3].includes(Number(latestOrder?.status))
          uni.showToast({
            title: paid ? '支付成功' : '支付已提交，状态稍后更新',
            icon: paid ? 'success' : 'none'
          })
          if (onPaid) await onPaid()
          resolve(paid ? 'paid' : 'submitted')
        } catch {
          resolve('failed')
        }
      },
      fail: () => {
        uni.showToast({ title: '支付未完成', icon: 'none' })
        resolve('failed')
      }
    })
  })
}
