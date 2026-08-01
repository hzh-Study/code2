const DEV = import.meta.env.DEV

export const API_BASE = DEV ? '/api/v1' : (import.meta.env.VITE_API_BASE || 'http://localhost:8000/api/v1')
// 修复：空字符串也应视为未配置，回退到默认地址，避免图片 URL 拼接异常
export const IMG_BASE = DEV ? '' : (import.meta.env.VITE_IMG_BASE || 'http://localhost:8000')

export function imgUrl(path) {
  if (!path) return ''
  if (path.startsWith('http')) return path
  if (!path.startsWith('/')) path = '/' + path
  return IMG_BASE + path
}
