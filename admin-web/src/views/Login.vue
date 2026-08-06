<template>
  <main class="login-page">
    <div class="login-card">
      <div class="brand-lockup">
        <span class="brand-mark">拾</span>
        <span class="brand-name">拾味堂</span>
      </div>
      <div class="form-heading">
        <h2>欢迎回来</h2>
        <p>登录拾味堂管理后台</p>
      </div>
      <el-form :model="form" label-position="left" label-width="84px" @submit.prevent="onSubmit" class="login-form">
        <el-form-item label="管理员账号">
          <el-input v-model.trim="form.username" placeholder="请输入管理员账号" :prefix-icon="User" size="large" autocomplete="username" />
        </el-form-item>
        <el-form-item label="登录密码">
          <el-input v-model="form.password" type="password" placeholder="请输入登录密码" :prefix-icon="Lock" size="large" show-password autocomplete="current-password" />
        </el-form-item>
        <el-button native-type="submit" type="primary" size="large" class="submit" :loading="loading" :disabled="loading">
          {{ loading ? '正在登录' : '登录后台' }}
        </el-button>
      </el-form>
      <p v-if="devMode" class="hint">开发环境账号：admin / admin123</p>
    </div>
  </main>
</template>

<script setup>
import { ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { User, Lock } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { adminLogin } from '@/api/auth'

const devMode = import.meta.env.DEV
const router = useRouter()
const route = useRoute()
const form = ref({ username: '', password: '' })
const loading = ref(false)

async function onSubmit() {
  if (loading.value) return
  const username = form.value.username.trim()
  if (!username || !form.value.password) {
    ElMessage.warning('请输入账号和密码')
    return
  }
  form.value.username = username
  loading.value = true
  try {
    const data = await adminLogin({ username, password: form.value.password })
    localStorage.setItem('admin_token', data.token)
    localStorage.setItem('admin_username', data.username)
    ElMessage.success('登录成功')
    router.replace(route.query.redirect || '/')
  } catch {
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
  background: var(--bg);
}
.login-card {
  width: 100%;
  max-width: 400px;
  background: var(--bg-elevated);
  border: 1px solid var(--border-light);
  border-radius: var(--radius-lg);
  padding: 40px 32px;
  box-shadow: var(--shadow-md);
}
.brand-lockup {
  display: flex;
  align-items: center;
  gap: 12px;
  justify-content: center;
  margin-bottom: var(--space-xl);
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-semibold);
  letter-spacing: 1px;
  color: var(--text);
}
.brand-mark {
  display: inline-flex;
  width: 38px;
  height: 38px;
  border-radius: var(--radius-md);
  background: var(--brand);
  color: #fff;
  font-size: 18px;
  font-weight: 700;
  align-items: center;
  justify-content: center;
}
.form-heading {
  text-align: center;
  margin-bottom: var(--space-xl);
}
.form-heading h2 {
  margin: 0 0 var(--space-xs);
  font-size: var(--font-size-2xl);
}
.form-heading p {
  margin: 0;
  color: var(--text-muted);
}
.login-form :deep(.el-form-item) {
  margin-bottom: var(--space-lg);
}
.login-form :deep(.el-form-item__label) {
  line-height: 44px;
  text-align: justify;
  text-align-last: justify;
  padding-right: 12px;
}
.login-form :deep(.el-input__wrapper) {
  min-height: 44px;
  background: var(--bg-elevated);
}
.submit {
  width: 100%;
  height: 44px;
  margin-top: var(--space-xs);
  font-size: var(--font-size-md);
  box-shadow: none !important;
}
.hint {
  text-align: center;
  color: var(--text-muted);
  font-size: var(--font-size-xs);
  margin: var(--space-md) 0 0;
}
</style>