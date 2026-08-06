<template>
  <view class="page">
    <UiState v-if="loading" type="loading" title="正在核对订单" />
    <UiState v-else-if="error" type="error" title="订单信息加载失败" description="请检查网络后重新尝试" action-text="重新加载" @action="load" />
    <template v-else>
    <view class="section">
      <view class="section-head">
        <view class="section-title">用餐方式</view>
        <view class="required">必选</view>
      </view>
      <view class="mode-row">
        <view class="mode" :class="{ active: diningMode === 1 }" role="radio" tabindex="0" :aria-checked="diningMode === 1" @click="diningMode = 1" @keydown.enter="diningMode = 1">
          <view class="mode-icon dine-in"><view class="plate"></view></view>
          <view><view class="mode-title">堂食</view><view class="mode-copy">店内享用</view></view>
          <view class="radio"><view class="radio-dot"></view></view>
        </view>
        <view class="mode" :class="{ active: diningMode === 2 }" role="radio" tabindex="0" :aria-checked="diningMode === 2" @click="diningMode = 2" @keydown.enter="diningMode = 2">
          <view class="mode-icon takeaway"><view class="bag-line"></view></view>
          <view><view class="mode-title">打包</view><view class="mode-copy">打包带走</view></view>
          <view class="radio"><view class="radio-dot"></view></view>
        </view>
      </view>
    </view>

    <view class="section product-section">
      <view class="section-head">
        <view class="section-title">订单商品</view>
        <view class="section-count">共 {{ itemCount }} 件</view>
      </view>
      <view v-for="item in items" :key="item.id" class="product-line">
        <view class="product-main"><text class="product-name">{{ item.name }}</text><text class="product-qty">×{{ item.quantity }}</text></view>
        <text class="product-price">¥{{ money(item.subtotal) }}</text>
      </view>
    </view>

    <view class="section total-section">
      <view class="summary-line"><text>商品小计</text><text>¥{{ money(total) }}</text></view>
      <view class="summary-line final"><text>应付合计</text><text class="final-price"><text>¥</text>{{ money(total) }}</text></view>
    </view>

    <view class="submit-safe bottom-action-safe">
      <view class="submit-bar bottom-action-bar">
        <view class="submit-total"><text class="submit-label">应付</text><text class="submit-price">¥{{ money(total) }}</text></view>
        <view class="submit-button" :class="{ disabled: submitting || !items.length }" role="button" tabindex="0" :aria-disabled="submitting || !items.length" aria-live="polite" @click="submit" @keydown.enter="submit">{{ submitting ? '提交中…' : '提交订单' }}</view>
      </view>
    </view>
    </template>
  </view>
</template>

<script setup>
import { computed, ref } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import { createOrder } from '../../api'
import cartState, { loadCart } from '../../store/cart'
import { loginIfNeeded } from '../../store/user'
import { payWithParams } from '../../utils/payment'
import UiState from '../../components/UiState.vue'

const items = computed(() => cartState.items)
const diningMode = ref(null)
const submitting = ref(false)
const loading = ref(true)
const error = ref(false)
const itemCount = computed(() => items.value.reduce((sum, item) => sum + Number(item.quantity || 0), 0))
const total = computed(() => items.value.reduce((sum, item) => sum + Number(item.subtotal || 0), 0))

function money(value) {
  return Number(value || 0).toFixed(2)
}

function goOrders() {
  setTimeout(() => uni.switchTab({ url: '/pages/orders/orders' }), 700)
}

async function submit() {
  if (submitting.value) return
  if (!items.value.length) return uni.showToast({ title: '购物车为空', icon: 'none' })
  if (!diningMode.value) return uni.showToast({ title: '请选择堂食或打包', icon: 'none' })
  submitting.value = true
  try {
    const result = await createOrder(diningMode.value)
    cartState.items = []
    if (!result?.pay_params) {
      uni.showToast({
        title: result?.message || '订单已创建，请到订单列表完成支付',
        icon: 'none'
      })
      goOrders()
      return
    }
    const outcome = await payWithParams({
      orderId: result.order_id || result.id,
      orderNo: result.order_no,
      payParams: result.pay_params
    })
    if (outcome === 'missing' || outcome === 'failed') {
      uni.showToast({ title: '订单已创建，请到订单列表完成支付', icon: 'none' })
    }
    goOrders()
  } catch {
    // request.js 已 toast 具体错误
  } finally {
    submitting.value = false
  }
}

async function load() {
  loading.value = true
  error.value = false
  try {
    await loginIfNeeded()
    await loadCart()
  } catch {
    error.value = true
  } finally {
    loading.value = false
  }
}

onShow(load)
</script>

<style scoped>
.page { min-height: 100vh; padding: 12px 12px calc(94px + env(safe-area-inset-bottom)); box-sizing: border-box; background: var(--c-bg); }
.section { margin-bottom: 12px; padding: 18px 16px; border: 1px solid var(--c-border-light); border-radius: var(--r-lg); background: var(--c-bg-card); }
.section-head { display: flex; align-items: center; justify-content: space-between; }
.section-title { font-size: var(--font-md); font-weight: 800; }
.required { padding: 2px 8px; border-radius: var(--r-full); background: var(--c-primary-bg); color: var(--c-primary); font-size: 10px; font-weight: 700; }
.section-count { color: var(--c-text-placeholder); font-size: var(--font-xs); }
.mode-row { margin-top: 16px; display: flex; gap: 10px; }
.mode { position: relative; min-height: 82px; flex: 1; padding: 12px; box-sizing: border-box; display: flex; align-items: center; gap: 10px; border: 1px solid var(--c-border); border-radius: var(--r-md); }
.mode.active { border-color: var(--c-primary); background: var(--c-primary-bg); }
.mode-icon { position: relative; width: 36px; height: 36px; flex-shrink: 0; display: flex; align-items: center; justify-content: center; border-radius: 50%; background: var(--c-bg-soft); color: var(--c-text-secondary); }
.mode.active .mode-icon { background: #fff; color: var(--c-primary); }
.plate { width: 22px; height: 9px; box-sizing: border-box; border: 2px solid currentColor; border-radius: 50%; }
.plate::before { content: ''; position: absolute; top: 8px; left: 17px; width: 2px; height: 13px; background: currentColor; }
.takeaway { box-sizing: border-box; border: 2px solid currentColor; border-top: 0; border-radius: 3px 3px 7px 7px; transform: scale(.58); }
.takeaway::before { content: ''; position: absolute; top: 2px; left: 7px; width: 17px; height: 10px; border: 3px solid currentColor; border-bottom: 0; border-radius: 12px 12px 0 0; }
.mode-title { color: var(--c-text); font-size: var(--font-sm); font-weight: 700; }
.mode-copy { margin-top: 2px; color: var(--c-text-placeholder); font-size: 10px; }
.radio { position: absolute; top: 8px; right: 8px; width: 16px; height: 16px; box-sizing: border-box; display: flex; align-items: center; justify-content: center; border: 1px solid var(--c-border-strong); border-radius: 50%; }
.mode.active .radio { border-color: var(--c-primary); }
.radio-dot { width: 8px; height: 8px; border-radius: 50%; }
.mode.active .radio-dot { background: var(--c-primary); }
.product-section { padding-bottom: 8px; }
.product-line { min-height: 48px; display: flex; align-items: center; justify-content: space-between; border-bottom: 1px solid var(--c-border-light); }
.product-line:last-child { border-bottom: 0; }
.product-main { min-width: 0; flex: 1; display: flex; align-items: center; }
.product-name { overflow: hidden; color: var(--c-text-secondary); font-size: var(--font-sm); text-overflow: ellipsis; white-space: nowrap; }
.product-qty { margin-left: 8px; color: var(--c-text-placeholder); font-size: var(--font-xs); }
.product-price { color: var(--c-text); font-size: var(--font-sm); font-weight: 700; }
.total-section { padding-top: 10px; padding-bottom: 10px; }
.summary-line { min-height: 44px; display: flex; align-items: center; justify-content: space-between; color: var(--c-text-secondary); font-size: var(--font-sm); }
.summary-line.final { border-top: 1px solid var(--c-border-light); color: var(--c-text); font-weight: 700; }
.final-price { color: var(--c-primary); font-size: 21px; font-weight: 800; }
.final-price text { margin-right: 2px; font-size: var(--font-xs); }
.submit-bar { min-height: 76px; padding-left: 18px; }
.submit-total { flex: 1; }
.submit-label { margin-right: 7px; color: var(--c-text-secondary); font-size: var(--font-xs); }
.submit-price { color: var(--c-primary); font-size: 21px; font-weight: 800; }
.submit-button { min-width: 144px; height: 48px; display: flex; align-items: center; justify-content: center; border-radius: var(--r-md); background: var(--c-primary); color: #fff; font-size: var(--font-md); font-weight: 700; }
.submit-button.disabled { background: var(--c-bg-disabled); color: var(--c-text-disabled); }
.mode:active, .submit-button:active { opacity: .72; }
</style>
