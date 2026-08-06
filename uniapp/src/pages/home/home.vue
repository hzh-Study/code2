<template>
  <view class="page">
    <view class="store-hero">
      <view class="store-mark">拾</view>
      <view class="store-copy">
        <view class="store-name">拾味堂</view>
        <view class="store-slogan">现点现做，认真吃饭</view>
      </view>
      <view class="open-state"><view class="open-dot"></view>营业中</view>
    </view>

    <UiState v-if="loading" type="loading" title="正在准备今日菜单" />
    <UiState v-else-if="error" type="error" title="首页加载失败" description="请检查网络后重新尝试" action-text="重新加载" @action="load" />
    <template v-else>
      <view class="section categories-section">
        <view class="section-head"><view><view class="section-title">菜品分类</view><view class="section-copy">按口味快速找到想吃的菜</view></view><view class="text-action" role="button" tabindex="0" @click="goMenu()" @keydown.enter="goMenu()">全部菜品</view></view>
        <view class="category-grid">
          <view v-for="category in categories" :key="category.id" class="category-button" role="button" tabindex="0" @click="goMenu(category.id)" @keydown.enter="goMenu(category.id)">
            <view class="category-index">{{ String(category.sort_order || category.id).padStart(2, '0') }}</view>
            <view class="category-name">{{ category.name }}</view>
          </view>
        </view>
      </view>

      <view class="section hot-section">
        <view class="section-head"><view><view class="section-title">今日推荐</view><view class="section-copy">后厨精选的人气菜品</view></view></view>
        <scroll-view class="hot-scroll" scroll-x show-scrollbar="false">
          <view class="hot-row">
            <view v-for="dish in hotDishes" :key="dish.id" class="hot-item" role="button" tabindex="0" @click="goMenu(dish.category_id)" @keydown.enter="goMenu(dish.category_id)">
              <image v-if="dish.image" class="hot-image" :src="imgUrl(dish.image)" mode="aspectFill" />
              <view v-else class="hot-image no-image">暂无图片</view>
              <view class="hot-name">{{ dish.name }}</view>
              <view class="hot-price"><text>¥</text>{{ money(dish.price) }}</view>
            </view>
          </view>
        </scroll-view>
        <UiState v-if="!hotDishes.length" title="今日暂无推荐" description="可以前往完整菜单看看" action-text="去点餐" @action="goMenu()" />
      </view>
    </template>
  </view>
</template>

<script setup>
import { ref } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import { getCategories, getHotDishes } from '../../api'
import { imgUrl } from '../../config'
import { loginIfNeeded } from '../../store/user'
import UiState from '../../components/UiState.vue'

const categories = ref([])
const hotDishes = ref([])
const loading = ref(true)
const error = ref(false)

function money(value) {
  return Number(value || 0).toFixed(2)
}

function goMenu(categoryId) {
  if (categoryId) uni.setStorageSync('menu_category_id', categoryId)
  else uni.removeStorageSync('menu_category_id')
  uni.switchTab({ url: '/pages/index/index' })
}

async function load() {
  const isInitialLoad = !categories.value.length && !hotDishes.value.length
  loading.value = isInitialLoad
  error.value = false
  try {
    await loginIfNeeded()
    const [categoryData, hotData] = await Promise.all([getCategories(), getHotDishes()])
    categories.value = categoryData || []
    hotDishes.value = (hotData || []).slice(0, 4)
  } catch (requestError) {
    if (isInitialLoad) error.value = true
  } finally {
    loading.value = false
  }
}

onShow(load)
</script>

<style scoped>
.page { min-height: 100vh; padding-bottom: 24px; background: var(--c-bg); }
.store-hero { min-height: 132px; padding: 24px 18px; box-sizing: border-box; display: flex; align-items: center; background: var(--c-text); color: #fff; }
.store-mark { width: 52px; height: 52px; flex-shrink: 0; display: flex; align-items: center; justify-content: center; border-radius: var(--r-md); background: var(--c-primary); font-size: 24px; font-weight: 800; }
.store-copy { min-width: 0; flex: 1; margin-left: 14px; }
.store-name { font-size: 25px; font-weight: 800; }
.store-slogan { margin-top: 4px; color: #c8c3bd; font-size: var(--font-xs); }
.open-state { align-self: flex-start; display: flex; align-items: center; gap: 5px; color: #dfeee4; font-size: 10px; }
.open-dot { width: 7px; height: 7px; border-radius: 50%; background: #72be8a; }
.section { margin-top: 10px; padding: 18px 16px; background: var(--c-bg-card); border-top: 1px solid var(--c-border-light); border-bottom: 1px solid var(--c-border-light); }
.section-head { display: flex; align-items: flex-end; justify-content: space-between; }
.section-title { font-size: var(--font-lg); font-weight: 800; }
.section-copy { margin-top: 2px; color: var(--c-text-placeholder); font-size: 10px; }
.text-action { min-height: 44px; display: flex; align-items: center; color: var(--c-primary); font-size: var(--font-xs); font-weight: 700; }
.category-grid { margin-top: 14px; display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 8px; }
.category-button { min-height: 70px; padding: 10px; box-sizing: border-box; border: 1px solid var(--c-border-light); border-radius: var(--r-md); background: var(--c-bg-soft); }
.category-index { color: var(--c-primary); font-family: monospace; font-size: 10px; }
.category-name { margin-top: 7px; overflow: hidden; font-size: var(--font-sm); font-weight: 700; text-overflow: ellipsis; white-space: nowrap; }
.hot-section { padding-right: 0; }
.hot-section .section-head { padding-right: 16px; }
.hot-scroll { width: 100%; margin-top: 14px; white-space: nowrap; }
.hot-row { display: inline-flex; gap: 10px; padding-right: 16px; }
.hot-item { width: 146px; overflow: hidden; border: 1px solid var(--c-border-light); border-radius: var(--r-md); background: var(--c-bg-card); }
.hot-image { width: 146px; height: 104px; background: var(--c-bg-soft); }
.no-image { display: flex; align-items: center; justify-content: center; color: var(--c-text-placeholder); font-size: 10px; }
.hot-name { padding: 10px 10px 0; overflow: hidden; font-size: var(--font-sm); font-weight: 700; text-overflow: ellipsis; white-space: nowrap; }
.hot-price { padding: 4px 10px 12px; color: var(--c-primary); font-size: var(--font-md); font-weight: 800; }
.hot-price text { margin-right: 2px; font-size: 10px; }
.category-button:active, .hot-item:active, .text-action:active { opacity: .72; }
@media (max-width: 340px) { .category-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); } .open-state { display: none; } }
</style>
