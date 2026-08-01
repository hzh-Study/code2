<template>
  <view class="page">
    <view class="tabs">
      <view
        v-for="t in tabs"
        :key="t.value"
        class="tab"
        :class="{ active: active === t.value }"
        @click="switchTab(t.value)"
      >
        <text class="tab-label">{{ t.label }}</text>
        <view v-if="active === t.value" class="tab-indicator"></view>
      </view>
    </view>

    <view v-if="!orders.length" class="empty">
      <view class="empty-icon">📋</view>
      <view class="empty-text">暂无订单</view>
      <view class="empty-hint">下单后会在这里展示哦</view>
    </view>

    <view v-for="o in orders" :key="o.id" class="order-card" @click="goDetail(o.id)">
      <view class="oc-head">
        <text class="oc-no">订单号 {{ o.order_no }}</text>
        <view class="oc-status-wrap" :class="'s' + o.status">
          <text class="oc-status">{{ statusLabel(o.status) }}</text>
        </view>
      </view>
      <view class="oc-detail" v-if="o.detail">{{ o.detail }}</view>
      <view class="oc-foot">
        <text class="oc-amount">¥{{ Number(o.total_amount || 0).toFixed(2) }}</text>
        <view class="oc-actions" @click.stop>
          <text v-if="o.status === 1" class="act pay" @click="pay(o)">去支付</text>
          <text v-if="o.status === 1" class="act cancel" @click="cancel(o)">取消</text>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import { loginIfNeeded } from '../../store/user'
import { getOrders, repayOrder, simulatePay, cancelOrder } from '../../api'

const tabs = [
  { label: '全部', value: null },
  { label: '待支付', value: 1 },
  { label: '待出餐', value: 2 },
  { label: '已完成', value: 3 }
]
const active = ref(null)
const orders = ref([])

function statusLabel(s) {
  return { 1: '待支付', 2: '待出餐', 3: '已完成', 4: '已取消' }[s] || ''
}
let loadSeq = 0
async function load() {
  const seq = ++loadSeq
  try {
    const data = await getOrders(active.value)
    if (seq !== loadSeq) return
    orders.value = data
  } catch (e) {}
}
function switchTab(v) {
  active.value = v
  load()
}
function goDetail(id) {
  uni.navigateTo({ url: `/pages/orders/detail?id=${id}` })
}
async function pay(o) {
  try {
    const res = await repayOrder(o.id)
    if (!res || !res.pay_params) {
      uni.showToast({ title: '支付参数异常', icon: 'none' })
      return
    }
    if (res.pay_params.dev) {
      try {
        await simulatePay(res.order_no)
        uni.showToast({ title: '支付成功', icon: 'success' })
      } catch (e) {
        uni.showToast({ title: '支付失败', icon: 'none' })
      }
      load()
    } else {
      uni.requestPayment({
        ...res.pay_params,
        success: () => { uni.showToast({ title: '支付成功', icon: 'success' }); load() },
        fail: () => uni.showToast({ title: '支付未完成', icon: 'none' })
      })
    }
  } catch (e) {}
}
async function cancel(o) {
  const ok = await new Promise((r) => uni.showModal({
    title: '确认取消',
    content: `取消订单 ${o.order_no}？`,
    success: (res) => r(res.confirm)
  }))
  if (!ok) return
  try {
    await cancelOrder(o.id)
    uni.showToast({ title: '已取消', icon: 'none' })
    load()
  } catch (e) {}
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
.page { padding-bottom: var(--sp-20); min-height: 100vh; background: var(--c-bg); }

/* ── 顶部选项卡 ── */
.tabs {
  display: flex; background: var(--c-bg-card);
  padding: var(--sp-12) 0;
  position: sticky; top: 0; z-index: 10;
  box-shadow: var(--shadow-sm);
}
.tab {
  flex: 1; text-align: center;
  padding: var(--sp-8) 0;
  display: flex; flex-direction: column; align-items: center;
  position: relative;
}
.tab-label { font-size: var(--font-base); color: var(--c-text-secondary); transition: all .25s var(--ease); }
.tab.active .tab-label { color: var(--c-primary); font-weight: 700; }
.tab-indicator {
  width: 20px; height: 3px; border-radius: var(--r-full);
  background: var(--c-primary); margin-top: var(--sp-4);
}

/* ── 空状态 ── */
.empty {
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  padding-top: 160px;
}
.empty-icon { font-size: 48px; opacity: .6; margin-bottom: var(--sp-16); }
.empty-text { font-size: var(--font-lg); font-weight: 700; color: var(--c-text-secondary); }
.empty-hint { font-size: var(--font-sm); color: var(--c-text-placeholder); margin-top: var(--sp-8); }

/* ── 订单卡片 ── */
.order-card {
  background: var(--c-bg-card);
  border-radius: var(--r-lg);
  padding: var(--sp-16) var(--sp-20);
  margin: var(--sp-10) var(--sp-12);
  box-shadow: var(--shadow-sm);
  transition: transform .2s var(--ease);
}
.order-card:active { transform: scale(.98); }
.oc-head { display: flex; justify-content: space-between; align-items: center; }
.oc-no { font-size: var(--font-sm); color: var(--c-text-secondary); }
.oc-status-wrap {
  padding: var(--sp-4) var(--sp-10);
  border-radius: var(--r-full);
  font-size: var(--font-xs); font-weight: 600;
}
.oc-status { font-size: var(--font-xs); font-weight: 700; }

/* 状态颜色胶囊 */
.s1 { background: var(--c-accent-bg); }
.s1 .oc-status { color: var(--c-warning); }
.s2 { background: var(--c-primary-bg); }
.s2 .oc-status { color: var(--c-primary); }
.s3 { background: #e8f5e9; }
.s3 .oc-status { color: var(--c-success); }
.s4 { background: #f5f5f5; }
.s4 .oc-status { color: var(--c-text-placeholder); }

.oc-detail {
  color: var(--c-text-secondary); font-size: var(--font-sm);
  margin: var(--sp-10) 0;
  overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
}
.oc-foot { display: flex; justify-content: space-between; align-items: center; }
.oc-amount { color: var(--c-primary); font-weight: 800; font-size: var(--font-md); }
.oc-actions { display: flex; gap: var(--sp-10); }
.act {
  font-size: var(--font-sm); padding: var(--sp-8) var(--sp-16); border-radius: var(--r-full);
  transition: transform .15s var(--ease);
}
.act:active { transform: scale(.92); }
.pay {
  background: var(--c-primary); color: var(--c-text-inverse);
  box-shadow: 0 2px 8px rgba(232,93,44,.3);
}
.cancel { border: 1px solid var(--c-border); color: var(--c-text-secondary); }
</style>
