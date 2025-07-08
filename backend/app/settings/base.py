from pydantic_settings import BaseSettings, SettingsConfigDict

class BaseConfig(BaseSettings):
    app_env: str = "test"
    app_name: str = "个人财务管理系统"
    app_version: str = "0.1.0"
    database_url: str
    cors_origins: str
    debug: bool = False
    api_v1_prefix: str = "/api/v1"
    
    # 基金API配置
    fund_api_timeout: int = 10
    fund_api_retry_times: int = 3
    
    # 天天基金网API配置
    tiantian_fund_api_base_url: str = "https://fundgz.1234567.com.cn"
    tiantian_fund_info_base_url: str = "https://fund.eastmoney.com/pingzhongdata"
    
    # 雪球API配置
    xueqiu_api_base_url: str = "https://stock.xueqiu.com/v5/stock/chart/kline.json"
    
    # OKX API配置
    okx_api_base_url: str = "https://www.okx.com"
    okx_api_key: str = ""
    okx_secret_key: str = ""
    okx_passphrase: str = ""
    okx_sandbox: bool = True  # 是否使用沙盒环境
    
    # Wise API配置
    wise_api_token: str = ""
    wise_api_base_url: str = "https://api.transferwise.com"
    
    # PayPal API配置
    paypal_client_id: str = ""
    paypal_client_secret: str = ""
    paypal_api_base_url: str = "https://api-m.sandbox.paypal.com"  # 沙盒环境
    
    # 定时任务配置
    scheduler_timezone: str = "Asia/Shanghai"
    
    # 日志配置
    log_level: str = "INFO"
    log_file: str = "./logs/app.log"

    model_config = SettingsConfigDict(env_file_encoding="utf-8") 