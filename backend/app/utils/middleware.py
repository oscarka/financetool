import uuid
import time
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from app.utils.logger import log_api, log_security

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """请求日志中间件"""
    
    async def dispatch(self, request: Request, call_next):
        # 生成请求ID
        request_id = str(uuid.uuid4())
        
        # 记录请求开始
        start_time = time.time()
        
        # 获取客户端IP
        client_ip = request.client.host if request.client else "unknown"
        
        # 记录请求信息
        log_api(
            f"收到请求: {request.method} {request.url.path}",
            extra_data={
                "method": request.method,
                "path": str(request.url.path),
                "query_params": str(request.query_params),
                "client_ip": client_ip,
                "user_agent": request.headers.get("user-agent", "unknown")
            },
            request_id=request_id
        )
        
        # 安全检查 - 记录可疑请求
        if self._is_suspicious_request(request):
            log_security(
                f"可疑请求: {request.method} {request.url.path} from {client_ip}",
                level="WARNING",
                extra_data={
                    "method": request.method,
                    "path": str(request.url.path),
                    "client_ip": client_ip,
                    "user_agent": request.headers.get("user-agent", "unknown"),
                    "headers": dict(request.headers)
                },
                request_id=request_id
            )
        
        # 将request_id添加到request state中，供其他地方使用
        request.state.request_id = request_id
        
        try:
            # 处理请求
            response: Response = await call_next(request)
            
            # 计算处理时间
            process_time = time.time() - start_time
            
            # 记录响应
            log_api(
                f"请求完成: {response.status_code} in {process_time:.3f}s",
                extra_data={
                    "status_code": response.status_code,
                    "process_time": process_time
                },
                request_id=request_id
            )
            
            # 添加request_id到响应头
            response.headers["X-Request-ID"] = request_id
            
            return response
            
        except Exception as e:
            # 记录请求错误
            process_time = time.time() - start_time
            log_api(
                f"请求处理失败: {str(e)} in {process_time:.3f}s",
                level="ERROR",
                extra_data={
                    "error": str(e),
                    "process_time": process_time,
                    "exception_type": type(e).__name__
                },
                request_id=request_id
            )
            raise
    
    def _is_suspicious_request(self, request: Request) -> bool:
        """检查是否为可疑请求"""
        suspicious_patterns = [
            # 常见的攻击路径
            "/.env", "/admin", "/wp-admin", "/phpMyAdmin",
            "/config", "/backup", "/test", "/.git",
            # SQL注入尝试
            "SELECT", "UNION", "DROP", "INSERT",
            # XSS尝试
            "<script", "javascript:",
            # 路径遍历
            "../", "..\\",
        ]
        
        url_path = str(request.url.path).lower()
        query_string = str(request.url.query).lower()
        
        for pattern in suspicious_patterns:
            if pattern.lower() in url_path or pattern.lower() in query_string:
                return True
        
        # 检查User-Agent
        user_agent = request.headers.get("user-agent", "").lower()
        suspicious_agents = ["bot", "crawler", "scanner", "sqlmap", "nmap"]
        for agent in suspicious_agents:
            if agent in user_agent:
                return True
        
        return False