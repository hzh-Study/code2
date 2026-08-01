import { createRouter, createWebHashHistory } from 'vue-router'
import { ElMessage } from 'element-plus'

const routes = [
  { path: '/login', name: 'Login', component: () => import('@/views/Login.vue'), meta: { public: true } },
  {
    path: '/',
    component: () => import('@/layouts/DefaultLayout.vue'),
    redirect: '/dashboard',
    children: [
      { path: 'dashboard', name: 'Dashboard', component: () => import('@/views/Dashboard.vue') },
      { path: 'categories', name: 'Categories', component: () => import('@/views/category/Manage.vue') },
      { path: 'dishes', name: 'Dishes', component: () => import('@/views/dish/Manage.vue') },
      { path: 'orders', name: 'Orders', component: () => import('@/views/order/Manage.vue') }
    ]
  }
]

const router = createRouter({
  history: createWebHashHistory(),
  routes
})

router.beforeEach((to) => {
  const token = localStorage.getItem('admin_token')
  if (!to.meta.public && !token) {
    ElMessage.warning('请先登录')
    return { path: '/login', query: { redirect: to.fullPath } }
  }
  if (to.path === '/login' && token) {
    return '/'
  }
})

export default router
