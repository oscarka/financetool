#!/usr/bin/env node
/**
 * AI分析师API JavaScript客户端示例
 * 
 * 这个脚本演示了如何使用JavaScript/Node.js调用AI分析师API
 * 包含错误处理、重试机制和数据格式化
 */

const axios = require('axios');

class AIAnalystClient {
    constructor(baseUrl, apiKey, timeout = 30000) {
        this.baseUrl = baseUrl.replace(/\/$/, '');
        this.apiKey = apiKey;
        this.timeout = timeout;
        
        // 创建axios实例
        this.client = axios.create({
            baseURL: this.baseUrl,
            timeout: this.timeout,
            headers: {
                'X-API-Key': this.apiKey,
                'Content-Type': 'application/json',
                'User-Agent': 'AIAnalystClient-JS/1.0'
            }
        });
        
        // 添加响应拦截器处理错误
        this.client.interceptors.response.use(
            response => response,
            error => this.handleError(error)
        );
    }
    
    async handleError(error) {
        if (error.response) {
            const { status, data } = error.response;
            console.error(`API错误 ${status}:`, data.detail || data.message || '未知错误');
            
            if (status === 401) {
                throw new Error('API密钥无效或已过期');
            } else if (status === 429) {
                console.warn('请求频率超限，等待后重试...');
                await this.sleep(2000);
                throw new Error('请求频率超限');
            } else if (status >= 500) {
                throw new Error('服务器内部错误');
            }
        } else if (error.request) {
            throw new Error('网络连接错误');
        }
        throw error;
    }
    
    sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
    
    async makeRequest(endpoint, params = {}, maxRetries = 3) {
        for (let attempt = 1; attempt <= maxRetries; attempt++) {
            try {
                const response = await this.client.get(endpoint, { params });
                return response.data;
            } catch (error) {
                if (attempt === maxRetries) {
                    throw error;
                }
                
                if (error.message.includes('频率超限') || error.message.includes('服务器')) {
                    console.log(`重试 ${attempt}/${maxRetries}...`);
                    await this.sleep(1000 * attempt);
                } else {
                    throw error;
                }
            }
        }
    }
    
    // API方法
    async getAssetSummary(baseCurrency = 'CNY') {
        console.log(`获取资产总览 (基准货币: ${baseCurrency})`);
        return await this.makeRequest('/asset-summary', { base_currency: baseCurrency });
    }
    
    async getInvestmentHistory(options = {}) {
        const params = {
            limit: options.limit || 100,
            ...(options.startDate && { start_date: options.startDate }),
            ...(options.endDate && { end_date: options.endDate }),
            ...(options.platform && { platform: options.platform }),
            ...(options.assetType && { asset_type: options.assetType })
        };
        
        console.log('获取投资历史:', params);
        return await this.makeRequest('/investment-history', params);
    }
    
    async getPerformanceAnalysis(baseCurrency = 'CNY', days = 30) {
        console.log(`获取绩效分析 (${days}天, ${baseCurrency})`);
        return await this.makeRequest('/performance-analysis', {
            base_currency: baseCurrency,
            days: days
        });
    }
    
    async getExchangeRates(baseCurrency = 'CNY', targetCurrencies = null) {
        const params = { base_currency: baseCurrency };
        if (targetCurrencies) {
            params.target_currencies = targetCurrencies;
        }
        
        console.log('获取汇率数据:', params);
        return await this.makeRequest('/exchange-rates', params);
    }
    
    async getMarketData(fundCodes = null, days = 7) {
        const params = { days };
        if (fundCodes) {
            params.fund_codes = fundCodes;
        }
        
        console.log('获取市场数据:', params);
        return await this.makeRequest('/market-data', params);
    }
    
    async getPortfolioAnalysis(baseCurrency = 'CNY') {
        console.log(`获取投资组合分析 (${baseCurrency})`);
        return await this.makeRequest('/portfolio-analysis', { base_currency: baseCurrency });
    }
    
    async getDCAAnalysis() {
        console.log('获取定投计划分析');
        return await this.makeRequest('/dca-analysis');
    }
    
    async getRiskAssessment(baseCurrency = 'CNY', days = 90) {
        console.log(`获取风险评估 (${days}天, ${baseCurrency})`);
        return await this.makeRequest('/risk-assessment', {
            base_currency: baseCurrency,
            days: days
        });
    }
    
    async healthCheck() {
        return await this.makeRequest('/health');
    }
}

// 数据格式化工具
class DataFormatter {
    static formatCurrency(amount, currency = 'CNY') {
        const symbols = {
            'CNY': '¥',
            'USD': '$',
            'EUR': '€',
            'GBP': '£',
            'HKD': 'HK$'
        };
        
        const symbol = symbols[currency] || currency + ' ';
        return `${symbol}${amount.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
    }
    
    static formatPercentage(value) {
        return `${value.toFixed(2)}%`;
    }
    
    static formatDate(dateStr) {
        try {
            const date = new Date(dateStr);
            return date.toLocaleString('zh-CN', {
                year: 'numeric',
                month: '2-digit',
                day: '2-digit',
                hour: '2-digit',
                minute: '2-digit'
            });
        } catch (error) {
            return dateStr;
        }
    }
}

// 主演示函数
async function main() {
    // 配置
    const API_BASE_URL = 'http://localhost:8000/api/v1/ai-analyst';
    const API_KEY = 'ai_analyst_key_2024'; // 替换为实际API密钥
    
    const client = new AIAnalystClient(API_BASE_URL, API_KEY);
    
    console.log('='.repeat(60));
    console.log('AI分析师数据获取演示 (JavaScript版本)');
    console.log('='.repeat(60));
    
    try {
        // 1. 健康检查
        console.log('\n1. 健康检查...');
        const health = await client.healthCheck();
        console.log(`✓ API服务正常: ${health.message}`);
        
        // 2. 资产总览
        console.log('\n2. 资产总览...');
        const summary = await client.getAssetSummary();
        console.log('总资产:', summary.total_assets);
        console.log(`最后更新: ${DataFormatter.formatDate(summary.last_update_time)}`);
        
        if (summary.platform_breakdown.length > 0) {
            console.log('\n平台分布:');
            summary.platform_breakdown.slice(0, 3).forEach(platform => {
                console.log(`  - ${platform.platform}: ${DataFormatter.formatCurrency(platform.value)} (${DataFormatter.formatPercentage(platform.percentage)})`);
            });
        }
        
        // 3. 投资历史
        console.log('\n3. 投资历史...');
        const endDate = new Date().toISOString().split('T')[0];
        const startDate = new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0];
        
        const history = await client.getInvestmentHistory({
            startDate,
            endDate,
            limit: 5
        });
        
        console.log(`总操作次数: ${history.operations.length}`);
        console.log('总投入:', history.total_invested);
        
        if (history.operations.length > 0) {
            console.log('\n最近操作:');
            history.operations.slice(0, 3).forEach(op => {
                console.log(`  - ${DataFormatter.formatDate(op.date)}: ${op.operation_type} ${op.asset_name} ${DataFormatter.formatCurrency(op.amount, op.currency)}`);
            });
        }
        
        // 4. 绩效分析
        console.log('\n4. 绩效分析...');
        const performance = await client.getPerformanceAnalysis('CNY', 30);
        const overall = performance.overall_return;
        
        console.log(`30天收益率: ${DataFormatter.formatPercentage(overall.cny || 0)}`);
        console.log(`期初价值: ${DataFormatter.formatCurrency(overall.start_value || 0)}`);
        console.log(`期末价值: ${DataFormatter.formatCurrency(overall.end_value || 0)}`);
        
        // 5. 投资组合分析
        console.log('\n5. 投资组合分析...');
        const portfolio = await client.getPortfolioAnalysis();
        const portfolioSummary = portfolio.portfolio_summary;
        
        console.log(`组合总价值: ${DataFormatter.formatCurrency(portfolioSummary.total_value)}`);
        console.log(`资产数量: ${portfolioSummary.number_of_assets}`);
        console.log(`平台数量: ${portfolioSummary.number_of_platforms}`);
        console.log(`分散化评分: ${DataFormatter.formatPercentage(portfolio.diversification_score)}`);
        
        if (portfolio.rebalancing_suggestions.length > 0) {
            console.log('\n⚠️ 再平衡建议:');
            portfolio.rebalancing_suggestions.slice(0, 2).forEach(suggestion => {
                console.log(`  - ${suggestion.reason}`);
            });
        }
        
        // 6. 风险评估
        console.log('\n6. 风险评估...');
        const risk = await client.getRiskAssessment('CNY', 90);
        const metrics = risk.risk_metrics;
        
        console.log(`年化波动率: ${DataFormatter.formatPercentage(metrics.annual_volatility * 100)}`);
        console.log(`最大回撤: ${DataFormatter.formatPercentage(metrics.max_drawdown * 100)}`);
        console.log(`夏普比率: ${metrics.sharpe_ratio.toFixed(2)}`);
        console.log(`风险等级: ${metrics.risk_level}`);
        
        // 7. 汇率数据
        console.log('\n7. 汇率数据...');
        const rates = await client.getExchangeRates('CNY', 'USD,EUR');
        
        if (rates.rates.length > 0) {
            console.log('当前汇率:');
            rates.rates.slice(0, 3).forEach(rate => {
                console.log(`  ${rate.from_currency}/${rate.to_currency}: ${rate.rate.toFixed(4)}`);
            });
        }
        
        console.log('\n' + '='.repeat(60));
        console.log('数据获取完成！');
        
    } catch (error) {
        console.error('\n❌ 获取数据时发生错误:');
        console.error(error.message);
        
        if (error.message.includes('API密钥')) {
            console.log('\n请检查:');
            console.log('1. API密钥是否正确');
            console.log('2. 服务器是否正在运行');
            console.log('3. 网络连接是否正常');
        }
    }
}

// 导出类供其他模块使用
module.exports = {
    AIAnalystClient,
    DataFormatter
};

// 如果直接运行此脚本
if (require.main === module) {
    main().catch(console.error);
}