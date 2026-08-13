<template>
  <section class="page-panel">
      <div class="page-head"><div><h1>订单管理</h1><p>查看订单详情并跟进出餐状态</p></div><span>共 {{ total }} 笔订单</span></div>
      <div class="toolbar">
        <div class="status-tabs" role="tablist" aria-label="订单状态筛选">
          <button v-for="tab in statusTabs" :key="String(tab.value)" type="button" :class="{ active: filters.status === tab.value }" @click="selectStatus(tab.value)">{{ tab.label }}</button>
        </div>
        <div class="filters">
          <el-input
            v-model="filters.keyword"
            placeholder="搜索订单号"
            clearable
            :prefix-icon="Search"
            @input="onKeywordInput"
            @clear="resetAndLoad"
          />
        </div>
      </div>
    <div v-if="error && !loading" class="request-state" role="alert"><strong>订单加载失败</strong><span>请检查网络连接后重新尝试</span><el-button type="primary" @click="load">重新加载</el-button></div>
    <div v-else class="table-scroll">
    <el-table :data="list" v-loading="loading" class="data-table" empty-text="暂无符合条件的订单">
      <el-table-column label="#" width="64" align="center">
        <template #default="{ $index }">
          <span class="row-index">{{ (filters.page - 1) * filters.page_size + $index + 1 }}</span>
        </template>
      </el-table-column>
      <el-table-column prop="order_no" label="订单号" width="160">
        <template #default="{ row }">
          <button type="button" class="order-no-btn" :title="row.order_no" @click="copyOrderNo(row.order_no)">
            {{ truncateOrderNo(row.order_no) }}
          </button>
        </template>
      </el-table-column>
      <el-table-column prop="username" label="用户" width="110">
        <template #default="{ row }">
          <span class="cell-user">{{ row.username }}</span>
        </template>
      </el-table-column>
      <el-table-column prop="detail" label="菜品" min-width="200" show-overflow-tooltip />
      <el-table-column prop="dining_mode_label" label="方式" width="80">
        <template #default="{ row }">
          <span class="mode-label">{{ row.dining_mode_label }}</span>
        </template>
      </el-table-column>
      <el-table-column label="金额" width="110">
        <template #default="{ row }">
          <span class="amount">¥{{ Number(row.total_amount || 0).toFixed(2) }}</span>
        </template>
      </el-table-column>
      <el-table-column label="状态" width="100">
        <template #default="{ row }">
          <span class="status-pill" :class="statusClass(row.status)">{{ row.status_label }}</span>
        </template>
      </el-table-column>
      <el-table-column prop="created_at" label="下单时间" width="170">
        <template #default="{ row }">
          <span class="cell-time">{{ row.created_at }}</span>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="200" fixed="right">
        <template #default="{ row }">
          <div class="action-btns">
            <el-button size="small" text type="primary" :loading="detailLoadingId === row.id" :disabled="completingId !== null" @click="openDetail(row)">详情</el-button>
            <el-button v-if="Number(row.status) === 2" size="small" type="success" :loading="completingId === row.id" :disabled="completingId !== null" @click="onComplete(row)">标记完成</el-button>
          </div>
        </template>
      </el-table-column>
    </el-table>
    </div>

    <el-pagination
      class="pager"
      layout="total, sizes, prev, pager, next, jumper"
      :total="total"
      :current-page="filters.page"
      :page-size="filters.page_size"
      :page-sizes="[10, 20, 50]"
      @current-change="(p) => { filters.page = p; load() }"
      @size-change="onPageSizeChange"
    />

    <el-dialog v-model="detailVisible" title="订单详情" width="min(620px, calc(100vw - 24px))" class="detail-dialog">
      <template v-if="detail">
        <el-descriptions :column="detailColumns" border class="detail-desc">
          <el-descriptions-item label="订单号">
            <button type="button" class="order-no-btn" :title="detail.order_no" @click="copyOrderNo(detail.order_no)">
              {{ detail.order_no }}
            </button>
          </el-descriptions-item>
          <el-descriptions-item label="状态">
            <span class="status-pill" :class="statusClass(detail.status)">{{ detail.status_label }}</span>
          </el-descriptions-item>
          <el-descriptions-item label="用户">{{ detail.username }}</el-descriptions-item>
          <el-descriptions-item label="方式">{{ detail.dining_mode_label }}</el-descriptions-item>
          <el-descriptions-item label="下单时间">{{ detail.created_at }}</el-descriptions-item>
          <el-descriptions-item label="支付时间">{{ detail.paid_at }}</el-descriptions-item>
          <el-descriptions-item label="金额" :span="detailColumns">
            <span class="amount-lg">¥{{ Number(detail.total_amount).toFixed(2) }}</span>
          </el-descriptions-item>
        </el-descriptions>
        <el-table :data="detail.items" size="small" class="items-table" style="margin-top: 16px">
          <el-table-column prop="dish_name" label="菜品" />
          <el-table-column prop="price" label="单价" width="90">
            <template #default="{ row }">¥{{ Number(row.price).toFixed(2) }}</template>
          </el-table-column>
          <el-table-column prop="quantity" label="数量" width="70" />
          <el-table-column label="小计" width="90">
            <template #default="{ row }">
              <span class="amount">¥{{ Number(row.subtotal).toFixed(2) }}</span>
            </template>
          </el-table-column>
        </el-table>
      </template>
    </el-dialog>
  </section>
</template>

<script setup>
import { onBeforeUnmount, onMounted, reactive, ref } from 'vue'
import { Search } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { listOrders, orderDetail, completeOrder } from '@/api/order'
import { useAutoRefresh } from '@/composables/useAutoRefresh'

const statusTabs = [
  { label: '全部', value: null },
  { label: '待支付', value: 1 },
  { label: '待出餐', value: 2 },
  { label: '已完成', value: 3 },
  { label: '已取消', value: 4 }
]
const list = ref([])
const total = ref(0)
const loading = ref(false)
const detailVisible = ref(false)
const detail = ref(null)
const error = ref(false)
const detailLoadingId = ref(null)
const completingId = ref(null)
const detailColumns = ref(2)
const filters = reactive({ status: null, keyword: '', page: 1, page_size: 20 })
let loadSeq = 0
let mobileDetailQuery = null
let keywordTimer = null

function syncDetailColumns() {
  detailColumns.value = mobileDetailQuery?.matches ? 1 : 2
}

function statusClass(status) {
  return { 1: 'is-neutral', 2: 'is-warning', 3: 'is-success', 4: 'is-muted' }[status] || 'is-muted'
}

function truncateOrderNo(orderNo) {
  const value = String(orderNo || '')
  if (value.length <= 12) return value
  return `${value.slice(0, 6)}…${value.slice(-4)}`
}

async function copyOrderNo(orderNo) {
  const value = String(orderNo || '')
  if (!value) return
  try {
    if (navigator.clipboard?.writeText) {
      await navigator.clipboard.writeText(value)
    } else {
      const input = document.createElement('textarea')
      input.value = value
      input.setAttribute('readonly', '')
      input.style.position = 'fixed'
      input.style.opacity = '0'
      document.body.appendChild(input)
      input.select()
      document.execCommand('copy')
      document.body.removeChild(input)
    }
    ElMessage.success('已复制订单号')
  } catch {
    ElMessage.error('复制失败')
  }
}

function selectStatus(status) {
  filters.status = status
  resetAndLoad()
}

function onKeywordInput() {
  clearTimeout(keywordTimer)
  keywordTimer = setTimeout(() => {
    resetAndLoad()
  }, 300)
}

function onPageSizeChange(size) {
  filters.page_size = size
  filters.page = 1
  load()
}

async function load(silent = false) {
  const requestSeq = ++loadSeq
  if (!silent) loading.value = true
  error.value = false
  try {
    const params = Object.fromEntries(
      Object.entries(filters).filter(([_, v]) => v != null && v !== '')
    )
    const data = await listOrders(params) || {}
    if (requestSeq !== loadSeq) return
    list.value = data.list || []
    total.value = data.total || 0
  } catch (requestError) {
    if (requestSeq === loadSeq) error.value = true
  } finally {
    if (requestSeq === loadSeq) loading.value = false
  }
}
function resetAndLoad() {
  filters.page = 1
  return load()
}
let detailSeq = 0
async function openDetail(row) {
  if (detailLoadingId.value !== null) return
  detailLoadingId.value = row.id
  const seq = ++detailSeq
  try {
    const data = await orderDetail(row.id)
    if (seq !== detailSeq) return  // 已有更新的请求，丢弃旧响应
    detail.value = data
    detailVisible.value = true
  } catch {
  } finally {
    if (seq === detailSeq) detailLoadingId.value = null
  }
}
async function onComplete(row) {
  try {
    await ElMessageBox.confirm(`确认将订单「${row.order_no}」标记为已完成？`, '提示', { type: 'warning' })
  } catch {
    return
  }
  try {
    completingId.value = row.id
    await completeOrder(row.id)
    ElMessage.success('已标记完成')
    await load()
  } catch {
  } finally {
    completingId.value = null
  }
}

onMounted(() => {
  mobileDetailQuery = window.matchMedia('(max-width: 680px)')
  syncDetailColumns()
  mobileDetailQuery.addEventListener('change', syncDetailColumns)
  load()
})

// 后台刷新使用 silent 模式，避免已有数据时显示 loading 蒙层
useAutoRefresh(() => load(true), 5000)

onBeforeUnmount(() => {
  clearTimeout(keywordTimer)
  mobileDetailQuery?.removeEventListener('change', syncDetailColumns)
})
</script>

<style scoped>
.page-panel { background: var(--bg-elevated); border: 1px solid var(--border-light); border-radius: var(--radius-lg); padding: var(--space-xl); max-width: 1480px; margin: 0 auto; }
.page-head { display: flex; justify-content: space-between; align-items: center; gap: var(--space-md); }
.page-head h1 { margin: 0 0 4px; font-size: var(--font-size-xl); }
.page-head p { margin: 0; color: var(--text-muted); font-size: var(--font-size-sm); }
.page-head > span { color: var(--text-muted); font-size: var(--font-size-sm); }
.toolbar { display: flex; align-items: center; justify-content: space-between; gap: var(--space-md); padding: var(--space-lg) 0 var(--space-md); margin-top: var(--space-lg); border-top: 1px solid var(--border-light); }
.status-tabs { display: flex; gap: 4px; overflow-x: auto; }
.status-tabs button { border: 1px solid transparent; background: transparent; color: var(--text-secondary); padding: 8px 14px; border-radius: var(--radius-md); cursor: pointer; white-space: nowrap; }
.status-tabs button:hover { background: var(--bg-subtle); }
.status-tabs button.active { color: var(--brand-dark); background: var(--brand-lighter); border-color: #f6c7b3; font-weight: var(--font-weight-medium); }
.filters { display: flex; gap: var(--space-xs); flex-wrap: wrap; }
.filters .el-input { width: 240px; }
.table-scroll { overflow-x: auto; padding-right: 4px; }
.data-table { min-width: 1080px; }

.row-index {
  color: var(--text-muted);
  font-variant-numeric: tabular-nums;
}

.order-no-btn {
  border: 0;
  padding: 0;
  background: transparent;
  font-family: var(--font-mono);
  font-size: var(--font-size-sm);
  color: var(--brand-dark);
  cursor: pointer;
  text-align: left;
  white-space: nowrap;
}

.order-no-btn:hover {
  text-decoration: underline;
}

.cell-user {
  font-weight: var(--font-weight-medium);
}

.cell-time {
  font-size: var(--font-size-sm);
  color: var(--text-muted);
}

.amount {
  font-weight: var(--font-weight-semibold);
  color: var(--brand);
}

.amount-lg {
  font-weight: var(--font-weight-bold);
  color: var(--brand);
  font-size: var(--font-size-lg);
}
.mode-label { color: var(--text-secondary); white-space: nowrap; }

.action-btns {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  row-gap: 4px;
}

.pager {
  justify-content: flex-end;
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: var(--space-md);
  padding-top: var(--space-md);
  border-top: 1px solid var(--border-light);
}

.detail-desc {
  border-radius: var(--radius-md);
  overflow: hidden;
}

.items-table {
  border-radius: var(--radius-md);
  overflow: hidden;
}
@media (max-width: 980px) {
  .toolbar { align-items: stretch; flex-direction: column; }
  .filters { justify-content: flex-end; }
}
@media (max-width: 680px) {
  .page-panel { padding: var(--space-md) var(--space-sm); }
  .page-head p, .page-head > span { display: none; }
  .filters { justify-content: flex-start; width: 100%; }
  .filters .el-input { width: 100%; }
  .pager { justify-content: flex-start; overflow-x: auto; }
  .detail-desc :deep(.el-descriptions__label) { width: 78px; white-space: nowrap; }
  .detail-desc :deep(.el-descriptions__content) { min-width: 0; overflow-wrap: anywhere; }
}
</style>
