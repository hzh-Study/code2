<template>
  <view class="page">
    <!-- 品牌头 -->
    <view class="hero">
      <view class="logo">拾</view>
      <view class="hero-text">
        <view class="title">拾味堂</view>
        <view class="sub">现点现做 · 堂食 / 外卖</view>
      </view>
    </view>

    <!-- 分类标签：:scroll-left 让点击的分类自动滚动到可视区 -->
    <scroll-view class="tabs" scroll-x :scroll-left="tabScrollLeft" scroll-with-animation>
      <view
        v-for="cat in categories"
        :key="cat.id"
        :id="'tab-' + cat.id"
        class="tab"
        :class="{ active: activeCat === cat.id }"
        @click="selectCat(cat.id)"
      >{{ cat.name }}</view>
    </scroll-view>

    <!-- 菜品列表 -->
    <view class="dish-list">
      <view v-for="d in dishes" :key="d.id" class="dish">
        <image class="dish-img" :src="imgUrl(d.image)" mode="aspectFill" />
        <view class="dish-info">
          <view class="dish-name">{{ d.name }}</view>
          <view class="dish-desc">{{ d.description }}</view>
          <view class="dish-bottom">
            <text class="price">¥{{ Number(d.price).toFixed(2) }}</text>
            <view class="add-btn" @click="addToCart(d)">＋</view>
          </view>
        </view>
      </view>
    </view>

    <!-- 底部购物车条 -->
    <view class="cart-bar" @click="goCart">
      <view class="cart-icon">
        🛒
        <text v-if="cartCount" class="badge">{{ cartCount }}</text>
      </view>
      <view class="cart-total">¥{{ cartTotal.toFixed(2) }}</view>
      <view class="checkout" @click.stop="goOrder">去结算</view>
    </view>
  </view>
</template>

<script setup>
import { ref, nextTick, getCurrentInstance } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import { loginIfNeeded } from '../../store/user'
import { imgUrl } from '../../config'
import { getCategories, getDishes, getCart, addCart } from '../../api'

const categories = ref([])
const activeCat = ref(null)
const tabScrollLeft = ref(0)
const dishes = ref([])
const cartCount = ref(0)
const cartTotal = ref(0)
let adding = false
// 修复：分类切换竞态序号，与 orders.vue 的 loadSeq 同理
let dishSeq = 0

async function loadCategories() {
  categories.value = await getCategories()
  if (categories.value.length && activeCat.value == null) {
    activeCat.value = categories.value[0].id
  }
}
async function loadDishes() {
  const seq = ++dishSeq
  const data = await getDishes(activeCat.value)
  // 修复：快速切换分类时，先发后至的过期响应会覆盖最新菜品列表，需丢弃
  if (seq !== dishSeq) return
  dishes.value = data
}
async function loadCart() {
  // 修复：接口可能返回 null/undefined，兜底为空数组避免 reduce 报错
  const items = await getCart() || []
  cartCount.value = items.reduce((s, it) => s + Number(it.quantity || 0), 0)
  cartTotal.value = items.reduce((s, it) => s + Number(it.subtotal), 0)
}
async function selectCat(id) {
  activeCat.value = id
  scrollTabIntoView(id)
  await loadDishes()
}

// 计算被点击分类相对滚动容器的偏移，滚动到让它露出后续项的位置
function scrollTabIntoView(id) {
  nextTick(() => {
    // #ifdef H5
    // H5 端真正的滚动层是 uni-scroll-view-content，直接操作其 scrollLeft 最可靠
    const tabEl = document.getElementById('tab-' + id)
    if (tabEl) {
      // 原生 scrollIntoView：让被点项在滚动容器内水平居中，前后项自然露出
      tabEl.scrollIntoView({ behavior: 'smooth', inline: 'center', block: 'nearest' })
    }
    // #endif

    // #ifndef H5
    // 小程序端用 scroll-view 的 scroll-left 属性驱动
    const query = uni.createSelectorQuery().in(getCurrentInstance().proxy)
    query.select('#tab-' + id).boundingClientRect()
    query.select('.tabs').boundingClientRect()
    query.select('.tabs').scrollOffset()
    query.exec((res) => {
      if (!res || !res[0] || !res[1] || !res[2]) return
      const tab = res[0]
      const container = res[1]
      const curScrollLeft = res[2].scrollLeft
      const target = curScrollLeft + (tab.left - container.left) - 12
      tabScrollLeft.value = Math.max(0, target)
    })
    // #endif
  })
}
async function addToCart(d) {
  // 修复：防止快速连续点击导致重复加购
  if (adding) return
  adding = true
  try {
    await addCart(d.id, 1)
    await loadCart()
    uni.showToast({ title: '已加入', icon: 'success' })
  } finally {
    adding = false
  }
}
function goCart() {
  uni.switchTab({ url: '/pages/cart/cart' })
}
function goOrder() {
  if (!cartCount.value) return uni.showToast({ title: '购物车为空', icon: 'none' })
  uni.navigateTo({ url: '/pages/order/order' })
}

onShow(async () => {
  try {
    await loginIfNeeded()
  } catch (e) {
    uni.showToast({ title: '登录失败，请重试', icon: 'none' })
    return
  }
  await loadCategories()
  await loadDishes()
  await loadCart()
})
</script>

<style scoped>
.page { padding-bottom: 80px; }

/* ── 品牌头 ── */
.hero {
  display: flex; align-items: center; gap: var(--sp-12);
  padding: var(--sp-24) var(--sp-16) var(--sp-20);
  background: linear-gradient(135deg, var(--c-primary), var(--c-primary-light));
  color: var(--c-text-inverse);
}
.logo {
  width: 48px; height: 48px; border-radius: var(--r-md);
  background: rgba(255,255,255,.22);
  backdrop-filter: blur(6px);
  display: flex; align-items: center; justify-content: center;
  font-size: 24px; font-weight: 700;
}
.title { font-size: var(--font-xl); font-weight: 800; letter-spacing: 0.5px; }
.sub { font-size: var(--font-xs); opacity: .85; margin-top: 2px; }

/* ── 分类标签 ── */
.tabs { white-space: nowrap; padding: var(--sp-12) var(--sp-8); background: var(--c-bg-card); }
.tabs :deep(.uni-scroll-view-content) { overflow-x: auto; -webkit-overflow-scrolling: touch; }
.tab {
  display: inline-block;
  padding: var(--sp-8) var(--sp-16); margin: 0 var(--sp-4);
  border-radius: var(--r-full);
  font-size: var(--font-base); color: var(--c-text-secondary);
  background: var(--c-bg-soft);
  transition: all .25s var(--ease);
}
.tab.active {
  color: var(--c-text-inverse);
  background: var(--c-primary);
  font-weight: 600;
  box-shadow: 0 2px 10px rgba(232,93,44,.3);
}

/* ── 菜品列表 ── */
.dish-list { padding: var(--sp-12); }
.dish {
  display: flex; gap: var(--sp-12);
  background: var(--c-bg-card);
  border-radius: var(--r-lg);
  padding: var(--sp-12);
  margin-bottom: var(--sp-12);
  box-shadow: var(--shadow-sm);
  transition: transform .2s var(--ease), box-shadow .2s var(--ease);
}
.dish:active { transform: scale(.98); box-shadow: var(--shadow-md); }
.dish-img {
  width: 96px; height: 72px; border-radius: var(--r-sm);
  background: var(--c-bg-soft); flex-shrink: 0;
  object-fit: cover;
}
.dish-info { flex: 1; display: flex; flex-direction: column; justify-content: space-between; min-height: 72px; }
.dish-name { font-size: var(--font-md); font-weight: 700; line-height: 1.3; }
.dish-desc {
  font-size: var(--font-xs); color: var(--c-text-secondary);
  margin: var(--sp-4) 0;
  overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
}
.dish-bottom { display: flex; align-items: center; justify-content: space-between; margin-top: auto; }
.price { color: var(--c-primary); font-weight: 800; font-size: var(--font-md); }
.add-btn {
  width: 32px; height: 32px; border-radius: 50%;
  background: var(--c-primary); color: var(--c-text-inverse);
  text-align: center; line-height: 32px; font-size: 18px;
  box-shadow: 0 2px 8px rgba(232,93,44,.3);
  transition: transform .15s var(--ease);
}
.add-btn:active { transform: scale(.88); }

/* ── 底部购物车条 ── */
.cart-bar {
  position: fixed; left: 0; right: 0; bottom: var(--window-bottom, 0px);
  height: 60px; background: var(--c-bar-bg);
  display: flex; align-items: center;
  padding: 0 var(--sp-16);
  color: var(--c-text-inverse); z-index: 20;
  box-shadow: 0 -2px 12px rgba(201,74,30,.25);
}
.cart-icon { font-size: 24px; position: relative; }
.badge {
  position: absolute; top: -6px; right: -10px;
  background: var(--c-text-inverse); color: var(--c-primary);
  font-size: var(--font-xs); border-radius: var(--r-full);
  font-weight: 700;
  padding: 0 5px; min-width: 16px; text-align: center;
  box-shadow: 0 1px 4px rgba(0,0,0,.15);
}
.cart-total { flex: 1; margin-left: var(--sp-16); font-weight: 700; font-size: var(--font-md); }
.checkout {
  background: var(--c-text-inverse); color: var(--c-primary);
  padding: var(--sp-8) var(--sp-24); border-radius: var(--r-full);
  font-weight: 700; font-size: var(--font-base);
  box-shadow: 0 2px 10px rgba(0,0,0,.12);
  transition: transform .15s var(--ease);
}
.checkout:active { transform: scale(.95); }
</style>
