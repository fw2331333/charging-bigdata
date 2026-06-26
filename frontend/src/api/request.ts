/** Axios 实例：统一请求后端 API */
import axios from 'axios'

const request = axios.create({
  baseURL: '/api/v1',
  timeout: 30000,
})

request.interceptors.response.use(
  (res) => res.data,
  (err) => Promise.reject(err),
)

export default request
