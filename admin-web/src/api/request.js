import axios from 'axios'
import { ElMessage } from 'element-plus'
import router from '@/router'

const request = axios.create({
  baseURL: import.meta.env.VITE_API_BASE || '/api',
  timeout: 15000,
})

// 请求拦截器：自动附加 admin token
request.interceptors.request.use((config) => {
  const token = localStorage.getItem('admin_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// 防止并发 401 重复弹出 Toast 和重复导航
let isHandling401 = false

// 响应拦截器：统一处理业务错误
request.interceptors.response.use(
  (response) => {
    const { data } = response
    if (data.code === 0) {
      return data.data
    }
    ElMessage.error(data.msg || '请求失败')
    return Promise.reject(data)
  },
  (error) => {
    if (error.response?.status === 401) {
      if (!isHandling401) {
        isHandling401 = true
        localStorage.removeItem('admin_token')
        localStorage.removeItem('admin_username')
        ElMessage.warning('登录已过期，请重新登录')
        router.replace({ path: '/login', query: { redirect: router.currentRoute.value.fullPath } })
        setTimeout(() => { isHandling401 = false }, 1000)
      }
      return Promise.reject(new Error('未登录或登录已过期'))
    } else {
      ElMessage.error(error.response?.data?.msg || '网络错误')
    }
    return Promise.reject(error)
  }
)

export default request
