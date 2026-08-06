import { onBeforeUnmount, ref } from 'vue'

/**
 * Auto-refresh composable — polls a fetch function at a fixed interval.
 * Pauses when the browser tab is hidden to save resources.
 *
 * @param {() => Promise<void>} fn - The async function to call repeatedly (e.g. load())
 * @param {number} [intervalMs=5000] - Polling interval in milliseconds
 */
export function useAutoRefresh(fn, intervalMs = 5000) {
  const enabled = ref(true)
  let timer = null

  function schedule() {
    if (!enabled.value) return
    timer = setTimeout(async () => {
      try { await fn() } catch { /* errors handled inside fn */ }
      schedule()
    }, intervalMs)
  }

  function start() {
    stop()
    enabled.value = true
    schedule()
  }

  function stop() {
    enabled.value = false
    if (timer != null) { clearTimeout(timer); timer = null }
  }

  // Pause when tab is hidden, resume when visible
  function onVisibilityChange() {
    if (document.hidden) stop()
    else start()
  }

  document.addEventListener('visibilitychange', onVisibilityChange)
  start()

  onBeforeUnmount(() => {
    document.removeEventListener('visibilitychange', onVisibilityChange)
    stop()
  })

  return { start, stop, enabled }
}
