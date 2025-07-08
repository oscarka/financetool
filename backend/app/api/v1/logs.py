from fastapi import APIRouter, Query, HTTPException, Depends
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from pydantic import BaseModel
import json
import os
from pathlib import Path
from app.utils.logger import LogCategory

router = APIRouter()

class LogEntry(BaseModel):
    """日志条目模型"""
    timestamp: str
    level: str
    category: str
    module: str
    function: str
    line: int
    message: str
    request_id: Optional[str] = None
    user_id: Optional[str] = None
    extra_data: Optional[Dict[str, Any]] = None
    exception: Optional[str] = None

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
    recent_errors: List[LogEntry]

def parse_log_line(line: str) -> Optional[LogEntry]:
    """解析日志行"""
    try:
        # 尝试解析JSON格式的日志
        log_data = json.loads(line.strip())
        return LogEntry(**log_data)
    except (json.JSONDecodeError, ValueError, TypeError):
        # 如果不是JSON格式，尝试解析普通格式
        try:
            # 简单的格式解析 (这里可以根据实际格式调整)
            if " [" in line and "] " in line:
                parts = line.strip().split(" ", 3)
                if len(parts) >= 4:
                    timestamp = f"{parts[0]} {parts[1]}"
                    level = parts[2].strip("[]")
                    category = parts[3].split("]")[0].strip("[")
                    message = parts[3].split("]", 1)[1].strip() if "]" in parts[3] else parts[3]
                    
                    return LogEntry(
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
    # 添加分类日志文件
    for category in LogCategory:
        log_file = log_dir / f"{category.value}.log"
        if log_file.exists():
            log_files.append(log_file)
    
    # 添加主日志文件
    main_log = log_dir / "app.log"
    if main_log.exists():
        log_files.append(main_log)
    
    return log_files

def read_logs_from_files(
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    level: Optional[str] = None,
    category: Optional[str] = None,
    search: Optional[str] = None,
    limit: int = 100
) -> List[LogEntry]:
    """从日志文件读取日志"""
    logs = []
    log_files = get_log_files()
    
    for log_file in log_files:
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                for line in f:
                    log_entry = parse_log_line(line)
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

@router.get("/logs", response_model=List[LogEntry])
async def get_logs(
    start_time: Optional[datetime] = Query(None, description="开始时间"),
    end_time: Optional[datetime] = Query(None, description="结束时间"),
    level: Optional[str] = Query(None, description="日志级别 (DEBUG, INFO, WARNING, ERROR, CRITICAL)"),
    category: Optional[str] = Query(None, description="日志分类"),
    search: Optional[str] = Query(None, description="搜索关键词"),
    limit: int = Query(100, ge=1, le=1000, description="返回数量限制")
):
    """获取日志列表"""
    try:
        logs = read_logs_from_files(
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

@router.get("/logs/stats", response_model=LogStats)
async def get_log_stats():
    """获取日志统计信息"""
    try:
        # 获取最近的日志
        recent_logs = read_logs_from_files(limit=1000)
        
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

@router.get("/logs/categories")
async def get_log_categories():
    """获取所有日志分类"""
    return {
        "categories": [category.value for category in LogCategory],
        "levels": ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
    }

@router.get("/logs/recent/{category}")
async def get_recent_logs_by_category(
    category: str,
    limit: int = Query(50, ge=1, le=500, description="返回数量限制")
):
    """获取指定分类的最近日志"""
    try:
        # 验证分类是否有效
        if category not in [cat.value for cat in LogCategory]:
            raise HTTPException(status_code=400, detail=f"无效的日志分类: {category}")
        
        logs = read_logs_from_files(category=category, limit=limit)
        return logs
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取分类日志失败: {str(e)}")

@router.delete("/logs/cleanup")
async def cleanup_old_logs(
    days: int = Query(7, ge=1, le=30, description="保留天数")
):
    """清理旧日志文件"""
    try:
        log_dir = Path("./logs")
        if not log_dir.exists():
            return {"message": "日志目录不存在"}
        
        cutoff_time = datetime.now() - timedelta(days=days)
        deleted_files = []
        
        for log_file in log_dir.glob("*.log"):
            try:
                file_mtime = datetime.fromtimestamp(log_file.stat().st_mtime)
                if file_mtime < cutoff_time:
                    log_file.unlink()
                    deleted_files.append(str(log_file))
            except Exception as e:
                print(f"Error deleting {log_file}: {e}")
        
        return {
            "message": f"已删除 {len(deleted_files)} 个日志文件",
            "deleted_files": deleted_files
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"清理日志失败: {str(e)}")