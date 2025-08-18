"""
FastAPI MCP客户端服务
独立测试环节2: MCP客户端通信和自然语言查询
"""

import aiohttp
import asyncio
import json
import logging
import psycopg2
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
from app.services.chart_config_generator import ChartConfigGenerator
from app.services.deepseek_ai_service import DeepSeekAIService

logger = logging.getLogger(__name__)

@dataclass
class MCPQueryResult:
    """MCP查询结果数据类"""
    success: bool
    sql: Optional[str] = None
    data: Optional[List[Dict]] = None
    error: Optional[str] = None
    execution_time: Optional[float] = None
    row_count: Optional[int] = None
    ai_analysis: Optional[Dict] = None # 新增字段
    method: Optional[str] = None # 新增字段

class MCPDatabaseClient:
    """MCP数据库客户端"""
    
    def __init__(self, mcp_server_url: str = "http://localhost:3001", use_mock: bool = False):
        self.mcp_server_url = mcp_server_url
        self.use_mock = use_mock
        self.session = None
        self.timeout = aiohttp.ClientTimeout(total=30)
        
        # 初始化DeepSeek AI服务
        self.deepseek_service = DeepSeekAIService()
        
        # 数据库连接配置
        self.db_config = {
            'host': 'localhost',
            'port': 5432,
            'database': 'financetool_test',
            'user': 'financetool_user',
            'password': 'financetool_pass'
        }
        
        # 模拟数据
        self.mock_data = {
            "asset_snapshot": [
                {
                    "platform": "支付宝",
                    "asset_type": "基金", 
                    "asset_code": "005827",
                    "asset_name": "易方达蓝筹精选混合",
                    "balance_cny": 85230.45,
                    "snapshot_time": "2024-01-15 09:00:00"
                },
                {
                    "platform": "支付宝",
                    "asset_type": "基金",
                    "asset_code": "110022", 
                    "asset_name": "易方达消费行业股票",
                    "balance_cny": 73229.85,
                    "snapshot_time": "2024-01-15 09:00:00"
                },
                {
                    "platform": "Wise",
                    "asset_type": "外汇",
                    "asset_code": "USD",
                    "asset_name": "美元现金",
                    "balance_cny": 6458.23,
                    "snapshot_time": "2024-01-15 09:00:00"
                },
                {
                    "platform": "Wise", 
                    "asset_type": "外汇",
                    "asset_code": "EUR",
                    "asset_name": "欧元现金", 
                    "balance_cny": 1700.00,
                    "snapshot_time": "2024-01-15 09:00:00"
                },
                {
                    "platform": "IBKR",
                    "asset_type": "股票",
                    "asset_code": "AAPL", 
                    "asset_name": "苹果公司",
                    "balance_cny": 42.03,
                    "snapshot_time": "2024-01-15 09:00:00"
                },
                {
                    "platform": "OKX",
                    "asset_type": "数字货币",
                    "asset_code": "BTC",
                    "asset_name": "比特币",
                    "balance_cny": 1205.67,
                    "snapshot_time": "2024-01-15 09:00:00"
                }
            ]
        }
        
        # 预定义的业务查询模板
        self.query_templates = {
            "platform_distribution": {
                "sql": """
                    SELECT platform, SUM(balance_cny) as total_value, COUNT(*) as asset_count
                    FROM asset_snapshot 
                    WHERE snapshot_time = (SELECT MAX(snapshot_time) FROM asset_snapshot)
                    GROUP BY platform 
                    ORDER BY total_value DESC
                """,
                "chart_hint": "bar",
                "description": "各平台资产分布对比"
            },
            "asset_type_distribution": {
                "sql": """
                    SELECT asset_type, SUM(balance_cny) as total_value, COUNT(*) as asset_count
                    FROM asset_snapshot 
                    WHERE snapshot_time = (SELECT MAX(snapshot_time) FROM asset_snapshot)
                    GROUP BY asset_type 
                    ORDER BY total_value DESC
                """,
                "chart_hint": "pie",
                "description": "各资产类型分布对比"
            },
            "monthly_trend": {
                "sql": """
                    SELECT TO_CHAR(snapshot_time, 'YYYY-MM-DD') as date, SUM(balance_cny) as total_value
                    FROM asset_snapshot 
                    WHERE snapshot_time >= CURRENT_DATE - INTERVAL '30 days'
                    GROUP BY TO_CHAR(snapshot_time, 'YYYY-MM-DD')
                    ORDER BY date ASC
                """,
                "chart_hint": "line",
                "description": "最近30天资产变化趋势"
            },
            "top_assets": {
                "sql": """
                    SELECT asset_name, balance_cny as total_value, platform, asset_type
                    FROM asset_snapshot 
                    WHERE snapshot_time = (SELECT MAX(snapshot_time) FROM asset_snapshot)
                    ORDER BY balance_cny DESC 
                    LIMIT 10
                """,
                "chart_hint": "bar",
                "description": "前10大资产排名"
            }
        }
    
    async def __aenter__(self):
        """异步上下文管理器入口"""
        self.session = aiohttp.ClientSession(timeout=self.timeout)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        if self.session:
            await self.session.close()
    
    async def health_check(self) -> bool:
        """检查MCP服务器健康状态"""
        if self.use_mock:
            # 模拟模式：总是返回True
            return True
            
        try:
            if not self.session:
                self.session = aiohttp.ClientSession(timeout=self.timeout)
                
            async with self.session.get(f"{self.mcp_server_url}/health") as response:
                return response.status == 200
                
        except Exception as e:
            logger.error(f"MCP健康检查失败: {e}")
            return False
    
    async def execute_sql(self, sql: str, max_rows: int = 1000) -> MCPQueryResult:
        """执行SQL查询"""
        start_time = datetime.now()
        
        if self.use_mock:
            # 模拟模式：返回模拟数据
            execution_time = (datetime.now() - start_time).total_seconds()
            
            # 根据SQL内容返回相应的模拟数据
            if "platform" in sql.lower():
                mock_data = [
                    {"platform": "支付宝", "total_value": 158460.30, "asset_count": 2},
                    {"platform": "Wise", "total_value": 8158.23, "asset_count": 2},
                    {"platform": "IBKR", "total_value": 42.03, "asset_count": 1},
                    {"platform": "OKX", "total_value": 1205.67, "asset_count": 1}
                ]
            elif "asset_type" in sql.lower():
                mock_data = [
                    {"asset_type": "基金", "total_value": 158460.30, "asset_count": 2},
                    {"asset_type": "外汇", "total_value": 8158.23, "asset_count": 2},
                    {"asset_type": "股票", "total_value": 42.03, "asset_count": 1},
                    {"asset_type": "数字货币", "total_value": 1205.67, "asset_count": 1}
                ]
            else:
                mock_data = self.mock_data["asset_snapshot"]
            
            return MCPQueryResult(
                success=True,
                sql=sql,
                data=mock_data,
                execution_time=execution_time,
                row_count=len(mock_data)
            )
        
        # 非模拟模式：通过MCP服务器执行SQL
        try:
            if not self.session:
                self.session = aiohttp.ClientSession(timeout=self.timeout)
            
            request_data = {
                "method": "execute_sql",
                "params": {
                    "sql": sql,
                    "max_rows": max_rows
                }
            }
            
            logger.info(f"通过MCP服务器执行SQL: {sql}")
            
            async with self.session.post(
                f"{self.mcp_server_url}/query",
                json=request_data
            ) as response:
                
                execution_time = (datetime.now() - start_time).total_seconds()
                
                if response.status == 200:
                    result = await response.json()
                    data = result.get("data", [])
                    
                    return MCPQueryResult(
                        success=True,
                        sql=sql,
                        data=data,
                        execution_time=execution_time,
                        row_count=len(data)
                    )
                else:
                    error_text = await response.text()
                    return MCPQueryResult(
                        success=False,
                        sql=sql,
                        error=f"HTTP {response.status}: {error_text}",
                        execution_time=execution_time
                    )
                    
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            logger.error(f"SQL执行异常: {e}")
            return MCPQueryResult(
                success=False,
                sql=sql,
                error=str(e),
                execution_time=execution_time
            )
    
    async def natural_language_query(self, question: str) -> MCPQueryResult:
        """自然语言查询处理"""
        start_time = datetime.now()
        
        if self.use_mock:
            # 模拟模式：使用模板匹配
            template_result = self._match_query_template(question)
            if template_result:
                logger.info(f"使用模板匹配: {template_result['description']}")
                return await self.execute_sql(template_result["sql"])
            else:
                # 如果没有匹配的模板，返回通用模拟数据
                return await self.execute_sql("SELECT * FROM asset_snapshot LIMIT 10")
        
        # 非模拟模式：优先使用DeepSeek AI，然后通过MCP服务器进行自然语言处理
        try:
            # 1. 尝试使用DeepSeek AI分析问题
            logger.info(f"使用DeepSeek AI分析问题: {question}")
            ai_analysis = await self.deepseek_service.analyze_financial_question(question)
            
            if ai_analysis and ai_analysis.get('sql'):
                # DeepSeek AI成功生成SQL，直接执行
                generated_sql = ai_analysis['sql']
                logger.info(f"DeepSeek AI生成的SQL: {generated_sql}")
                
                # 执行生成的SQL
                sql_result = await self.execute_sql(generated_sql)
                
                # 如果SQL执行成功，添加AI分析信息
                if sql_result.success:
                    sql_result.ai_analysis = ai_analysis
                    sql_result.method = "deepseek_ai"
                
                return sql_result
            else:
                logger.info("DeepSeek AI未返回有效SQL，尝试MCP服务器")
        
        except Exception as e:
            logger.warning(f"DeepSeek AI分析失败，回退到MCP服务器: {e}")
        
        # 2. 如果DeepSeek AI失败，回退到MCP服务器
        try:
            if not self.session:
                self.session = aiohttp.ClientSession(timeout=self.timeout)
            
            # 先尝试模板匹配
            template_result = self._match_query_template(question)
            if template_result:
                logger.info(f"使用模板匹配: {template_result['description']}")
                return await self.execute_sql(template_result["sql"])
            
            # 使用MCP的自然语言处理
            request_data = {
                "method": "natural_query",
                "params": {
                    "question": question,
                    "context": self._get_database_context(),
                    "max_rows": 1000
                }
            }
            
            logger.info(f"通过MCP服务器进行自然语言查询: {question}")
            
            async with self.session.post(
                f"{self.mcp_server_url}/nl-query",
                json=request_data
            ) as response:
                
                if response.status == 200:
                    result = await response.json()
                    
                    # 执行生成的SQL
                    generated_sql = result.get("sql")
                    if generated_sql:
                        return await self.execute_sql(generated_sql)
                    else:
                        return MCPQueryResult(
                            success=False,
                            error="MCP未返回有效SQL"
                        )
                else:
                    error_text = await response.text()
                    return MCPQueryResult(
                        success=False,
                        error=f"自然语言处理失败: HTTP {response.status}: {error_text}"
                    )
                    
        except Exception as e:
            logger.error(f"自然语言查询异常: {e}")
            return MCPQueryResult(
                success=False,
                error=str(e),
                execution_time=(datetime.now() - start_time).total_seconds()
            )
    
    def _match_query_template(self, question: str) -> Optional[Dict]:
        """匹配查询模板"""
        question_lower = question.lower()
        
        # 平台分布关键词
        if any(word in question_lower for word in ['平台', '分布', 'platform']):
            return self.query_templates["platform_distribution"]
        
        # 资产类型关键词
        if any(word in question_lower for word in ['类型', '种类', '占比', '比例']):
            return self.query_templates["asset_type_distribution"]
        
        # 趋势关键词
        if any(word in question_lower for word in ['趋势', '变化', '走势', 'trend']):
            return self.query_templates["monthly_trend"]
        
        return None
    
    def _get_database_context(self) -> Dict:
        """获取数据库上下文信息"""
        import json
        import os
        
        # 加载完整的Schema信息
        schema_file = os.path.join(os.path.dirname(__file__), "../../../database_schema_for_mcp.json")
        try:
            with open(schema_file, 'r', encoding='utf-8') as f:
                full_schema = json.load(f)
            return full_schema["database_schema"]
        except Exception as e:
            logger.warning(f"无法加载完整Schema，使用简化版本: {e}")
            # 简化版本作为备用
            return {
                "domain": "personal_finance",
                "primary_table": "asset_snapshot",
                "key_fields": ["platform", "asset_type", "balance_cny", "snapshot_time"],
                "common_aggregations": ["SUM", "COUNT", "AVG"],
                "time_field": "snapshot_time",
                "value_field": "balance_cny",
                "tables": {
                    "asset_snapshot": {
                        "description": "资产快照表 - 核心分析数据源",
                        "columns": {
                            "platform": "平台名称 (支付宝, Wise, IBKR, OKX)",
                            "asset_type": "资产类型 (基金, 外汇, 股票, 数字货币)",
                            "asset_code": "资产代码",
                            "balance_cny": "人民币余额 - 主要分析字段",
                            "snapshot_time": "快照时间"
                        }
                    },
                    "user_operations": {
                        "description": "用户操作记录表 - 交易历史分析",
                        "columns": {
                            "operation_date": "操作时间",
                            "platform": "操作平台",
                            "operation_type": "操作类型 (买入, 卖出, 转账)",
                            "amount": "操作金额"
                        }
                    }
                }
            }
    
    async def get_database_schema(self) -> Dict:
        """获取数据库Schema信息"""
        try:
            if not self.session:
                self.session = aiohttp.ClientSession(timeout=self.timeout)
            
            request_data = {
                "method": "describe_tables",
                "params": {
                    "tables": ["asset_snapshot", "user_operations", "asset_positions"]
                }
            }
            
            async with self.session.post(
                f"{self.mcp_server_url}/schema",
                json=request_data
            ) as response:
                
                if response.status == 200:
                    return await response.json()
                else:
                    return {"error": f"Schema查询失败: HTTP {response.status}"}
                    
        except Exception as e:
            logger.error(f"Schema查询异常: {e}")
            return {"error": str(e)}

# 独立测试类
class MCPClientTester:
    """MCP客户端测试器"""
    
    def __init__(self, mcp_server_url: str = "http://localhost:3001"):
        self.mcp_server_url = mcp_server_url
        
    async def test_health_check(self) -> bool:
        """测试健康检查"""
        print("🔍 测试MCP客户端健康检查...")
        
        async with MCPDatabaseClient(self.mcp_server_url) as client:
            result = await client.health_check()
            
            if result:
                print("✅ MCP客户端连接正常")
                return True
            else:
                print("❌ MCP客户端连接失败")
                return False
    
    async def test_direct_sql(self) -> bool:
        """测试直接SQL执行"""
        print("🔍 测试直接SQL执行...")
        
        test_sql = "SELECT COUNT(*) as total FROM asset_snapshot"
        
        async with MCPDatabaseClient(self.mcp_server_url) as client:
            result = await client.execute_sql(test_sql)
            
            if result.success:
                print(f"✅ SQL执行成功:")
                print(f"   - 执行时间: {result.execution_time:.2f}秒")
                print(f"   - 返回行数: {result.row_count}")
                print(f"   - 数据样本: {result.data[0] if result.data else 'None'}")
                return True
            else:
                print(f"❌ SQL执行失败: {result.error}")
                return False
    
    async def test_template_matching(self) -> bool:
        """测试模板匹配"""
        print("🔍 测试查询模板匹配...")
        
        test_questions = [
            "显示各平台的资产分布",
            "各种资产类型的占比",
            "最近的资产变化趋势"
        ]
        
        async with MCPDatabaseClient(self.mcp_server_url) as client:
            results = []
            
            for question in test_questions:
                print(f"   测试问题: {question}")
                result = await client.natural_language_query(question)
                
                if result.success:
                    print(f"   ✅ 查询成功，返回 {result.row_count} 行")
                    results.append(True)
                else:
                    print(f"   ❌ 查询失败: {result.error}")
                    results.append(False)
            
            success_rate = sum(results) / len(results)
            print(f"📊 模板匹配成功率: {success_rate:.1%}")
            
            return success_rate >= 0.8  # 80%成功率
    
    async def test_schema_query(self) -> bool:
        """测试Schema查询"""
        print("🔍 测试数据库Schema查询...")
        
        async with MCPDatabaseClient(self.mcp_server_url) as client:
            schema = await client.get_database_schema()
            
            if "error" not in schema:
                print("✅ Schema查询成功")
                tables = schema.get("tables", [])
                print(f"   发现 {len(tables)} 个表")
                return True
            else:
                print(f"❌ Schema查询失败: {schema['error']}")
                return False
    
    async def run_full_test(self) -> Dict[str, bool]:
        """运行完整的客户端测试"""
        print("=" * 50)
        print("🧪 MCP客户端测试套件")
        print("=" * 50)
        
        results = {}
        
        # 1. 健康检查
        results["health"] = await self.test_health_check()
        
        if not results["health"]:
            print("❌ 健康检查失败，跳过后续测试")
            return results
        
        # 2. 直接SQL测试
        results["sql"] = await self.test_direct_sql()
        
        # 3. 模板匹配测试
        results["template"] = await self.test_template_matching()
        
        # 4. Schema查询测试
        results["schema"] = await self.test_schema_query()
        
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
    tester = MCPClientTester()
    results = await tester.run_full_test()
    
    if all(results.values()):
        print("\n🎉 MCP客户端测试完成，可以进入下一步！")
        exit(0)
    else:
        print("\n❌ 客户端测试中存在问题，请检查错误信息后重试")
        exit(1)

if __name__ == "__main__":
    asyncio.run(main())