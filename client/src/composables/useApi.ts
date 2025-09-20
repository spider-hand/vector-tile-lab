import { Configuration } from '@/services'

const useApi = () => {
  const basePath = import.meta.env.VITE_API_BASE_URL
  const apiConfig = new Configuration({
    basePath: basePath,
    fetchApi: fetch,
  })

  return {
    apiConfig,
  }
}

export default useApi
