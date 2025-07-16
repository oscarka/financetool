import axios from 'axios'

// 根据环境变量确定API基础URL
const getBaseURL = () => {
    // 优先使用环境变量VITE_API_BASE_URL
    if (import.meta.env.VITE_API_BASE_URL) {
        return import.meta.env.VITE_API_BASE_URL
    }

    // 开发环境默认使用本地后端
    if (import.meta.env.DEV) {
        return 'http://localhost:8000/api/v1'
    }

    // 生产环境默认值（如果没有设置环境变量）
    return '/api/v1'
}

// 创建axios实例
const api = axios.create({
    baseURL: getBaseURL(),
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

    // 批量获取最新净值 - 新增优化接口
    getBatchLatestNav: (fundCodes: string[]): Promise<APIResponse> =>
        api.post('/funds/nav/batch-latest', fundCodes),

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
            console.log('[日志] updateDCAPlan 响应:', response)
            return response as unknown as APIResponse
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

    // 定时任务管理API
    // 获取定时任务列表
    getSchedulerJobs: (): Promise<APIResponse> =>
        api.get('/funds/scheduler/jobs'),

    // 更新任务执行时间
    updateJobSchedule: (jobId: string, hour: number, minute: number): Promise<APIResponse> =>
        api.post(`/funds/scheduler/jobs/${jobId}/update?hour=${hour}&minute=${minute}`),

    // 启动定时任务调度器
    startScheduler: (): Promise<APIResponse> =>
        api.post('/funds/scheduler/start'),

    // 停止定时任务调度器
    stopScheduler: (): Promise<APIResponse> =>
        api.post('/funds/scheduler/stop'),

    // 重启定时任务调度器
    restartScheduler: (): Promise<APIResponse> =>
        api.post('/funds/scheduler/restart'),

    // 手动执行净值更新任务
    manualUpdateNavs: (): Promise<APIResponse> =>
        api.post('/funds/scheduler/update-navs'),
}

// Wise相关API
export const wiseAPI = {
    // 获取Wise配置信息
    getConfig: (): Promise<APIResponse> =>
        api.get('/wise/config'),

    // 测试Wise连接
    testConnection: (): Promise<APIResponse> =>
        api.get('/wise/test'),

    // 获取Wise汇总信息
    getSummary: (): Promise<APIResponse> =>
        api.get('/wise/summary'),

    // 获取存储的余额数据
    getStoredBalances: (): Promise<APIResponse> =>
        api.get('/wise/stored-balances'),

    // 获取存储的交易记录
    getStoredTransactions: (params?: any): Promise<APIResponse> =>
        api.get('/wise/stored-transactions', { params }),

    // 获取汇率信息
    getExchangeRates: (source: string, target: string): Promise<APIResponse> =>
        api.get(`/wise/exchange-rates?source=${source}&target=${target}`),

    // 获取历史汇率
    getExchangeRateHistory: (params: any): Promise<APIResponse> =>
        api.get('/wise/exchange-rates/history', { params }),

    // 同步余额数据
    syncBalances: (): Promise<APIResponse> =>
        api.post('/wise/sync-balances'),

    // 同步交易记录
    syncTransactions: (): Promise<APIResponse> =>
        api.post('/wise/sync-transactions'),
}

// OKX相关API
export const okxAPI = {
    // 获取OKX配置信息
    getConfig: (): Promise<APIResponse> =>
        api.get('/okx/config'),

    // 测试OKX连接
    testConnection: (): Promise<APIResponse> =>
        api.get('/okx/test'),

    // 获取OKX汇总信息
    getSummary: (): Promise<APIResponse> =>
        api.get('/okx/summary'),

    // 获取OKX账户资产
    getAccount: (): Promise<APIResponse> =>
        api.get('/okx/account'),

    // 获取OKX持仓信息
    getPositions: (): Promise<APIResponse> =>
        api.get('/okx/positions'),

    // 获取存储的持仓数据
    getStoredPositions: (): Promise<APIResponse> =>
        api.get('/okx/stored-positions'),

    // 获取OKX账单流水
    getBills: (params?: any): Promise<APIResponse> =>
        api.get('/okx/bills', { params }),

    // 获取存储的交易记录
    getStoredTransactions: (params?: any): Promise<APIResponse> =>
        api.get('/okx/stored-transactions', { params }),

    // 获取OKX单个币种行情
    getTicker: (instId: string): Promise<APIResponse> =>
        api.get(`/okx/ticker?inst_id=${instId}`),

    // 获取OKX所有币种行情
    getAllTickers: (instType: string = 'SPOT'): Promise<APIResponse> =>
        api.get(`/okx/tickers?inst_type=${instType}`),

    // 获取OKX交易产品信息
    getInstruments: (instType: string = 'SPOT'): Promise<APIResponse> =>
        api.get(`/okx/instruments?inst_type=${instType}`),

    // 获取资金账户余额
    getAssetBalances: (params?: any): Promise<APIResponse> =>
        api.get('/okx/asset-balances', { params }),

    // 获取储蓄账户余额
    getSavingsBalance: (params?: any): Promise<APIResponse> =>
        api.get('/okx/savings-balance', { params }),

    // 获取存储的余额数据
    getStoredBalances: (): Promise<APIResponse> =>
        api.get('/okx/stored-balances'),

    // 获取存储的市场数据
    getStoredMarketData: (params?: any): Promise<APIResponse> =>
        api.get('/okx/stored-market-data', { params }),

    // 同步余额数据
    syncBalances: (): Promise<APIResponse> =>
        api.post('/okx/sync-balances'),

    // 同步交易记录
    syncTransactions: (days?: number): Promise<APIResponse> =>
        api.post(`/okx/sync-transactions${days ? `?days=${days}` : ''}`),

    // 同步持仓数据
    syncPositions: (): Promise<APIResponse> =>
        api.post('/okx/sync-positions'),

    // 同步市场数据
    syncMarketData: (instIds?: string[]): Promise<APIResponse> =>
        api.post('/okx/sync-market-data', instIds || []),
}

// 汇率相关API
export const exchangeRateAPI = {
    // 获取货币列表
    getCurrencyList: (): Promise<APIResponse> =>
        api.get('/exchange-rates/currencies'),

    // 获取所有汇率
    getAllRates: (): Promise<APIResponse> =>
        api.get('/exchange-rates/rates'),

    // 获取指定货币汇率
    getRate: (currency: string): Promise<APIResponse> =>
        api.get(`/exchange-rates/rates/${currency}`),

    // 获取历史汇率
    getHistoricalRates: (currency: string, startDate?: string, endDate?: string): Promise<APIResponse> => {
        const params = new URLSearchParams();
        if (startDate) params.append('start_date', startDate);
        if (endDate) params.append('end_date', endDate);
        return api.get(`/exchange-rates/rates/${currency}/history?${params.toString()}`);
    },

    // 货币转换
    convertCurrency: (amount: number, fromCurrency: string, toCurrency: string = 'CNY'): Promise<APIResponse> =>
        api.get(`/exchange-rates/convert?amount=${amount}&from_currency=${fromCurrency}&to_currency=${toCurrency}`),
}

// IBKR相关API
export const ibkrAPI = {
    // 获取IBKR配置信息
    getConfig: (): Promise<APIResponse> =>
        api.get('/ibkr/config'),

    // 测试IBKR连接
    testConnection: (): Promise<APIResponse> =>
        api.get('/ibkr/test'),

    // 获取IBKR账户信息
    getAccount: (accountId: string): Promise<APIResponse> =>
        api.get(`/ibkr/accounts/${accountId}`),

    // 获取IBKR账户余额
    getBalances: (accountId?: string): Promise<APIResponse> => {
        const url = accountId ? `/ibkr/balances?account_id=${accountId}` : '/ibkr/balances';
        return api.get(url);
    },

    // 获取IBKR持仓信息
    getPositions: (accountId?: string): Promise<APIResponse> => {
        const url = accountId ? `/ibkr/positions?account_id=${accountId}` : '/ibkr/positions';
        return api.get(url);
    },

    // 获取IBKR同步日志
    getLogs: (params?: {
        account_id?: string;
        limit?: number;
        status?: string;
    }): Promise<APIResponse> =>
        api.get('/ibkr/logs', { params }),

    // 获取IBKR汇总信息
    getSummary: (): Promise<APIResponse> =>
        api.get('/ibkr/summary'),

    // 获取IBKR健康检查
    getHealth: (): Promise<APIResponse> =>
        api.get('/ibkr/health'),

    // 获取最近请求记录（调试用）
    getRecentRequests: (limit: number = 20): Promise<APIResponse> =>
        api.get(`/ibkr/debug/recent-requests?limit=${limit}`),

    // 手动触发数据同步（测试用）
    syncData: (data: {
        account_id: string;
        timestamp: string;
        balances: {
            total_cash: number;
            net_liquidation: number;
            buying_power: number;
            currency: string;
        };
        positions: Array<{
            symbol: string;
            quantity: number;
            market_value: number;
            average_cost: number;
            currency: string;
        }>;
    }): Promise<APIResponse> =>
        api.post('/ibkr/sync', data, {
            headers: {
                'X-API-Key': (import.meta as any).env?.VITE_IBKR_API_KEY || 'test_key'
            }
        }),
}

export default api 