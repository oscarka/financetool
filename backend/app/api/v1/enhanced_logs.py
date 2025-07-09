from fastapi import APIRouter, Query, HTTPException, Depends
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from pydantic import BaseModel
import json
import os
from pathlib import Path
from app.utils.enhanced_logger import LogCategory
import traceback

router = APIRouter()

class DetailedLogEntry(BaseModel):
    """详细日志条目模型"""
    timestamp: str
    level: str
    category: str
    module: str
    function: str
    line: int
    message: str
    request_id: Optional[str] = None
    user_id: Optional[str] = None
    details: Optional[Dict[str, Any]] = None
    exception: Optional[Dict[str, Any]] = None

class LogQuery(BaseModel):
    """日志查询参数"""
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    level: Optional[str] = None
    category: Optional[str] = None
    search: Optional[str] = None
    limit: int = 100

class LogStats(BaseModel):
    """日志统计信息"""
    total_logs: int
    level_counts: Dict[str, int]
    category_counts: Dict[str, int]
    recent_errors: List[DetailedLogEntry]

def parse_detailed_log_line(line: str) -> Optional[DetailedLogEntry]:
    """解析详细日志行"""
    try:
        # 尝试解析JSON格式的日志
        log_data = json.loads(line.strip())
        
        # 确保必要字段存在
        if not all(key in log_data for key in ['timestamp', 'level', 'category', 'message']):
            return None
            
        # 处理details字段
        details = log_data.get('details', {})
        if isinstance(details, dict):
            # 如果details是字典，直接使用
            pass
        else:
            # 如果details不是字典，尝试从extra_data获取
            details = log_data.get('extra_data', {})
        
        # 处理exception字段
        exception = log_data.get('exception')
        if isinstance(exception, str):
            # 如果是字符串，转换为字典格式
            exception = {
                'message': exception,
                'type': 'Exception'
            }
        
        return DetailedLogEntry(
            timestamp=log_data['timestamp'],
            level=log_data['level'],
            category=log_data['category'],
            module=log_data.get('module', 'unknown'),
            function=log_data.get('function', 'unknown'),
            line=log_data.get('line', 0),
            message=log_data['message'],
            request_id=log_data.get('request_id'),
            user_id=log_data.get('user_id'),
            details=details,
            exception=exception
        )
    except (json.JSONDecodeError, ValueError, TypeError) as e:
        # 如果不是JSON格式，尝试解析普通格式
        try:
            if " [" in line and "] " in line:
                parts = line.strip().split(" ", 3)
                if len(parts) >= 4:
                    timestamp = f"{parts[0]} {parts[1]}"
                    level = parts[2].strip("[]")
                    category = parts[3].split("]")[0].strip("[")
                    message = parts[3].split("]", 1)[1].strip() if "]" in parts[3] else parts[3]
                    
                    return DetailedLogEntry(
                        timestamp=timestamp,
                        level=level,
                        category=category,
                        module="unknown",
                        function="unknown",
                        line=0,
                        message=message
                    )
        except Exception:
            pass
    return None

def get_log_files() -> List[Path]:
    """获取所有日志文件"""
    log_dir = Path("./logs")
    if not log_dir.exists():
        return []
    
    log_files = []
    
    # 查找所有.log文件
    for log_file in log_dir.glob("*.log"):
        log_files.append(log_file)
    
    return log_files

def read_detailed_logs_from_files(
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    level: Optional[str] = None,
    category: Optional[str] = None,
    search: Optional[str] = None,
    limit: int = 100
) -> List[DetailedLogEntry]:
    """从日志文件读取详细日志"""
    logs = []
    log_files = get_log_files()
    
    for log_file in log_files:
        # 从文件名提取分类信息
        file_category = None
        if log_file.name.startswith("LogCategory."):
            # 处理 LogCategory.API.log 格式
            file_category = log_file.name.replace("LogCategory.", "").replace(".log", "").lower()
        else:
            # 处理 api.log 格式
            file_category = log_file.name.replace(".log", "").lower()
        
        # 如果指定了分类过滤，只处理对应分类的文件
        if category and file_category != category.lower():
            continue
            
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                for line in f:
                    log_entry = parse_detailed_log_line(line)
                    if not log_entry:
                        continue
                    
                    # 应用过滤条件
                    if level and log_entry.level.upper() != level.upper():
                        continue
                    
                    if category and log_entry.category != category:
                        continue
                    
                    if search and search.lower() not in log_entry.message.lower():
                        continue
                    
                    # 时间过滤
                    if start_time or end_time:
                        try:
                            log_time = datetime.fromisoformat(log_entry.timestamp.replace('Z', '+00:00'))
                            if start_time and log_time < start_time:
                                continue
                            if end_time and log_time > end_time:
                                continue
                        except ValueError:
                            continue
                    
                    logs.append(log_entry)
                    
                    if len(logs) >= limit:
                        break
                        
        except Exception as e:
            # 如果读取文件失败，记录错误但继续处理其他文件
            print(f"Error reading log file {log_file}: {e}")
            continue
    
    # 按时间戳排序（最新的在前）
    logs.sort(key=lambda x: x.timestamp, reverse=True)
    return logs[:limit]

@router.get("/logs/detailed", response_model=List[DetailedLogEntry])
async def get_detailed_logs(
    start_time: Optional[datetime] = Query(None, description="开始时间"),
    end_time: Optional[datetime] = Query(None, description="结束时间"),
    level: Optional[str] = Query(None, description="日志级别 (DEBUG, INFO, WARNING, ERROR, CRITICAL)"),
    category: Optional[str] = Query(None, description="日志分类"),
    search: Optional[str] = Query(None, description="搜索关键词"),
    limit: int = Query(100, ge=1, le=1000, description="返回数量限制")
):
    """获取详细日志列表"""
    try:
        logs = read_detailed_logs_from_files(
            start_time=start_time,
            end_time=end_time,
            level=level,
            category=category,
            search=search,
            limit=limit
        )
        return logs
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取日志失败: {str(e)}")

@router.get("/logs/detailed/stats", response_model=LogStats)
async def get_detailed_log_stats():
    """获取详细日志统计信息"""
    try:
        # 获取最近的日志
        recent_logs = read_detailed_logs_from_files(limit=1000)
        
        # 统计信息
        total_logs = len(recent_logs)
        level_counts = {}
        category_counts = {}
        recent_errors = []
        
        for log in recent_logs:
            # 统计级别
            level_counts[log.level] = level_counts.get(log.level, 0) + 1
            
            # 统计分类
            category_counts[log.category] = category_counts.get(log.category, 0) + 1
            
            # 收集最近的错误
            if log.level in ['ERROR', 'CRITICAL'] and len(recent_errors) < 10:
                recent_errors.append(log)
        
        return LogStats(
            total_logs=total_logs,
            level_counts=level_counts,
            category_counts=category_counts,
            recent_errors=recent_errors
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取日志统计失败: {str(e)}")

@router.get("/logs/detailed/categories")
async def get_detailed_log_categories():
    """获取所有日志分类"""
    return {
        "categories": [category.value for category in LogCategory],
        "category_descriptions": {
            "api": "API请求相关",
            "database": "数据库操作",
            "scheduler": "定时任务",
            "business": "业务逻辑",
            "error": "错误日志",
            "system": "系统运行",
            "security": "安全相关",
            "fund_api": "基金API调用",
            "okx_api": "OKX加密货币API",
            "wise_api": "Wise金融API",
            "paypal_api": "PayPal支付API",
            "exchange_api": "汇率API",
            "external_other": "其他外部API"
        }
    }

@router.get("/logs/detailed/recent/{category}")
async def get_recent_detailed_logs_by_category(
    category: str,
    limit: int = Query(50, ge=1, le=500, description="返回数量限制")
):
    """获取指定分类的最近详细日志"""
    try:
        logs = read_detailed_logs_from_files(category=category, limit=limit)
        return logs
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取分类日志失败: {str(e)}")

@router.post("/logs/detailed/test")
async def test_detailed_logging():
    """测试详细日志记录"""
    from app.utils.enhanced_logger import (
        log_api_detailed, log_database_detailed, log_business_detailed,
        log_fund_api_detailed, log_error_detailed, log_fund_operation,
        log_database_operation, log_api_request
    )
    
    try:
        # 测试各种类型的详细日志
        log_api_detailed("测试API日志", extra_data={
            "test_param": "test_value",
            "user_agent": "test-browser",
            "ip_address": "127.0.0.1"
        })
        
        log_database_detailed("测试数据库日志", extra_data={
            "table": "users",
            "operation": "SELECT",
            "query": "SELECT * FROM users WHERE id = 1",
            "execution_time": 0.15
        })
        
        log_business_detailed("测试业务日志", extra_data={
            "user_id": 123,
            "action": "login",
            "result": "success"
        })
        
        log_fund_api_detailed("测试基金API日志", extra_data={
            "endpoint": "/api/fund/nav",
            "fund_code": "000001",
            "response_time": 0.5,
            "status_code": 200
        })
        
        log_fund_operation(
            operation_type="buy",
            fund_code="000001",
            amount=1000.0,
            quantity=100.0,
            price=10.0,
            platform="蚂蚁财富",
            user_id=123
        )
        
        log_database_operation(
            operation="INSERT",
            table="fund_operations",
            record_id=456,
            data={"fund_code": "000001", "amount": 1000.0},
            execution_time=0.02
        )
        
        log_api_request(
            method="POST",
            path="/api/funds/operations",
            params={"fund_code": "000001"},
            response_status=200,
            execution_time=0.15
        )
        
        # 测试错误日志
        try:
            raise ValueError("这是一个测试错误")
        except Exception as e:
            log_error_detailed("测试错误日志", extra_data={
                "error_type": "ValueError",
                "error_message": str(e),
                "stack_trace": traceback.format_exc()
            })
        
        return {"success": True, "message": "详细日志测试完成"}
    except Exception as e:
        log_error_detailed("测试日志记录失败", extra_data={"error": str(e)})
        raise HTTPException(status_code=500, detail=f"测试日志记录失败: {str(e)}")

@router.get("/logs/detailed/debug")
async def debug_detailed_logs():
    """调试详细日志文件"""
    try:
        log_dir = Path("./logs")
        if not log_dir.exists():
            return {"error": "日志目录不存在"}
        
        log_files = list(log_dir.glob("*.log"))
        file_info = []
        
        for log_file in log_files:
            try:
                file_size = log_file.stat().st_size
                with open(log_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    last_line = lines[-1] if lines else ""
                    
                file_info.append({
                    "filename": log_file.name,
                    "size_bytes": file_size,
                    "size_mb": round(file_size / 1024 / 1024, 2),
                    "line_count": len(lines),
                    "last_line": last_line[:200] + "..." if len(last_line) > 200 else last_line
                })
            except Exception as e:
                file_info.append({
                    "filename": log_file.name,
                    "error": str(e)
                })
        
        return {
            "log_directory": str(log_dir.absolute()),
            "files": file_info,
            "total_files": len(log_files)
        }
    except Exception as e:
        return {"error": f"调试日志失败: {str(e)}"}