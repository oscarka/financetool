"""
调度器配置示例 - 更新版本
"""

# ==================== 高频任务（每小时/每4小时） ====================

# OKX市场数据同步 - 每小时
OKX_MARKET_DATA_CONFIG = {
    "job_id": "okx_market_data_hourly",
    "name": "OKX市场数据同步",
    "task_id": "okx_market_data_sync",
    "schedule": {
        "type": "interval",
        "hours": 1
    },
    "config": {
        "symbols": ["BTC-USDT", "ETH-USDT", "SOL-USDT"],
        "update_prices": True
    }
}

# OKX余额同步 - 每4小时
OKX_BALANCE_CONFIG = {
    "job_id": "okx_balance_4hourly",
    "name": "OKX余额同步",
    "task_id": "okx_balance_sync",
    "schedule": {
        "type": "interval",
        "hours": 4
    },
    "config": {
        "sync_positions": True,
        "inst_types": ["SPOT", "MARGIN"]
    }
}

# ==================== 日常任务（每日） ====================

# 基金净值更新 - 每日15:30（基金收盘后）
FUND_NAV_CONFIG = {
    "job_id": "fund_nav_daily",
    "name": "基金净值更新",
    "task_id": "fund_nav_update",
    "schedule": {
        "type": "cron",
        "hour": 15,
        "minute": 30
    },
    "config": {
        "update_all": True,
        "data_source": "tiantian",
        "retry_times": 3
    }
}

# Wise余额同步 - 每日16:00
WISE_BALANCE_CONFIG = {
    "job_id": "wise_balance_daily",
    "name": "Wise余额同步",
    "task_id": "wise_balance_sync",
    "schedule": {
        "type": "cron",
        "hour": 16,
        "minute": 0
    },
    "config": {
        "sync_all_accounts": True,
        "currencies": ["USD", "AUD", "CNY", "HKD", "JPY"]
    }
}

# IBKR余额同步 - 每日17:00（美股开盘前）
IBKR_BALANCE_CONFIG = {
    "job_id": "ibkr_balance_daily",
    "name": "IBKR余额同步",
    "task_id": "ibkr_balance_sync",
    "schedule": {
        "type": "cron",
        "hour": 17,
        "minute": 0
    },
    "config": {
        "sync_positions": True
    }
}

# 定投计划执行 - 每日09:00
DCA_EXECUTE_CONFIG = {
    "job_id": "dca_execute_daily",
    "name": "定投计划执行",
    "task_id": "dca_execute",
    "schedule": {
        "type": "cron",
        "hour": 9,
        "minute": 0
    },
    "config": {
        "execute_all_plans": True,
        "check_exclude_dates": True
    }
}

# Wise交易同步 - 每日18:00
WISE_TRANSACTION_CONFIG = {
    "job_id": "wise_transaction_daily",
    "name": "Wise交易同步",
    "task_id": "wise_transaction_sync",
    "schedule": {
        "type": "cron",
        "hour": 18,
        "minute": 0
    },
    "config": {
        "sync_days": 7,
        "include_pending": True
    }
}

# 基金持仓同步 - 每日16:30
FUND_POSITION_CONFIG = {
    "job_id": "fund_position_daily",
    "name": "基金持仓同步",
    "task_id": "fund_position_sync",
    "schedule": {
        "type": "cron",
        "hour": 16,
        "minute": 30
    },
    "config": {
        "sync_all_funds": True
    }
}

# ==================== 周期性任务（每周/每月） ====================

# 数据清理 - 每周日凌晨2:00
DATA_CLEANUP_CONFIG = {
    "job_id": "data_cleanup_weekly",
    "name": "数据清理",
    "task_id": "data_cleanup",
    "schedule": {
        "type": "cron",
        "day_of_week": "sun",
        "hour": 2,
        "minute": 0
    },
    "config": {
        "cleanup_days": 90,
        "cleanup_types": ["logs", "temp_data", "old_snapshots"]
    }
}

# 数据备份 - 每周六凌晨3:00
DATA_BACKUP_CONFIG = {
    "job_id": "data_backup_weekly",
    "name": "数据备份",
    "task_id": "data_backup",
    "schedule": {
        "type": "cron",
        "day_of_week": "sat",
        "hour": 3,
        "minute": 0
    },
    "config": {
        "backup_type": "full",
        "compression": True,
        "include_logs": True
    }
}

# 月度报表生成 - 每月1日早上6:00
REPORT_CONFIG = {
    "job_id": "report_generation_monthly",
    "name": "月度报表生成",
    "task_id": "report_generation",
    "schedule": {
        "type": "cron",
        "day": 1,
        "hour": 6,
        "minute": 0
    },
    "config": {
        "report_type": "monthly_summary",
        "include_charts": True,
        "export_format": "pdf"
    }
}

# ==================== 推荐配置组合 ====================

# 核心任务配置（建议优先启用）
CORE_JOBS = [
    FUND_NAV_CONFIG,        # 基金净值更新
    WISE_BALANCE_CONFIG,    # Wise余额同步
    IBKR_BALANCE_CONFIG,    # IBKR余额同步
    DCA_EXECUTE_CONFIG,     # 定投计划执行
]

# 扩展任务配置（根据需要启用）
EXTENDED_JOBS = [
    OKX_BALANCE_CONFIG,     # OKX余额同步
    WISE_TRANSACTION_CONFIG, # Wise交易同步
    FUND_POSITION_CONFIG,   # 基金持仓同步
]

# 维护任务配置（建议启用）
MAINTENANCE_JOBS = [
    DATA_CLEANUP_CONFIG,    # 数据清理
    DATA_BACKUP_CONFIG,     # 数据备份
    REPORT_CONFIG,          # 报表生成
]

# 所有默认任务配置
DEFAULT_JOBS = CORE_JOBS + EXTENDED_JOBS + MAINTENANCE_JOBS

# 调度器配置示例
SCHEDULER_CONFIG = {
    "timezone": "Asia/Shanghai",
    "job_defaults": {
        "coalesce": True,
        "max_instances": 1,
        "misfire_grace_time": 300
    },
    "default_jobs": DEFAULT_JOBS
}

# ==================== 使用说明 ====================
"""
调度任务配置说明：

1. 高频任务（每小时/每4小时）：
   - OKX市场数据：实时价格更新
   - OKX余额：账户余额监控

2. 日常任务（每日）：
   - 基金净值：15:30更新（基金收盘后）
   - Wise余额：16:00同步
   - IBKR余额：17:00同步（美股开盘前）
   - 定投执行：09:00检查并执行
   - 交易同步：18:00同步交易记录
   - 持仓同步：16:30同步持仓数据

3. 维护任务（每周/每月）：
   - 数据清理：周日凌晨2:00
   - 数据备份：周六凌晨3:00
   - 报表生成：每月1日早上6:00

配置建议：
1. 先启用核心任务（CORE_JOBS）
2. 根据业务需要添加扩展任务
3. 确保维护任务正常运行
4. 监控任务执行日志，及时调整配置
""" 