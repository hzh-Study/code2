<template>
  <view class="page">
    <view v-if="!items.length" class="empty empty-enter">
      <view class="empty-icon">
        <view class="bag"></view>
      </view>
      <view class="empty-text">购物车空空如也</view>
      <view class="empty-hint">去逛逛美味吧～</view>
      <view class="btn-go" @click="goIndex">去点餐</view>
    </view>
    <view v-else>
      <view v-for="it in items" :key="it.id" class="cart-item">
        <view class="ci-bar"></view>
        <image class="ci-img" :src="imgUrl(it.image)" mode="aspectFill" />
        <view class="ci-info">
          <view class="ci-name">{{ it.name }}</view>
          <view class="ci-price">¥{{ Number(it.price).toFixed(2) }}</view>
        </view>
        <view class="stepper">
          <text class="step" @click="change(it, -1)">－</text>
          <text class="qty">{{ it.quantity }}</text>
          <text class="step" @click="change(it, 1)">＋</text>
        </view>
      </view>
    </view>

    <view class="footer" v-if="items.length">
      <view class="footer-left">
        <view class="item-count">{{ items.reduce((s, it) => s + it.quantity, 0) }} 件商品</view>
        <view class="total">合计 <text class="amt">¥{{ total.toFixed(2) }}</text></view>
      </view>
      <view class="btn" @click="goOrder">去结算</view>
    </view>
  </view>
</template>

<script setup>
import { ref } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import { loginIfNeeded } from '../../store/user'
import { imgUrl } from '../../config'
import { getCart, updateCart } from '../../api'

const items = ref([])
const total = ref(0)
let updating = false

async function load() {
  // 修复：接口可能返回 null/undefined，兜底为空数组避免 reduce 报错
  items.value = await getCart() || []
  total.value = items.value.reduce((s, it) => s + Number(it.subtotal), 0)
}
async function change(it, delta) {
  // 修复：防止快速连续点击导致并发请求和状态错乱
  if (updating) return
  updating = true
  const qty = it.quantity + delta
  try {
    if (qty < 1) {
      await updateCart(it.dish_id, 0)
    } else {
      await updateCart(it.dish_id, qty)
    }
    await load()
  } catch (e) {
    uni.showToast({ title: '更新失败', icon: 'none' })
  } finally {
    updating = false
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
  } catch (e) {
    uni.showToast({ title: '登录失败，请重试', icon: 'none' })
    return
  }
  await load()
})
</script>

<style scoped>
.page {
  padding-bottom: 80px;
  min-height: 100vh;
  background: linear-gradient(180deg, #faf8f5, #f5f0ea);
}

/* ── 空状态入场动画 ── */
@keyframes fadeSlideUp {
  from { opacity: 0; transform: translateY(24px); }
  to   { opacity: 1; transform: translateY(0); }
}
.empty-enter {
  animation: fadeSlideUp .5s ease-out both;
}

/* ── 空状态 ── */
.empty {
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  padding-top: 160px;
}
.empty-icon {
  position: relative;
  width: 80px; height: 80px;
  margin-bottom: 20px;
  display: flex; align-items: center; justify-content: center;
}
/* CSS 纯手绘购物袋 */
.bag {
  position: relative;
  width: 48px; height: 44px;
  border: 3px solid #e85d2c;
  border-radius: 0 0 10px 10px;
}
.bag::before {
  content: '';
  position: absolute;
  top: -16px; left: 50%;
  transform: translateX(-50%);
  width: 22px; height: 16px;
  border: 3px solid #e85d2c;
  border-bottom: none;
  border-radius: 12px 12px 0 0;
}
.empty-text { font-size: var(--font-lg); font-weight: 700; color: var(--c-text-secondary); }
.empty-hint { font-size: var(--font-sm); color: var(--c-text-placeholder); margin-top: var(--sp-8); }

/* 去点餐按钮 */
.btn-go {
  margin-top: 28px;
  padding: 12px 36px;
  background: linear-gradient(135deg, #e85d2c, #f07a4a);
  color: #fff;
  font-size: 16px;
  font-weight: 700;
  border-radius: 999px;
  box-shadow: 0 4px 16px rgba(232,93,44,.35);
  transition: transform .15s ease;
}
.btn-go:active { transform: scale(.94); }

/* ── 购物车项 ── */
.cart-item {
  display: flex; align-items: center; gap: var(--sp-12);
  background: var(--c-bg-card);
  border-radius: var(--r-lg);
  padding: var(--sp-16);
  padding-left: 20px;
  margin: var(--sp-12) var(--sp-12);
  box-shadow: var(--shadow-sm);
  position: relative;
  overflow: hidden;
}
/* 左侧品牌色指示条 */
.ci-bar {
  position: absolute;
  left: 0; top: 8px; bottom: 8px;
  width: 4px;
  background: #e85d2c;
  border-radius: 0 4px 4px 0;
}
.ci-img {
  width: 72px; height: 72px; border-radius: 12px;
  background: var(--c-bg-soft); flex-shrink: 0;
  object-fit: cover;
  box-shadow: 0 2px 8px rgba(0,0,0,.08);
}
.ci-info { flex: 1; }
.ci-name { font-size: 16px; font-weight: 600; line-height: 1.3; }
.ci-price {
  color: #e85d2c; font-weight: 700; margin-top: var(--sp-8);
  font-size: var(--font-md);
  display: inline-block;
  background: #fff3ed;
  padding: 2px 10px;
  border-radius: 999px;
}

/* ── 步进器（胶囊式，触控热区 ≥ 44px）── */
.stepper { display: flex; align-items: center; gap: 8px; }
.step {
  width: 32px; height: 44px; line-height: 44px; text-align: center;
  border-radius: 8px; border: 1.5px solid #e85d2c;
  color: #e85d2c; font-size: 18px; font-weight: 600;
  transition: all .15s ease;
}
.step:active {
  background: #e85d2c; color: #fff;
  transform: scale(.92);
}
.qty {
  min-width: 28px; text-align: center;
  font-size: var(--font-md); font-weight: 700;
}

/* ── 底部结算栏 ── */
.footer {
  position: fixed; bottom: var(--window-bottom, 0px); left: 0; right: 0;
  height: 60px; background: var(--c-bar-bg); color: var(--c-text-inverse);
  display: flex; align-items: center; padding: 0 var(--sp-16); z-index: 20;
  box-shadow: 0 -4px 20px rgba(0,0,0,.12);
}
.footer-left { flex: 1; }
.item-count {
  font-size: 12px; opacity: .75; line-height: 1;
  margin-bottom: 2px;
}
.total { font-size: var(--font-base); }
.amt { color: var(--c-text-inverse); font-weight: 800; font-size: var(--font-lg); }
.btn {
  background: linear-gradient(135deg, #e85d2c, #f07a4a);
  color: #fff;
  padding: var(--sp-10) var(--sp-24); border-radius: var(--r-full);
  font-weight: 700; font-size: var(--font-base);
  box-shadow: 0 4px 16px rgba(232,93,44,.35);
  transition: transform .15s ease;
}
.btn:active { transform: scale(.94); }
</style>
