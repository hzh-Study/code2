<template>
  <view class="page">
    <scroll-view class="tabs" scroll-x>
      <view class="tabs-inner">
        <view v-for="tab in tabs" :key="String(tab.value)" class="tab" :class="{ active: active === tab.value }" role="tab" tabindex="0" :aria-selected="active === tab.value" @click="switchTab(tab.value)" @keydown.enter="switchTab(tab.value)">{{ tab.label }}</view>
      </view>
    </scroll-view>

    <UiState v-if="loading" type="loading" title="正在读取订单" />
    <UiState v-else-if="error" type="error" title="订单加载失败" description="请检查网络后重新尝试" action-text="重新加载" @action="retry" />
    <UiState v-else-if="!orders.length" :title="`暂无${activeLabel}订单`" description="完成点餐后，订单进度会展示在这里" action-text="去点餐" @action="goOrdering" />

    <view v-else class="order-list">
      <view v-for="order in orders" :key="order.id" class="order-card" role="button" tabindex="0" :aria-label="`查看订单${order.order_no}`" @click="goDetail(order.id)" @keydown.enter="goDetail(order.id)">
        <view class="order-head">
          <view><view class="order-no">{{ order.order_no }}</view><view class="order-time">{{ order.created_at }}</view></view>
          <view class="status-badge" :class="`status-${order.status}`">{{ statusLabel(order.status) }}</view>
        </view>
        <view class="order-content">
          <image v-if="order.thumbnail" class="thumbnail" :src="imgUrl(order.thumbnail)" mode="aspectFill" />
          <view v-else class="thumbnail no-image">拾味堂</view>
          <view class="order-summary">
            <view class="detail">{{ order.detail || '订单商品' }}</view>
            <view class="meta"><text>{{ diningLabel(order.dining_mode) }}</text><text>{{ itemCount(order) }} 件商品</text></view>
          </view>
        </view>
        <view class="order-foot">
          <view class="total-label">订单金额 <text>¥{{ money(order.total_amount) }}</text></view>
          <view v-if="order.status === 1" class="actions" @click.stop>
            <view class="action secondary" :class="{ disabled: operatingId === order.id }" role="button" tabindex="0" :aria-disabled="operatingId === order.id" @click="cancel(order)" @keydown.enter.stop="cancel(order)">取消订单</view>
            <view class="action primary" :class="{ disabled: operatingId === order.id }" role="button" tabindex="0" :aria-disabled="operatingId === order.id" aria-live="polite" @click="pay(order)" @keydown.enter.stop="pay(order)">{{ operatingId === order.id ? '处理中…' : '去支付' }}</view>
          </view>
          <view v-else class="detail-link">查看详情 <text>›</text></view>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup>
import { computed, ref } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import { cancelOrder, getOrders, repayOrder } from '../../api'
import { imgUrl } from '../../config'
import { loginIfNeeded } from '../../store/user'
import { payWithParams } from '../../utils/payment'
import UiState from '../../components/UiState.vue'

const tabs = [
  { label: '全部', value: null },
  { label: '待支付', value: 1 },
  { label: '待出餐', value: 2 },
  { label: '已完成', value: 3 },
  { label: '已取消', value: 4 }
]
const active = ref(null)
const orders = ref([])
const loading = ref(true)
const operatingId = ref(null)
const error = ref(false)
let loadSeq = 0

const activeLabel = computed(() => {
  const label = tabs.find((tab) => tab.value === active.value)?.label
  return label === '全部' ? '' : (label || '')
})

function money(value) {
  return Number(value || 0).toFixed(2)
}

function statusLabel(status) {
  return { 1: '待支付', 2: '待出餐', 3: '已完成', 4: '已取消' }[status] || '未知状态'
}

function diningLabel(mode) {
  return { 1: '堂食', 2: '打包带走' }[mode] || '未知'
}

function itemCount(order) {
  return order.item_count || 0
}

async function load() {
  const seq = ++loadSeq
  loading.value = true
  error.value = false
  try {
    const data = await getOrders(active.value)
    if (seq === loadSeq) orders.value = data || []
  } catch (requestError) {
    if (seq === loadSeq) error.value = true
  } finally {
    if (seq === loadSeq) loading.value = false
  }
}

async function retry() {
  await loginIfNeeded().catch(() => undefined)
  await load()
}

function switchTab(value) {
  if (active.value === value) return
  active.value = value
  load()
}

function goDetail(id) {
  uni.navigateTo({ url: `/pages/orders/detail?id=${id}` })
}

function goOrdering() {
  uni.switchTab({ url: '/pages/index/index' })
}

async function pay(order) {
  if (operatingId.value) return
  operatingId.value = order.id
  try {
    const result = await repayOrder(order.id)
    const outcome = await payWithParams({
      orderId: order.id,
      orderNo: result?.order_no || order.order_no,
      payParams: result?.pay_params,
      onPaid: load
    })
    if (outcome === 'missing') {
      uni.showToast({ title: '支付参数异常', icon: 'none' })
    }
  } catch {
    // request.js 已 toast
  } finally {
    operatingId.value = null
  }
}

async function cancel(order) {
  if (operatingId.value) return
  const confirmed = await new Promise((resolve) => uni.showModal({
    title: '取消订单',
    content: `确定取消订单 ${order.order_no} 吗？`,
    confirmText: '取消订单',
    confirmColor: '#b42318',
    success: (result) => resolve(result.confirm),
    fail: () => resolve(false)
  }))
  if (!confirmed) return
  operatingId.value = order.id
  try {
    await cancelOrder(order.id)
    uni.showToast({ title: '订单已取消', icon: 'none' })
    await load()
  } catch (e) {
    uni.showToast({ title: e?.message || '取消失败，请重试', icon: 'none' })
  } finally {
    operatingId.value = null
  }
}

onShow(async () => {
  try {
    await loginIfNeeded()
    await load()
  } catch (e) {
    loading.value = false  // 避免登录失败时 loading 永久为 true，导致无限 loading 动画
    error.value = true
  }
})
</script>

<style scoped>
.page { min-height: 100vh; background: var(--c-bg); }
.tabs { position: sticky; top: 0; z-index: 10; width: 100%; white-space: nowrap; background: var(--c-bg-card); border-bottom: 1px solid var(--c-border-light); }
.tabs-inner { min-width: 100%; height: 54px; display: inline-flex; padding: 0 6px; box-sizing: border-box; }
.tab { position: relative; min-width: 72px; height: 54px; padding: 0 10px; box-sizing: border-box; display: flex; align-items: center; justify-content: center; color: var(--c-text-secondary); font-size: var(--font-sm); }
.tab.active { color: var(--c-primary); font-weight: 800; }
.tab.active::after { content: ''; position: absolute; right: 18px; bottom: 0; left: 18px; height: 3px; border-radius: 2px 2px 0 0; background: var(--c-primary); }
.order-list { padding: 10px 12px 20px; }
.order-card { margin-bottom: 10px; padding: 16px; border: 1px solid var(--c-border-light); border-radius: var(--r-lg); background: var(--c-bg-card); }
.order-head { display: flex; align-items: flex-start; justify-content: space-between; }
.order-no { color: var(--c-text); font-size: var(--font-sm); font-weight: 700; }
.order-time { margin-top: 4px; color: var(--c-text-placeholder); font-size: 10px; }
.order-content { margin-top: 14px; display: flex; gap: 12px; }
.thumbnail { width: 68px; height: 68px; flex-shrink: 0; border-radius: var(--r-md); background: var(--c-bg-soft); }
.no-image { display: flex; align-items: center; justify-content: center; color: var(--c-text-placeholder); font-size: 10px; }
.order-summary { min-width: 0; flex: 1; }
.detail { min-height: 40px; overflow: hidden; color: var(--c-text); display: -webkit-box; font-size: var(--font-sm); line-height: 20px; -webkit-box-orient: vertical; -webkit-line-clamp: 2; }
.meta { margin-top: 6px; display: flex; gap: 12px; color: var(--c-text-placeholder); font-size: 10px; }
.order-foot { min-height: 50px; margin-top: 14px; padding-top: 10px; display: flex; align-items: center; justify-content: space-between; border-top: 1px solid var(--c-border-light); }
.total-label { color: var(--c-text-secondary); font-size: var(--font-xs); }
.total-label text { margin-left: 4px; color: var(--c-text); font-size: var(--font-md); font-weight: 800; }
.actions { display: flex; gap: 8px; }
.action { min-width: 86px; height: 44px; padding: 0 10px; box-sizing: border-box; display: flex; align-items: center; justify-content: center; border-radius: var(--r-md); font-size: var(--font-xs); font-weight: 700; }
.action.secondary { border: 1px solid var(--c-border); color: var(--c-text-secondary); }
.action.primary { background: var(--c-primary); color: #fff; }
.detail-link { min-width: 88px; height: 44px; display: flex; align-items: center; justify-content: flex-end; color: var(--c-text-secondary); font-size: var(--font-xs); }
.detail-link text { margin-left: 5px; font-size: 20px; }
.tab:active, .order-card:active, .action:active { opacity: .72; }
</style>
