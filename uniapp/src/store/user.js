import { reactive } from 'vue'
import request from '../utils/request'

const state = reactive({
  token: uni.getStorageSync('token') || '',
  userInfo: uni.getStorageSync('userInfo') || null
})

export function getToken() {
  return state.token
}
export function getUser() {
  return state.userInfo
}
export function setAuth(token, user) {
  state.token = token
  state.userInfo = user
  uni.setStorageSync('token', token)
  uni.setStorageSync('userInfo', user)
}
export function logout() {
  state.token = ''
  state.userInfo = null
  uni.removeStorageSync('token')
  uni.removeStorageSync('userInfo')
  // 修复：登出时清空进行中的登录 Promise，避免旧登录成功后再次写回已失效的认证信息
  loginPromise = null
}

// 静默登录：微信环境用 code，H5/开发模式用本地 dev code
let loginPromise = null

export function loginIfNeeded() {
  if (state.token) return Promise.resolve(state.userInfo)
  if (loginPromise) return loginPromise
  loginPromise = doLogin().finally(() => { loginPromise = null })
  return loginPromise
}

async function doLogin() {
  let code = 'h5_dev_openid'
  try {
    const res = await new Promise((resolve, reject) => {
      uni.login({ provider: 'weixin', success: resolve, fail: reject })
    })
    if (res && res.code) code = res.code
  } catch (e) {
    // H5 环境 uni.login 会失败，使用固定 openid 确保同一设备始终映射同一用户
    code = 'h5_dev_openid'
  }
  const data = await request('/client/auth/login', 'POST', { code, nickname: '微信用户', avatar: '' })
  // 修复：登录过程中若被登出，loginPromise 会被清空，此时应丢弃本次登录结果
  if (!loginPromise) return
  setAuth(data.token, data.user)
  return data.user
}

export default state
