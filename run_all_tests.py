#!/usr/bin/env python3
"""
MCP智能图表系统 - 统一测试运行脚本
按步骤运行所有独立测试，确保每个环节都正常工作
"""

import subprocess
import asyncio
import sys
import os
from typing import Dict, List

class TestRunner:
    """统一测试运行器"""
    
    def __init__(self):
        self.test_results = {}
        self.current_dir = os.path.dirname(os.path.abspath(__file__))
        
    def print_banner(self, title: str):
        """打印测试标题横幅"""
        print("\n" + "=" * 60)
        print(f"🧪 {title}")
        print("=" * 60)
    
    def print_step(self, step: int, title: str, description: str):
        """打印测试步骤"""
        print(f"\n📋 步骤 {step}: {title}")
        print(f"   {description}")
        print("-" * 40)
    
    async def run_test_step(self, step: str, command: List[str], description: str) -> bool:
        """运行单个测试步骤"""
        print(f"\n🔍 运行测试: {description}")
        
        try:
            # 运行测试命令
            process = await asyncio.create_subprocess_exec(
                *command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=self.current_dir
            )
            
            stdout, stderr = await process.communicate()
            
            # 输出测试结果
            if stdout:
                print(stdout.decode())
            if stderr:
                print(stderr.decode())
            
            # 检查退出码
            success = process.returncode == 0
            
            self.test_results[step] = success
            
            if success:
                print(f"✅ {step} 测试通过")
            else:
                print(f"❌ {step} 测试失败 (退出码: {process.returncode})")
            
            return success
            
        except Exception as e:
            print(f"❌ {step} 测试异常: {e}")
            self.test_results[step] = False
            return False
    
    def check_prerequisites(self) -> bool:
        """检查前提条件"""
        print("🔍 检查前提条件...")
        
        # 检查Python版本
        if sys.version_info < (3, 8):
            print("❌ 需要Python 3.8或更高版本")
            return False
        
        # 检查必要的包
        required_packages = ['aiohttp', 'asyncio', 'fastapi']
        missing_packages = []
        
        for package in required_packages:
            try:
                __import__(package)
            except ImportError:
                missing_packages.append(package)
        
        if missing_packages:
            print(f"❌ 缺少必要的包: {', '.join(missing_packages)}")
            print("请运行: pip install aiohttp fastapi uvicorn")
            return False
        
        # 检查数据库连接
        database_url = os.getenv("DATABASE_URL")
        if not database_url:
            print("⚠️  未设置DATABASE_URL环境变量，将使用默认配置")
        
        print("✅ 前提条件检查通过")
        return True
    
    async def run_all_tests(self):
        """运行所有测试步骤"""
        
        self.print_banner("MCP智能图表系统 - 完整测试套件")
        
        # 检查前提条件
        if not self.check_prerequisites():
            print("\n❌ 前提条件不满足，测试终止")
            return False
        
        # 测试步骤定义
        test_steps = [
            {
                "step": "step1_mcp_server",
                "title": "MCP数据库服务器",
                "description": "安装、启动和基础连接测试",
                "command": ["python3", "backend/mcp_database_setup.py"],
                "required": True
            },
            {
                "step": "step2_mcp_client", 
                "title": "MCP客户端",
                "description": "客户端通信和查询测试",
                "command": ["python3", "-m", "backend.app.services.mcp_client"],
                "required": True
            },
            {
                "step": "step3_chart_config",
                "title": "图表配置生成器",
                "description": "数据分析和配置生成测试",
                "command": ["python3", "-m", "backend.app.services.chart_config_generator"],
                "required": True
            }
        ]
        
        # 运行测试步骤
        for i, test_step in enumerate(test_steps, 1):
            self.print_step(
                i, 
                test_step["title"], 
                test_step["description"]
            )
            
            success = await self.run_test_step(
                test_step["step"],
                test_step["command"],
                test_step["description"]
            )
            
            # 如果是必需步骤且失败，停止后续测试
            if test_step.get("required", False) and not success:
                print(f"\n❌ 必需步骤失败，停止后续测试")
                break
            
            # 步骤间暂停
            if i < len(test_steps):
                print(f"\n⏳ 等待3秒后进行下一步...")
                await asyncio.sleep(3)
        
        # 输出最终结果
        self.print_test_summary()
        
        # 检查整体成功率
        success_count = sum(self.test_results.values())
        total_count = len(self.test_results)
        
        return success_count == total_count
    
    def print_test_summary(self):
        """打印测试总结"""
        self.print_banner("测试结果总结")
        
        success_count = 0
        total_count = len(self.test_results)
        
        for step, success in self.test_results.items():
            status = "✅ 通过" if success else "❌ 失败"
            print(f"{step:20}: {status}")
            if success:
                success_count += 1
        
        success_rate = (success_count / total_count * 100) if total_count > 0 else 0
        
        print(f"\n📊 测试统计:")
        print(f"   通过: {success_count}/{total_count}")
        print(f"   成功率: {success_rate:.1f}%")
        
        if success_count == total_count:
            print("\n🎉 所有测试通过！系统已准备就绪。")
            print("\n📋 下一步操作:")
            print("   1. 启动FastAPI服务器:")
            print("      cd backend && uvicorn app.main:app --reload --port 8000")
            print("   2. 测试API端点:")
            print("      python3 -m backend.app.api.v1.mcp_smart_chart")
            print("   3. 开始Flutter集成")
        else:
            print(f"\n⚠️  有 {total_count - success_count} 个测试失败")
            print("   请检查失败的步骤并修复后重试")
    
    def save_test_report(self):
        """保存测试报告"""
        import json
        from datetime import datetime
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "results": self.test_results,
            "summary": {
                "total": len(self.test_results),
                "passed": sum(self.test_results.values()),
                "failed": len(self.test_results) - sum(self.test_results.values())
            }
        }
        
        with open("test_report.json", "w") as f:
            json.dump(report, f, indent=2)
        
        print(f"\n📄 测试报告已保存到: test_report.json")

# 快速测试功能
class QuickTest:
    """快速测试单个组件"""
    
    @staticmethod
    async def test_mcp_server():
        """快速测试MCP服务器"""
        print("🔍 快速测试MCP服务器...")
        runner = TestRunner()
        success = await runner.run_test_step(
            "quick_mcp_server",
            ["python3", "backend/mcp_database_setup.py"],
            "MCP服务器快速测试"
        )
        return success
    
    @staticmethod
    async def test_mcp_client():
        """快速测试MCP客户端"""
        print("🔍 快速测试MCP客户端...")
        runner = TestRunner()
        success = await runner.run_test_step(
            "quick_mcp_client",
            ["python3", "-m", "backend.app.services.mcp_client"],
            "MCP客户端快速测试"
        )
        return success
    
    @staticmethod
    async def test_chart_generator():
        """快速测试图表生成器"""
        print("🔍 快速测试图表生成器...")
        runner = TestRunner()
        success = await runner.run_test_step(
            "quick_chart_generator",
            ["python3", "-m", "backend.app.services.chart_config_generator"],
            "图表生成器快速测试"
        )
        return success

async def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="MCP智能图表系统测试运行器")
    parser.add_argument("--quick", choices=["mcp-server", "mcp-client", "chart-generator"], 
                       help="快速测试单个组件")
    parser.add_argument("--save-report", action="store_true", help="保存测试报告")
    
    args = parser.parse_args()
    
    if args.quick:
        # 快速测试模式
        if args.quick == "mcp-server":
            success = await QuickTest.test_mcp_server()
        elif args.quick == "mcp-client":
            success = await QuickTest.test_mcp_client()
        elif args.quick == "chart-generator":
            success = await QuickTest.test_chart_generator()
        
        if success:
            print("✅ 快速测试通过")
            exit(0)
        else:
            print("❌ 快速测试失败")
            exit(1)
    
    else:
        # 完整测试模式
        runner = TestRunner()
        success = await runner.run_all_tests()
        
        if args.save_report:
            runner.save_test_report()
        
        if success:
            print("\n🎉 全部测试完成，系统准备就绪！")
            exit(0)
        else:
            print("\n❌ 部分测试失败，请检查并修复")
            exit(1)

if __name__ == "__main__":
    asyncio.run(main())