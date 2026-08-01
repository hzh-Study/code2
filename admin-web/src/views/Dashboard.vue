<template>
  <div class="dashboard" v-loading="loading">
    <el-row :gutter="20" class="stat-row">
      <el-col :span="8">
        <el-card class="stat-card" :body-style="{ padding: '24px' }">
          <div class="stat-icon-wrap icon-orders">
            <el-icon :size="22"><List /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-label">今日订单</div>
            <div class="stat-value">{{ stats.today_orders }}</div>
            <div class="stat-sub">笔交易</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card class="stat-card" :body-style="{ padding: '24px' }">
          <div class="stat-icon-wrap icon-sales">
            <el-icon :size="22"><Coin /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-label">今日销售额</div>
            <div class="stat-value">¥{{ Number(stats.today_sales || 0).toFixed(2) }}</div>
            <div class="stat-sub">已支付</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card class="stat-card" :body-style="{ padding: '24px' }">
          <div class="stat-icon-wrap icon-dishes">
            <el-icon :size="22"><Dish /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-label">在售菜品</div>
            <div class="stat-value">{{ stats.on_sale_dishes }}</div>
            <div class="stat-sub">道菜品</div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-card class="recent-card">
      <template #header>
        <div class="recent-header">
          <span class="recent-title">最近订单</span>
          <span class="recent-count">共 {{ recent.length }} 条</span>
        </div>
      </template>
      <el-table :data="recent" stripe>
        <el-table-column prop="order_no" label="订单号" width="200">
          <template #default="{ row }">
            <span class="order-no">{{ row.order_no }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="username" label="用户" width="120" />
        <el-table-column prop="dining_mode_label" label="方式" width="90">
          <template #default="{ row }">
            <el-tag size="small" :type="row.dining_mode_label === '堂食' ? '' : 'warning'" effect="plain">{{ row.dining_mode_label }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="total_amount" label="金额" width="110">
          <template #default="{ row }">
            <span class="amount">¥{{ Number(row.total_amount || 0).toFixed(2) }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="status_label" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="statusTagType(row.status_label)" size="small">{{ row.status_label }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="下单时间" />
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { List, Coin, Dish } from '@element-plus/icons-vue'
import { dashboard } from '@/api/order'

const loading = ref(false)
const stats = ref({ today_orders: 0, today_sales: 0, on_sale_dishes: 0 })
const recent = ref([])

function statusTagType(label) {
  if (label && label.includes('取消')) return 'info'
  if (label && label.includes('完成')) return 'success'
  if (label && label.includes('待出')) return 'primary'
  if (label && label.includes('待支付')) return 'warning'
  return ''
}

onMounted(async () => {
  loading.value = true
  try {
    const data = await dashboard() || {}
    stats.value = {
      today_orders: data.today_orders || 0,
      today_sales: data.today_sales || 0,
      on_sale_dishes: data.on_sale_dishes || 0
    }
    recent.value = data.recent_orders || []
  } catch (e) {
    // 错误已在 request.js 统一提示
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.dashboard {
  min-height: 200px;
}

.stat-row {
  margin-bottom: var(--space-lg);
}

.stat-card {
  border-radius: var(--radius-lg);
  overflow: hidden;
  transition: all var(--duration-normal) var(--ease-out);
}

.stat-card:hover {
  transform: translateY(-3px);
}

.stat-card :deep(.el-card__body) {
  display: flex;
  align-items: center;
  gap: var(--space-md);
}

.stat-icon-wrap {
  width: 52px;
  height: 52px;
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  flex-shrink: 0;
}

.icon-orders {
  background: linear-gradient(135deg, #1890ff, #40a9ff);
  box-shadow: 0 4px 14px rgba(24, 144, 255, 0.3);
}

.icon-sales {
  background: var(--brand-gradient);
  box-shadow: 0 4px 14px rgba(232, 93, 44, 0.3);
}

.icon-dishes {
  background: linear-gradient(135deg, #52c41a, #73d13d);
  box-shadow: 0 4px 14px rgba(82, 196, 26, 0.3);
}

.stat-content {
  flex: 1;
  min-width: 0;
}

.stat-label {
  color: var(--text-muted);
  font-size: var(--font-size-sm);
  margin-bottom: 4px;
}

.stat-value {
  font-size: 28px;
  font-weight: var(--font-weight-bold);
  color: var(--text);
  line-height: var(--line-height-tight);
  margin-bottom: 2px;
}

.stat-sub {
  color: var(--text-placeholder);
  font-size: var(--font-size-xs);
}

.recent-card {
  border-radius: var(--radius-lg);
}

.recent-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.recent-title {
  font-weight: var(--font-weight-semibold);
  font-size: var(--font-size-md);
}

.recent-count {
  font-size: var(--font-size-sm);
  color: var(--text-muted);
}

.order-no {
  font-family: var(--font-mono);
  font-size: var(--font-size-sm);
  color: var(--text-secondary);
}

.amount {
  font-weight: var(--font-weight-semibold);
  color: var(--brand);
}
</style>
