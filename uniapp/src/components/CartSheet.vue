<template>
  <view v-if="rendered" class="cart-sheet-root" :class="{ visible }">
    <view class="cart-sheet-mask" @click="close" />
    <view class="cart-sheet-panel" @click.stop>
      <view class="sheet-head">
        <view>
          <view class="head-title">已选菜品</view>
          <view class="head-sub">共 {{ cartCount }} 件，请核对数量</view>
        </view>
        <view class="head-actions">
          <view
            class="clear-button"
            :class="{ disabled: cartState.clearing }"
            role="button"
            tabindex="0"
            :aria-disabled="cartState.clearing"
            aria-label="清空购物车"
            @click="handleClear"
            @keydown.enter="handleClear"
          >{{ cartState.clearing ? '清空中…' : '清空' }}</view>
          <view class="close-button" role="button" tabindex="0" aria-label="关闭购物车" @click="close" @keydown.enter="close">×</view>
        </view>
      </view>

      <scroll-view class="sheet-list" scroll-y>
        <view class="sheet-list-inner">
        <view v-for="item in cartState.items" :key="item.id" class="cart-item">
          <image v-if="item.image" class="item-image" :src="imgUrl(item.image)" mode="aspectFill" />
          <view v-else class="item-image no-image">暂无图片</view>
          <view class="item-info">
            <view class="item-name">{{ item.name }}</view>
            <view class="item-price">¥{{ money(item.price) }} / 份</view>
            <view class="item-bottom">
              <view class="subtotal">小计 <text>¥{{ money(item.subtotal) }}</text></view>
              <QuantityStepper
                size="small"
                :model-value="Number(item.quantity)"
                :name="item.name"
                :disabled="isCartUpdating(item.dish_id)"
                @change="change(item, $event)"
              />
            </view>
          </view>
        </view>
        </view>
      </scroll-view>

      <view class="sheet-footer">
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
import { ref, watch } from 'vue'
import cartState, { cartCount, cartTotal, changeCartQuantity, clearAllCart, isCartUpdating, loadCart } from '../store/cart'
import { onUnmounted } from 'vue'
import { imgUrl } from '../config'
import QuantityStepper from './QuantityStepper.vue'

const props = defineProps({
  visible: { type: Boolean, default: false }
})

const emit = defineEmits(['update:visible'])

const rendered = ref(false)
let closeTimer = null

watch(() => props.visible, async (next) => {
  if (next) {
    // 先加载购物车，确认有数据后再渲染，避免空购物车闪现后立即关闭
    await loadCart().catch(() => undefined)
    if (!cartCount.value) {
      // 购物车为空，通知父组件关闭，不渲染
      close()
      return
    }
    rendered.value = true
    return
  }
  if (closeTimer) clearTimeout(closeTimer)
  closeTimer = setTimeout(() => {
    if (!props.visible) rendered.value = false
    closeTimer = null
  }, 320)
})

onUnmounted(() => {
  if (closeTimer) clearTimeout(closeTimer)
})

watch(cartCount, (count) => {
  if (props.visible && !count) close()
})

function money(value) {
  return Number(value || 0).toFixed(2)
}

function close() {
  emit('update:visible', false)
}

async function change(item, delta) {
  await changeCartQuantity(item.dish_id, delta)
}

async function handleClear() {
  const cleared = await clearAllCart()
  if (cleared) close()
}

function goOrder() {
  if (!cartCount.value) return uni.showToast({ title: '请先选择菜品', icon: 'none' })
  close()
  uni.navigateTo({ url: '/pages/order/order' })
}
</script>

<style scoped>
.cart-sheet-root {
  position: fixed;
  top: 0;
  right: 0;
  bottom: var(--window-bottom, 0px);
  left: 0;
  z-index: 30;
  pointer-events: none;
}

.cart-sheet-root.visible {
  pointer-events: auto;
}

.cart-sheet-mask {
  position: absolute;
  inset: 0;
  background: rgba(43, 43, 43, 0.45);
  opacity: 0;
  transition: opacity var(--duration-normal) var(--ease);
}

.cart-sheet-root.visible .cart-sheet-mask {
  opacity: 1;
}

.cart-sheet-panel {
  position: absolute;
  right: 0;
  bottom: 0;
  left: 0;
  max-height: 65vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  border-radius: var(--r-xl) var(--r-xl) 0 0;
  background: var(--c-bg-card);
  box-shadow: var(--shadow-lg);
  transform: translateY(100%);
  transition: transform var(--duration-slow) var(--ease);
}

.cart-sheet-root.visible .cart-sheet-panel {
  transform: translateY(0);
}

.sheet-head {
  flex-shrink: 0;
  padding: 16px 16px 12px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid var(--c-border-light);
}

.head-title {
  font-size: var(--font-lg);
  font-weight: 800;
}

.head-sub {
  margin-top: 2px;
  color: var(--c-text-placeholder);
  font-size: var(--font-xs);
}

.head-actions {
  display: flex;
  align-items: center;
  gap: 4px;
}

.clear-button {
  min-width: 44px;
  height: 44px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--c-danger);
  font-size: var(--font-sm);
}

.close-button {
  width: 44px;
  height: 44px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--c-text-secondary);
  font-size: 28px;
  line-height: 1;
}

.sheet-list {
  flex: 1;
  min-height: 0;
  max-height: calc(65vh - 140px);
}

.sheet-list-inner {
  padding: 0 20px 0 16px;
  box-sizing: border-box;
}

.cart-item {
  display: flex;
  gap: 12px;
  padding: 14px 0;
  border-bottom: 1px solid var(--c-border-light);
}

.cart-item:last-child {
  border-bottom: 0;
}

.item-image {
  width: 72px;
  height: 72px;
  flex-shrink: 0;
  border-radius: var(--r-md);
  background: var(--c-bg-soft);
}

.no-image {
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--c-text-placeholder);
  font-size: 11px;
}

.item-info {
  min-width: 0;
  flex: 1;
}

.item-name {
  overflow: hidden;
  font-size: 15px;
  font-weight: 700;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.item-price {
  margin-top: 4px;
  color: var(--c-text-placeholder);
  font-size: var(--font-xs);
}

.item-bottom {
  min-height: 32px;
  margin-top: 4px;
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 8px;
}

.item-bottom :deep(.quantity-stepper) {
  flex-shrink: 0;
}

.subtotal {
  color: var(--c-text-secondary);
  font-size: 11px;
}

.subtotal text {
  margin-left: 3px;
  color: var(--c-primary);
  font-size: var(--font-sm);
  font-weight: 800;
}

.sheet-footer {
  flex-shrink: 0;
  min-height: 72px;
  padding: 10px 12px;
  display: flex;
  align-items: center;
  gap: 12px;
  border-top: 1px solid var(--c-border-light);
}

.amount-info {
  flex: 1;
}

.amount-label {
  color: var(--c-text-secondary);
  font-size: var(--font-xs);
}

.amount {
  color: var(--c-primary);
  font-size: 23px;
  font-weight: 800;
  line-height: 1.2;
}

.amount text {
  margin-right: 2px;
  font-size: var(--font-xs);
}

.settle-button {
  min-width: 132px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--r-md);
  background: var(--c-primary);
  color: #fff;
  font-size: var(--font-md);
  font-weight: 700;
}

.clear-button:active,
.close-button:active,
.settle-button:active {
  opacity: 0.72;
}
</style>
