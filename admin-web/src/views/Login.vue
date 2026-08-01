<template>
  <div class="login-wrap">
    <div class="login-bg-shape shape-1"></div>
    <div class="login-bg-shape shape-2"></div>
    <div class="login-card">
      <div class="brand">
        <div class="brand-logo">
          <span class="brand-mark">拾</span>
        </div>
        <h1 class="brand-title">拾味堂</h1>
        <p class="brand-subtitle">餐厅管理后台</p>
      </div>
      <el-form :model="form" @submit.prevent="onSubmit" class="login-form">
        <el-form-item>
          <el-input v-model="form.username" placeholder="管理员账号" :prefix-icon="User" size="large" />
        </el-form-item>
        <el-form-item>
          <el-input v-model="form.password" type="password" placeholder="密码" :prefix-icon="Lock" size="large" show-password />
        </el-form-item>
        <el-button type="primary" size="large" class="submit" :loading="loading" @click="onSubmit">登 录</el-button>
      </el-form>
      <p v-if="devMode" class="hint">默认账号：admin / admin123</p>
      <div class="login-footer">
        <span>堂食 / 外卖一体化经营</span>
      </div>
    </div>
  </div>
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
  // 修复：防止用户快速点击或回车导致重复提交登录请求
  if (loading.value) return
  if (!form.value.username || !form.value.password) {
    ElMessage.warning('请输入账号和密码')
    return
  }
  loading.value = true
  try {
    const data = await adminLogin(form.value)
    localStorage.setItem('admin_token', data.token)
    localStorage.setItem('admin_username', data.username)
    ElMessage.success('登录成功')
    router.replace(route.query.redirect || '/')
  } catch (e) {
    // 错误信息已统一处理
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-wrap {
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #faf8f5 0%, #f0ebe5 50%, #fff3ea 100%);
  position: relative;
  overflow: hidden;
}

.login-bg-shape {
  position: absolute;
  border-radius: 50%;
  opacity: 0.5;
  filter: blur(80px);
  pointer-events: none;
}

.shape-1 {
  width: 500px;
  height: 500px;
  background: radial-gradient(circle, rgba(232, 93, 44, 0.12) 0%, transparent 70%);
  top: -10%;
  right: -5%;
  animation: float 8s ease-in-out infinite;
}

.shape-2 {
  width: 400px;
  height: 400px;
  background: radial-gradient(circle, rgba(255, 122, 69, 0.1) 0%, transparent 70%);
  bottom: -10%;
  left: -5%;
  animation: float 10s ease-in-out infinite reverse;
}

@keyframes float {
  0%, 100% { transform: translate(0, 0); }
  50% { transform: translate(30px, -20px); }
}

.login-card {
  width: 400px;
  background: rgba(255, 255, 255, 0.92);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border-radius: var(--radius-xl);
  padding: 40px 36px 32px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.06), 0 1px 3px rgba(0, 0, 0, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.6);
  position: relative;
  z-index: 1;
  animation: cardIn 0.6s var(--ease-out) both;
}

@keyframes cardIn {
  from {
    opacity: 0;
    transform: translateY(20px) scale(0.98);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

.brand {
  text-align: center;
  margin-bottom: 32px;
}

.brand-logo {
  display: inline-flex;
  margin-bottom: 16px;
}

.brand-mark {
  display: flex;
  width: 60px;
  height: 60px;
  border-radius: 16px;
  background: var(--brand-gradient);
  color: #fff;
  font-size: 28px;
  font-weight: 700;
  align-items: center;
  justify-content: center;
  box-shadow: 0 8px 24px rgba(232, 93, 44, 0.25);
  letter-spacing: 2px;
}

.brand-title {
  font-size: 24px;
  font-weight: 700;
  color: var(--text);
  margin: 0 0 6px;
  letter-spacing: 2px;
}

.brand-subtitle {
  color: var(--text-muted);
  font-size: var(--font-size-sm);
  margin: 0;
  letter-spacing: 1px;
}

.login-form {
  margin-bottom: 8px;
}

.login-form :deep(.el-input__wrapper) {
  background: #f8f6f3;
  box-shadow: none !important;
  border: 1px solid transparent;
  border-radius: var(--radius-md);
  padding: 4px 12px;
  transition: all var(--duration-normal) var(--ease-out);
}

.login-form :deep(.el-input__wrapper:hover) {
  border-color: var(--border);
}

.login-form :deep(.el-input__wrapper.is-focus) {
  background: #fff;
  border-color: var(--brand);
  box-shadow: 0 0 0 3px rgba(232, 93, 44, 0.08) !important;
}

.submit {
  width: 100%;
  height: 46px;
  font-size: var(--font-size-md);
  letter-spacing: 4px;
  margin-top: 4px;
  background: var(--brand-gradient) !important;
  border: none !important;
  box-shadow: 0 6px 20px rgba(232, 93, 44, 0.3) !important;
  transition: all var(--duration-normal) var(--ease-out) !important;
}

.submit:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 28px rgba(232, 93, 44, 0.38) !important;
}

.submit:active {
  transform: translateY(0);
}

.hint {
  text-align: center;
  color: var(--text-muted);
  font-size: var(--font-size-xs);
  margin-top: 16px;
  padding: 8px 12px;
  background: #faf9f7;
  border-radius: var(--radius-sm);
}

.login-footer {
  text-align: center;
  margin-top: 24px;
  padding-top: 20px;
  border-top: 1px solid var(--border-light);
}

.login-footer span {
  font-size: var(--font-size-xs);
  color: var(--text-placeholder);
  letter-spacing: 0.5px;
}
</style>
