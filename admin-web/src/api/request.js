import axios from 'axios'
import { ElMessage } from 'element-plus'

const request = axios.create({
  baseURL: '/api',
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
      localStorage.removeItem('admin_token')
      localStorage.removeItem('admin_username')
      ElMessage.warning('登录已过期，请重新登录')
      setTimeout(() => { window.location.hash = '#/login' }, 300)
    } else {
      ElMessage.error(error.response?.data?.msg || '网络错误')
    }
    return Promise.reject(error)
  }
)

export default request
