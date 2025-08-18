#!/usr/bin/env python3
"""
测试MCP服务器连接的脚本
"""

import asyncio
import aiohttp
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_mcp_server():
    """测试MCP服务器连接"""
    mcp_url = "http://localhost:3001"
    
    try:
        # 测试1: 基本连接
        logger.info("测试1: 检查MCP服务器是否响应...")
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(f"{mcp_url}/health", timeout=5) as response:
                    logger.info(f"健康检查响应: {response.status}")
                    if response.status == 200:
                        data = await response.json()
                        logger.info(f"健康检查数据: {data}")
                    else:
                        logger.error(f"健康检查失败: {response.status}")
            except asyncio.TimeoutError:
                logger.error("健康检查超时")
            except Exception as e:
                logger.error(f"健康检查异常: {e}")
        
        # 测试2: 尝试执行SQL查询
        logger.info("测试2: 尝试执行SQL查询...")
        sql_query = "SELECT COUNT(*) as count FROM asset_snapshot"
        
        try:
            async with session.post(
                f"{mcp_url}/query",
                json={
                    "method": "execute_sql",
                    "params": {
                        "sql": sql_query,
                        "max_rows": 10
                    }
                },
                timeout=10
            ) as response:
                logger.info(f"SQL查询响应: {response.status}")
                if response.status == 200:
                    data = await response.json()
                    logger.info(f"SQL查询结果: {data}")
                else:
                    error_text = await response.text()
                    logger.error(f"SQL查询失败: {response.status}, {error_text}")
        except asyncio.TimeoutError:
            logger.error("SQL查询超时")
        except Exception as e:
            logger.error(f"SQL查询异常: {e}")
            
    except Exception as e:
        logger.error(f"测试过程中发生异常: {e}")

if __name__ == "__main__":
    asyncio.run(test_mcp_server())
