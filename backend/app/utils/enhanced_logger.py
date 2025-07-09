import logging
import sys
import os
from datetime import datetime
from pathlib import Path
import json
from typing import Optional, Dict, Any
from enum import Enum
import traceback

class LogCategory(str, Enum):
    """日志分类"""
    # 基础分类
    API = "api"          # API请求相关
    DATABASE = "database" # 数据库操作
    SCHEDULER = "scheduler" # 定时任务
    BUSINESS = "business"  # 业务逻辑
    ERROR = "error"       # 错误日志
    SYSTEM = "system"     # 系统运行
    SECURITY = "security" # 安全相关
    
    # 外部服务分类
    FUND_API = "fund_api"     # 基金API调用
    OKX_API = "okx_api"       # OKX加密货币API
    WISE_API = "wise_api"     # Wise金融API
    PAYPAL_API = "paypal_api" # PayPal支付API
    EXCHANGE_API = "exchange_api" # 汇率API
    EXTERNAL_OTHER = "external_other" # 其他外部API

class DetailedFormatter(logging.Formatter):
    """详细日志格式化器"""
    
    def format(self, record: logging.LogRecord) -> str:
        # 创建详细的日志数据
        log_data = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "category": getattr(record, 'category', LogCategory.SYSTEM),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
            "message": record.getMessage(),
            "details": {}
        }
        
        # 添加额外的上下文信息
        extra_data = getattr(record, 'extra_data', None)
        if extra_data:
            log_data["details"].update(extra_data)
            
        request_id = getattr(record, 'request_id', None)
        if request_id:
            log_data['request_id'] = request_id
            
        user_id = getattr(record, 'user_id', None)
        if user_id:
            log_data['user_id'] = user_id
        
        # 如果有异常信息，添加详细的堆栈跟踪
        if record.exc_info:
            log_data['exception'] = {
                'type': type(record.exc_info[1]).__name__,
                'message': str(record.exc_info[1]),
                'traceback': traceback.format_exception(*record.exc_info)
            }
        
        return json.dumps(log_data, ensure_ascii=False, separators=(',', ':'))

class EnhancedLogger:
    """增强的日志记录器"""
    
    def __init__(self):
        self.loggers: Dict[LogCategory, logging.Logger] = {}
        self._setup_loggers()
    
    def _setup_loggers(self):
        """设置各种类别的日志记录器"""
        
        # 确保日志目录存在
        log_dir = Path("./logs")
        log_dir.mkdir(exist_ok=True)
        
        # 是否是生产环境
        is_production = os.getenv("APP_ENV") == "prod"
        
        for category in LogCategory:
            logger = logging.getLogger(f"app.{category}")
            logger.setLevel(logging.INFO if is_production else logging.DEBUG)
            
            # 清除现有的处理器
            logger.handlers.clear()
            
            # 控制台处理器
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(logging.INFO if is_production else logging.DEBUG)
            
            if is_production:
                # 生产环境使用详细格式
                console_handler.setFormatter(DetailedFormatter())
            else:
                # 开发环境使用可读格式
                formatter = logging.Formatter(
                    fmt='%(asctime)s [%(levelname)s] [%(name)s] %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S'
                )
                console_handler.setFormatter(formatter)
            
            logger.addHandler(console_handler)
            
            # 文件处理器 - 总是使用详细格式
            file_handler = logging.FileHandler(
                log_dir / f"{category}.log", 
                encoding='utf-8'
            )
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(DetailedFormatter())
            logger.addHandler(file_handler)
            
            # 防止日志向上传播
            logger.propagate = False
            
            self.loggers[category] = logger
    
    def get_logger(self, category: LogCategory) -> logging.Logger:
        """获取指定分类的日志记录器"""
        return self.loggers.get(category, self.loggers[LogCategory.SYSTEM])
    
    def log(self, category: LogCategory, level: str, message: str, 
            extra_data: Optional[Dict[str, Any]] = None,
            request_id: Optional[str] = None,
            user_id: Optional[str] = None):
        """记录日志"""
        logger = self.get_logger(category)
        
        # 创建日志记录
        extra: Dict[str, Any] = {'category': category.value}
        if extra_data:
            extra['extra_data'] = extra_data
        if request_id:
            extra['request_id'] = request_id
        if user_id:
            extra['user_id'] = user_id
        
        # 根据级别记录日志
        if level.upper() == 'DEBUG':
            logger.debug(message, extra=extra)
        elif level.upper() == 'INFO':
            logger.info(message, extra=extra)
        elif level.upper() == 'WARNING':
            logger.warning(message, extra=extra)
        elif level.upper() == 'ERROR':
            logger.error(message, extra=extra)
        elif level.upper() == 'CRITICAL':
            logger.critical(message, extra=extra)

# 全局日志管理器实例
enhanced_logger = EnhancedLogger()

# 便捷函数 - 增强版本
def log_api_detailed(message: str, level: str = "INFO", **kwargs):
    """记录详细的API相关日志"""
    enhanced_logger.log(LogCategory.API, level, message, **kwargs)

def log_database_detailed(message: str, level: str = "INFO", **kwargs):
    """记录详细的数据库相关日志"""
    enhanced_logger.log(LogCategory.DATABASE, level, message, **kwargs)

def log_scheduler_detailed(message: str, level: str = "INFO", **kwargs):
    """记录详细的定时任务相关日志"""
    enhanced_logger.log(LogCategory.SCHEDULER, level, message, **kwargs)

def log_fund_api_detailed(message: str, level: str = "INFO", **kwargs):
    """记录详细的基金API调用相关日志"""
    enhanced_logger.log(LogCategory.FUND_API, level, message, **kwargs)

def log_okx_api_detailed(message: str, level: str = "INFO", **kwargs):
    """记录详细的OKX API调用相关日志"""
    enhanced_logger.log(LogCategory.OKX_API, level, message, **kwargs)

def log_wise_api_detailed(message: str, level: str = "INFO", **kwargs):
    """记录详细的Wise API调用相关日志"""
    enhanced_logger.log(LogCategory.WISE_API, level, message, **kwargs)

def log_paypal_api_detailed(message: str, level: str = "INFO", **kwargs):
    """记录详细的PayPal API调用相关日志"""
    enhanced_logger.log(LogCategory.PAYPAL_API, level, message, **kwargs)

def log_exchange_api_detailed(message: str, level: str = "INFO", **kwargs):
    """记录详细的汇率API调用相关日志"""
    enhanced_logger.log(LogCategory.EXCHANGE_API, level, message, **kwargs)

def log_external_other_detailed(message: str, level: str = "INFO", **kwargs):
    """记录详细的其他外部API调用相关日志"""
    enhanced_logger.log(LogCategory.EXTERNAL_OTHER, level, message, **kwargs)

def log_business_detailed(message: str, level: str = "INFO", **kwargs):
    """记录详细的业务逻辑相关日志"""
    enhanced_logger.log(LogCategory.BUSINESS, level, message, **kwargs)

def log_error_detailed(message: str, level: str = "ERROR", **kwargs):
    """记录详细的错误日志"""
    enhanced_logger.log(LogCategory.ERROR, level, message, **kwargs)

def log_system_detailed(message: str, level: str = "INFO", **kwargs):
    """记录详细的系统运行相关日志"""
    enhanced_logger.log(LogCategory.SYSTEM, level, message, **kwargs)

def log_security_detailed(message: str, level: str = "WARNING", **kwargs):
    """记录详细的安全相关日志"""
    enhanced_logger.log(LogCategory.SECURITY, level, message, **kwargs)

# 业务专用日志函数
def log_fund_operation(operation_type: str, fund_code: str, amount: float, 
                      quantity: float, price: float, platform: str, **kwargs):
    """记录基金操作详情"""
    log_business_detailed(
        f"基金操作: {operation_type}",
        extra_data={
            "operation_type": operation_type,
            "fund_code": fund_code,
            "amount": amount,
            "quantity": quantity,
            "price": price,
            "platform": platform,
            "operation_time": datetime.now().isoformat(),
            **kwargs
        }
    )

def log_fund_api_call(endpoint: str, fund_code: str, response_data: dict, 
                     execution_time: float, **kwargs):
    """记录基金API调用详情"""
    log_fund_api_detailed(
        f"基金API调用: {endpoint}",
        extra_data={
            "endpoint": endpoint,
            "fund_code": fund_code,
            "response_data": response_data,
            "execution_time": execution_time,
            "call_time": datetime.now().isoformat(),
            **kwargs
        }
    )

def log_database_operation(operation: str, table: str, record_id: Optional[int] = None, 
                          data: Optional[dict] = None, execution_time: Optional[float] = None, **kwargs):
    """记录数据库操作详情"""
    extra_data = {
        "operation": operation,
        "table": table,
        "operation_time": datetime.now().isoformat(),
        **kwargs
    }
    if record_id is not None:
        extra_data["record_id"] = record_id
    if data is not None:
        extra_data["data"] = data
    if execution_time is not None:
        extra_data["execution_time"] = execution_time
    
    log_database_detailed(f"数据库操作: {operation}", extra_data=extra_data)

def log_api_request(method: str, path: str, params: Optional[dict] = None, 
                   response_status: Optional[int] = None, execution_time: Optional[float] = None, **kwargs):
    """记录API请求详情"""
    extra_data = {
        "method": method,
        "path": path,
        "request_time": datetime.now().isoformat(),
        **kwargs
    }
    if params is not None:
        extra_data["params"] = params
    if response_status is not None:
        extra_data["response_status"] = response_status
    if execution_time is not None:
        extra_data["execution_time"] = execution_time
    
    log_api_detailed(f"API请求: {method} {path}", extra_data=extra_data)