import axios from 'axios'

const api = axios.create({
    baseURL: '/api',
    timeout: 30000,
    headers: { 'Content-Type': 'application/json' },
})

// ── Documents ──────────────────────────────────────
export const uploadDocument = (file, userId = 'default_user', description = '') => {
    const form = new FormData()
    form.append('file', file)
    return api.post(`/documents/upload?user_id=${userId}&description=${encodeURIComponent(description)}`, form, {
        headers: { 'Content-Type': 'multipart/form-data' },
    })
}

export const listDocuments = (userId = 'default_user', tier = null, skip = 0, limit = 50) => {
    const params = { user_id: userId, skip, limit }
    if (tier) params.tier = tier
    return api.get('/documents/', { params })
}

export const getDocument = (docId) => api.get(`/documents/${docId}`)

export const deleteDocument = (docId, userId = 'default_user') =>
    api.delete(`/documents/${docId}?user_id=${userId}`)

export const recordAccess = (docId, query = '', score = 0) =>
    api.post(`/documents/${docId}/access?query_used=${encodeURIComponent(query)}&relevance_score=${score}`)

// ── Search ──────────────────────────────────────────
export const semanticSearch = (query, userId = 'default_user', k = 5, minScore = 0, tierFilter = null) =>
    api.post('/search/', {
        query,
        user_id: userId,
        k,
        min_score: minScore,
        tier_filter: tierFilter || null,
    })

// ── Analytics ──────────────────────────────────────
export const getAnalytics = (userId = 'default_user') =>
    api.get('/analytics/', { params: { user_id: userId } })

export const getLifecycleData = (userId = 'default_user') =>
    api.get('/analytics/lifecycle', { params: { user_id: userId } })

export const getTierSummary = (userId = 'default_user') =>
    api.get('/analytics/tiers', { params: { user_id: userId } })

export const healthCheck = () => axios.get('/health')

export default api
