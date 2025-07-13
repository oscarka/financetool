"""
调度器配置示例
"""

# 基金净值更新任务配置示例
FUND_NAV_UPDATE_CONFIG = {
    "job_id": "fund_nav_daily_update",
    "name": "每日基金净值更新",
    "task_id": "fund_nav_update",
    "schedule": {
        "type": "cron",
        "hour": 15,
        "minute": 30,
        "second": 0
    },
    "config": {
        "update_all": True,
        "data_source": "tiantian",
        "retry_times": 3
    }
}

# Wise余额同步任务配置示例
WISE_BALANCE_SYNC_CONFIG = {
    "job_id": "wise_balance_daily_sync",
    "name": "每日Wise余额同步",
    "task_id": "wise_balance_sync",
    "schedule": {
        "type": "cron",
        "hour": 16,
        "minute": 30,
        "second": 0
    },
    "config": {
        "sync_all_accounts": True,
        "currencies": ["USD", "AUD", "CNY", "HKD", "JPY"]
    }
}

# OKX余额同步任务配置示例
OKX_BALANCE_SYNC_CONFIG = {
    "job_id": "okx_balance_hourly_sync",
    "name": "每小时OKX余额同步",
    "task_id": "okx_balance_sync",
    "schedule": {
        "type": "interval",
        "hours": 1
    },
    "config": {
        "sync_positions": True,
        "inst_types": ["SPOT", "MARGIN"]
    }
}

# IBKR余额同步任务配置示例
IBKR_BALANCE_SYNC_CONFIG = {
    "job_id": "ibkr_balance_daily_sync",
    "name": "每日IBKR余额同步",
    "task_id": "ibkr_balance_sync",
    "schedule": {
        "type": "cron",
        "hour": 17,
        "minute": 0,
        "second": 0
    },
    "config": {
        "sync_positions": True
    }
}

# 数据清理任务配置示例
DATA_CLEANUP_CONFIG = {
    "job_id": "data_cleanup_weekly",
    "name": "每周数据清理",
    "task_id": "data_cleanup",
    "schedule": {
        "type": "cron",
        "day_of_week": "sun",
        "hour": 2,
        "minute": 0,
        "second": 0
    },
    "config": {
        "cleanup_days": 90,
        "cleanup_types": ["logs", "temp_data"]
    }
}

# 报表生成任务配置示例
REPORT_GENERATION_CONFIG = {
    "job_id": "report_generation_monthly",
    "name": "每月报表生成",
    "task_id": "report_generation",
    "schedule": {
        "type": "cron",
        "day": 1,
        "hour": 6,
        "minute": 0,
        "second": 0
    },
    "config": {
        "report_type": "monthly_summary",
        "include_charts": True,
        "export_format": "pdf"
    }
}

# 一次性任务配置示例
ONE_TIME_TASK_CONFIG = {
    "job_id": "one_time_backup",
    "name": "一次性数据备份",
    "task_id": "data_backup",
    "schedule": {
        "type": "date",
        "run_date": "2024-12-31 23:59:59"
    },
    "config": {
        "backup_type": "full",
        "compression": True
    }
}

# 所有默认任务配置
DEFAULT_JOBS = [
    FUND_NAV_UPDATE_CONFIG,
    WISE_BALANCE_SYNC_CONFIG,
    OKX_BALANCE_SYNC_CONFIG,
    IBKR_BALANCE_SYNC_CONFIG,
    DATA_CLEANUP_CONFIG,
    REPORT_GENERATION_CONFIG
]

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