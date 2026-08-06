import request from './request'

export function listOrders(params) {
  return request.get('/v1/admin/orders', { params })
}

export function orderDetail(id) {
  return request.get(`/v1/admin/orders/${id}`)
}

export function completeOrder(id) {
  return request.post(`/v1/admin/orders/${id}/status`)
}

export function dashboard() {
  return request.get('/v1/admin/dashboard')
}
