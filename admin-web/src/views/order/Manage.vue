<template>
  <el-card shadow="never" class="page">
    <template #header>
      <div class="head">
        <div class="filters">
          <el-select v-model="filters.status" placeholder="全部状态" clearable style="width: 130px" @change="resetAndLoad">
            <el-option v-for="(label, val) in STATUS" :key="val" :label="label" :value="Number(val)" />
          </el-select>
          <el-date-picker v-model="dateRange" type="daterange" range-separator="至" start-placeholder="开始日期"
            end-placeholder="结束日期" value-format="YYYY-MM-DD" @change="onDateChange" />
          <el-button :icon="Search" @click="resetAndLoad">查询</el-button>
        </div>
      </div>
    </template>

    <el-table :data="list" stripe v-loading="loading" size="default" class="data-table">
      <el-table-column prop="order_no" label="订单号" width="200">
        <template #default="{ row }">
          <span class="order-no">{{ row.order_no }}</span>
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
          <el-tag size="small" :type="row.dining_mode_label === '堂食' ? '' : 'warning'" effect="plain">{{ row.dining_mode_label }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="金额" width="110">
        <template #default="{ row }">
          <span class="amount">¥{{ Number(row.total_amount || 0).toFixed(2) }}</span>
        </template>
      </el-table-column>
      <el-table-column label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="tagType(row.status)" size="small">{{ row.status_label }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="created_at" label="下单时间" width="170">
        <template #default="{ row }">
          <span class="cell-time">{{ row.created_at }}</span>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="150" fixed="right">
        <template #default="{ row }">
          <div class="action-btns">
            <el-button text type="primary" @click="openDetail(row)">详情</el-button>
            <el-button v-if="Number(row.status) === 2" text type="success" @click="onComplete(row)">标记完成</el-button>
          </div>
        </template>
      </el-table-column>
    </el-table>

    <el-pagination class="pager" layout="total, prev, pager, next" :total="total" :current-page="filters.page"
      :page-size="filters.page_size" @current-change="(p) => { filters.page = p; load() }" />

    <el-dialog v-model="detailVisible" title="订单详情" width="560px" class="detail-dialog">
      <template v-if="detail">
        <el-descriptions :column="2" border class="detail-desc">
          <el-descriptions-item label="订单号">
            <span class="order-no">{{ detail.order_no }}</span>
          </el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="tagType(detail.status)" size="small">{{ detail.status_label }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="用户">{{ detail.username }}</el-descriptions-item>
          <el-descriptions-item label="方式">{{ detail.dining_mode_label }}</el-descriptions-item>
          <el-descriptions-item label="下单时间">{{ detail.created_at }}</el-descriptions-item>
          <el-descriptions-item label="支付时间">{{ detail.paid_at }}</el-descriptions-item>
          <el-descriptions-item label="金额" :span="2">
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
  </el-card>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { Search } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { listOrders, orderDetail, completeOrder } from '@/api/order'

const STATUS = { 1: '待支付', 2: '待出餐', 3: '已完成', 4: '已取消' }
const list = ref([])
const total = ref(0)
const loading = ref(false)
const detailVisible = ref(false)
const detail = ref(null)
const dateRange = ref([])
const filters = reactive({ status: null, start: '', end: '', page: 1, page_size: 12 })

function tagType(status) {
  return { 1: 'warning', 2: 'primary', 3: 'success', 4: 'info' }[status] || ''
}
function onDateChange(val) {
  filters.start = val ? val[0] : ''
  filters.end = val ? val[1] : ''
  resetAndLoad()
}

async function load() {
  loading.value = true
  try {
    const data = await listOrders(filters) || {}
    list.value = data.list || []
    total.value = data.total || 0
  } finally {
    loading.value = false
  }
}
function resetAndLoad() {
  filters.page = 1
  load()
}
async function openDetail(row) {
  detail.value = await orderDetail(row.id)
  detailVisible.value = true
}
async function onComplete(row) {
  try {
    await ElMessageBox.confirm(`确认将订单「${row.order_no}」标记为已完成？`, '提示', { type: 'warning' })
  } catch {
    return
  }
  try {
    await completeOrder(row.id)
    ElMessage.success('已标记完成')
    load()
  } catch { /* */ }
}

onMounted(load)
</script>

<style scoped>
.head {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.filters {
  display: flex;
  gap: var(--space-xs);
  flex-wrap: wrap;
}

.data-table {
  margin-top: 4px;
}

.order-no {
  font-family: var(--font-mono);
  font-size: var(--font-size-sm);
  color: var(--text-secondary);
  background: #faf9f7;
  padding: 2px 8px;
  border-radius: var(--radius-sm);
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

.action-btns {
  display: flex;
  gap: 4px;
}

.pager {
  justify-content: flex-end;
  display: flex;
  margin-top: var(--space-sm);
}

.detail-desc {
  border-radius: var(--radius-md);
  overflow: hidden;
}

.items-table {
  border-radius: var(--radius-md);
  overflow: hidden;
}
</style>
