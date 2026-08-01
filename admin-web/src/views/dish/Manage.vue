<template>
  <el-card shadow="never" class="page">
    <template #header>
      <div class="head">
        <div class="filters">
          <el-select v-model="filters.category_id" placeholder="全部分类" clearable style="width: 150px" @change="resetAndLoad">
            <el-option v-for="c in categories" :key="c.id" :label="c.name" :value="c.id" />
          </el-select>
          <el-input v-model="filters.keyword" placeholder="搜索菜名" clearable style="width: 180px" @keyup.enter="resetAndLoad" @clear="resetAndLoad" />
          <el-button :icon="Search" @click="resetAndLoad">查询</el-button>
        </div>
        <el-button type="primary" :icon="Plus" @click="openCreate">新增菜品</el-button>
      </div>
    </template>

    <el-row :gutter="20" v-loading="loading">
      <el-col v-for="d in list" :key="d.id" :xs="12" :sm="8" :md="6" :lg="6" class="card-col">
        <el-card shadow="hover" class="dish-card" :body-style="{ padding: '0' }">
          <div class="thumb" :style="{ backgroundImage: d.image ? `url(${resolveImg(d.image)})` : 'none' }">
            <span v-if="d.status === 0" class="off-tag">已下架</span>
          </div>
          <div class="info">
            <div class="name">{{ d.name }}</div>
            <div class="meta">
              <span class="price">¥{{ Number(d.price || 0).toFixed(2) }}</span>
              <span class="cat">{{ d.category_name }}</span>
            </div>
            <div class="desc">{{ d.description }}</div>
            <div class="actions">
              <el-switch :model-value="d.status === 1" @change="onToggle(d)" active-text="在售" inactive-text="下架" inline-prompt />
              <div class="action-btns">
                <el-button text type="primary" @click="openEdit(d)">编辑</el-button>
                <el-button text type="danger" @click="onDelete(d)">删除</el-button>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-pagination class="pager" layout="total, prev, pager, next" :total="total" :current-page="filters.page"
      :page-size="filters.page_size" @current-change="(p) => { filters.page = p; load() }" />

    <el-dialog v-model="dialogVisible" :title="form.id ? '编辑菜品' : '新增菜品'" width="520px" class="custom-dialog">
      <el-form label-width="80px" class="dialog-form">
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
            :http-request="onUpload" accept="image/*" v-loading="uploading">
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
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" :loading="saving" @click="onSave">保存</el-button>
        </div>
      </template>
    </el-dialog>
  </el-card>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
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
const deleting = ref(false)
const filters = reactive({ category_id: null, keyword: '', page: 1, page_size: 12 })

const form = reactive({ id: null, name: '', price: 0, category_id: null, image: '', description: '', status: 1 })

function resolveImg(path) {
  if (!path) return ''
  if (path.startsWith('http')) return path
  return `${import.meta.env.VITE_API_BASE ? import.meta.env.VITE_API_BASE.replace(/\/api$/, '') : ''}${path}`
}

async function load() {
  loading.value = true
  try {
    const data = await listDishes(filters) || {}
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

function openCreate() {
  Object.assign(form, { id: null, name: '', price: 0, category_id: categories.value[0]?.id || null, image: '', description: '', status: 1 })
  dialogVisible.value = true
}
function openEdit(d) {
  Object.assign(form, { id: d.id, name: d.name, price: d.price, category_id: d.category_id, image: d.image, description: d.description, status: d.status })
  dialogVisible.value = true
}
async function onUpload(req) {
  const file = req.file
  if (file.size > 2 * 1024 * 1024) {
    ElMessage.error('图片大小不能超过 2MB')
    return
  }
  if (!file.type.startsWith('image/')) {
    ElMessage.error('仅支持图片格式')
    return
  }
  uploading.value = true
  try {
    const fd = new FormData()
    fd.append('file', file)
    const data = await uploadImage(fd)
    form.image = data.url
    ElMessage.success('上传成功')
  } catch { /* */ }
  finally { uploading.value = false }
}
async function onSave() {
  if (!form.name || !form.category_id) return ElMessage.warning('请填写菜名与分类')
  saving.value = true
  try {
    const payload = { name: form.name, price: form.price, category_id: form.category_id, image: form.image, description: form.description, status: form.status }
    if (form.id) await updateDish(form.id, payload)
    else await createDish(payload)
    ElMessage.success('已保存')
    dialogVisible.value = false
    load()
  } finally {
    saving.value = false
  }
}
async function onToggle(d) {
  if (d._toggling) return
  d._toggling = true
  try {
    const res = await toggleDish(d.id)
    d.status = res.status
    ElMessage.success('状态已更新')
  } catch { /* */ }
  finally { d._toggling = false }
}
async function onDelete(d) {
  if (deleting.value) return
  try {
    await ElMessageBox.confirm(`确认删除「${d.name}」？`, '提示', { type: 'warning' })
  } catch {
    return
  }
  deleting.value = true
  try {
    await deleteDish(d.id)
    ElMessage.success('已删除')
    load()
  } catch { /* */ }
  finally { deleting.value = false }
}

onMounted(async () => {
  try {
    categories.value = await listCategories()
  } catch (e) {
    // 错误已在 request.js 统一提示
  }
  load()
})
</script>

<style scoped>
.head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: var(--space-sm);
  flex-wrap: wrap;
}

.filters {
  display: flex;
  gap: var(--space-xs);
  flex-wrap: wrap;
}

.card-col {
  margin-bottom: var(--space-lg);
}

.dish-card {
  border-radius: var(--radius-lg);
  overflow: hidden;
  transition: all var(--duration-normal) var(--ease-out);
}

.dish-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-lg) !important;
}

.thumb {
  height: 150px;
  background: linear-gradient(135deg, #f5f0ea, #ebe4da) center/cover no-repeat;
  position: relative;
}

.off-tag {
  position: absolute;
  top: 10px;
  left: 10px;
  background: rgba(0, 0, 0, 0.6);
  backdrop-filter: blur(4px);
  color: #fff;
  font-size: var(--font-size-xs);
  padding: 3px 10px;
  border-radius: var(--radius-full);
  letter-spacing: 0.5px;
}

.info {
  padding: var(--space-sm) var(--space-md) var(--space-md);
}

.name {
  font-weight: var(--font-weight-semibold);
  font-size: var(--font-size-md);
  color: var(--text);
  margin-bottom: 4px;
}

.meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin: var(--space-xs) 0;
}

.price {
  color: var(--brand);
  font-weight: var(--font-weight-bold);
  font-size: var(--font-size-md);
}

.cat {
  color: var(--text-muted);
  font-size: var(--font-size-xs);
  background: #faf9f7;
  padding: 2px 10px;
  border-radius: var(--radius-full);
  border: 1px solid var(--border-light);
}

.desc {
  color: var(--text-muted);
  font-size: var(--font-size-xs);
  height: 18px;
  overflow: hidden;
  line-height: 18px;
}

.actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: var(--space-sm);
  padding-top: var(--space-sm);
  border-top: 1px solid var(--border-light);
}

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
  margin-top: var(--space-sm);
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
