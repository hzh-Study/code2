<template>
  <div class="dashboard" v-loading="loading">
    <header class="page-intro">
      <div>
        <p class="date-label">{{ todayLabel }}</p>
        <h1>经营看板</h1>
      </div>
      <el-button plain :loading="loading" :disabled="loading" @click="load">刷新数据</el-button>
    </header>

    <div v-if="error && !loading" class="request-state" role="alert">
      <strong>经营数据加载失败</strong><span>请检查网络连接后重新尝试</span><el-button type="primary" @click="load">重新加载</el-button>
    </div>
    <template v-else>
    <section class="metrics" aria-label="今日关键指标">
      <div class="metric">
        <span class="metric-label">今日订单数</span>
        <strong>{{ stats.today_orders }}</strong>
        <small>今日创建的全部订单</small>
      </div>
      <div class="metric">
        <span class="metric-label">今日销售额</span>
        <strong>¥{{ Number(stats.today_sales || 0).toFixed(2) }}</strong>
        <small>今日已支付订单合计</small>
      </div>
      <div class="metric">
        <span class="metric-label">在售菜品数</span>
        <strong>{{ stats.on_sale_dishes }}</strong>
        <small>当前可供顾客下单</small>
      </div>
    </section>

    <section class="work-row">
      <div class="pending-panel">
        <div class="section-heading">
          <div>
            <h2>待处理</h2>
            <p>优先跟进需要出餐的订单</p>
          </div>
          <el-button text type="primary" @click="$router.push('/orders')">查看订单</el-button>
        </div>
        <div class="pending-value">
          <span>{{ pendingOrders }}</span>
          <div><strong>笔待出餐</strong><small>请及时确认并完成出餐</small></div>
        </div>
      </div>
      <div class="status-panel">
        <div class="status-item"><span>待支付</span><strong>{{ statusCounts.pendingPay }}</strong></div>
        <div class="status-item"><span>待出餐</span><strong class="accent">{{ statusCounts.pendingMeal }}</strong></div>
        <div class="status-item"><span>已完成</span><strong>{{ statusCounts.completed }}</strong></div>
      </div>
    </section>

    <section class="table-panel">
      <div class="section-heading table-heading">
        <div>
          <h2>最近订单</h2>
          <p>最近 {{ recent.length }} 笔订单的履约状态</p>
        </div>
        <el-button text type="primary" @click="$router.push('/orders')">全部订单</el-button>
      </div>
      <div class="table-scroll">
      <el-table :data="recent" :empty-text="loading ? '正在加载' : '暂无近期订单'">
        <el-table-column prop="order_no" label="订单号" width="200">
          <template #default="{ row }">
            <span class="order-no">{{ row.order_no }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="username" label="用户" width="120" />
        <el-table-column prop="dining_mode_label" label="方式" width="90">
          <template #default="{ row }">
            <span class="mode-label">{{ row.dining_mode_label }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="total_amount" label="金额" width="110">
          <template #default="{ row }">
            <span class="amount">¥{{ Number(row.total_amount || 0).toFixed(2) }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="status_label" label="状态" width="100">
          <template #default="{ row }">
            <span class="status-pill" :class="statusClass(row.status)">{{ row.status_label }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="下单时间" />
      </el-table>
      </div>
    </section>
    </template>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { dashboard } from '@/api/order'
import { useAutoRefresh } from '@/composables/useAutoRefresh'

const loading = ref(false)
const stats = ref({ today_orders: 0, today_sales: 0, on_sale_dishes: 0 })
const recent = ref([])
const error = ref(false)
const statusCounts = ref({ pendingPay: 0, pendingMeal: 0, completed: 0 })

const todayLabel = new Intl.DateTimeFormat('zh-CN', { year: 'numeric', month: 'long', day: 'numeric', weekday: 'long' }).format(new Date())
const pendingOrders = computed(() => statusCounts.value.pendingMeal)

function statusClass(status) {
  return { 1: 'is-neutral', 2: 'is-warning', 3: 'is-success', 4: 'is-muted' }[status] || 'is-neutral'
}

async function load() {
  loading.value = true
  error.value = false
  try {
    const data = await dashboard() || {}
    stats.value = {
      today_orders: data.today_orders || 0,
      today_sales: data.today_sales || 0,
      on_sale_dishes: data.on_sale_dishes || 0
    }
    const counts = data.status_counts || {}
    statusCounts.value = {
      pendingPay: Number(counts.pending_pay || 0),
      pendingMeal: Number(counts.pending_meal || 0),
      completed: Number(counts.completed || 0)
    }
    recent.value = data.recent_orders || []
  } catch (e) {
    error.value = true
  } finally {
    loading.value = false
  }
}

useAutoRefresh(load, 5000)

onMounted(() => {
  load()
})
</script>

<style scoped>
.dashboard { max-width: 1440px; margin: 0 auto; min-height: 240px; }
.page-intro { display: flex; align-items: flex-end; justify-content: space-between; margin-bottom: var(--space-xl); }
.page-intro h1 { margin: 4px 0 0; font-size: var(--font-size-2xl); }
.date-label { margin: 0; color: var(--text-muted); font-size: var(--font-size-sm); }
.metrics { display: grid; grid-template-columns: repeat(3, 1fr); background: var(--bg-elevated); border: 1px solid var(--border-light); border-radius: var(--radius-lg); margin-bottom: var(--space-lg); }
.metric { position: relative; padding: 24px 28px; min-width: 0; }
.metric + .metric::before { content: ''; position: absolute; left: 0; top: 22px; bottom: 22px; width: 1px; background: var(--border-light); }
.metric-label { display: block; color: var(--text-secondary); font-size: var(--font-size-sm); }
.metric strong { display: block; margin: 8px 0 4px; font-size: clamp(28px, 3vw, 38px); line-height: 1.2; }
.metric small, .section-heading p, .pending-value small { display: block; color: var(--text-muted); font-size: var(--font-size-xs); }
.work-row { display: grid; grid-template-columns: minmax(280px, 1.1fr) minmax(320px, 1fr); gap: var(--space-lg); margin-bottom: var(--space-lg); }
.pending-panel, .status-panel, .table-panel { background: var(--bg-elevated); border: 1px solid var(--border-light); border-radius: var(--radius-lg); }
.pending-panel { padding: var(--space-lg) var(--space-xl); }
.section-heading { display: flex; align-items: center; justify-content: space-between; gap: var(--space-md); }
.section-heading h2 { margin: 0 0 3px; font-size: var(--font-size-lg); }
.section-heading p { margin: 0; }
.pending-value { display: flex; align-items: center; gap: var(--space-md); margin-top: var(--space-xl); }
.pending-value > span { color: var(--brand); font-size: 42px; font-weight: var(--font-weight-bold); line-height: 1; }
.pending-value strong { display: block; font-size: var(--font-size-sm); margin-bottom: 3px; }
.status-panel { display: grid; grid-template-columns: repeat(3, 1fr); align-items: center; padding: var(--space-lg); }
.status-item { text-align: center; padding: var(--space-sm); }
.status-item + .status-item { border-left: 1px solid var(--border-light); }
.status-item span { display: block; color: var(--text-muted); font-size: var(--font-size-xs); }
.status-item strong { display: block; margin-top: var(--space-xs); font-size: var(--font-size-xl); }
.status-item .accent { color: var(--brand); }
.table-panel { padding: var(--space-lg) var(--space-xl) var(--space-sm); }
.table-heading { margin-bottom: var(--space-md); }
.table-scroll { overflow-x: auto; }
.table-scroll .el-table { min-width: 760px; }
.order-no { font-family: var(--font-mono); font-size: var(--font-size-sm); color: var(--text-secondary); }
.amount { font-weight: var(--font-weight-semibold); color: var(--text); }
.mode-label { color: var(--text-secondary); }
@media (max-width: 900px) { .work-row { grid-template-columns: 1fr; } }
@media (max-width: 680px) {
  .metrics { grid-template-columns: 1fr; }
  .metric { padding: var(--space-lg); }
  .metric + .metric::before { left: var(--space-lg); right: var(--space-lg); top: 0; bottom: auto; width: auto; height: 1px; }
  .status-panel { padding: var(--space-sm); }
  .table-panel { padding: var(--space-md) var(--space-sm) var(--space-xs); }
  .page-intro { align-items: center; }
}
</style>
