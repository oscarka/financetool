import axios from 'axios'

// 创建axios实例
const api = axios.create({
    baseURL: 'http://localhost:8000/api/v1',
    timeout: 300000, // 5分钟超时，给分红同步足够时间
    headers: {
        'Content-Type': 'application/json',
    },
})

// 响应拦截器
api.interceptors.response.use(
    (response) => response.data,
    (error) => {
        console.error('API Error:', error)
        throw error
    }
)

// API响应类型
export interface APIResponse<T = any> {
    success: boolean
    message: string
    data?: T
    total?: number
    page?: number
    page_size?: number
}

// 基金相关API
export const fundAPI = {
    // 获取基金信息
    getFundInfo: (fundCode: string): Promise<APIResponse> =>
        api.get(`/funds/info/${fundCode}`),

    // 获取所有基金
    getAllFunds: (): Promise<APIResponse> =>
        api.get('/funds/info'),

    // 创建基金信息
    createFundInfo: (data: any): Promise<APIResponse> =>
        api.post('/funds/info', data),

    // 同步基金信息
    syncFundInfo: (fundCode: string): Promise<APIResponse> =>
        api.post(`/funds/info/${fundCode}/sync`),

    // 获取基金净值历史
    getFundNavHistory: (fundCode: string, days: number = 30): Promise<APIResponse> =>
        api.get(`/funds/nav/${fundCode}?days=${days}`),

    // 获取基金历史净值（akshare）
    getFundNavHistoryByCode: (fundCode: string, forceUpdate?: boolean, includeDividend?: boolean): Promise<APIResponse> =>
        api.get(`/funds/nav_history?fund_code=${fundCode}${forceUpdate ? '&force_update=true' : ''}${includeDividend ? '&include_dividend=true' : ''}`),

    // 获取最新净值
    getLatestNav: (fundCode: string): Promise<APIResponse> =>
        api.get(`/funds/nav/${fundCode}/latest`),

    // 同步基金净值
    syncFundNav: (fundCode: string, navDate: string): Promise<APIResponse> =>
        api.post(`/funds/nav/${fundCode}/sync?nav_date=${navDate}`),

    // 同步最新净值
    syncLatestNav: (fundCode: string): Promise<APIResponse> =>
        api.post(`/funds/nav/${fundCode}/sync/latest`),

    // 创建基金操作
    createFundOperation: (data: any): Promise<APIResponse> =>
        api.post('/funds/operations', data),

    // 获取基金操作记录
    getFundOperations: (params?: any): Promise<APIResponse> =>
        api.get('/funds/operations', { params }),

    // 更新基金操作记录
    updateFundOperation: (id: number, data: any): Promise<APIResponse> =>
        api.put(`/funds/operations/${id}`, data),

    // 删除基金操作记录
    deleteFundOperation: (id: number): Promise<APIResponse> =>
        api.delete(`/funds/operations/${id}`),

    // 获取基金持仓
    getFundPositions: (): Promise<APIResponse> =>
        api.get('/funds/positions'),

    // 获取可卖出的持仓
    getAvailablePositions: (): Promise<APIResponse> =>
        api.get('/funds/positions/available'),

    // 获取持仓汇总
    getPositionSummary: (): Promise<APIResponse> =>
        api.get('/funds/positions/summary'),

    // 创建定投计划
    createDCAPlan: (data: any): Promise<APIResponse> =>
        api.post('/funds/dca/plans', data),

    // 获取定投计划
    getDCAPlans: (): Promise<APIResponse> =>
        api.get('/funds/dca/plans'),

    // 获取定投计划详情
    getDCAPlan: (planId: number): Promise<APIResponse> =>
        api.get(`/funds/dca/plans/${planId}`),

    // 更新定投计划
    updateDCAPlan: async (planId: number, data: any): Promise<APIResponse> => {
        const url = `/funds/dca/plans/${planId}`
        console.log('[日志] updateDCAPlan 请求 url:', url)
        console.log('[日志] updateDCAPlan 请求参数:', data)
        try {
            const response = await api.put(url, data)
            console.log('[日志] updateDCAPlan 响应:', response.data)
            return response.data
        } catch (error) {
            console.error('[日志] updateDCAPlan 异常:', error)
            throw error
        }
    },

    // 删除定投计划
    deleteDCAPlan: (planId: number): Promise<APIResponse> =>
        api.delete(`/funds/dca/plans/${planId}`),

    // 执行定投计划
    executeDCAPlan: (planId: number, executionType: string = 'manual'): Promise<APIResponse> =>
        api.post(`/funds/dca/plans/${planId}/execute?execution_type=${executionType}`),

    // 批量执行所有到期定投计划
    executeAllDCAPlans: (): Promise<APIResponse> =>
        api.post('/funds/dca/plans/execute-all'),

    // 获取定投计划统计
    getDCAPlanStatistics: (planId: number): Promise<APIResponse> =>
        api.get(`/funds/dca/plans/${planId}/statistics`),

    // 同步基金分红数据
    syncFundDividends: (fundCode: string): Promise<APIResponse> =>
        api.post(`/funds/dividends/${fundCode}/sync`),

    // 更新待确认的定投操作
    updatePendingOperations: (): Promise<APIResponse> =>
        api.post('/funds/dca/plans/update-pending'),

    // 处理分红操作
    processDividend: (operationId: number, processType: string): Promise<APIResponse> =>
        api.post(`/funds/operations/${operationId}/process-dividend?process_type=${processType}`),

    // 生成历史定投记录
    generateHistoricalOperations: (planId: number, params?: any): Promise<APIResponse> => {
        const queryParams = new URLSearchParams()
        if (params?.end_date) {
            queryParams.append('end_date', params.end_date)
        }
        if (params?.exclude_dates && params.exclude_dates.length > 0) {
            params.exclude_dates.forEach((date: string) => {
                queryParams.append('exclude_dates', date)
            })
        }
        const queryString = queryParams.toString()
        return api.post(`/funds/dca/plans/${planId}/generate-history${queryString ? `?${queryString}` : ''}`)
    },

    // 更新定投计划状态
    updatePlanStatuses: (): Promise<APIResponse> =>
        api.post('/funds/dca/plans/update-status'),

    // 删除定投计划操作记录
    deletePlanOperations: (planId: number): Promise<APIResponse> =>
        api.delete(`/funds/dca/plans/${planId}/operations`),

    // 更新定投计划统计
    updatePlanStatistics: (planId: number): Promise<APIResponse> =>
        api.post(`/funds/dca/plans/${planId}/update-statistics`),

    // 清理定投计划超出区间的历史操作记录
    cleanPlanOperations: (planId: number, startDate: string, endDate: string): Promise<APIResponse> =>
        api.post(`/funds/dca/plans/${planId}/clean-operations?start_date=${startDate}&end_date=${endDate}`),
}

export default api 