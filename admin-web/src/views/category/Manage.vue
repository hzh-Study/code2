<template>
  <el-card shadow="never" class="page">
    <template #header>
      <div class="head">
        <span class="page-title">分类管理</span>
        <el-button type="primary" :icon="Plus" @click="openCreate">新增分类</el-button>
      </div>
    </template>
    <el-table :data="list" stripe v-loading="loading" size="default" class="data-table">
      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column prop="name" label="分类名称">
        <template #default="{ row }">
          <span class="cell-name">{{ row.name }}</span>
        </template>
      </el-table-column>
      <el-table-column prop="sort_order" label="排序" width="100">
        <template #default="{ row }">
          <span class="cell-sort">{{ row.sort_order }}</span>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="180" fixed="right">
        <template #default="{ row }">
          <div class="action-btns">
            <el-button text type="primary" @click="openEdit(row)">编辑</el-button>
            <el-button text type="danger" @click="onDelete(row)">删除</el-button>
          </div>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="dialogVisible" :title="form.id ? '编辑分类' : '新增分类'" width="440px" class="custom-dialog">
      <el-form label-width="80px" class="dialog-form">
        <el-form-item label="名称">
          <el-input v-model="form.name" placeholder="如：招牌硬菜" />
        </el-form-item>
        <el-form-item label="排序">
          <el-input-number v-model="form.sort_order" :min="0" />
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" :loading="saving" @click="onSave">保存</el-button>
        </div>
      </template>
    </el-dialog>
  </el-card>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { Plus } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { listCategories, createCategory, updateCategory, deleteCategory } from '@/api/category'

const list = ref([])
const loading = ref(false)
const dialogVisible = ref(false)
const saving = ref(false)
const form = reactive({ id: null, name: '', sort_order: 0 })

async function load() {
  loading.value = true
  try {
    list.value = await listCategories()
  } finally {
    loading.value = false
  }
}

function openCreate() {
  Object.assign(form, { id: null, name: '', sort_order: 0 })
  dialogVisible.value = true
}
function openEdit(row) {
  Object.assign(form, { id: row.id, name: row.name, sort_order: row.sort_order })
  dialogVisible.value = true
}
async function onSave() {
  if (!form.name) return ElMessage.warning('请输入分类名称')
  saving.value = true
  try {
    if (form.id) {
      await updateCategory(form.id, { name: form.name, sort_order: form.sort_order })
    } else {
      await createCategory({ name: form.name, sort_order: form.sort_order })
    }
    ElMessage.success('已保存')
    dialogVisible.value = false
    load()
  } finally {
    saving.value = false
  }
}
async function onDelete(row) {
  try {
    await ElMessageBox.confirm(`确认删除分类「${row.name}」？`, '提示', { type: 'warning' })
  } catch {
    return
  }
  try {
    await deleteCategory(row.id)
    ElMessage.success('已删除')
    load()
  } catch { /* error already handled by request.js */ }
}

onMounted(load)
</script>

<style scoped>
.head {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.page-title {
  font-weight: var(--font-weight-semibold);
  font-size: var(--font-size-md);
  color: var(--text);
}

.data-table {
  margin-top: 4px;
}

.cell-name {
  font-weight: var(--font-weight-medium);
  color: var(--text);
}

.cell-sort {
  font-family: var(--font-mono);
  font-size: var(--font-size-sm);
  color: var(--text-muted);
  background: #faf9f7;
  padding: 2px 10px;
  border-radius: var(--radius-sm);
}

.action-btns {
  display: flex;
  gap: 4px;
}

.dialog-form {
  padding-top: var(--space-sm);
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: var(--space-xs);
}
</style>
