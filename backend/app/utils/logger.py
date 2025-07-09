import logging
import sys
import os
from datetime import datetime
from pathlib import Path
import json
from typing import Optional, Dict, Any
from enum import Enum

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

class StructuredFormatter(logging.Formatter):
    """结构化日志格式化器"""
    
    def format(self, record: logging.LogRecord) -> str:
        # 创建结构化日志数据
        log_data = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "category": getattr(record, 'category', LogCategory.SYSTEM),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
            "message": record.getMessage(),
        }
        
        # 添加额外的上下文信息
        extra_data = getattr(record, 'extra_data', None)
        if extra_data:
            log_data.update(extra_data)
            
        request_id = getattr(record, 'request_id', None)
        if request_id:
            log_data['request_id'] = request_id
            
        user_id = getattr(record, 'user_id', None)
        if user_id:
            log_data['user_id'] = user_id
        
        # 如果有异常信息，添加堆栈跟踪
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)
        
        return json.dumps(log_data, ensure_ascii=False, separators=(',', ':'))

class CategoryLogger:
    """分类日志记录器"""
    
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
            
            # 控制台处理器 - 在Railway上主要用这个
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(logging.INFO if is_production else logging.DEBUG)
            
            if is_production:
                # 生产环境使用结构化格式
                console_handler.setFormatter(StructuredFormatter())
            else:
                # 开发环境使用可读格式
                formatter = logging.Formatter(
                    fmt='%(asctime)s [%(levelname)s] [%(name)s] %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S'
                )
                console_handler.setFormatter(formatter)
            
            logger.addHandler(console_handler)
            
            # 文件处理器 - 总是创建文件，便于日志查看器读取
            file_handler = logging.FileHandler(
                log_dir / f"{category}.log", 
                encoding='utf-8'
            )
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(StructuredFormatter())
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
app_logger = CategoryLogger()

# 便捷函数
def log_api(message: str, level: str = "INFO", **kwargs):
    """记录API相关日志"""
    app_logger.log(LogCategory.API, level, message, **kwargs)

def log_database(message: str, level: str = "INFO", **kwargs):
    """记录数据库相关日志"""
    app_logger.log(LogCategory.DATABASE, level, message, **kwargs)

def log_scheduler(message: str, level: str = "INFO", **kwargs):
    """记录定时任务相关日志"""
    app_logger.log(LogCategory.SCHEDULER, level, message, **kwargs)

def log_fund_api(message: str, level: str = "INFO", **kwargs):
    """记录基金API调用相关日志"""
    app_logger.log(LogCategory.FUND_API, level, message, **kwargs)

def log_okx_api(message: str, level: str = "INFO", **kwargs):
    """记录OKX API调用相关日志"""
    app_logger.log(LogCategory.OKX_API, level, message, **kwargs)

def log_wise_api(message: str, level: str = "INFO", **kwargs):
    """记录Wise API调用相关日志"""
    app_logger.log(LogCategory.WISE_API, level, message, **kwargs)

def log_paypal_api(message: str, level: str = "INFO", **kwargs):
    """记录PayPal API调用相关日志"""
    app_logger.log(LogCategory.PAYPAL_API, level, message, **kwargs)

def log_exchange_api(message: str, level: str = "INFO", **kwargs):
    """记录汇率API调用相关日志"""
    app_logger.log(LogCategory.EXCHANGE_API, level, message, **kwargs)

def log_external_other(message: str, level: str = "INFO", **kwargs):
    """记录其他外部API调用相关日志"""
    app_logger.log(LogCategory.EXTERNAL_OTHER, level, message, **kwargs)

def log_business(message: str, level: str = "INFO", **kwargs):
    """记录业务逻辑相关日志"""
    app_logger.log(LogCategory.BUSINESS, level, message, **kwargs)

def log_error(message: str, level: str = "ERROR", **kwargs):
    """记录错误日志"""
    app_logger.log(LogCategory.ERROR, level, message, **kwargs)

def log_system(message: str, level: str = "INFO", **kwargs):
    """记录系统运行相关日志"""
    app_logger.log(LogCategory.SYSTEM, level, message, **kwargs)

def log_security(message: str, level: str = "WARNING", **kwargs):
    """记录安全相关日志"""
    app_logger.log(LogCategory.SECURITY, level, message, **kwargs)