<template>
  <view class="page" :class="{ 'has-actions': order?.status === 1 }">
    <UiState v-if="loading" type="loading" title="正在读取订单" />
    <UiState v-else-if="error" type="error" title="订单详情加载失败" description="请检查网络后重新尝试" action-text="重新加载" @action="retry" />
    <template v-else-if="order">
      <view class="status-panel" :class="`status-${order.status}`">
        <view class="status-mark"><view class="mark-core"></view></view>
        <view class="status-copy">
          <view class="status-title">{{ statusLabel(order.status) }}</view>
          <view class="status-hint">{{ statusHint(order.status) }}</view>
        </view>
      </view>

      <view class="section">
        <view class="section-title">菜品明细</view>
        <view v-for="item in order.items" :key="item.id" class="dish-line">
          <view class="dish-main"><view class="dish-name">{{ item.dish_name }}</view><view class="dish-unit">¥{{ money(item.price) }} × {{ item.quantity }}</view></view>
          <view class="dish-subtotal">¥{{ money(item.subtotal) }}</view>
        </view>
        <view class="total-line"><text>订单合计</text><text class="total-price"><text>¥</text>{{ money(order.total_amount) }}</text></view>
      </view>

      <view class="section info-section">
        <view class="section-title">订单信息</view>
        <view class="info-line"><text class="info-key">订单编号</text><text class="info-value order-no">{{ order.order_no }}</text></view>
        <view class="info-line"><text class="info-key">下单时间</text><text class="info-value">{{ order.created_at }}</text></view>
        <view class="info-line"><text class="info-key">用餐方式</text><text class="info-value">{{ order.dining_mode === 1 ? '堂食' : order.dining_mode === 2 ? '打包带走' : '未知' }}</text></view>
        <view v-if="order.address" class="info-line address-line"><text class="info-key">收货信息</text><text class="info-value">{{ order.address }}</text></view>
        <view v-if="order.paid_at" class="info-line"><text class="info-key">支付时间</text><text class="info-value">{{ order.paid_at }}</text></view>
      </view>

      <view v-if="order.status === 1" class="action-safe bottom-action-safe">
        <view class="action-bar bottom-action-bar">
          <view class="action secondary" :class="{ disabled: operating }" role="button" tabindex="0" :aria-disabled="operating" @click="cancel" @keydown.enter="cancel">取消订单</view>
          <view class="action primary" :class="{ disabled: operating }" role="button" tabindex="0" :aria-disabled="operating" aria-live="polite" @click="pay" @keydown.enter="pay">{{ operating ? '处理中…' : '去支付' }}</view>
        </view>
      </view>
    </template>
  </view>
</template>

<script setup>
import { ref } from 'vue'
import { onLoad } from '@dcloudio/uni-app'
import { cancelOrder, getOrderDetail, repayOrder } from '../../api'
import { loginIfNeeded } from '../../store/user'
import { payWithParams } from '../../utils/payment'
import UiState from '../../components/UiState.vue'

const order = ref(null)
const loading = ref(true)
const operating = ref(false)
const error = ref(false)
let orderId = null

function money(value) {
  return Number(value || 0).toFixed(2)
}

function statusLabel(status) {
  return { 1: '等待支付', 2: '后厨制作中', 3: '订单已完成', 4: '订单已取消' }[status] || '未知状态'
}

function statusHint(status) {
  return { 1: '请尽快完成支付，超时订单将自动取消', 2: '餐品正在制作，请留意取餐进度', 3: '感谢光临，期待下次再见', 4: '该订单已关闭，无需继续操作' }[status] || ''
}

async function load() {
  error.value = false
  try {
    order.value = await getOrderDetail(orderId)
  } catch (requestError) {
    error.value = true
  }
}

async function retry() {
  loading.value = true
  try {
    await loginIfNeeded().catch(() => undefined)
    await load()
  } finally {
    loading.value = false
  }
}

async function pay() {
  if (operating.value) return
  operating.value = true
  try {
    const result = await repayOrder(orderId)
    const outcome = await payWithParams({
      orderId,
      orderNo: result?.order_no || order.value?.order_no,
      payParams: result?.pay_params,
      onPaid: load
    })
    if (outcome === 'missing') {
      uni.showToast({ title: '支付参数异常', icon: 'none' })
    }
  } catch {
    await load()
  } finally {
    operating.value = false
  }
}

async function cancel() {
  if (operating.value) return
  const confirmed = await new Promise((resolve) => uni.showModal({
    title: '取消订单',
    content: '确定取消当前订单吗？',
    confirmText: '取消订单',
    confirmColor: '#b42318',
    success: (result) => resolve(result.confirm),
    fail: () => resolve(false)
  }))
  if (!confirmed) return
  operating.value = true
  try {
    await cancelOrder(orderId)
    uni.showToast({ title: '订单已取消', icon: 'none' })
    await load()
  } catch (e) {
    await load()
  } finally {
    operating.value = false
  }
}

onLoad(async (options) => {
  orderId = options?.id
  if (!orderId) {
    uni.showToast({ title: '订单参数错误', icon: 'none' })
    setTimeout(() => uni.navigateBack(), 800)
    return
  }
  try {
    await loginIfNeeded()
    await load()
  } catch (e) {
    error.value = true
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.page { min-height: 100vh; padding: 12px 12px 24px; box-sizing: border-box; background: var(--c-bg); }
.page.has-actions { padding-bottom: calc(96px + env(safe-area-inset-bottom)); }
.status-panel { min-height: 94px; padding: 18px; box-sizing: border-box; display: flex; align-items: center; gap: 14px; border-radius: var(--r-lg); background: var(--c-text); color: #fff; }
.status-mark { width: 44px; height: 44px; flex-shrink: 0; display: flex; align-items: center; justify-content: center; border: 2px solid currentColor; border-radius: 50%; }
.mark-core { width: 12px; height: 12px; border-radius: 50%; background: currentColor; }
.status-1 { color: #ffd38c; }
.status-2 { color: #ff9b70; }
.status-3 { color: #8fd4a6; }
.status-4 { color: #c8c3bd; }
.status-copy { color: #fff; }
.status-title { font-size: var(--font-lg); font-weight: 800; }
.status-hint { margin-top: 4px; color: #c8c3bd; font-size: 11px; line-height: 17px; }
.section { margin-top: 12px; padding: 18px 16px 10px; border: 1px solid var(--c-border-light); border-radius: var(--r-lg); background: var(--c-bg-card); }
.section-title { margin-bottom: 8px; font-size: var(--font-md); font-weight: 800; }
.dish-line { min-height: 58px; display: flex; align-items: center; justify-content: space-between; border-bottom: 1px solid var(--c-border-light); }
.dish-main { min-width: 0; flex: 1; }
.dish-name { overflow: hidden; color: var(--c-text); font-size: var(--font-sm); font-weight: 700; text-overflow: ellipsis; white-space: nowrap; }
.dish-unit { margin-top: 3px; color: var(--c-text-placeholder); font-size: 10px; }
.dish-subtotal { margin-left: 12px; color: var(--c-text); font-size: var(--font-sm); font-weight: 700; }
.total-line { min-height: 62px; display: flex; align-items: center; justify-content: space-between; color: var(--c-text); font-size: var(--font-sm); font-weight: 700; }
.total-price { color: var(--c-primary); font-size: 22px; font-weight: 800; }
.total-price text { margin-right: 2px; font-size: var(--font-xs); }
.info-section { padding-bottom: 12px; }
.info-line { min-height: 44px; display: flex; align-items: center; justify-content: space-between; }
.info-key { flex-shrink: 0; color: var(--c-text-placeholder); font-size: var(--font-xs); }
.info-value { margin-left: 18px; color: var(--c-text-secondary); font-size: var(--font-xs); text-align: right; word-break: break-all; }
.order-no { font-family: 'SFMono-Regular', Consolas, monospace; }
.address-line { align-items: flex-start; padding: 10px 0; }
.action-bar { min-height: 76px; gap: 10px; }
.action { height: 48px; display: flex; align-items: center; justify-content: center; border-radius: var(--r-md); font-size: var(--font-sm); font-weight: 700; }
.action.secondary { min-width: 112px; border: 1px solid var(--c-border); color: var(--c-text-secondary); }
.action.primary { flex: 1; background: var(--c-primary); color: #fff; }
.action.disabled { background: var(--c-bg-disabled); color: var(--c-text-disabled); }
.action:active { opacity: .72; }
</style>
