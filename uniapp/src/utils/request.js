import { API_BASE } from '../config'
import { refreshAuth } from './auth-refresh'

function rawRequest(url, method, data) {
  const token = uni.getStorageSync('token') || ''
  const header = token ? { Authorization: `Bearer ${token}` } : {}
  return new Promise((resolve, reject) => {
    uni.request({
      url: API_BASE + url,
      method,
      data,
      header,
      timeout: 15000,
      success: resolve,
      fail: reject
    })
  })
}

export default async function request(url, method = 'GET', data = {}, options = {}) {
  if (!API_BASE) {
    const error = new Error('请先配置小程序 API 地址')
    uni.showToast({ title: error.message, icon: 'none' })
    throw error
  }

  let response
  try {
    response = await rawRequest(url, method, data)
  } catch (cause) {
    uni.showToast({ title: '网络错误', icon: 'none' })
    throw cause
  }

  if (response.statusCode === 401 && options.retryAuth !== false) {
    try {
      await refreshAuth()
      return request(url, method, data, { ...options, retryAuth: false })
    } catch (cause) {
      uni.showToast({ title: '登录已过期，请重试', icon: 'none' })
      throw cause
    }
  }

  const body = response.data
  if (response.statusCode >= 200 && response.statusCode < 300 && body?.code === 0) {
    return body.data
  }
  const message = body?.msg || body?.detail || (response.statusCode === 401 ? '登录已过期' : '请求失败')
  uni.showToast({ title: message, icon: 'none' })
  throw Object.assign(new Error(message), { response, body })
}
