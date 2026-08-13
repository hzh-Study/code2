<template>
  <view class="page">
    <view v-if="cartState.items.length" class="cart-head">
      <view>
        <view class="head-title">已选菜品</view>
        <view class="head-sub">共 {{ cartCount }} 件，请核对数量</view>
      </view>
      <view class="clear-button" :class="{ disabled: cartState.clearing }" role="button" tabindex="0" :aria-disabled="cartState.clearing" aria-label="清空购物车" @click="clearAll" @keydown.enter="clearAll">{{ cartState.clearing ? '清空中…' : '清空' }}</view>
    </view>

    <UiState v-if="cartState.loading" type="loading" title="正在读取购物车" />
    <UiState v-else-if="cartState.error" type="error" title="购物车加载失败" description="请检查网络后重新尝试" action-text="重新加载" @action="retry" />
    <UiState v-else-if="!cartState.items.length" title="购物车还是空的" description="从今日菜单里挑几道喜欢的菜吧" action-text="去点餐" @action="goIndex" />

    <view v-else class="cart-list">
      <view v-for="item in cartState.items" :key="item.id" class="cart-item">
        <image v-if="item.image" class="item-image" :src="imgUrl(item.image)" mode="aspectFill" />
        <view v-else class="item-image no-image">暂无图片</view>
        <view class="item-info">
          <view class="item-name">{{ item.name }}</view>
          <view class="item-price">¥{{ money(item.price) }} / 份</view>
          <view class="item-bottom">
            <view class="subtotal">小计 <text>¥{{ money(item.subtotal) }}</text></view>
            <QuantityStepper :model-value="Number(item.quantity)" :name="item.name" :disabled="isCartUpdating(item.dish_id)" @change="change(item, $event)" />
          </view>
        </view>
      </view>
    </view>

    <view v-if="cartState.items.length" class="settlement-safe bottom-action-safe">
      <view class="settlement bottom-action-bar">
        <view class="amount-info">
          <view class="amount-label">合计</view>
          <view class="amount"><text>¥</text>{{ money(cartTotal) }}</view>
        </view>
        <view class="settle-button" role="button" tabindex="0" @click="goOrder" @keydown.enter="goOrder">去结算</view>
      </view>
    </view>
  </view>
</template>

<script setup>
import { onShow } from '@dcloudio/uni-app'
import cartState, { cartCount, cartTotal, changeCartQuantity, clearAllCart, isCartUpdating, loadCart } from '../../store/cart'
import { imgUrl } from '../../config'
import { loginIfNeeded } from '../../store/user'
import QuantityStepper from '../../components/QuantityStepper.vue'
import UiState from '../../components/UiState.vue'

function money(value) {
  return Number(value || 0).toFixed(2)
}

async function change(item, delta) {
  await changeCartQuantity(item.dish_id, delta)
}

async function clearAll() {
  await clearAllCart()
}

async function retry() {
  try {
    await loginIfNeeded().catch(() => undefined)
    await loadCart()
  } catch (e) {
    uni.showToast({ title: e?.message || '加载失败，请重试', icon: 'none' })
  }
}

function goOrder() {
  uni.navigateTo({ url: '/pages/order/order' })
}

function goIndex() {
  uni.switchTab({ url: '/pages/index/index' })
}

onShow(async () => {
  try {
    await loginIfNeeded()
    await loadCart()
  } catch (e) {
    cartState.error = true
  }
})
</script>

<style scoped>
.page { min-height: 100vh; padding-bottom: calc(92px + env(safe-area-inset-bottom)); box-sizing: border-box; background: var(--c-bg); }
.cart-head { height: 78px; padding: 0 16px; display: flex; align-items: center; justify-content: space-between; background: var(--c-bg-card); border-bottom: 1px solid var(--c-border-light); }
.head-title { font-size: var(--font-lg); font-weight: 800; }
.head-sub { margin-top: 2px; color: var(--c-text-placeholder); font-size: var(--font-xs); }
.clear-button { min-width: 44px; height: 44px; display: flex; align-items: center; justify-content: center; color: var(--c-danger); font-size: var(--font-sm); }
.cart-list { margin-top: 10px; padding: 0 12px; background: var(--c-bg-card); }
.cart-item { display: flex; gap: 12px; padding: 16px 4px; border-bottom: 1px solid var(--c-border-light); }
.cart-item:last-child { border-bottom: 0; }
.item-image { width: 82px; height: 82px; flex-shrink: 0; border-radius: var(--r-md); background: var(--c-bg-soft); }
.no-image { display: flex; align-items: center; justify-content: center; color: var(--c-text-placeholder); font-size: 11px; }
.item-info { min-width: 0; flex: 1; }
.item-name { overflow: hidden; font-size: 15px; font-weight: 700; text-overflow: ellipsis; white-space: nowrap; }
.item-price { margin-top: 4px; color: var(--c-text-placeholder); font-size: var(--font-xs); }
.item-bottom { min-height: 48px; margin-top: 4px; display: flex; align-items: flex-end; justify-content: space-between; }
.subtotal { color: var(--c-text-secondary); font-size: 11px; }
.subtotal text { margin-left: 3px; color: var(--c-primary); font-size: var(--font-sm); font-weight: 800; }
.settlement { padding-left: 18px; }
.amount-info { flex: 1; }
.amount-label { color: var(--c-text-secondary); font-size: var(--font-xs); }
.amount { color: var(--c-primary); font-size: 23px; font-weight: 800; line-height: 1.2; }
.amount text { margin-right: 2px; font-size: var(--font-xs); }
.settle-button { min-width: 132px; height: 48px; display: flex; align-items: center; justify-content: center; border-radius: var(--r-md); background: var(--c-primary); color: #fff; font-size: var(--font-md); font-weight: 700; }
.clear-button:active, .settle-button:active { opacity: .72; }
</style>
