<template>
  <section class="page-panel">
      <div class="page-head">
        <div><h1>分类管理</h1><p>分类按排序值从小到大展示，共 {{ list.length }} 个分类</p></div>
        <el-button type="primary" :icon="Plus" :disabled="loading" @click="openCreate">新增分类</el-button>
      </div>
    <div v-if="error && !loading" class="request-state" role="alert"><strong>分类加载失败</strong><span>请检查网络连接后重新尝试</span><el-button type="primary" @click="load">重新加载</el-button></div>
    <div v-else class="table-scroll">
    <el-table :data="list" v-loading="loading" class="data-table" empty-text="暂无分类">
      <el-table-column prop="id" label="编号" width="100" />
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
            <el-button text type="danger" :loading="deletingId === row.id" :disabled="deletingId !== null" @click="onDelete(row)">删除</el-button>
          </div>
        </template>
      </el-table-column>
    </el-table>
    </div>

    <el-dialog v-model="dialogVisible" :title="form.id ? '编辑分类' : '新增分类'"
      width="min(440px, calc(100vw - 24px))" class="custom-dialog" :before-close="beforeDialogClose"
      :close-on-click-modal="!saving" :close-on-press-escape="!saving" :show-close="!saving">
      <el-form label-width="80px" class="dialog-form" :disabled="saving">
        <el-form-item label="名称">
          <el-input v-model="form.name" placeholder="如：招牌硬菜" />
        </el-form-item>
        <el-form-item label="排序">
          <el-input-number v-model="form.sort_order" :min="0" />
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button :disabled="saving" @click="closeDialog">取消</el-button>
          <el-button type="primary" :loading="saving" @click="onSave">保存</el-button>
        </div>
      </template>
    </el-dialog>
  </section>
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
const error = ref(false)
const deletingId = ref(null)
const form = reactive({ id: null, name: '', sort_order: 0 })

async function load() {
  loading.value = true
  error.value = false
  try {
    list.value = await listCategories()
  } catch (requestError) {
    error.value = true
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
function closeDialog() {
  if (!saving.value) dialogVisible.value = false
}
function beforeDialogClose(done) {
  if (!saving.value) done()
}
async function onSave() {
  if (saving.value) return
  const name = form.name.trim()
  if (!name) return ElMessage.warning('请输入分类名称')
  form.name = name
  saving.value = true
  try {
    if (form.id) {
      await updateCategory(form.id, { name, sort_order: form.sort_order })
    } else {
      await createCategory({ name, sort_order: form.sort_order })
    }
    ElMessage.success('已保存')
    dialogVisible.value = false
    await load()
  } catch {
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
    deletingId.value = row.id
    await deleteCategory(row.id)
    ElMessage.success('已删除')
    await load()
  } catch {
  } finally {
    deletingId.value = null
  }
}

onMounted(load)
</script>

<style scoped>
.page-panel { background: var(--bg-elevated); border: 1px solid var(--border-light); border-radius: var(--radius-lg); padding: var(--space-xl); max-width: 1200px; margin: 0 auto; }
.page-head { display: flex; justify-content: space-between; align-items: center; gap: var(--space-md); padding-bottom: var(--space-lg); border-bottom: 1px solid var(--border-light); }
.page-head h1 { margin: 0 0 4px; font-size: var(--font-size-xl); }
.page-head p { margin: 0; color: var(--text-muted); font-size: var(--font-size-sm); }
.table-scroll { overflow-x: auto; }
.data-table { min-width: 620px; }

.cell-name {
  font-weight: var(--font-weight-medium);
  color: var(--text);
}

.cell-sort { font-family: var(--font-mono); font-size: var(--font-size-sm); color: var(--text-muted); }

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
@media (max-width: 560px) {
  .page-panel { padding: var(--space-md) var(--space-sm); }
  .page-head { align-items: flex-start; }
  .page-head p { display: none; }
}
</style>
