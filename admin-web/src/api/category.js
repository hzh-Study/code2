import request from './request'

export function listCategories() {
  return request.get('/v1/admin/categories')
}

export function createCategory(data) {
  return request.post('/v1/admin/categories', data)
}

export function updateCategory(id, data) {
  return request.put(`/v1/admin/categories/${id}`, data)
}

export function deleteCategory(id) {
  return request.delete(`/v1/admin/categories/${id}`)
}
