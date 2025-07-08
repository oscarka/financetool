#!/usr/bin/env python3
"""
轻量级API测试工具 (仅使用标准库)
快速测试和调用API接口
"""
import urllib.request
import urllib.error
import json
import time
from datetime import datetime
import argparse
import sys

class SimpleAPITester:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url.rstrip('/')
        
        # 核心API接口列表
        self.endpoints = {
            "系统": [
                ("GET", "/health", "健康检查"),
                ("GET", "/", "根路径"),
            ],
            "基金": [
                ("GET", "/api/v1/funds/operations", "基金操作列表"),
                ("GET", "/api/v1/funds/positions", "持仓信息"),
                ("GET", "/api/v1/funds/positions/summary", "持仓汇总"),
                ("GET", "/api/v1/funds/info", "基金信息"),
                ("GET", "/api/v1/funds/dca/plans", "定投计划"),
                ("GET", "/api/v1/funds/scheduler/jobs", "调度器状态"),
            ],
            "汇率": [
                ("GET", "/api/v1/exchange-rates/currencies", "支持货币"),
                ("GET", "/api/v1/exchange-rates/rates", "汇率查询"),
                ("GET", "/api/v1/exchange-rates/rates/USD", "USD汇率"),
            ],
            "PayPal": [
                ("GET", "/api/v1/paypal/config", "配置信息"),
                ("GET", "/api/v1/paypal/test", "连接测试"),
                ("GET", "/api/v1/paypal/summary", "账户汇总"),
            ],
            "Wise": [
                ("GET", "/api/v1/wise/config", "配置信息"),
                ("GET", "/api/v1/wise/test", "连接测试"),
                ("GET", "/api/v1/wise/summary", "账户汇总"),
            ]
        }

    def test_endpoint(self, method, path, timeout=10):
        """测试单个接口"""
        url = f"{self.base_url}{path}"
        start_time = time.time()
        
        try:
            req = urllib.request.Request(url, method=method)
            req.add_header('Content-Type', 'application/json')
            req.add_header('Accept', 'application/json')
            
            with urllib.request.urlopen(req, timeout=timeout) as response:
                response_time = (time.time() - start_time) * 1000
                content = response.read().decode('utf-8')
                
                try:
                    json_data = json.loads(content)
                except:
                    json_data = None
                
                return {
                    "success": True,
                    "status_code": response.getcode(),
                    "response_time": response_time,
                    "content": content[:200] if len(content) > 200 else content,
                    "json_data": json_data
                }
        except urllib.error.HTTPError as e:
            response_time = (time.time() - start_time) * 1000
            try:
                content = e.read().decode('utf-8')
            except:
                content = str(e)
            
            return {
                "success": True,  # HTTP错误也算是成功的响应
                "status_code": e.code,
                "response_time": response_time,
                "content": content[:200] if len(content) > 200 else content,
                "json_data": None
            }
        except urllib.error.URLError as e:
            return {
                "success": False,
                "error": f"连接错误: {str(e)}",
                "response_time": (time.time() - start_time) * 1000
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "response_time": (time.time() - start_time) * 1000
            }

    def batch_test(self):
        """批量测试所有接口"""
        print(f"🧪 开始测试 {self.base_url} 的API接口...")
        print("=" * 80)
        
        total_success = 0
        total_apis = 0
        
        for category, endpoints in self.endpoints.items():
            print(f"\n📂 {category} 模块:")
            print("-" * 50)
            
            for method, path, name in endpoints:
                total_apis += 1
                print(f"  测试: {method} {name}...", end="", flush=True)
                
                result = self.test_endpoint(method, path)
                
                if result["success"]:
                    if result["status_code"] == 200:
                        print(f" ✅ 成功 ({result['response_time']:.0f}ms)")
                        total_success += 1
                    elif result["status_code"] == 404:
                        print(f" ⚠️  404 接口不存在 ({result['response_time']:.0f}ms)")
                    elif result["status_code"] == 500:
                        print(f" 🚨 500 服务器错误 ({result['response_time']:.0f}ms)")
                    else:
                        print(f" ⚠️  HTTP {result['status_code']} ({result['response_time']:.0f}ms)")
                else:
                    print(f" ❌ 失败: {result['error']} ({result['response_time']:.0f}ms)")
        
        print("\n" + "=" * 80)
        health_rate = (total_success / total_apis) * 100 if total_apis > 0 else 0
        print(f"📊 测试完成!")
        print(f"   总接口数: {total_apis}")
        print(f"   正常接口: {total_success}")
        print(f"   健康率: {health_rate:.1f}%")
        
        if health_rate >= 90:
            print("🎉 系统运行良好!")
        elif health_rate >= 70:
            print("⚠️  系统部分功能异常")
        else:
            print("🚨 系统存在较多问题")

    def interactive_test(self):
        """交互式测试"""
        print("🚀 交互式API测试工具")
        print("=" * 50)
        
        while True:
            print("\n请选择要测试的模块:")
            categories = list(self.endpoints.keys())
            for i, category in enumerate(categories, 1):
                print(f"  {i}. {category}")
            print("  0. 退出")
            
            try:
                choice_input = input(f"\n请输入选择 (0-{len(categories)}): ").strip()
                if not choice_input:
                    continue
                    
                choice = int(choice_input)
                if choice == 0:
                    print("👋 再见!")
                    break
                
                if 1 <= choice <= len(categories):
                    category = categories[choice - 1]
                    endpoints = self.endpoints[category]
                    
                    print(f"\n📂 {category} 模块 - 可用接口:")
                    for i, (method, path, name) in enumerate(endpoints, 1):
                        print(f"  {i}. {method} {name}")
                    print("  0. 返回上级")
                    
                    endpoint_input = input(f"\n请选择接口 (0-{len(endpoints)}): ").strip()
                    if not endpoint_input:
                        continue
                        
                    endpoint_choice = int(endpoint_input)
                    if endpoint_choice == 0:
                        continue
                    
                    if 1 <= endpoint_choice <= len(endpoints):
                        method, path, name = endpoints[endpoint_choice - 1]
                        print(f"\n🔍 调用: {method} {path}")
                        print("-" * 30)
                        
                        result = self.test_endpoint(method, path)
                        
                        if result["success"]:
                            status_emoji = "✅" if result["status_code"] == 200 else "⚠️"
                            print(f"{status_emoji} 状态码: {result['status_code']}")
                            print(f"⏱️  响应时间: {result['response_time']:.0f}ms")
                            
                            if result["json_data"]:
                                print("\n📄 JSON响应:")
                                print(json.dumps(result["json_data"], indent=2, ensure_ascii=False))
                            else:
                                print(f"\n📄 原始响应:\n{result['content']}")
                        else:
                            print(f"❌ 请求失败: {result['error']}")
                            print(f"⏱️  响应时间: {result['response_time']:.0f}ms")
                        
                        input("\n按Enter继续...")
                    else:
                        print("❌ 无效选择")
                else:
                    print("❌ 无效选择")
            except (ValueError, KeyboardInterrupt, EOFError):
                print("\n👋 退出")
                break

    def quick_health_check(self):
        """快速健康检查"""
        print("🏥 快速健康检查...")
        
        # 检查核心接口
        core_endpoints = [
            ("GET", "/health", "系统健康"),
            ("GET", "/api/v1/funds/operations", "基金模块"),
            ("GET", "/api/v1/exchange-rates/currencies", "汇率模块"),
        ]
        
        for method, path, name in core_endpoints:
            print(f"  检查 {name}...", end="", flush=True)
            result = self.test_endpoint(method, path, timeout=5)
            if result["success"] and result["status_code"] == 200:
                print(f" ✅ 正常 ({result['response_time']:.0f}ms)")
            else:
                error = result.get('error', f"HTTP {result.get('status_code', 'Unknown')}")
                print(f" ❌ {error}")

    def generate_simple_report(self):
        """生成简单报告"""
        print("📄 正在生成API健康报告...")
        
        report_lines = []
        report_lines.append(f"# API健康报告")
        report_lines.append(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append(f"服务器: {self.base_url}")
        report_lines.append("")
        
        total_success = 0
        total_apis = 0
        
        for category, endpoints in self.endpoints.items():
            report_lines.append(f"## {category} 模块")
            report_lines.append("")
            
            for method, path, name in endpoints:
                total_apis += 1
                result = self.test_endpoint(method, path)
                
                if result["success"] and result["status_code"] == 200:
                    status = "✅ 正常"
                    total_success += 1
                elif result["success"]:
                    status = f"⚠️ HTTP {result['status_code']}"
                else:
                    status = f"❌ {result['error']}"
                
                response_time = f"{result['response_time']:.0f}ms"
                report_lines.append(f"- **{name}**: {status} ({response_time})")
            
            report_lines.append("")
        
        health_rate = (total_success / total_apis) * 100 if total_apis > 0 else 0
        report_lines.insert(4, f"- 总接口数: {total_apis}")
        report_lines.insert(5, f"- 正常接口: {total_success}")
        report_lines.insert(6, f"- 健康率: {health_rate:.1f}%")
        report_lines.insert(7, "")
        
        report_content = "\n".join(report_lines)
        
        filename = f"api_health_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        print(f"✅ 报告已保存到: {filename}")
        return filename


def main():
    parser = argparse.ArgumentParser(description="轻量级API测试工具")
    parser.add_argument("--url", default="http://localhost:8000", help="API服务器地址")
    parser.add_argument("--mode", choices=["batch", "interactive", "health", "report"], 
                        default="interactive", help="运行模式")
    
    args = parser.parse_args()
    
    tester = SimpleAPITester(args.url)
    
    if args.mode == "batch":
        tester.batch_test()
    elif args.mode == "health":
        tester.quick_health_check()
    elif args.mode == "report":
        tester.generate_simple_report()
    else:
        tester.interactive_test()


if __name__ == "__main__":
    main()