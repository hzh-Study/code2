<template>
  <el-container class="layout">
    <el-aside :width="asideWidth" class="aside">
      <div class="logo">
        <span class="logo-mark">拾</span>
        <span class="logo-text">拾味堂</span>
      </div>
      <el-menu :default-active="activeMenu" class="menu" background-color="transparent" text-color="var(--sidebar-text)"
        active-text-color="var(--sidebar-text-active)" router>
        <el-menu-item index="/dashboard">
          <el-icon><DataLine /></el-icon><span>数据看板</span>
        </el-menu-item>
        <el-menu-item index="/categories">
          <el-icon><Menu /></el-icon><span>分类管理</span>
        </el-menu-item>
        <el-menu-item index="/dishes">
          <el-icon><Dish /></el-icon><span>菜品管理</span>
        </el-menu-item>
        <el-menu-item index="/orders">
          <el-icon><List /></el-icon><span>订单管理</span>
        </el-menu-item>
      </el-menu>
      <div class="aside-footer">
        <span class="version">v1.0.0</span>
      </div>
    </el-aside>
    <el-container>
      <el-header class="header">
        <span class="header-title">{{ pageTitle }}</span>
        <div class="header-right">
          <div class="user-badge">
            <span class="user-avatar">{{ avatarLetter }}</span>
            <span class="username">{{ username }}</span>
          </div>
          <el-button text type="primary" class="logout-btn" @click="logout">退出登录</el-button>
        </div>
      </el-header>
      <el-main class="main">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { DataLine, Menu, Dish, List } from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()

const asideWidth = 'var(--sidebar-width)'
const activeMenu = computed(() => route.path)
const pageTitle = computed(() => ({
  '/dashboard': '数据看板',
  '/categories': '分类管理',
  '/dishes': '菜品管理',
  '/orders': '订单管理'
}[route.path] || ''))
const username = localStorage.getItem('admin_username') || 'admin'
const avatarLetter = computed(() => (username.charAt(0) || 'A').toUpperCase())

function logout() {
  localStorage.removeItem('admin_token')
  localStorage.removeItem('admin_username')
  router.replace('/login')
}
</script>

<style scoped>
.layout {
  height: 100vh;
}

.aside {
  background: var(--sidebar-bg);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  position: relative;
}

.aside::before {
  content: '';
  position: absolute;
  top: 0;
  right: 0;
  width: 1px;
  height: 100%;
  background: linear-gradient(to bottom, rgba(245, 230, 210, 0.15), rgba(245, 230, 210, 0.05));
}

.logo {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 20px 20px 24px;
  color: #fff;
}

.logo-mark {
  width: 36px;
  height: 36px;
  border-radius: 10px;
  background: var(--brand-gradient);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 18px;
  color: #fff;
  box-shadow: 0 4px 12px rgba(232, 93, 44, 0.3);
  letter-spacing: 1px;
}

.logo-text {
  font-weight: 600;
  font-size: 16px;
  letter-spacing: 1px;
}

.menu {
  border-right: none !important;
  flex: 1;
  padding: 0 8px;
}

.menu :deep(.el-menu-item) {
  height: 44px;
  line-height: 44px;
  border-radius: var(--radius-md);
  margin-bottom: 4px;
  padding-left: 16px !important;
  transition: all var(--duration-fast) var(--ease-out);
}

.menu :deep(.el-menu-item:hover) {
  background: var(--sidebar-bg-hover) !important;
}

.menu :deep(.el-menu-item.is-active) {
  background: var(--sidebar-bg-active) !important;
  color: var(--sidebar-text-active) !important;
  font-weight: var(--font-weight-medium);
  position: relative;
}

.menu :deep(.el-menu-item.is-active::before) {
  content: '';
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 3px;
  height: 20px;
  background: var(--brand);
  border-radius: 0 2px 2px 0;
}

.menu :deep(.el-menu-item .el-icon) {
  font-size: 18px;
  margin-right: 10px;
}

.aside-footer {
  padding: 16px 20px;
  border-top: 1px solid rgba(245, 230, 210, 0.15);
}

.version {
  font-size: 11px;
  color: rgba(245, 230, 210, 0.4);
  letter-spacing: 0.5px;
}

.header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: var(--bg-elevated);
  border-bottom: 1px solid var(--border-light);
  padding: 0 var(--space-xl);
  height: var(--header-height);
  box-shadow: var(--shadow-xs);
  position: relative;
  z-index: 2;
}

.header-title {
  font-weight: var(--font-weight-semibold);
  font-size: var(--font-size-lg);
  color: var(--text);
  letter-spacing: 0.3px;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.user-badge {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 4px 12px 4px 4px;
  background: #faf9f7;
  border-radius: var(--radius-full);
}

.user-avatar {
  width: 30px;
  height: 30px;
  border-radius: 50%;
  background: var(--brand-gradient);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-semibold);
}

.username {
  color: var(--text-secondary);
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
}

.logout-btn {
  font-size: var(--font-size-sm) !important;
}

.main {
  background: var(--bg);
  padding: var(--space-xl);
  overflow-y: auto;
}
</style>
