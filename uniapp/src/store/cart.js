import { computed, reactive } from 'vue'
import { addCart, clearCart, getCart, updateCart } from '../api'

const state = reactive({
  items: [],
  loading: false,
  error: false,
  /** dishId -> true，同菜串行、不同菜可并行 */
  updatingIds: {},
  clearing: false
})

export const cartCount = computed(() =>
  state.items.reduce((sum, item) => sum + Number(item.quantity || 0), 0)
)

export const cartTotal = computed(() =>
  state.items.reduce((sum, item) => sum + Number(item.subtotal || 0), 0)
)

export function dishQuantity(dishId) {
  return Number(state.items.find((item) => item.dish_id === dishId)?.quantity || 0)
}

export function isCartUpdating(dishId) {
  return !!state.updatingIds[dishId]
}

export async function loadCart() {
  state.loading = true
  state.error = false
  try {
    const data = await getCart() || []
    const unavailable = data.filter((item) => (item.status ?? 1) !== 1)
    if (unavailable.length) {
      await Promise.allSettled(unavailable.map((item) => updateCart(item.dish_id, 0)))
      uni.showToast({ title: '已移除下架菜品', icon: 'none' })
    }
    state.items = data.filter((item) => (item.status ?? 1) === 1)
  } catch (requestError) {
    state.error = true
    throw requestError
  } finally {
    state.loading = false
  }
}

export async function changeCartQuantity(dishId, delta) {
  if (state.updatingIds[dishId]) return
  state.updatingIds[dishId] = true
  try {
    const current = dishQuantity(dishId)
    if (!current && delta > 0) await addCart(dishId, 1)
    else await updateCart(dishId, Math.max(0, current + delta))
    await loadCart()
  } finally {
    delete state.updatingIds[dishId]
  }
}

export async function clearAllCart() {
  const confirmed = await new Promise((resolve) => uni.showModal({
    title: '清空购物车',
    content: '确定移除全部已选菜品吗？',
    confirmText: '清空',
    confirmColor: '#b42318',
    success: (result) => resolve(result.confirm),
    fail: () => resolve(false)
  }))
  if (!confirmed) return false

  state.clearing = true
  try {
    await clearCart()
    state.items = []
    uni.showToast({ title: '购物车已清空', icon: 'success' })
    return true
  } finally {
    state.clearing = false
  }
}

export default state
