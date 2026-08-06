import request from '../utils/request'

export const getCategories = () => request('/client/categories')
export const getHotDishes = () => request('/client/dishes/hot')
export const getDishes = (categoryId) =>
  request('/client/dishes' + (categoryId ? `?category_id=${categoryId}` : ''))

export const getCart = () => request('/client/cart')
export const addCart = (dishId, quantity = 1) =>
  request('/client/cart/add', 'POST', { dish_id: dishId, quantity })
export const updateCart = (dishId, quantity) =>
  request('/client/cart/update', 'POST', { dish_id: dishId, quantity })
export const clearCart = () => request('/client/cart/clear', 'POST')

export const createOrder = (diningMode) =>
  request('/client/orders', 'POST', { dining_mode: diningMode })
export const getOrders = (status) =>
  request('/client/orders' + (status != null ? `?status=${status}` : ''))
export const getOrderDetail = (id) => request(`/client/orders/${id}`)
export const cancelOrder = (id) => request(`/client/orders/${id}/cancel`, 'POST')
export const repayOrder = (id) => request(`/client/orders/${id}/repay`, 'POST')

// 开发模式：本地模拟微信支付回调
export const simulatePay = (orderNo) =>
  request('/client/pay/notify', 'POST', { order_no: orderNo })
