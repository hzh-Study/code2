<template>
  <view class="page" v-if="order">
    <!-- 状态头部 -->
    <view class="status-header" :class="'sh' + order.status">
      <view class="status-icon">
        <text v-if="order.status === 1">💳</text>
        <text v-else-if="order.status === 2">🍳</text>
        <text v-else-if="order.status === 3">✅</text>
        <text v-else>❌</text>
      </view>
      <view class="status-label">{{ statusLabel(order.status) }}</view>
    </view>

    <view class="card">
      <view class="section-title">订单信息</view>
      <view class="meta">
        <view class="meta-row">
          <text class="meta-key">订单号</text>
          <text class="meta-val">{{ order.order_no }}</text>
        </view>
        <view class="meta-row">
          <text class="meta-key">下单时间</text>
          <text class="meta-val">{{ order.created_at }}</text>
        </view>
        <view class="meta-row">
          <text class="meta-key">用餐方式</text>
          <text class="meta-val">{{ order.dining_mode === 1 ? '堂食' : '打包' }}</text>
        </view>
        <view class="meta-row" v-if="order.address">
          <text class="meta-key">配送地址</text>
          <text class="meta-val">{{ order.address }}</text>
        </view>
      </view>
    </view>

    <view class="card">
      <view class="section-title">菜品明细</view>
      <view v-for="it in order.items" :key="it.id" class="line">
        <text class="item-name">{{ it.dish_name }} x{{ it.quantity }}</text>
        <text class="item-amt">¥{{ Number(it.subtotal || 0).toFixed(2) }}</text>
      </view>
      <view class="line total-line">
        <text>合计</text>
        <text class="amt">¥{{ Number(order.total_amount || 0).toFixed(2) }}</text>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref } from 'vue'
import { onLoad } from '@dcloudio/uni-app'
import { loginIfNeeded } from '../../store/user'
import { getOrderDetail } from '../../api'

const order = ref(null)
function statusLabel(s) {
  return { 1: '待支付', 2: '待出餐', 3: '已完成', 4: '已取消' }[s] || ''
}

onLoad(async (opts) => {
  if (!opts || !opts.id) {
    uni.showToast({ title: '参数错误', icon: 'none' })
    setTimeout(() => uni.navigateBack(), 800)
    return
  }
  try {
    await loginIfNeeded()
    order.value = await getOrderDetail(opts.id)
  } catch (e) {
    uni.showToast({ title: '加载失败', icon: 'none' })
  }
})
</script>

<style scoped>
.page { padding-bottom: var(--sp-20); min-height: 100vh; background: var(--c-bg); }

/* ── 状态头部 ── */
.status-header {
  display: flex; flex-direction: column; align-items: center;
  padding: var(--sp-24) var(--sp-16) var(--sp-20);
}
.status-icon { font-size: 44px; margin-bottom: var(--sp-10); }
.status-label { font-size: var(--font-xl); font-weight: 800; letter-spacing: 0.5px; }
.sh1 .status-label { color: var(--c-warning); }
.sh2 .status-label { color: var(--c-primary); }
.sh3 .status-label { color: var(--c-success); }
.sh4 .status-label { color: var(--c-text-placeholder); }

/* ── 卡片 ── */
.card {
  background: var(--c-bg-card);
  border-radius: var(--r-lg);
  padding: var(--sp-20);
  margin: 0 var(--sp-12) var(--sp-12);
  box-shadow: var(--shadow-sm);
}
.section-title {
  font-weight: 700; font-size: var(--font-md);
  margin-bottom: var(--sp-16);
  padding-bottom: var(--sp-10);
  border-bottom: 1px solid var(--c-border-light);
}

/* ── 订单信息（key-value 表格布局）── */
.meta { display: flex; flex-direction: column; gap: var(--sp-12); }
.meta-row { display: flex; justify-content: space-between; align-items: baseline; }
.meta-key { font-size: var(--font-sm); color: var(--c-text-secondary); flex-shrink: 0; margin-right: var(--sp-12); }
.meta-val { font-size: var(--font-sm); color: var(--c-text); text-align: right; flex: 1; word-break: break-all; }

/* ── 菜品明细 ── */
.line {
  display: flex; justify-content: space-between;
  padding: var(--sp-10) 0;
  font-size: var(--font-base);
}
.item-name { color: var(--c-text-secondary); flex: 1; }
.item-amt { font-weight: 600; color: var(--c-text); }
.total-line {
  border-top: 1.5px dashed var(--c-border);
  margin-top: var(--sp-8);
  font-weight: 700; color: var(--c-text);
  padding-top: var(--sp-12);
}
.amt { color: var(--c-primary); font-weight: 800; font-size: var(--font-lg); }
</style>
