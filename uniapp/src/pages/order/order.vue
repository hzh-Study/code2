<template>
  <view class="page">
    <view class="card">
      <view class="section-title">用餐方式</view>
      <view class="mode-row">
        <view class="mode" :class="{ active: diningMode === 1 }" @click="diningMode = 1">🍽 堂食</view>
        <view class="mode" :class="{ active: diningMode === 2 }" @click="diningMode = 2">🥡 打包</view>
      </view>
      <input
        v-if="diningMode === 2"
        class="addr"
        v-model="address"
        placeholder="请输入配送地址 / 联系电话"
      />
    </view>

    <view class="card">
      <view class="section-title">订单明细</view>
      <view v-for="it in items" :key="it.id" class="line">
        <text class="line-name">{{ it.name }} x{{ it.quantity }}</text>
        <text class="line-amt">¥{{ Number(it.subtotal).toFixed(2) }}</text>
      </view>
      <view class="line total-line">
        <text>合计</text>
        <text class="amt">¥{{ total.toFixed(2) }}</text>
      </view>
    </view>

    <view class="footer" :class="{ disabled: submitting }" @click="submit">提交订单 · ¥{{ total.toFixed(2) }}</view>
  </view>
</template>

<script setup>
import { ref } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import { loginIfNeeded } from '../../store/user'
import { getCart, createOrder, simulatePay } from '../../api'

const items = ref([])
const total = ref(0)
const diningMode = ref(1)
const address = ref('')
const submitting = ref(false)

async function loadCart() {
  // 修复：接口可能返回 null/undefined，兜底为空数组避免 reduce 报错
  items.value = await getCart() || []
  total.value = items.value.reduce((s, it) => s + Number(it.subtotal), 0)
}

async function submit() {
  if (submitting.value) return
  if (!items.value.length) return uni.showToast({ title: '购物车为空', icon: 'none' })
  if (diningMode.value === 2 && !address.value.trim())
    return uni.showToast({ title: '请填写配送地址', icon: 'none' })
  submitting.value = true
  // 修复：真实微信支付在回调中释放锁，finally 不应提前释放
  let keepLocked = false
  try {
    const res = await createOrder(diningMode.value, address.value.trim() || null)
    const { order_no, pay_params } = res

    // 开发模式 / 无微信环境：直接模拟支付回调完成下单
    if (pay_params && pay_params.dev) {
      try {
        await simulatePay(order_no)
        uni.showToast({ title: '下单成功', icon: 'success' })
        setTimeout(() => uni.switchTab({ url: '/pages/orders/orders' }), 800)
      } catch (e) {
        uni.showToast({ title: '支付失败，请到订单中重试', icon: 'none' })
        setTimeout(() => uni.switchTab({ url: '/pages/orders/orders' }), 1000)
      }
      return
    }

    if (!pay_params) {
      uni.showToast({ title: '支付参数异常', icon: 'none' })
      return
    }

    // 微信环境：拉起微信支付
    keepLocked = true
    uni.requestPayment({
      ...pay_params,
      success: () => {
        submitting.value = false
        uni.showToast({ title: '支付成功', icon: 'success' })
        setTimeout(() => uni.switchTab({ url: '/pages/orders/orders' }), 800)
      },
      fail: () => {
        submitting.value = false
        uni.showToast({ title: '支付未完成，可去订单列表重试', icon: 'none' })
        setTimeout(() => uni.switchTab({ url: '/pages/orders/orders' }), 1000)
      }
    })
  } catch (e) {
    // createOrder failed, request.js already showed toast
  } finally {
    if (!keepLocked) submitting.value = false
  }
}

onShow(async () => {
  try {
    await loginIfNeeded()
  } catch (e) {
    uni.showToast({ title: '登录失败，请重试', icon: 'none' })
    return
  }
  await loadCart()
})
</script>

<style scoped>
.page { padding-bottom: 80px; min-height: 100vh; background: var(--c-bg); }

/* ── 卡片 ── */
.card {
  background: var(--c-bg-card);
  border-radius: var(--r-lg);
  padding: var(--sp-20);
  margin: var(--sp-12);
  box-shadow: var(--shadow-sm);
}
.section-title {
  font-weight: 700; font-size: var(--font-md);
  margin-bottom: var(--sp-16);
  padding-bottom: var(--sp-10);
  border-bottom: 1px solid var(--c-border-light);
}

/* ── 用餐方式 ── */
.mode-row { display: flex; gap: var(--sp-12); }
.mode {
  flex: 1; text-align: center;
  padding: var(--sp-16) 0;
  border-radius: var(--r-md);
  background: var(--c-bg-soft);
  color: var(--c-text-secondary);
  font-weight: 600; font-size: var(--font-base);
  transition: all .25s var(--ease);
}
.mode.active {
  background: var(--c-primary); color: var(--c-text-inverse);
  box-shadow: 0 2px 10px rgba(232,93,44,.3);
}
.addr {
  margin-top: var(--sp-16);
  background: var(--c-bg-soft); border: 1px solid var(--c-border-light);
  border-radius: var(--r-sm); padding: var(--sp-12) var(--sp-16);
  font-size: var(--font-base);
}

/* ── 订单明细 ── */
.line {
  display: flex; justify-content: space-between;
  padding: var(--sp-10) 0;
  font-size: var(--font-base); color: var(--c-text-secondary);
}
.line-name { flex: 1; }
.line-amt { font-weight: 600; color: var(--c-text); }
.total-line {
  border-top: 1.5px dashed var(--c-border);
  margin-top: var(--sp-8);
  font-weight: 700; color: var(--c-text);
  padding-top: var(--sp-12);
}
.amt { color: var(--c-primary); font-weight: 800; font-size: var(--font-lg); }

/* ── 底部提交按钮 ── */
.footer {
  position: fixed; bottom: 0; left: 0; right: 0;
  height: 60px;
  background: linear-gradient(135deg, var(--c-primary), var(--c-primary-light));
  color: var(--c-text-inverse);
  text-align: center; line-height: 60px;
  font-weight: 700; font-size: var(--font-md);
  letter-spacing: 0.5px;
  box-shadow: 0 -2px 16px rgba(232,93,44,.25);
  transition: opacity .2s var(--ease);
}
.footer:active { opacity: .85; }
.footer.disabled { opacity: .5; pointer-events: none; }
</style>
