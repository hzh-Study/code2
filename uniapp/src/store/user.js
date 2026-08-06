import { reactive } from 'vue'
import request from '../utils/request'
import { registerAuthRefresh } from '../utils/auth-refresh'

const state = reactive({
  token: uni.getStorageSync('token') || '',
  userInfo: uni.getStorageSync('userInfo') || null
})

let loginPromise = null
let authGeneration = 0

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
  authGeneration += 1
  loginPromise = null
  state.token = ''
  state.userInfo = null
  uni.removeStorageSync('token')
  uni.removeStorageSync('userInfo')
}

export function loginIfNeeded() {
  if (state.token) return Promise.resolve(state.userInfo)
  if (loginPromise) return loginPromise

  const generation = authGeneration
  const currentLogin = doLogin(generation)
  loginPromise = currentLogin
  const clearCurrent = () => {
    if (loginPromise === currentLogin) loginPromise = null
  }
  currentLogin.then(clearCurrent, clearCurrent)
  return currentLogin
}

function getH5DevCode() {
  const storageKey = 'h5_dev_openid_v2'
  let code = uni.getStorageSync(storageKey)
  if (!code) {
    code = `h5_${Date.now()}_${Math.random().toString(36).slice(2, 12)}`
    uni.setStorageSync(storageKey, code)
  }
  return code
}

async function doLogin(generation) {
  let code = ''
  try {
    const result = await new Promise((resolve, reject) => {
      uni.login({ provider: 'weixin', success: resolve, fail: reject })
    })
    if (result?.code) code = result.code
  } catch (error) {
    // #ifdef H5
    if (import.meta.env.DEV) code = getH5DevCode()
    // #endif
  }
  // #ifdef H5
  if (!code && import.meta.env.DEV) code = getH5DevCode()
  // #endif
  if (!code) throw new Error('当前环境无法完成微信登录')

  const data = await request(
    '/client/auth/login',
    'POST',
    { code, nickname: '微信用户', avatar: '' },
    { retryAuth: false }
  )
  if (generation !== authGeneration) return state.userInfo
  setAuth(data.token, data.user)
  return data.user
}

registerAuthRefresh(async () => {
  logout()
  await loginIfNeeded()
})

export default state
