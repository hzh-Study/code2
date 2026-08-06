const DEV = import.meta.env.DEV
const configuredApiBase = (import.meta.env.VITE_API_BASE || '').trim().replace(/\/+$/, '')
const configuredImgBase = (import.meta.env.VITE_IMG_BASE || '').trim().replace(/\/+$/, '')

let defaultApiBase = '/api/v1'

// 小程序没有 Vite 代理；真机联调请用 VITE_API_BASE 配置局域网 HTTPS 地址。
// #ifndef H5
defaultApiBase = DEV ? 'http://127.0.0.1:8000/api/v1' : ''
// #endif

export const API_BASE = configuredApiBase || defaultApiBase
export const IMG_BASE = configuredImgBase || API_BASE.replace(/\/api\/v1$/, '')

export function imgUrl(path) {
  if (!path) return ''
  if (/^https?:\/\//i.test(path)) return path
  if (!path.startsWith('/')) path = '/' + path
  return IMG_BASE + path
}
