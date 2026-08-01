import request from './request'

export function adminLogin(data) {
  return request.post('/v1/admin/auth/login', data)
}
