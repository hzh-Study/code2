let refreshHandler = null
let refreshing = null

export function registerAuthRefresh(handler) {
  refreshHandler = handler
}

export function refreshAuth() {
  if (!refreshHandler) return Promise.reject(new Error('登录模块尚未初始化'))
  if (refreshing) return refreshing

  const current = Promise.resolve().then(() => refreshHandler())
  refreshing = current
  const clearCurrent = () => {
    if (refreshing === current) refreshing = null
  }
  current.then(clearCurrent, clearCurrent)
  return current
}
