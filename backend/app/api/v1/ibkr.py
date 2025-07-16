from fastapi import APIRouter, HTTPException, Header, Query, Request
from typing import List, Dict, Any, Optional
from datetime import datetime
from loguru import logger

from app.services.ibkr_api_service import IBKRAPIService
from app.models.schemas import IBKRSyncRequest, IBKRSyncResponse
from app.utils.database import engine
from sqlalchemy import text

router = APIRouter(prefix="/ibkr", tags=["IBKR API"])

# 初始化IBKR API服务
ibkr_service = IBKRAPIService()


def _get_client_ip(request: Request) -> str:
    """获取客户端真实IP地址"""
    # 优先检查X-Forwarded-For头部（代理环境）
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        # 取第一个IP（客户端IP）
        return forwarded_for.split(",")[0].strip()
    
    # 检查X-Real-IP头部
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip
    
    # 最后使用客户端IP
    return request.client.host if request.client else "unknown"


def _validate_api_key(api_key: Optional[str]) -> bool:
    """验证API密钥"""
    if not api_key:
        return False
    return ibkr_service._validate_api_key(api_key)


@router.post("/sync", response_model=IBKRSyncResponse)
async def sync_ibkr_data(
    request: Request,
    sync_request: IBKRSyncRequest,
    x_api_key: str = Header(..., alias="X-API-Key", description="IBKR API密钥")
):
    """
    接收IBKR数据同步请求
    
    ## 请求格式
    ```json
    {
        "account_id": "U13638726",
        "timestamp": "2024-01-01T12:00:00Z",
        "balances": {
            "total_cash": 2.74,
            "net_liquidation": 5.70,
            "buying_power": 2.74,
            "currency": "USD"
        },
        "positions": [
            {
                "symbol": "TSLA",
                "quantity": 0.01,
                "market_value": 2.96,
                "average_cost": 0.0,
                "currency": "USD"
            }
        ]
    }
    ```
    
    ## 响应格式
    ```json
    {
        "status": "success",
        "message": "IBKR data synchronized successfully",
        "received_at": "2024-01-01T12:00:00Z",
        "records_updated": {
            "balances": 1,
            "positions": 1
        }
    }
    ```
    """
    try:
        # 1. 验证API密钥
        if not _validate_api_key(x_api_key):
            logger.warning(f"IBKR API密钥验证失败，来源IP: {_get_client_ip(request)}")
            raise HTTPException(status_code=401, detail="Invalid API key")
        
        # 2. 获取客户端信息
        client_ip = _get_client_ip(request)
        user_agent = request.headers.get("User-Agent", "unknown")
        
        logger.info(f"接收到IBKR同步请求: account_id={sync_request.account_id}, IP={client_ip}")
        
        # 3. 处理同步请求
        response = await ibkr_service.sync_data(
            request_data=sync_request,
            client_ip=client_ip,
            user_agent=user_agent
        )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"IBKR数据同步处理失败: {e}")
        raise HTTPException(status_code=500, detail=f"Synchronization failed: {str(e)}")


@router.get("/config")
async def get_ibkr_config():
    """获取IBKR API配置信息"""
    try:
        config = await ibkr_service.get_config()
        return {
            "success": True,
            "data": config
        }
    except Exception as e:
        logger.error(f"获取IBKR配置失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取配置失败: {str(e)}")


@router.get("/test")
async def test_ibkr_connection():
    """测试IBKR API连接状态"""
    try:
        result = await ibkr_service.test_connection()
        return {
            "success": True,
            "data": result
        }
    except Exception as e:
        logger.error(f"测试IBKR连接失败: {e}")
        raise HTTPException(status_code=500, detail=f"测试连接失败: {str(e)}")


@router.get("/accounts/{account_id}")
async def get_ibkr_account_info(account_id: str):
    """获取指定IBKR账户信息"""
    try:
        account_info = await ibkr_service.get_account_info(account_id)
        if not account_info:
            raise HTTPException(status_code=404, detail=f"Account not found: {account_id}")
        
        return {
            "success": True,
            "data": account_info
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取IBKR账户信息失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取账户信息失败: {str(e)}")


@router.get("/balances")
async def get_ibkr_balances(
    account_id: Optional[str] = Query(None, description="账户ID，不提供则返回所有账户")
):
    """获取IBKR账户余额"""
    logger.info(f"🌐 收到获取IBKR余额请求 - account_id: {account_id}")
    try:
        balances = await ibkr_service.get_latest_balances(account_id)
        logger.info(f"✅ 成功返回余额数据 - 数量: {len(balances)}")
        return {
            "success": True,
            "data": balances,
            "count": len(balances)
        }
    except Exception as e:
        logger.error(f"❌ 获取IBKR余额失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取余额失败: {str(e)}")


@router.get("/positions")
async def get_ibkr_positions(
    account_id: Optional[str] = Query(None, description="账户ID，不提供则返回所有账户")
):
    """获取IBKR持仓信息"""
    logger.info(f"🌐 收到获取IBKR持仓请求 - account_id: {account_id}")
    try:
        positions = await ibkr_service.get_latest_positions(account_id)
        logger.info(f"✅ 成功返回持仓数据 - 数量: {len(positions)}")
        return {
            "success": True,
            "data": positions,
            "count": len(positions)
        }
    except Exception as e:
        logger.error(f"❌ 获取IBKR持仓失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取持仓失败: {str(e)}")


@router.get("/logs")
async def get_ibkr_sync_logs(
    account_id: Optional[str] = Query(None, description="账户ID过滤"),
    limit: int = Query(50, ge=1, le=100, description="返回记录数量限制"),
    status: Optional[str] = Query(None, description="状态过滤: success, error, partial")
):
    """获取IBKR同步日志"""
    try:
        logs = await ibkr_service.get_sync_logs(account_id, limit, status)
        return {
            "success": True,
            "data": logs,
            "count": len(logs)
        }
    except Exception as e:
        logger.error(f"获取IBKR同步日志失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取同步日志失败: {str(e)}")


@router.get("/summary")
async def get_ibkr_summary():
    """获取IBKR账户汇总信息"""
    try:
        # 获取最新余额
        balances = await ibkr_service.get_latest_balances()
        
        # 获取最新持仓
        positions = await ibkr_service.get_latest_positions()
        
        # 获取最近同步日志
        recent_logs = await ibkr_service.get_sync_logs(limit=10)
        
        # 计算汇总信息
        total_accounts = len(set(b['account_id'] for b in balances))
        total_positions = len(positions)
        total_net_liquidation = sum(b['net_liquidation'] for b in balances)
        total_cash = sum(b['total_cash'] for b in balances)
        
        # 最近同步状态
        last_sync = recent_logs[0] if recent_logs else None
        last_sync_status = last_sync['status'] if last_sync else 'unknown'
        last_sync_time = last_sync['created_at'] if last_sync else None
        
        summary = {
            "total_accounts": total_accounts,
            "total_positions": total_positions,
            "total_net_liquidation": total_net_liquidation,
            "total_cash": total_cash,
            "last_sync_status": last_sync_status,
            "last_sync_time": last_sync_time,
            "last_updated": datetime.now().isoformat()
        }
        
        return {
            "success": True,
            "data": summary
        }
    except Exception as e:
        logger.error(f"获取IBKR汇总信息失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取汇总信息失败: {str(e)}")


@router.get("/health")
async def ibkr_health_check():
    """IBKR服务健康检查"""
    try:
        config_check = await ibkr_service.get_config()
        connection_check = await ibkr_service.test_connection()
        
        # 添加数据库诊断信息
        db_info = {}
        try:
            from app.utils.database import SessionLocal
            from sqlalchemy import text
            db = SessionLocal()
            # 检查IBKR相关表
            ibkr_accounts_count = db.execute(text("SELECT COUNT(*) FROM ibkr_accounts")).scalar()
            ibkr_balances_count = db.execute(text("SELECT COUNT(*) FROM ibkr_balances")).scalar()
            ibkr_positions_count = db.execute(text("SELECT COUNT(*) FROM ibkr_positions")).scalar()
            ibkr_sync_logs_count = db.execute(text("SELECT COUNT(*) FROM ibkr_sync_logs")).scalar()
            db.close()
            
            db_info = {
                "ibkr_accounts_count": ibkr_accounts_count,
                "ibkr_balances_count": ibkr_balances_count,
                "ibkr_positions_count": ibkr_positions_count,
                "ibkr_sync_logs_count": ibkr_sync_logs_count
            }
        except Exception as e:
            db_info = {"error": str(e)}
        
        health_status = {
            "service": "ibkr",
            "status": "healthy" if connection_check.get("config_valid") and connection_check.get("database_ok") else "unhealthy",
            "config_valid": connection_check.get("config_valid", False),
            "database_ok": connection_check.get("database_ok", False),
            "api_configured": config_check.get("api_configured", False),
            "database_info": db_info,
            "timestamp": datetime.now().isoformat()
        }
        
        return {
            "success": True,
            "data": health_status
        }
    except Exception as e:
        logger.error(f"IBKR健康检查失败: {e}")
        return {
            "success": False,
            "error": str(e),
            "data": {
                "service": "ibkr",
                "status": "unhealthy",
                "timestamp": datetime.now().isoformat()
            }
        }


# 安全相关的管理端点（仅用于调试和监控）
@router.get("/debug/recent-requests")
async def get_recent_requests(
    request: Request,
    limit: int = Query(20, ge=1, le=50, description="返回记录数量")
):
    """获取最近的请求记录（仅用于调试）"""
    try:
        # 验证API密钥（可选，用于调试）
        x_api_key = request.headers.get("X-API-Key")
        if x_api_key and not _validate_api_key(x_api_key):
            raise HTTPException(status_code=401, detail="Invalid API key")
        
        # 获取最近的同步日志
        logs = await ibkr_service.get_sync_logs(limit=limit)
        
        # 过滤敏感信息
        filtered_logs = []
        for log in logs:
            filtered_log = {
                "id": log["id"],
                "account_id": log["account_id"],
                "status": log["status"],
                "records_processed": log["records_processed"],
                "records_inserted": log["records_inserted"],
                "source_ip": log["source_ip"],
                "sync_duration_ms": log["sync_duration_ms"],
                "created_at": log["created_at"],
                "has_error": bool(log["error_message"])
            }
            filtered_logs.append(filtered_log)
        
        return {
            "success": True,
            "data": filtered_logs,
            "count": len(filtered_logs)
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取最近请求记录失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取请求记录失败: {str(e)}")


@router.get("/audit-logs")
async def get_audit_logs(
    table_name: Optional[str] = Query(None, description="表名过滤"),
    operation: Optional[str] = Query(None, description="操作类型过滤: INSERT, UPDATE, DELETE"),
    limit: int = Query(50, ge=1, le=100, description="返回记录数量限制"),
    offset: int = Query(0, ge=0, description="偏移量")
):
    """获取IBKR相关表的审计日志"""
    try:
        # 检查audit_log表是否存在
        with engine.connect() as conn:
            # 检查表是否存在
            result = conn.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = 'audit_log'
                )
            """))
            table_exists = result.scalar()
            
            if not table_exists:
                return {
                    "success": True,
                    "data": [],
                    "count": 0,
                    "message": "audit_log表不存在"
                }
            
            # 构建查询
            query = """
                SELECT 
                    id,
                    table_name,
                    operation,
                    old_data,
                    new_data,
                    source_ip,
                    user_agent,
                    api_key,
                    request_id,
                    session_id,
                    changed_at
                FROM audit_log
                WHERE 1=1
            """
            params = {}
            
            if table_name:
                query += " AND table_name = :table_name"
                params['table_name'] = table_name
            
            if operation:
                query += " AND operation = :operation"
                params['operation'] = operation
            
            # 只查询IBKR相关表
            query += " AND table_name IN ('ibkr_accounts', 'ibkr_balances', 'ibkr_positions', 'ibkr_sync_logs')"
            
            # 添加排序和分页
            query += " ORDER BY changed_at DESC LIMIT :limit OFFSET :offset"
            params['limit'] = limit
            params['offset'] = offset
            
            # 执行查询
            result = conn.execute(text(query), params)
            rows = result.fetchall()
            
            # 格式化结果
            audit_logs = []
            for row in rows:
                audit_log = {
                    "id": row[0],
                    "table_name": row[1],
                    "operation": row[2],
                    "old_data": row[3],
                    "new_data": row[4],
                    "source_ip": str(row[5]) if row[5] else None,
                    "user_agent": row[6],
                    "api_key": row[7],
                    "request_id": row[8],
                    "session_id": row[9],
                    "changed_at": row[10].isoformat() if row[10] else None
                }
                audit_logs.append(audit_log)
            
            return {
                "success": True,
                "data": audit_logs,
                "count": len(audit_logs),
                "total_count": len(audit_logs)  # 简化，实际应该查询总数
            }
            
    except Exception as e:
        logger.error(f"获取审计日志失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取审计日志失败: {str(e)}")