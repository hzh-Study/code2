<template>
  <el-container class="layout">
    <div v-if="mobileOpen" class="nav-mask" @click="mobileOpen = false"></div>
    <el-aside :width="asideWidth" class="aside" :class="{ 'is-open': mobileOpen }">
      <div class="logo">
        <span class="logo-mark">拾</span>
        <span class="logo-text">拾味堂后台</span>
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
        <el-button text class="aside-logout" :icon="SwitchButton" @click="logout">退出登录</el-button>
      </div>
    </el-aside>
    <el-container>
      <el-header class="header">
        <div class="header-leading">
          <el-button class="menu-toggle" text :icon="Expand" :aria-label="mobileOpen ? '关闭导航' : '打开导航'"
            :aria-expanded="mobileOpen" @click="mobileOpen = !mobileOpen" />
          <div>
            <span class="header-title">{{ pageTitle }}</span>
            <span class="header-subtitle">{{ pageSubtitle }}</span>
          </div>
        </div>
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
import { computed, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { DataLine, Menu, Dish, List, Expand, SwitchButton } from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const mobileOpen = ref(false)

const asideWidth = 'var(--sidebar-width)'
const activeMenu = computed(() => route.path)
const pageTitle = computed(() => ({
  '/dashboard': '数据看板',
  '/categories': '分类管理',
  '/dishes': '菜品管理',
  '/orders': '订单管理'
}[route.path] || ''))
const pageSubtitle = computed(() => ({
  '/dashboard': '今日经营概览',
  '/categories': '维护菜品分类与展示顺序',
  '/dishes': '管理菜品信息与售卖状态',
  '/orders': '跟进订单与出餐进度'
}[route.path] || ''))
const username = ref(localStorage.getItem('admin_username') || 'admin')
const avatarLetter = computed(() => (username.value.charAt(0) || 'A').toUpperCase())
watch(() => route.path, () => { mobileOpen.value = false })

function logout() {
  localStorage.removeItem('admin_token')
  localStorage.removeItem('admin_username')
  router.replace('/login')
}
</script>

<style scoped>
.layout {
  height: 100vh;
  min-width: 0;
}

.aside {
  background: var(--sidebar-bg);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  position: relative;
}

.aside::before { content: ''; position: absolute; inset: 0 0 0 auto; width: 1px; background: rgba(245, 230, 210, 0.12); }

.logo {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 22px 20px 28px;
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
  display: flex;
  align-items: center;
  justify-content: space-between;
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
  position: relative;
  z-index: 2;
}
.header-leading { display: flex; align-items: center; gap: var(--space-sm); min-width: 0; }
.header-leading > div { display: flex; flex-direction: column; }
.header-subtitle { color: var(--text-muted); font-size: var(--font-size-xs); margin-top: 1px; }
.menu-toggle { display: none !important; font-size: 20px !important; }

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
  min-width: 0;
}
.nav-mask { display: none; }
@media (max-width: 900px) {
  .aside { position: fixed; inset: 0 auto 0 0; z-index: 20; transform: translateX(-100%); transition: transform var(--duration-normal) var(--ease-out); }
  .aside.is-open { transform: translateX(0); }
  .nav-mask { display: block; position: fixed; inset: 0; z-index: 19; background: rgba(43, 43, 43, 0.42); }
  .menu-toggle { display: inline-flex !important; }
  .main { padding: var(--space-lg); }
}

.aside-logout {
  display: none !important;
  color: var(--sidebar-text) !important;
}
@media (max-width: 560px) {
  .header { padding: 0 var(--space-sm); }
  .header-subtitle, .username, .logout-btn { display: none !important; }
  .aside-logout { display: inline-flex !important; }
  .user-badge { padding-right: 4px; background: transparent; }
  .main { padding: var(--space-md) var(--space-sm); }
}
</style>
