import api from './api'

export interface ConfigInfo {
    app_env: string
    app_name: string
    app_version: string
    debug: boolean
    database_url: string
    cors_origins: string[]
    log_level: string
    log_file: string
    
    // API配置
    fund_api_timeout: number
    fund_api_retry_times: number
    
    // 第三方API配置
    okx_api_configured: boolean
    wise_api_configured: boolean
    paypal_api_configured: boolean
    ibkr_api_configured: boolean
    
    // 调度器配置
    enable_scheduler: boolean
    scheduler_timezone: string
    
    // 安全配置
    security_enable_rate_limiting: boolean
    security_rate_limit_per_minute: number
    
    // 性能配置
    performance_monitoring_enabled: boolean
    performance_sampling_rate: number
    cache_enabled: boolean
    cache_default_ttl: number
    
    // 数据同步配置
    sync_batch_size: number
    sync_max_retries: number
    sync_retry_delay: number
    
    // 系统配置
    notification_enabled: boolean
    backup_enabled: boolean
    data_cleanup_enabled: boolean
    data_cleanup_retention_days: number
}

export interface ConfigValidationResult {
    valid: boolean
    errors: string[]
    warnings: string[]
}

export interface EnvironmentInfo {
    current_env: string
    available_envs: string[]
    env_variables: Record<string, string>
    system_info: {
        python_version: string
        platform: string
        memory_usage: string
        disk_usage: string
    }
}

class ConfigAPI {
    /**
     * 获取系统配置信息
     */
    async getConfig(): Promise<ConfigInfo> {
        const response = await api.get('/config')
        return response.data
    }

    /**
     * 验证配置
     */
    async validateConfig(): Promise<{ success: boolean; data: ConfigValidationResult; error?: string }> {
        try {
            const response = await api.post('/config/validate')
            return response.data
        } catch (error: any) {
            console.error('配置验证失败:', error)
            return {
                success: false,
                data: { valid: false, errors: [], warnings: [] },
                error: error.response?.data?.detail || error.message
            }
        }
    }

    /**
     * 获取环境信息
     */
    async getEnvironmentInfo(): Promise<{ success: boolean; data: EnvironmentInfo; error?: string }> {
        try {
            const response = await api.get('/config/environment')
            return response.data
        } catch (error: any) {
            console.error('获取环境信息失败:', error)
            return {
                success: false,
                data: {} as EnvironmentInfo,
                error: error.response?.data?.detail || error.message
            }
        }
    }

    /**
     * 更新配置
     */
    async updateConfig(config: Partial<ConfigInfo>): Promise<{ success: boolean; data: ConfigInfo; error?: string }> {
        try {
            const response = await api.put('/config', config)
            return response.data
        } catch (error: any) {
            console.error('更新配置失败:', error)
            return {
                success: false,
                data: {} as ConfigInfo,
                error: error.response?.data?.detail || error.message
            }
        }
    }

    /**
     * 重新加载配置
     */
    async reloadConfig(): Promise<{ success: boolean; message: string; error?: string }> {
        try {
            const response = await api.post('/config/reload')
            return response.data
        } catch (error: any) {
            console.error('重新加载配置失败:', error)
            return {
                success: false,
                message: '',
                error: error.response?.data?.detail || error.message
            }
        }
    }

    /**
     * 导出配置
     */
    async exportConfig(): Promise<{ success: boolean; data: string; error?: string }> {
        try {
            const response = await api.get('/config/export')
            return response.data
        } catch (error: any) {
            console.error('导出配置失败:', error)
            return {
                success: false,
                data: '',
                error: error.response?.data?.detail || error.message
            }
        }
    }

    /**
     * 导入配置
     */
    async importConfig(configData: string): Promise<{ success: boolean; data: ConfigInfo; error?: string }> {
        try {
            // 直接将字符串解析为对象后上传
            const response = await api.post('/config/import', JSON.parse(configData))
            return response.data
        } catch (error: any) {
            console.error('导入配置失败:', error)
            return {
                success: false,
                data: {} as ConfigInfo,
                error: error.response?.data?.detail || error.message
            }
        }
    }

    /**
     * 获取配置历史
     */
    async getConfigHistory(): Promise<{ success: boolean; data: any[]; error?: string }> {
        try {
            const response = await api.get('/config/history')
            return response.data
        } catch (error: any) {
            console.error('获取配置历史失败:', error)
            return {
                success: false,
                data: [],
                error: error.response?.data?.detail || error.message
            }
        }
    }

    /**
     * 重置配置到默认值
     */
    async resetConfig(): Promise<{ success: boolean; data: ConfigInfo; error?: string }> {
        try {
            const response = await api.post('/config/reset')
            return response.data
        } catch (error: any) {
            console.error('重置配置失败:', error)
            return {
                success: false,
                data: {} as ConfigInfo,
                error: error.response?.data?.detail || error.message
            }
        }
    }
}

export const configAPI = new ConfigAPI() 