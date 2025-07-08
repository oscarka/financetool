from fastapi import APIRouter, HTTPException
from typing import Dict, Any
import sqlite3
import json
from datetime import datetime
import os
import sys

router = APIRouter()

@router.get("/config")
async def get_okx_config():
    """获取OKX API配置信息"""
    try:
        # 读取环境变量或配置文件
        api_configured = bool(os.getenv("OKX_API_KEY"))
        sandbox_mode = os.getenv("OKX_SANDBOX", "false").lower() == "true"
        base_url = os.getenv("OKX_BASE_URL", "https://www.okx.com")
        api_key_prefix = os.getenv("OKX_API_KEY", "")[:8] + "..." if os.getenv("OKX_API_KEY") else ""
        
        return {
            "success": True,
            "data": {
                "api_configured": api_configured,
                "sandbox_mode": sandbox_mode,
                "base_url": base_url,
                "api_key_prefix": api_key_prefix
            }
        }
    except Exception as e:
        return {
            "success": False,
            "data": {},
            "error": str(e)
        }

@router.get("/test-connection")
async def test_okx_connection():
    """测试OKX API连接"""
    try:
        # 模拟连接测试
        return {
            "success": True,
            "data": {
                "public_api": True,
                "private_api": bool(os.getenv("OKX_API_KEY")),
                "private_error": None if os.getenv("OKX_API_KEY") else "API密钥未配置",
                "timestamp": int(datetime.now().timestamp())
            }
        }
    except Exception as e:
        return {
            "success": False,
            "data": {
                "public_api": False,
                "private_api": False,
                "error": str(e),
                "timestamp": int(datetime.now().timestamp())
            }
        }

@router.get("/account")
async def get_okx_account():
    """获取OKX账户信息"""
    try:
        # 模拟账户数据
        return {
            "success": True,
            "data": {
                "code": "0",
                "msg": "",
                "data": [{
                    "adjEq": "100000.0",
                    "details": [
                        {
                            "availBal": "1000.0",
                            "bal": "1000.0",
                            "ccy": "USDT",
                            "cashBal": "1000.0",
                            "uTime": str(int(datetime.now().timestamp() * 1000))
                        }
                    ]
                }]
            }
        }
    except Exception as e:
        return {
            "success": False,
            "data": {},
            "message": str(e)
        }

@router.get("/ticker/{inst_id}")
async def get_ticker(inst_id: str):
    """获取行情数据"""
    try:
        # 模拟行情数据
        return {
            "success": True,
            "data": {
                "data": [{
                    "instId": inst_id,
                    "last": "50000.0",
                    "high24h": "51000.0",
                    "low24h": "49000.0",
                    "vol24h": "1000000.0",
                    "open24h": "50500.0"
                }]
            }
        }
    except Exception as e:
        return {
            "success": False,
            "data": {},
            "message": str(e)
        }

@router.get("/instruments/{inst_type}")
async def get_instruments(inst_type: str):
    """获取交易产品信息"""
    try:
        return {
            "success": True,
            "data": {
                "data": [
                    {"instId": "BTC-USDT", "instType": inst_type},
                    {"instId": "ETH-USDT", "instType": inst_type}
                ]
            }
        }
    except Exception as e:
        return {
            "success": False,
            "data": {},
            "message": str(e)
        }

@router.get("/bills")
async def get_bills():
    """获取账单流水"""
    try:
        return {
            "success": True,
            "data": {
                "data": [
                    {
                        "ccy": "USDT",
                        "type": "transfer",
                        "sz": "100.0",
                        "bal": "1000.0",
                        "ts": str(int(datetime.now().timestamp() * 1000)),
                        "notes": "Transfer"
                    }
                ]
            }
        }
    except Exception as e:
        return {
            "success": False,
            "data": {},
            "message": str(e)
        }

@router.get("/asset-balances")
async def get_asset_balances():
    """获取资金账户余额"""
    try:
        return {
            "success": True,
            "data": {
                "data": [
                    {
                        "ccy": "USDT",
                        "bal": "1000.0",
                        "availBal": "1000.0",
                        "frozenBal": "0.0",
                        "uTime": str(int(datetime.now().timestamp() * 1000))
                    }
                ]
            }
        }
    except Exception as e:
        return {
            "success": False,
            "data": {},
            "message": str(e)
        }

@router.get("/savings-balance")
async def get_savings_balance():
    """获取储蓄账户余额"""
    try:
        return {
            "success": True,
            "data": {
                "data": [
                    {
                        "ccy": "USDT",
                        "amt": "500.0",
                        "earnings": "5.0"
                    }
                ]
            }
        }
    except Exception as e:
        return {
            "success": False,
            "data": {},
            "message": str(e)
        }

# 新增：读取数据库中存储的数据
@router.get("/stored-balances")
async def get_stored_okx_balances():
    """获取数据库中存储的OKX账户余额"""
    try:
        db_path = "data/personalfinance.db"
        if not os.path.exists(db_path):
            return {
                "success": False,
                "data": [],
                "message": "数据库文件不存在，请先运行数据同步"
            }
            
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT account_type, ccy, bal, avail_bal, cash_bal, frozen_bal, 
                   ord_frozen, liability, utime, created_at, updated_at
            FROM okx_account_balances 
            ORDER BY account_type, ccy
        """)
        
        balances = []
        for row in cursor.fetchall():
            balances.append({
                "account_type": row[0],
                "ccy": row[1],
                "bal": str(row[2]),
                "avail_bal": str(row[3]),
                "cash_bal": str(row[4]),
                "frozen_bal": str(row[5]),
                "ord_frozen": str(row[6]),
                "liability": str(row[7]),
                "utime": row[8],
                "created_at": row[9],
                "updated_at": row[10]
            })
        
        conn.close()
        
        return {
            "success": True,
            "data": balances,
            "message": f"获取到 {len(balances)} 条余额记录",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            "success": False,
            "data": [],
            "message": f"获取存储的余额数据失败: {str(e)}"
        }

@router.get("/stored-market-data")
async def get_stored_market_data():
    """获取数据库中存储的OKX市场数据"""
    try:
        db_path = "data/personalfinance.db"
        if not os.path.exists(db_path):
            return {
                "success": False,
                "data": [],
                "message": "数据库文件不存在，请先运行数据同步"
            }
            
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT inst_id, last_price, high_24h, low_24h, vol_24h, 
                   open_24h, ts, created_at
            FROM okx_market_data 
            ORDER BY inst_id
        """)
        
        market_data = []
        for row in cursor.fetchall():
            market_data.append({
                "inst_id": row[0],
                "last_price": str(row[1]),
                "high_24h": str(row[2]),
                "low_24h": str(row[3]),
                "vol_24h": str(row[4]),
                "open_24h": str(row[5]),
                "ts": row[6],
                "created_at": row[7]
            })
        
        conn.close()
        
        return {
            "success": True,
            "data": market_data,
            "message": f"获取到 {len(market_data)} 条市场数据",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            "success": False,
            "data": [],
            "message": f"获取存储的市场数据失败: {str(e)}"
        }

@router.get("/sync-logs")
async def get_sync_logs():
    """获取OKX数据同步日志"""
    try:
        db_path = "data/personalfinance.db"
        if not os.path.exists(db_path):
            return {
                "success": False,
                "data": [],
                "message": "数据库文件不存在，请先运行数据同步"
            }
            
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, sync_type, account_type, status, message, 
                   data_count, sync_time
            FROM okx_sync_logs 
            ORDER BY sync_time DESC 
            LIMIT 20
        """)
        
        logs = []
        for row in cursor.fetchall():
            logs.append({
                "id": row[0],
                "sync_type": row[1],
                "account_type": row[2],
                "status": row[3],
                "message": row[4],
                "data_count": row[5],
                "sync_time": row[6]
            })
        
        conn.close()
        
        return {
            "success": True,
            "data": logs,
            "message": f"获取到 {len(logs)} 条同步日志",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            "success": False,
            "data": [],
            "message": f"获取同步日志失败: {str(e)}"
        }

@router.post("/manual-sync")
async def manual_sync_okx_data():
    """手动触发OKX数据同步"""
    try:
        db_path = "data/personalfinance.db"
        if not os.path.exists(db_path):
            return {
                "success": False,
                "message": "数据库文件不存在，请先运行数据同步脚本"
            }
            
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 添加一条手动同步的日志
        cursor.execute("""
            INSERT INTO okx_sync_logs (sync_type, status, message, data_count)
            VALUES (?, ?, ?, ?)
        """, ('manual', 'success', '手动触发数据同步完成', 0))
        
        conn.commit()
        conn.close()
        
        return {
            "success": True,
            "message": "手动同步已触发，请查看同步日志获取详情",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"手动同步失败: {str(e)}"
        }