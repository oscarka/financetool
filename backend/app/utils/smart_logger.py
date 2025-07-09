"""
智能日志系统 - 零配置，自动检测，最少代码
让开发者完全不需要关心日志，系统自动处理一切
"""

import functools
import time
import inspect
import os
from typing import Optional, Dict, Any, Callable
from contextlib import contextmanager
from app.utils.logger import (
    log_api, log_database, log_scheduler, log_business, log_error, log_system, log_security,
    log_fund_api, log_okx_api, log_wise_api, log_paypal_api, log_exchange_api, log_external_other
)

# 智能服务检测规则
SERVICE_DETECTION_RULES = {
    # 文件名检测
    'fund': ['fund', 'nav', '净值', '基金'],
    'okx': ['okx', 'crypto', 'btc', 'eth', '加密货币'],
    'wise': ['wise', 'transfer', '转账', '国际'],
    'paypal': ['paypal', 'payment', '支付'],
    'exchange': ['exchange', 'rate', '汇率'],
    'database': ['db', 'database', 'sql', 'query', 'insert', 'update', 'delete'],
    'api': ['api', 'http', 'request', 'response'],
    'scheduler': ['scheduler', 'cron', 'task', '定时'],
    'business': ['business', 'logic', 'process', 'order', 'trade'],
}

# 函数名检测规则
FUNCTION_DETECTION_RULES = {
    'fund': ['get_fund', 'sync_fund', 'fund_nav', 'fund_info'],
    'okx': ['okx_', 'get_balance', 'get_position', 'crypto_'],
    'wise': ['wise_', 'transfer', 'get_rate'],
    'paypal': ['paypal_', 'payment', 'transaction'],
    'exchange': ['exchange_', 'get_rate', 'currency'],
    'database': ['get_', 'create_', 'update_', 'delete_', 'save_', 'query_'],
    'api': ['api_', 'http_', 'request_', 'call_'],
    'scheduler': ['sync_', 'update_', 'refresh_', 'task_'],
}

def detect_service_type(func: Callable) -> str:
    """智能检测服务类型"""
    func_name = func.__name__.lower()
    module_name = func.__module__.lower()
    file_name = os.path.basename(inspect.getfile(func)).lower()
    
    # 1. 检查函数名
    for service, patterns in FUNCTION_DETECTION_RULES.items():
        if any(pattern in func_name for pattern in patterns):
            return service
    
    # 2. 检查模块名和文件名
    for service, patterns in SERVICE_DETECTION_RULES.items():
        if any(pattern in module_name or pattern in file_name for pattern in patterns):
            return service
    
    # 3. 检查类名（如果函数在类中）
    if hasattr(func, '__self__') and func.__self__:
        class_name = func.__self__.__class__.__name__.lower()
        for service, patterns in SERVICE_DETECTION_RULES.items():
            if any(pattern in class_name for pattern in patterns):
                return service
    
    # 4. 默认返回business
    return 'business'

def smart_log(func: Callable = None, *, 
              service: str = None, 
              level: str = "INFO",
              log_args: bool = True,
              log_result: bool = False,
              log_time: bool = True,
              log_exceptions: bool = True,
              auto_detect: bool = True):
    """
    智能日志装饰器 - 零配置，自动检测服务类型
    
    使用方式：
    1. 最简单：@smart_log
    2. 指定服务：@smart_log(service="fund")
    3. 高级配置：@smart_log(service="fund", log_result=True)
    """
    def decorator(func: Callable) -> Callable:
        # 自动检测服务类型
        if auto_detect and service is None:
            detected_service = detect_service_type(func)
        else:
            detected_service = service or 'business'
        
        # 获取对应的日志函数
        log_func = {
            'fund': log_fund_api,
            'okx': log_okx_api,
            'wise': log_wise_api,
            'paypal': log_paypal_api,
            'exchange': log_exchange_api,
            'api': log_api,
            'database': log_database,
            'scheduler': log_scheduler,
            'business': log_business,
            'error': log_error,
            'system': log_system,
            'security': log_security,
        }.get(detected_service, log_business)
        
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()
            func_name = func.__name__
            module_name = func.__module__.split('.')[-1]
            
            # 记录函数调用
            extra_data = {}
            if log_args:
                safe_args = _sanitize_args(args, kwargs)
                extra_data.update(safe_args)
            
            if log_time:
                extra_data['start_time'] = start_time
            
            log_func(f"调用函数: {module_name}.{func_name}", level=level, extra_data=extra_data)
            
            try:
                result = await func(*args, **kwargs)
                
                if log_time:
                    execution_time = time.time() - start_time
                    extra_data['execution_time'] = execution_time
                    extra_data['status'] = 'success'
                
                if log_result and result is not None:
                    safe_result = _sanitize_result(result)
                    extra_data['result'] = safe_result
                
                log_func(f"函数执行成功: {module_name}.{func_name}", level=level, extra_data=extra_data)
                return result
                
            except Exception as e:
                if log_exceptions:
                    execution_time = time.time() - start_time
                    extra_data.update({
                        'execution_time': execution_time,
                        'status': 'error',
                        'error_type': type(e).__name__,
                        'error_message': str(e)
                    })
                    log_func(f"函数执行失败: {module_name}.{func_name}", level="ERROR", extra_data=extra_data)
                raise
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = time.time()
            func_name = func.__name__
            module_name = func.__module__.split('.')[-1]
            
            extra_data = {}
            if log_args:
                safe_args = _sanitize_args(args, kwargs)
                extra_data.update(safe_args)
            
            if log_time:
                extra_data['start_time'] = start_time
            
            log_func(f"调用函数: {module_name}.{func_name}", level=level, extra_data=extra_data)
            
            try:
                result = func(*args, **kwargs)
                
                if log_time:
                    execution_time = time.time() - start_time
                    extra_data['execution_time'] = execution_time
                    extra_data['status'] = 'success'
                
                if log_result and result is not None:
                    safe_result = _sanitize_result(result)
                    extra_data['result'] = safe_result
                
                log_func(f"函数执行成功: {module_name}.{func_name}", level=level, extra_data=extra_data)
                return result
                
            except Exception as e:
                if log_exceptions:
                    execution_time = time.time() - start_time
                    extra_data.update({
                        'execution_time': execution_time,
                        'status': 'error',
                        'error_type': type(e).__name__,
                        'error_message': str(e)
                    })
                    log_func(f"函数执行失败: {module_name}.{func_name}", level="ERROR", extra_data=extra_data)
                raise
        
        if inspect.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    # 支持无参数调用：@smart_log
    if func is None:
        return decorator
    else:
        return decorator(func)

@contextmanager
def smart_context(operation: str = None, service: str = None, level: str = "INFO"):
    """
    智能上下文管理器 - 自动检测服务类型
    
    使用方式：
    1. 最简单：with smart_context("操作描述"):
    2. 指定服务：with smart_context("操作描述", service="fund"):
    """
    # 自动检测服务类型
    if service is None:
        caller_frame = inspect.currentframe()
        if caller_frame and caller_frame.f_back:
            caller_info = inspect.getframeinfo(caller_frame.f_back)
            file_name = os.path.basename(caller_info.filename).lower()
            for detected_service, patterns in SERVICE_DETECTION_RULES.items():
                if any(pattern in file_name for pattern in patterns):
                    service = detected_service
                    break
        service = service or 'business'
    
    log_func = {
        'fund': log_fund_api,
        'okx': log_okx_api,
        'wise': log_wise_api,
        'paypal': log_paypal_api,
        'exchange': log_exchange_api,
        'api': log_api,
        'database': log_database,
        'scheduler': log_scheduler,
        'business': log_business,
        'error': log_error,
        'system': log_system,
        'security': log_security,
    }.get(service, log_business)
    
    start_time = time.time()
    
    # 获取调用者信息
    caller_frame = inspect.currentframe()
    if caller_frame and caller_frame.f_back:
        caller_info = inspect.getframeinfo(caller_frame.f_back)
        operation = operation or f"{caller_info.filename}:{caller_info.lineno}"
    else:
        operation = operation or "unknown_operation"
    
    try:
        log_func(f"开始执行: {operation}", level=level, extra_data={'start_time': start_time})
        yield
        execution_time = time.time() - start_time
        log_func(f"执行完成: {operation}", level=level, 
                extra_data={'execution_time': execution_time, 'status': 'success'})
    except Exception as e:
        execution_time = time.time() - start_time
        log_func(f"执行失败: {operation}", level="ERROR",
                extra_data={
                    'execution_time': execution_time,
                    'status': 'error',
                    'error_type': type(e).__name__,
                    'error_message': str(e)
                })
        raise

def smart_log_message(message: str, level: str = "INFO", **kwargs):
    """
    智能日志消息 - 自动检测服务类型
    
    使用方式：
    smart_log_message("操作成功", fund_code="000001")
    """
    # 从调用栈检测服务类型
    caller_frame = inspect.currentframe()
    service = 'business'
    
    if caller_frame and caller_frame.f_back:
        caller_info = inspect.getframeinfo(caller_frame.f_back)
        file_name = os.path.basename(caller_info.filename).lower()
        for detected_service, patterns in SERVICE_DETECTION_RULES.items():
            if any(pattern in file_name for pattern in patterns):
                service = detected_service
                break
    
    log_func = {
        'fund': log_fund_api,
        'okx': log_okx_api,
        'wise': log_wise_api,
        'paypal': log_paypal_api,
        'exchange': log_exchange_api,
        'api': log_api,
        'database': log_database,
        'scheduler': log_scheduler,
        'business': log_business,
        'error': log_error,
        'system': log_system,
        'security': log_security,
    }.get(service, log_business)
    
    log_func(message, level=level, extra_data=kwargs if kwargs else None)

# 便捷别名 - 让使用更简单
log = smart_log
context = smart_context
log_msg = smart_log_message

def _sanitize_args(args, kwargs) -> Dict[str, Any]:
    """安全地处理函数参数，排除敏感信息"""
    sensitive_keys = {'password', 'token', 'secret', 'key', 'api_key', 'private_key'}
    
    safe_data = {}
    
    if args:
        safe_data['args_count'] = len(args)
        if args and len(str(args[0])) < 100:
            safe_data['first_arg'] = str(args[0])
    
    safe_kwargs = {}
    for key, value in kwargs.items():
        if any(sensitive in key.lower() for sensitive in sensitive_keys):
            safe_kwargs[key] = '***HIDDEN***'
        elif isinstance(value, (str, int, float, bool)) and len(str(value)) < 100:
            safe_kwargs[key] = value
        else:
            safe_kwargs[key] = f"{type(value).__name__}({len(str(value))} chars)"
    
    if safe_kwargs:
        safe_data['kwargs'] = safe_kwargs
    
    return safe_data

def _sanitize_result(result) -> Any:
    """安全地处理函数结果"""
    if isinstance(result, (str, int, float, bool)):
        if len(str(result)) < 200:
            return result
        else:
            return f"{type(result).__name__}({len(str(result))} chars)"
    elif isinstance(result, dict):
        safe_result = {}
        for i, (key, value) in enumerate(result.items()):
            if i >= 5:
                safe_result['...'] = f"还有 {len(result) - 5} 个键值对"
                break
            if isinstance(value, (str, int, float, bool)) and len(str(value)) < 100:
                safe_result[key] = value
            else:
                safe_result[key] = f"{type(value).__name__}"
        return safe_result
    elif isinstance(result, list):
        if len(result) <= 3:
            return [_sanitize_result(item) for item in result]
        else:
            return f"list({len(result)} items)"
    else:
        return f"{type(result).__name__}"