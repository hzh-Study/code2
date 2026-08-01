import request from './request'

export function listDishes(params) {
  return request.get('/v1/admin/dishes', { params })
}

export function createDish(data) {
  return request.post('/v1/admin/dishes', data)
}

export function updateDish(id, data) {
  return request.put(`/v1/admin/dishes/${id}`, data)
}

export function deleteDish(id) {
  return request.delete(`/v1/admin/dishes/${id}`)
}

export function toggleDish(id) {
  return request.post(`/v1/admin/dishes/${id}/toggle`)
}

export function uploadImage(formData) {
  return request.post('/v1/admin/upload', formData)
}
