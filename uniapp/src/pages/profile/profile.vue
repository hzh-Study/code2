<template>
  <view class="page">
    <view class="profile-head">
      <image v-if="user?.avatar" class="avatar" :src="imgUrl(user.avatar)" mode="aspectFill" />
      <view v-else class="avatar avatar-fallback">{{ avatarLetter }}</view>
      <view class="profile-copy"><view class="nickname">{{ user?.nickname || '微信用户' }}</view><view class="profile-note">欢迎来到拾味堂</view></view>
    </view>

    <UiState v-if="loading" type="loading" title="正在读取账户信息" />
    <UiState v-else-if="error" type="error" title="账户信息加载失败" action-text="重新加载" @action="load" />
    <template v-else>
      <view class="menu-section">
        <view class="menu-row" role="button" tabindex="0" @click="goOrders" @keydown.enter="goOrders">
          <view><view class="menu-title">全部订单</view><view class="menu-copy">查看支付与出餐进度</view></view><text class="chevron">›</text>
        </view>
        <view class="menu-row" role="button" tabindex="0" @click="goOrdering" @keydown.enter="goOrdering">
          <view><view class="menu-title">继续点餐</view><view class="menu-copy">浏览今日在售菜品</view></view><text class="chevron">›</text>
        </view>
      </view>

      <view class="store-info">
        <view class="store-title">拾味堂</view>
        <view class="store-line"><text>营业时间</text><text>10:30 - 21:30</text></view>
        <view class="store-line"><text>服务方式</text><text>堂食 · 打包带走</text></view>
      </view>
    </template>
  </view>
</template>

<script setup>
import { computed, ref } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import { imgUrl } from '../../config'
import userState, { loginIfNeeded } from '../../store/user'
import UiState from '../../components/UiState.vue'

const loading = ref(true)
const error = ref(false)
const user = computed(() => userState.userInfo)
const avatarLetter = computed(() => (user.value?.nickname || '拾').slice(0, 1))

function goOrders() {
  uni.switchTab({ url: '/pages/orders/orders' })
}

function goOrdering() {
  uni.switchTab({ url: '/pages/index/index' })
}

async function load() {
  loading.value = true
  error.value = false
  try {
    await loginIfNeeded()
  } catch (requestError) {
    error.value = true
  } finally {
    loading.value = false
  }
}

onShow(load)
</script>

<style scoped>
.page { min-height: 100vh; background: var(--c-bg); }
.profile-head { min-height: 140px; padding: 28px 20px; box-sizing: border-box; display: flex; align-items: center; background: var(--c-text); color: #fff; }
.avatar { width: 66px; height: 66px; flex-shrink: 0; border: 2px solid rgba(255,255,255,.28); border-radius: 50%; background: var(--c-primary); }
.avatar-fallback { display: flex; align-items: center; justify-content: center; font-size: 26px; font-weight: 800; }
.profile-copy { min-width: 0; margin-left: 16px; }
.nickname { overflow: hidden; font-size: var(--font-xl); font-weight: 800; text-overflow: ellipsis; white-space: nowrap; }
.profile-note { margin-top: 4px; color: #c8c3bd; font-size: var(--font-xs); }
.menu-section { margin-top: 10px; padding: 0 16px; background: var(--c-bg-card); border-top: 1px solid var(--c-border-light); border-bottom: 1px solid var(--c-border-light); }
.menu-row { min-height: 76px; display: flex; align-items: center; justify-content: space-between; border-bottom: 1px solid var(--c-border-light); }
.menu-row:last-child { border-bottom: 0; }
.menu-title { font-size: var(--font-md); font-weight: 700; }
.menu-copy { margin-top: 3px; color: var(--c-text-placeholder); font-size: 10px; }
.chevron { color: var(--c-text-placeholder); font-size: 25px; }
.store-info { margin-top: 10px; padding: 18px 16px; background: var(--c-bg-card); border-top: 1px solid var(--c-border-light); border-bottom: 1px solid var(--c-border-light); }
.store-title { margin-bottom: 8px; font-size: var(--font-md); font-weight: 800; }
.store-line { min-height: 38px; display: flex; align-items: center; justify-content: space-between; color: var(--c-text-secondary); font-size: var(--font-xs); }
.store-line text:first-child { color: var(--c-text-placeholder); }
.menu-row:active { opacity: .72; }
</style>
