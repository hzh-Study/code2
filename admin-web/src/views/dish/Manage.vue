<template>
  <section class="page-panel">
      <div class="page-head">
        <div><h1>菜品管理</h1><p>集中维护菜品信息、分类与售卖状态</p></div>
        <el-button type="primary" :icon="Plus" :disabled="loading || !categories.length" @click="openCreate">新增菜品</el-button>
      </div>
      <div class="toolbar">
        <div class="filters">
          <el-input
            v-model="filters.keyword"
            placeholder="搜索菜品名称"
            clearable
            :prefix-icon="Search"
            @input="onKeywordInput"
            @clear="resetAndLoad"
          />
          <el-select v-model="filters.category_id" placeholder="全部分类" clearable @change="resetAndLoad">
            <el-option v-for="c in categories" :key="c.id" :label="c.name" :value="c.id" />
          </el-select>
        </div>
        <span class="result-count">共 {{ total }} 道菜品</span>
      </div>
    <div v-if="error && !loading" class="request-state" role="alert"><strong>菜品加载失败</strong><span>请检查网络连接后重新尝试</span><el-button type="primary" @click="load">重新加载</el-button></div>
    <div v-else class="table-scroll">
      <el-table :data="list" v-loading="loading" class="dish-table" empty-text="暂无符合条件的菜品">
        <el-table-column label="#" width="64" align="center">
          <template #default="{ $index }">
            <span class="row-index">{{ (filters.page - 1) * filters.page_size + $index + 1 }}</span>
          </template>
        </el-table-column>
        <el-table-column label="菜品" min-width="260">
          <template #default="{ row }">
            <div class="dish-cell">
              <div class="thumb"><img v-if="row.image" :src="resolveImg(row.image)" :alt="row.name"><span v-else>暂无图片</span></div>
              <div class="dish-copy"><strong>{{ row.name }}</strong><span>{{ row.description || '暂无简介' }}</span></div>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="价格" width="120"><template #default="{ row }"><span class="price">¥{{ Number(row.price || 0).toFixed(2) }}</span></template></el-table-column>
        <el-table-column prop="category_name" label="分类" width="150" />
        <el-table-column label="状态" width="110"><template #default="{ row }"><span class="status-pill" :class="row.status === 1 ? 'is-sale' : 'is-off'">{{ row.status === 1 ? '在售' : '已下架' }}</span></template></el-table-column>
        <el-table-column label="操作" width="220" fixed="right">
          <template #default="{ row }"><div class="action-btns"><el-button text type="primary" :disabled="deletingId !== null || togglingId !== null" @click="openEdit(row)">编辑</el-button><el-button text :loading="togglingId === row.id" :disabled="deletingId !== null || togglingId !== null" @click="onToggle(row)">{{ row.status === 1 ? '下架' : '上架' }}</el-button><el-button text type="danger" :loading="deletingId === row.id" :disabled="deletingId !== null || togglingId !== null" @click="onDelete(row)">删除</el-button></div></template>
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

    <el-dialog v-model="dialogVisible" :title="form.id ? '编辑菜品' : '新增菜品'"
      width="min(520px, calc(100vw - 24px))" class="custom-dialog" :before-close="beforeDialogClose"
      :close-on-click-modal="!formBusy" :close-on-press-escape="!formBusy" :show-close="!formBusy">
      <el-form label-width="80px" class="dialog-form" :disabled="saving">
        <el-form-item label="菜名">
          <el-input v-model="form.name" placeholder="菜品名称" />
        </el-form-item>
        <el-form-item label="价格">
          <el-input-number v-model="form.price" :min="0" :precision="2" :step="1" />
        </el-form-item>
        <el-form-item label="分类">
          <el-select v-model="form.category_id" placeholder="选择分类">
            <el-option v-for="c in categories" :key="c.id" :label="c.name" :value="c.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="图片">
          <el-upload class="avatar-uploader" :show-file-list="false" :auto-upload="true"
            :http-request="onUpload" accept=".jpg,.jpeg,.png,image/jpeg,image/png" :disabled="formBusy" v-loading="uploading">
            <img v-if="form.image" :src="resolveImg(form.image)" class="avatar" />
            <el-icon v-else class="avatar-uploader-icon"><Plus /></el-icon>
          </el-upload>
          <span class="tip">支持 jpg/png，≤2MB</span>
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="form.description" type="textarea" :rows="2" placeholder="一句话卖点" />
        </el-form-item>
        <el-form-item label="状态">
          <el-radio-group v-model="form.status">
            <el-radio :value="1">在售</el-radio>
            <el-radio :value="0">下架</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button :disabled="formBusy" @click="closeDialog">取消</el-button>
          <el-button type="primary" :loading="saving" :disabled="uploading" @click="onSave">保存</el-button>
        </div>
      </template>
    </el-dialog>
  </section>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, reactive, ref } from 'vue'
import { Plus, Search } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { listCategories } from '@/api/category'
import { listDishes, createDish, updateDish, deleteDish, toggleDish, uploadImage } from '@/api/dish'

const categories = ref([])
const list = ref([])
const total = ref(0)
const loading = ref(false)
const dialogVisible = ref(false)
const saving = ref(false)
const uploading = ref(false)
const deletingId = ref(null)
const togglingId = ref(null)
const error = ref(false)
const filters = reactive({ category_id: null, keyword: '', page: 1, page_size: 20 })

const form = reactive({ id: null, name: '', price: 0, category_id: null, image: '', description: '', status: 1 })
const formBusy = computed(() => saving.value || uploading.value)
let loadSeq = 0
let formSession = 0
let keywordTimer = null

function resolveImg(img) {
  if (!img) return ''
  const source = String(img).trim()
  if (/^(?:https?:|data:|blob:)/i.test(source) || source.startsWith('//')) return source

  const staticBase = import.meta.env.VITE_STATIC_BASE?.trim()
  if (staticBase) {
    return `${staticBase.replace(/\/+$/, '')}/${source.replace(/^\/+/, '')}`
  }

  try {
    const apiUrl = new URL(import.meta.env.VITE_API_BASE || '/api', window.location.origin)
    return new URL(source.startsWith('/') ? source : `/${source}`, `${apiUrl.origin}/`).href
  } catch {
    return source
  }
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

async function load() {
  const requestSeq = ++loadSeq
  loading.value = true
  error.value = false
  try {
    const params = Object.fromEntries(
      Object.entries(filters).filter(([_, v]) => v != null && v !== '')
    )
    const data = await listDishes(params) || {}
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

function openCreate() {
  formSession += 1
  Object.assign(form, { id: null, name: '', price: 0, category_id: categories.value[0]?.id || null, image: '', description: '', status: 1 })
  dialogVisible.value = true
}
function openEdit(d) {
  formSession += 1
  Object.assign(form, { id: d.id, name: d.name, price: d.price, category_id: d.category_id, image: d.image, description: d.description, status: d.status })
  dialogVisible.value = true
}
function closeDialog() {
  if (formBusy.value) return
  formSession += 1
  dialogVisible.value = false
}
function beforeDialogClose(done) {
  if (!formBusy.value) {
    formSession += 1
    done()
  }
}
async function onUpload(req) {
  const file = req.file
  if (file.size > 2 * 1024 * 1024) {
    ElMessage.error('图片大小不能超过 2MB')
    return
  }
  if (!['image/jpeg', 'image/png'].includes(file.type)) {
    ElMessage.error('仅支持 jpg/png 图片')
    return
  }
  const session = formSession
  uploading.value = true
  try {
    const fd = new FormData()
    fd.append('file', file)
    const data = await uploadImage(fd)
    if (session !== formSession || !dialogVisible.value) return
    form.image = data.url
    req.onSuccess?.(data)
    ElMessage.success('上传成功')
  } catch (error) {
    req.onError?.(error)
  }
  finally {
    if (session === formSession) uploading.value = false
  }
}
async function onSave() {
  if (formBusy.value) return
  const name = form.name.trim()
  if (!name || !form.category_id) return ElMessage.warning('请填写菜名与分类')
  form.name = name
  saving.value = true
  try {
    const payload = { name, price: form.price, category_id: form.category_id, image: form.image, description: form.description?.trim() || '', status: form.status }
    if (form.id) await updateDish(form.id, payload)
    else await createDish(payload)
    ElMessage.success('已保存')
    formSession += 1
    dialogVisible.value = false
    await load()
  } catch {
  } finally {
    saving.value = false
  }
}
async function onToggle(d) {
  if (togglingId.value !== null || deletingId.value !== null) return
  togglingId.value = d.id
  try {
    const data = await toggleDish(d.id)
    if (data?.status != null) d.status = Number(data.status)
    else await load()
  } catch {
  }
  finally { togglingId.value = null }
}
async function onDelete(d) {
  if (deletingId.value !== null) return
  try {
    await ElMessageBox.confirm(`确认删除「${d.name}」？`, '提示', { type: 'warning' })
  } catch {
    return
  }
  deletingId.value = d.id
  try {
    await deleteDish(d.id)
    ElMessage.success('已删除')
    await load()
  } catch {
  }
  finally { deletingId.value = null }
}

onMounted(async () => {
  try {
    categories.value = await listCategories()
  } catch {
  }
  await load()
})

onBeforeUnmount(() => {
  clearTimeout(keywordTimer)
})
</script>

<style scoped>
.page-panel { background: var(--bg-elevated); border: 1px solid var(--border-light); border-radius: var(--radius-lg); padding: var(--space-xl); max-width: 1440px; margin: 0 auto; }
.page-head { display: flex; justify-content: space-between; align-items: center; gap: var(--space-md); }
.page-head h1 { margin: 0 0 4px; font-size: var(--font-size-xl); }
.page-head p { margin: 0; color: var(--text-muted); font-size: var(--font-size-sm); }
.toolbar { display: flex; align-items: center; justify-content: space-between; gap: var(--space-md); padding: var(--space-lg) 0 var(--space-md); margin-top: var(--space-lg); border-top: 1px solid var(--border-light); }
.filters { display: flex; gap: var(--space-xs); flex-wrap: wrap; }
.filters .el-input { width: 220px; }
.filters .el-select { width: 160px; }
.result-count { color: var(--text-muted); font-size: var(--font-size-sm); white-space: nowrap; }
.table-scroll { overflow-x: auto; }
.dish-table { min-width: 880px; }
.dish-cell { display: flex; align-items: center; gap: var(--space-sm); min-width: 0; }
.thumb { width: 56px; height: 56px; flex: 0 0 auto; border-radius: var(--radius-md); overflow: hidden; background: var(--bg-subtle); display: flex; align-items: center; justify-content: center; color: var(--text-placeholder); font-size: 10px; }
.thumb img { width: 100%; height: 100%; object-fit: cover; }
.dish-copy { min-width: 0; }
.dish-copy strong { display: block; font-size: var(--font-size-base); margin-bottom: 4px; }
.dish-copy span { display: block; max-width: 300px; color: var(--text-muted); font-size: var(--font-size-xs); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.price { color: var(--brand); font-weight: var(--font-weight-semibold); }

.action-btns {
  display: flex;
  gap: 4px;
}

.tip {
  font-size: var(--font-size-xs);
  color: var(--text-muted);
  margin-left: var(--space-xs);
}

.avatar-uploader :deep(.el-upload) {
  border: 2px dashed var(--border);
  border-radius: var(--radius-md);
  width: 100px;
  height: 100px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all var(--duration-fast) var(--ease-out);
  cursor: pointer;
}

.avatar-uploader :deep(.el-upload:hover) {
  border-color: var(--brand);
  background: var(--brand-lighter);
}

.avatar {
  width: 100px;
  height: 100px;
  object-fit: cover;
  border-radius: var(--radius-md);
}

.avatar-uploader-icon {
  font-size: 28px;
  color: var(--text-placeholder);
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

.row-index {
  color: var(--text-muted);
  font-variant-numeric: tabular-nums;
}

.dialog-form {
  padding-top: var(--space-sm);
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: var(--space-xs);
}
@media (max-width: 680px) {
  .page-panel { padding: var(--space-md) var(--space-sm); }
  .page-head { align-items: flex-start; }
  .page-head p, .result-count { display: none; }
  .toolbar { align-items: stretch; }
  .filters { width: 100%; }
  .filters .el-input { width: 100%; }
  .filters .el-select { flex: 1; min-width: 140px; }
  .pager { justify-content: flex-start; overflow-x: auto; }
}
</style>
