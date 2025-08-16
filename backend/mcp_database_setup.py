#!/usr/bin/env python3
"""
MCP数据库服务器设置和测试脚本
独立测试环节1: MCP服务器连接和基础查询
"""

import subprocess
import asyncio
import aiohttp
import json
import os
import time
from typing import Dict, Optional, List

class MCPDatabaseSetup:
    """MCP数据库服务器设置类"""
    
    def __init__(self):
        self.mcp_server_port = 3001
        self.mcp_server_url = f"http://localhost:{self.mcp_server_port}"
        self.database_url = os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost:5432/railway")
        self.mcp_process = None
        
    def install_mcp_server(self) -> bool:
        """安装MCP数据库服务器"""
        try:
            print("📦 安装MCP数据库服务器...")
            
            # 创建package.json文件
            package_json = {
                "name": "mcp-database-server",
                "version": "1.0.0",
                "description": "MCP Database Server for Smart Charts",
                "dependencies": {
                    "@anthropic-ai/mcp-server-postgres": "^0.4.0",
                    "@types/node": "^20.0.0"
                },
                "scripts": {
                    "start": "mcp-server-postgres"
                }
            }
            
            with open("/workspace/backend/package.json", "w") as f:
                json.dump(package_json, f, indent=2)
            
            # 安装依赖
            result = subprocess.run(
                ["npm", "install"],
                cwd="/workspace/backend",
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                print("✅ MCP服务器安装成功")
                return True
            else:
                print(f"❌ 安装失败: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ 安装异常: {e}")
            return False
    
    def start_mcp_server(self) -> bool:
        """启动MCP数据库服务器"""
        try:
            print(f"🚀 启动MCP服务器在端口 {self.mcp_server_port}...")
            
            # MCP服务器启动命令
            cmd = [
                "npx", "@anthropic-ai/mcp-server-postgres",
                "--database-url", self.database_url,
                "--port", str(self.mcp_server_port),
                "--host", "0.0.0.0"
            ]
            
            self.mcp_process = subprocess.Popen(
                cmd,
                cwd="/workspace/backend",
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # 等待服务器启动
            print("⏳ 等待服务器启动...")
            time.sleep(10)
            
            if self.mcp_process.poll() is None:
                print("✅ MCP服务器启动成功")
                return True
            else:
                stdout, stderr = self.mcp_process.communicate()
                print(f"❌ 服务器启动失败: {stderr.decode()}")
                return False
                
        except Exception as e:
            print(f"❌ 启动异常: {e}")
            return False
    
    async def test_mcp_connection(self) -> bool:
        """测试MCP服务器连接"""
        try:
            print("🔍 测试MCP服务器连接...")
            
            async with aiohttp.ClientSession() as session:
                # 测试健康检查
                async with session.get(f"{self.mcp_server_url}/health") as response:
                    if response.status == 200:
                        print("✅ MCP服务器连接正常")
                        return True
                    else:
                        print(f"❌ 连接失败，状态码: {response.status}")
                        return False
                        
        except Exception as e:
            print(f"❌ 连接测试异常: {e}")
            return False
    
    async def test_schema_query(self) -> bool:
        """测试数据库Schema查询"""
        try:
            print("📋 测试数据库Schema查询...")
            
            async with aiohttp.ClientSession() as session:
                # 查询数据库表结构
                request_data = {
                    "method": "list_tables",
                    "params": {}
                }
                
                async with session.post(
                    f"{self.mcp_server_url}/query",
                    json=request_data
                ) as response:
                    
                    if response.status == 200:
                        result = await response.json()
                        tables = result.get("tables", [])
                        print(f"✅ 发现 {len(tables)} 个数据表:")
                        for table in tables[:5]:  # 显示前5个表
                            print(f"   - {table}")
                        return True
                    else:
                        print(f"❌ Schema查询失败，状态码: {response.status}")
                        return False
                        
        except Exception as e:
            print(f"❌ Schema查询异常: {e}")
            return False
    
    async def test_sample_query(self) -> bool:
        """测试示例SQL查询"""
        try:
            print("🔍 测试示例SQL查询...")
            
            # 简单的测试查询
            test_sql = "SELECT COUNT(*) as total_snapshots FROM asset_snapshot LIMIT 1"
            
            async with aiohttp.ClientSession() as session:
                request_data = {
                    "method": "execute_sql",
                    "params": {
                        "sql": test_sql,
                        "max_rows": 10
                    }
                }
                
                async with session.post(
                    f"{self.mcp_server_url}/query",
                    json=request_data
                ) as response:
                    
                    if response.status == 200:
                        result = await response.json()
                        data = result.get("data", [])
                        print(f"✅ 查询成功，返回 {len(data)} 行数据")
                        if data:
                            print(f"   示例结果: {data[0]}")
                        return True
                    else:
                        print(f"❌ SQL查询失败，状态码: {response.status}")
                        return False
                        
        except Exception as e:
            print(f"❌ SQL查询异常: {e}")
            return False
    
    def stop_mcp_server(self):
        """停止MCP服务器"""
        if self.mcp_process:
            print("🛑 停止MCP服务器...")
            self.mcp_process.terminate()
            self.mcp_process.wait()
            print("✅ MCP服务器已停止")
    
    async def run_full_test(self) -> Dict[str, bool]:
        """运行完整的MCP设置测试"""
        print("=" * 50)
        print("🧪 MCP数据库服务器测试套件")
        print("=" * 50)
        
        results = {}
        
        # 1. 安装测试
        results["install"] = self.install_mcp_server()
        
        if not results["install"]:
            print("❌ 安装失败，跳过后续测试")
            return results
        
        # 2. 启动测试
        results["start"] = self.start_mcp_server()
        
        if not results["start"]:
            print("❌ 启动失败，跳过后续测试")
            return results
        
        try:
            # 3. 连接测试
            results["connection"] = await self.test_mcp_connection()
            
            # 4. Schema测试
            results["schema"] = await self.test_schema_query()
            
            # 5. 查询测试
            results["query"] = await self.test_sample_query()
            
        finally:
            # 6. 清理
            self.stop_mcp_server()
        
        # 输出测试结果
        print("\n" + "=" * 50)
        print("📊 测试结果汇总:")
        print("=" * 50)
        
        for test_name, passed in results.items():
            status = "✅ 通过" if passed else "❌ 失败"
            print(f"{test_name:12}: {status}")
        
        overall_success = all(results.values())
        print(f"\n整体状态: {'✅ 全部通过' if overall_success else '❌ 存在失败'}")
        
        return results

# 独立测试脚本
async def main():
    """独立测试入口"""
    setup = MCPDatabaseSetup()
    results = await setup.run_full_test()
    
    if all(results.values()):
        print("\n🎉 MCP数据库服务器设置完成，可以进入下一步！")
        exit(0)
    else:
        print("\n❌ 设置过程中存在问题，请检查错误信息后重试")
        exit(1)

if __name__ == "__main__":
    asyncio.run(main())