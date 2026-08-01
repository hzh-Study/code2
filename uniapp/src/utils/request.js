import { API_BASE } from '../config'
import { getToken, logout } from '../store/user'

export default function request(url, method = 'GET', data = {}) {
  const token = getToken()
  const header = {}
  if (token) header.Authorization = 'Bearer ' + token
  return new Promise((resolve, reject) => {
    uni.request({
      url: API_BASE + url,
      method,
      data,
      header,
      timeout: 15000,
      success: (res) => {
        if (res.statusCode === 401) {
          logout()
          // 修复：index 是 tabBar 页面，应使用 switchTab 跳转，reLaunch 在部分平台无法打开 tabBar 页
          uni.switchTab({ url: '/pages/index/index' })
          reject(res)
          return
        }
        const body = res.data
        if (body && body.code === 0) {
          resolve(body.data)
        } else {
          // 修复：后端 HTTPException 返回 {detail: ...} 无 msg 字段，需读取 detail，否则用户只能看到"请求失败"而看不到真实原因
          uni.showToast({ title: (body && (body.msg || body.detail)) || '请求失败', icon: 'none' })
          reject(body)
        }
      },
      fail: () => {
        uni.showToast({ title: '网络错误', icon: 'none' })
        reject(new Error('网络错误'))
      }
    })
  })
}
