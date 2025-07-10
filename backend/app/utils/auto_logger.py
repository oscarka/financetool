import functools
import time
import inspect
from typing import Optional, Dict, Any, Callable
from contextlib import contextmanager
from app.utils.logger import (
    log_api, log_database, log_scheduler, log_business, log_error, log_system, log_security,
    log_fund_api, log_okx_api, log_wise_api, log_paypal_api, log_exchange_api, log_external_other
)

# 服务名称到日志函数的映射
SERVICE_LOG_MAPPING = {
    # 外部服务
    'fund': log_fund_api,
    'okx': log_okx_api,
    'wise': log_wise_api,
    'paypal': log_paypal_api,
    'exchange': log_exchange_api,
    'external': log_external_other,
    
    # 基础服务
    'api': log_api,
    'database': log_database,
    'scheduler': log_scheduler,
    'business': log_business,
    'error': log_error,
    'system': log_system,
    'security': log_security,
}

def auto_log(service: str = "business", level: str = "INFO", 
             log_args: bool = True, log_result: bool = False,
             log_time: bool = True, log_exceptions: bool = True):
    """
    自动日志装饰器 - 一行代码实现完整日志功能
    
    使用示例:
    @auto_log("fund")  # 自动记录基金API调用
    async def get_fund_nav(fund_code: str):
        return await api_call()
    
    @auto_log("database", log_result=True)  # 记录数据库操作和结果
    def create_user(user_data: dict):
        return db.insert(user_data)
    """
    def decorator(func: Callable) -> Callable:
        log_func = SERVICE_LOG_MAPPING.get(service, log_business)
        
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()
            func_name = func.__name__
            module_name = func.__module__.split('.')[-1]
            
            # 记录函数调用
            extra_data = {}
            if log_args:
                # 安全地记录参数（排除敏感信息）
                safe_args = _sanitize_args(args, kwargs)
                extra_data.update(safe_args)
            
            if log_time:
                extra_data['start_time'] = start_time
            
            log_func(f"调用函数: {module_name}.{func_name}", level=level, extra_data=extra_data)
            
            try:
                # 执行函数
                result = await func(*args, **kwargs)
                
                # 记录执行时间
                if log_time:
                    execution_time = time.time() - start_time
                    extra_data['execution_time'] = execution_time
                    extra_data['status'] = 'success'
                
                # 记录结果（可选）
                if log_result and result is not None:
                    print("[auto_log] 原始result:", repr(result))
                    safe_result = _sanitize_result(result)
                    print("[auto_log] 写入日志的result:", repr(safe_result))
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
            
            # 记录函数调用
            extra_data = {}
            if log_args:
                safe_args = _sanitize_args(args, kwargs)
                extra_data.update(safe_args)
            
            if log_time:
                extra_data['start_time'] = start_time
            
            log_func(f"调用函数: {module_name}.{func_name}", level=level, extra_data=extra_data)
            
            try:
                # 执行函数
                result = func(*args, **kwargs)
                
                # 记录执行时间
                if log_time:
                    execution_time = time.time() - start_time
                    extra_data['execution_time'] = execution_time
                    extra_data['status'] = 'success'
                
                # 记录结果（可选）
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
        
        # 根据函数类型返回对应的包装器
        if inspect.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator

@contextmanager
def log_context(service: str = "business", operation: str = None, 
                level: str = "INFO", log_exceptions: bool = True):
    """
    日志上下文管理器 - 一行代码记录代码块执行
    
    使用示例:
    with log_context("fund", "获取基金净值"):
        result = await api_call()
    
    with log_context("database", "批量插入"):
        db.bulk_insert(data)
    """
    log_func = SERVICE_LOG_MAPPING.get(service, log_business)
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
        if log_exceptions:
            execution_time = time.time() - start_time
            log_func(f"执行失败: {operation}", level="ERROR",
                    extra_data={
                        'execution_time': execution_time,
                        'status': 'error',
                        'error_type': type(e).__name__,
                        'error_message': str(e)
                    })
        raise

def log_api_call(service: str = "external", endpoint: str = None, 
                 method: str = "GET", timeout: float = 30.0):
    """
    API调用日志装饰器 - 专门用于记录外部API调用
    
    使用示例:
    @log_api_call("fund", "/api/fund/nav")
    async def get_fund_nav(fund_code: str):
        return await httpx.get(f"https://api.example.com/fund/{fund_code}")
    """
    def decorator(func: Callable) -> Callable:
        log_func = SERVICE_LOG_MAPPING.get(service, log_external_other)
        
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()
            func_name = func.__name__
            
            # 记录API调用开始
            extra_data = {
                'endpoint': endpoint if endpoint else func_name,
                'method': method,
                'timeout': timeout,
                'start_time': start_time
            }
            
            log_func(f"API调用开始: {method} {endpoint or func_name}", level="INFO", extra_data=extra_data)
            
            try:
                result = await func(*args, **kwargs)
                execution_time = time.time() - start_time
                
                extra_data.update({
                    'execution_time': execution_time,
                    'status': 'success',
                    'response_size': len(str(result)) if result else 0
                })
                
                log_func(f"API调用成功: {method} {endpoint or func_name}", level="INFO", extra_data=extra_data)
                return result
                
            except Exception as e:
                execution_time = time.time() - start_time
                extra_data.update({
                    'execution_time': execution_time,
                    'status': 'error',
                    'error_type': type(e).__name__,
                    'error_message': str(e)
                })
                log_func(f"API调用失败: {method} {endpoint or func_name}", level="ERROR", extra_data=extra_data)
                raise
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = time.time()
            func_name = func.__name__
            
            extra_data = {
                'endpoint': endpoint if endpoint else func_name,
                'method': method,
                'timeout': timeout,
                'start_time': start_time
            }
            
            log_func(f"API调用开始: {method} {endpoint or func_name}", level="INFO", extra_data=extra_data)
            
            try:
                result = func(*args, **kwargs)
                execution_time = time.time() - start_time
                
                extra_data.update({
                    'execution_time': execution_time,
                    'status': 'success',
                    'response_size': len(str(result)) if result else 0
                })
                
                log_func(f"API调用成功: {method} {endpoint or func_name}", level="INFO", extra_data=extra_data)
                return result
                
            except Exception as e:
                execution_time = time.time() - start_time
                extra_data.update({
                    'execution_time': execution_time,
                    'status': 'error',
                    'error_type': type(e).__name__,
                    'error_message': str(e)
                })
                log_func(f"API调用失败: {method} {endpoint or func_name}", level="ERROR", extra_data=extra_data)
                raise
        
        if inspect.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator

def _sanitize_args(args, kwargs) -> Dict[str, Any]:
    """安全地处理函数参数，排除敏感信息"""
    sensitive_keys = {'password', 'token', 'secret', 'key', 'api_key', 'private_key'}
    
    safe_data = {}
    
    # 处理位置参数
    if args:
        safe_data['args_count'] = len(args)
        # 只记录第一个参数（通常是主要参数）
        if args:
            first_arg = args[0]
            if isinstance(first_arg, (str, int, float, bool)) and len(str(first_arg)) < 100:
                safe_data['first_arg'] = first_arg
            else:
                safe_data['first_arg'] = _serialize_for_json(first_arg)
    
    # 处理关键字参数
    safe_kwargs = {}
    for key, value in kwargs.items():
        if any(sensitive in key.lower() for sensitive in sensitive_keys):
            safe_kwargs[key] = '***HIDDEN***'
        elif isinstance(value, (str, int, float, bool)) and len(str(value)) < 100:
            safe_kwargs[key] = value
        else:
            safe_kwargs[key] = _serialize_for_json(value)
    
    if safe_kwargs:
        safe_data['kwargs'] = safe_kwargs
    
    return safe_data

def _sanitize_result(result) -> Any:
    """安全地处理函数结果，处理不可序列化的对象"""
    return _serialize_for_json(result)

def _serialize_for_json(obj) -> Any:
    """将对象序列化为JSON兼容的格式"""
    if obj is None:
        return None
    
    # 处理基本类型
    if isinstance(obj, (str, int, float, bool)):
        return obj
    
    # 处理Decimal类型
    if hasattr(obj, '__class__') and obj.__class__.__name__ == 'Decimal':
        return float(obj)
    
    # 处理datetime类型
    if hasattr(obj, 'isoformat'):
        try:
            return obj.isoformat()
        except:
            return str(obj)
    
    # 处理SQLAlchemy ORM对象
    if hasattr(obj, '__table__') or hasattr(obj, '_sa_instance_state'):
        return _serialize_sqlalchemy_object(obj)
    
    # 处理列表
    if isinstance(obj, list):
        return [_serialize_for_json(item) for item in obj]
    
    # 处理字典
    if isinstance(obj, dict):
        return {key: _serialize_for_json(value) for key, value in obj.items()}
    
    # 处理元组
    if isinstance(obj, tuple):
        return tuple(_serialize_for_json(item) for item in obj)
    
    # 处理集合
    if isinstance(obj, (set, frozenset)):
        return list(_serialize_for_json(item) for item in obj)
    
    # 其他对象转换为字符串
    try:
        return str(obj)
    except:
        return f"<{type(obj).__name__} object>"

def _serialize_sqlalchemy_object(obj) -> dict:
    """序列化SQLAlchemy ORM对象"""
    try:
        # 尝试获取表名
        table_name = getattr(obj, '__tablename__', type(obj).__name__)
        
        # 获取所有列的值
        result = {'_type': f'SQLAlchemy_{table_name}'}
        
        for column in obj.__table__.columns:
            try:
                value = getattr(obj, column.name)
                if value is not None:
                    # 处理特殊类型
                    if hasattr(value, '__class__') and value.__class__.__name__ == 'Decimal':
                        result[column.name] = float(value)
                    elif hasattr(value, 'isoformat'):
                        result[column.name] = value.isoformat()
                    else:
                        result[column.name] = value
            except Exception:
                continue
        
        return result
    except Exception as e:
        return {
            '_type': f'SQLAlchemy_{type(obj).__name__}',
            '_error': f'序列化失败: {str(e)}',
            '_str': str(obj)
        }

# 便捷函数 - 一行代码记录日志
def quick_log(message: str, service: str = "business", level: str = "INFO", **kwargs):
    """一行代码记录日志"""
    log_func = SERVICE_LOG_MAPPING.get(service, log_business)
    log_func(message, level=level, extra_data=kwargs if kwargs else None)

def log_success(message: str, service: str = "business", **kwargs):
    """记录成功日志"""
    quick_log(message, service, "INFO", status="success", **kwargs)

def log_failure(message: str, service: str = "business", error: Exception = None, **kwargs):
    """记录失败日志"""
    extra_data = kwargs.copy()
    if error:
        extra_data.update({
            'error_type': type(error).__name__,
            'error_message': str(error)
        })
    quick_log(message, service, "ERROR", status="error", **extra_data)