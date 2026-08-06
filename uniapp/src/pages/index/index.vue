<template>
  <view class="page">
    <view class="shop-head">
      <view>
        <view class="eyebrow">拾味堂 · 今日营业</view>
        <view class="shop-title">现点现做，认真吃饭</view>
        <view class="shop-meta">后厨接单后制作 · 预计 15–25 分钟</view>
      </view>
      <view class="brand-mark">拾</view>
    </view>

    <view class="ordering-layout">
      <scroll-view class="category-rail" scroll-y>
        <view
          v-for="cat in categories"
          :key="cat.id"
          class="category-item"
          :class="{ active: activeCat === cat.id }"
          role="button"
          tabindex="0"
          :aria-label="`查看${cat.name}`"
          @click="selectCat(cat.id)"
          @keydown.enter="selectCat(cat.id)"
        >
          <view class="category-line"></view>
          <text>{{ cat.name }}</text>
        </view>
      </scroll-view>

      <scroll-view class="dish-scroll" scroll-y>
        <view class="dish-heading">
          <view class="dish-heading-main">{{ activeCategoryName }}</view>
          <view class="dish-heading-sub">{{ dishes.length }} 道在售菜品</view>
        </view>

        <UiState v-if="loading" type="loading" title="正在准备菜单" description="新鲜菜品马上呈现" />
        <UiState v-else-if="error" type="error" title="菜单加载失败" description="请检查网络后重新尝试" action-text="重新加载" @action="retry" />
        <UiState v-else-if="!dishes.length" title="暂无在售菜品" description="可以切换其他分类看看" />
        <view v-else class="dish-list">
          <view v-for="dish in dishes" :key="dish.id" class="dish-item">
            <image v-if="dish.image" class="dish-image" :src="imgUrl(dish.image)" mode="aspectFill" />
            <view v-else class="dish-image dish-image-empty">暂无图片</view>
            <view class="dish-info">
              <view class="dish-name">{{ dish.name }}</view>
              <view class="dish-desc">{{ dish.description || '今日新鲜制作' }}</view>
              <view class="dish-bottom">
                <view class="price"><text class="currency">¥</text>{{ price(dish.price) }}</view>
                <QuantityStepper v-if="dishQuantity(dish.id)" :model-value="dishQuantity(dish.id)" :name="dish.name" :disabled="isCartUpdating(dish.id)" @change="changeDish(dish, $event)" />
                <view v-else class="add-button" :class="{ disabled: isCartUpdating(dish.id) }" role="button" tabindex="0" :aria-disabled="isCartUpdating(dish.id)" :aria-label="`加入${dish.name}`" @click="changeDish(dish, 1)" @keydown.enter="changeDish(dish, 1)">+</view>
              </view>
            </view>
          </view>
        </view>
      </scroll-view>
    </view>

    <view class="cart-safe" :class="{ empty: !cartCount }">
      <view class="cart-bar">
        <view class="cart-trigger" role="button" tabindex="0" aria-label="查看购物车" @click="openCartSheet" @keydown.enter="openCartSheet">
          <view class="cart-symbol">
            <view class="cart-basket"></view>
            <text v-if="cartCount" class="badge">{{ cartCount > 99 ? '99+' : cartCount }}</text>
          </view>
          <view class="cart-summary">
            <view class="cart-price">¥{{ price(cartTotal) }}</view>
            <view class="cart-hint">{{ cartCount ? `已选 ${cartCount} 件` : '还未选择菜品' }}</view>
          </view>
        </view>
        <view class="checkout-button" :class="{ disabled: !cartCount }" role="button" tabindex="0" :aria-disabled="!cartCount" aria-label="去结算" @click="goOrder" @keydown.enter="goOrder">去结算</view>
      </view>
    </view>

    <CartSheet v-model:visible="cartSheetVisible" />
  </view>
</template>

<script setup>
import { computed, ref } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import { loginIfNeeded } from '../../store/user'
import { cartCount, cartTotal, changeCartQuantity, dishQuantity, isCartUpdating, loadCart } from '../../store/cart'
import { imgUrl } from '../../config'
import { getCategories, getDishes } from '../../api'
import QuantityStepper from '../../components/QuantityStepper.vue'
import UiState from '../../components/UiState.vue'
import CartSheet from '../../components/CartSheet.vue'

const categories = ref([])
const activeCat = ref(null)
const dishes = ref([])
const loading = ref(true)
const error = ref(false)
const cartSheetVisible = ref(false)
let dishSeq = 0

const activeCategoryName = computed(() => categories.value.find((item) => item.id === activeCat.value)?.name || '今日菜单')

function price(value) {
  return Number(value || 0).toFixed(2)
}

async function loadCategories() {
  categories.value = await getCategories() || []
  const requestedCategory = Number(uni.getStorageSync('menu_category_id'))
  if (requestedCategory && categories.value.some((item) => item.id === requestedCategory)) {
    activeCat.value = requestedCategory
    uni.removeStorageSync('menu_category_id')
  } else if (!categories.value.some((item) => item.id === activeCat.value)) {
    activeCat.value = categories.value[0]?.id ?? null
  }
}

async function loadDishes() {
  const seq = ++dishSeq
  loading.value = true
  error.value = false
  try {
    const data = await getDishes(activeCat.value)
    if (seq === dishSeq) dishes.value = data || []
  } catch (requestError) {
    if (seq === dishSeq) error.value = true
  } finally {
    if (seq === dishSeq) loading.value = false
  }
}

async function retry() {
  await loginIfNeeded().catch(() => undefined)
  await Promise.all([loadCategories(), loadCart().catch(() => undefined)])
  await loadDishes()
}

async function selectCat(id) {
  if (activeCat.value === id) return
  activeCat.value = id
  await loadDishes()
}

async function changeDish(dish, delta) {
  if (isCartUpdating(dish.id)) return
  try {
    await changeCartQuantity(dish.id, delta)
  } catch (e) {
    uni.showToast({ title: e?.message || '加购失败，请重试', icon: 'none' })
  }
}

function openCartSheet() {
  if (!cartCount.value) return uni.showToast({ title: '还未选择菜品', icon: 'none' })
  cartSheetVisible.value = true
}

function goOrder() {
  if (!cartCount.value) return uni.showToast({ title: '请先选择菜品', icon: 'none' })
  uni.navigateTo({ url: '/pages/order/order' })
}

onShow(async () => {
  try {
    await loginIfNeeded()
    await Promise.all([loadCategories(), loadCart().catch(() => undefined)])
    await loadDishes()
  } catch (requestError) {
    loading.value = false
    if (!categories.value.length || !dishes.value.length) error.value = true
  }
})
</script>

<style scoped>
.page { height: 100vh; overflow: hidden; background: var(--c-bg); }
.shop-head { height: 106px; box-sizing: border-box; display: flex; align-items: center; justify-content: space-between; padding: 18px 18px 16px; background: var(--c-bg-card); border-bottom: 1px solid var(--c-border-light); }
.eyebrow { color: var(--c-primary); font-size: var(--font-xs); font-weight: 700; letter-spacing: 1px; }
.shop-title { margin-top: 3px; color: var(--c-text); font-size: var(--font-xl); font-weight: 800; line-height: 1.3; }
.shop-meta { margin-top: 4px; color: var(--c-text-placeholder); font-size: var(--font-xs); }
.brand-mark { width: 46px; height: 46px; display: flex; align-items: center; justify-content: center; border-radius: var(--r-md); background: var(--c-text); color: var(--c-text-inverse); font-size: 22px; font-weight: 800; }
.ordering-layout { height: calc(100vh - 106px - 72px - env(safe-area-inset-bottom)); display: flex; }
.category-rail { width: 94px; height: 100%; flex-shrink: 0; background: #f1ece5; }
.category-item { position: relative; min-height: 56px; padding: 0 12px 0 16px; display: flex; align-items: center; box-sizing: border-box; color: var(--c-text-secondary); font-size: var(--font-sm); }
.category-item.active { background: var(--c-bg-card); color: var(--c-text); font-weight: 700; }
.category-line { position: absolute; left: 0; top: 14px; bottom: 14px; width: 3px; border-radius: 0 2px 2px 0; background: transparent; }
.category-item.active .category-line { background: var(--c-primary); }
.dish-scroll { height: 100%; flex: 1; min-width: 0; background: var(--c-bg-card); }
.dish-heading { padding: 16px 14px 10px; display: flex; align-items: baseline; justify-content: space-between; }
.dish-heading-main { font-size: var(--font-md); font-weight: 800; }
.dish-heading-sub { color: var(--c-text-placeholder); font-size: 11px; }
.dish-list { padding: 0 14px 18px; }
.dish-item { display: flex; gap: 12px; padding: 14px 0; border-bottom: 1px solid var(--c-border-light); }
.dish-image { width: 86px; height: 86px; flex-shrink: 0; border-radius: var(--r-md); background: var(--c-bg-soft); }
.dish-image-empty { display: flex; align-items: center; justify-content: center; color: var(--c-text-placeholder); font-size: 11px; }
.dish-info { min-width: 0; flex: 1; display: flex; flex-direction: column; }
.dish-name { overflow: hidden; color: var(--c-text); font-size: 15px; font-weight: 700; text-overflow: ellipsis; white-space: nowrap; }
.dish-desc { min-height: 34px; margin-top: 4px; overflow: hidden; color: var(--c-text-placeholder); display: -webkit-box; font-size: 11px; line-height: 17px; -webkit-box-orient: vertical; -webkit-line-clamp: 2; }
.dish-bottom { min-height: 44px; margin-top: auto; display: flex; align-items: flex-end; justify-content: space-between; }
.price { color: var(--c-primary); font-size: 17px; font-weight: 800; }
.currency { margin-right: 2px; font-size: 11px; }
.add-button { width: 44px; height: 44px; box-sizing: border-box; display: flex; align-items: center; justify-content: center; border: 1px solid var(--c-primary); border-radius: 50%; background: var(--c-primary); color: var(--c-text-inverse); font-size: 22px; font-weight: 500; }
.cart-safe { position: fixed; right: 0; bottom: var(--window-bottom, 0px); left: 0; z-index: 20; padding: 8px 12px calc(8px + env(safe-area-inset-bottom)); background: var(--c-bg-card); border-top: 1px solid var(--c-border-light); }
.cart-bar { height: 56px; display: flex; align-items: center; overflow: hidden; border-radius: var(--r-md); background: var(--c-text); color: var(--c-text-inverse); }
.cart-trigger { min-width: 0; flex: 1; height: 100%; padding-left: 12px; display: flex; align-items: center; }
.cart-symbol { position: relative; width: 44px; height: 44px; display: flex; align-items: center; justify-content: center; }
.cart-basket { width: 23px; height: 15px; box-sizing: border-box; border: 2px solid currentColor; border-top: 0; transform: skew(-7deg); }
.cart-basket::before { content: ''; position: absolute; width: 17px; height: 7px; margin: -7px 0 0 1px; border: 2px solid currentColor; border-bottom: 0; border-radius: 8px 8px 0 0; }
.badge { position: absolute; top: 0; right: -1px; min-width: 18px; height: 18px; padding: 0 4px; box-sizing: border-box; border-radius: var(--r-full); background: var(--c-primary); color: #fff; font-size: 10px; line-height: 18px; text-align: center; }
.cart-summary { min-width: 0; flex: 1; margin-left: 8px; }
.cart-price { font-size: var(--font-md); font-weight: 800; line-height: 1.2; }
.cart-hint { margin-top: 2px; color: #c8c3bd; font-size: 10px; }
.checkout-button { align-self: stretch; min-width: 104px; display: flex; align-items: center; justify-content: center; background: var(--c-primary); color: #fff; font-size: var(--font-base); font-weight: 700; }
.checkout-button.disabled { background: #5f5a54; color: #c8c3bd; }
.category-item:active, .step-button:active, .add-button:active, .checkout-button:active { opacity: .72; }
</style>
