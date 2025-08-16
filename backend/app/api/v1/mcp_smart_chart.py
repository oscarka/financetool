"""
MCP智能图表FastAPI端点
独立测试环节4: 完整的API接口集成
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Dict, List, Any, Optional
import logging
import asyncio
from datetime import datetime

from app.services.mcp_client import MCPDatabaseClient, MCPQueryResult
from app.services.chart_config_generator import ChartConfigGenerator, ChartConfig

logger = logging.getLogger(__name__)

# 请求响应模型
class ChartGenerationRequest(BaseModel):
    """图表生成请求模型"""
    question: str = Field(..., description="用户问题", example="显示各平台的资产分布")
    base_currency: str = Field("CNY", description="基准货币")
    max_rows: int = Field(1000, description="最大返回行数")

class ChartGenerationResponse(BaseModel):
    """图表生成响应模型"""
    success: bool
    chart_config: Optional[Dict[str, Any]] = None
    sql: Optional[str] = None
    execution_time: Optional[float] = None
    data_points: Optional[int] = None
    error: Optional[str] = None
    method: str  # "mcp" 或 "template"

class HealthCheckResponse(BaseModel):
    """健康检查响应模型"""
    status: str
    mcp_server_available: bool
    timestamp: str
    message: str

# 创建路由器
router = APIRouter(prefix="/mcp-smart-chart", tags=["MCP智能图表"])

# 全局MCP客户端配置
MCP_SERVER_URL = "http://localhost:3001"

@router.get("/health", response_model=HealthCheckResponse)
async def health_check():
    """健康检查端点"""
    try:
        async with MCPDatabaseClient(MCP_SERVER_URL) as client:
            mcp_available = await client.health_check()
        
        return HealthCheckResponse(
            status="healthy" if mcp_available else "degraded",
            mcp_server_available=mcp_available,
            timestamp=datetime.now().isoformat(),
            message="MCP服务器连接正常" if mcp_available else "MCP服务器连接失败"
        )
    except Exception as e:
        logger.error(f"健康检查失败: {e}")
        return HealthCheckResponse(
            status="unhealthy",
            mcp_server_available=False,
            timestamp=datetime.now().isoformat(),
            message=f"健康检查异常: {str(e)}"
        )

@router.post("/generate", response_model=ChartGenerationResponse)
async def generate_chart(request: ChartGenerationRequest):
    """生成智能图表"""
    start_time = datetime.now()
    
    try:
        logger.info(f"接收到图表生成请求: {request.question}")
        
        # 1. 使用MCP客户端查询数据
        async with MCPDatabaseClient(MCP_SERVER_URL) as client:
            query_result = await client.natural_language_query(request.question)
        
        if not query_result.success:
            logger.error(f"MCP查询失败: {query_result.error}")
            return ChartGenerationResponse(
                success=False,
                error=f"数据查询失败: {query_result.error}",
                method="mcp",
                execution_time=(datetime.now() - start_time).total_seconds()
            )
        
        # 2. 使用图表配置生成器创建图表配置
        config_generator = ChartConfigGenerator()
        chart_config = config_generator.generate_config(
            query_result.data,
            request.question,
            query_result.sql
        )
        
        execution_time = (datetime.now() - start_time).total_seconds()
        
        logger.info(f"图表生成成功: {chart_config.chart_type}, 数据点: {len(chart_config.data)}")
        
        return ChartGenerationResponse(
            success=True,
            chart_config=chart_config.to_dict(),
            sql=query_result.sql,
            execution_time=execution_time,
            data_points=len(chart_config.data),
            method="mcp"
        )
        
    except Exception as e:
        execution_time = (datetime.now() - start_time).total_seconds()
        logger.error(f"图表生成异常: {e}")
        
        return ChartGenerationResponse(
            success=False,
            error=f"图表生成异常: {str(e)}",
            method="mcp",
            execution_time=execution_time
        )

@router.get("/examples")
async def get_example_questions():
    """获取示例问题"""
    return {
        "examples": [
            {
                "question": "显示各平台的资产分布",
                "description": "查看不同平台的资产分配情况",
                "expected_chart": "bar"
            },
            {
                "question": "各资产类型的占比",
                "description": "分析投资组合中各类资产的比例",
                "expected_chart": "pie"
            },
            {
                "question": "最近30天的资产变化趋势",
                "description": "查看资产价值的时间变化",
                "expected_chart": "line"
            },
            {
                "question": "投资收益排行",
                "description": "对比各项投资的收益表现",
                "expected_chart": "bar"
            },
            {
                "question": "详细的交易记录",
                "description": "查看具体的交易明细",
                "expected_chart": "table"
            }
        ],
        "tips": [
            "使用描述性的问题，如'显示'、'对比'、'分析'等",
            "指定时间范围，如'最近30天'、'本月'等",
            "明确分析维度，如'按平台'、'按类型'等"
        ]
    }

@router.post("/test-sql")
async def test_sql_execution(sql: str):
    """测试SQL执行（开发用）"""
    try:
        async with MCPDatabaseClient(MCP_SERVER_URL) as client:
            result = await client.execute_sql(sql)
        
        return {
            "success": result.success,
            "data": result.data[:10] if result.data else None,  # 只返回前10行
            "row_count": result.row_count,
            "execution_time": result.execution_time,
            "error": result.error
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@router.get("/schema")
async def get_database_schema():
    """获取数据库Schema信息"""
    try:
        async with MCPDatabaseClient(MCP_SERVER_URL) as client:
            schema = await client.get_database_schema()
        
        return {
            "success": "error" not in schema,
            "schema": schema
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

# 独立测试类
class MCPAPITester:
    """MCP API端点测试器"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.api_prefix = "/api/v1/mcp-smart-chart"
        
    async def test_health_endpoint(self) -> bool:
        """测试健康检查端点"""
        print("🔍 测试健康检查端点...")
        
        import aiohttp
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}{self.api_prefix}/health") as response:
                    
                    if response.status == 200:
                        data = await response.json()
                        
                        if data.get("mcp_server_available"):
                            print("✅ 健康检查通过，MCP服务器可用")
                            return True
                        else:
                            print("⚠️ 健康检查通过，但MCP服务器不可用")
                            return False
                    else:
                        print(f"❌ 健康检查失败，状态码: {response.status}")
                        return False
                        
        except Exception as e:
            print(f"❌ 健康检查异常: {e}")
            return False
    
    async def test_chart_generation(self) -> bool:
        """测试图表生成端点"""
        print("🔍 测试图表生成端点...")
        
        import aiohttp
        
        test_questions = [
            "显示各平台的资产分布",
            "各资产类型的占比",
            "最近的资产变化趋势"
        ]
        
        success_count = 0
        
        try:
            async with aiohttp.ClientSession() as session:
                for question in test_questions:
                    print(f"   测试问题: {question}")
                    
                    request_data = {
                        "question": question,
                        "base_currency": "CNY",
                        "max_rows": 100
                    }
                    
                    async with session.post(
                        f"{self.base_url}{self.api_prefix}/generate",
                        json=request_data
                    ) as response:
                        
                        if response.status == 200:
                            data = await response.json()
                            
                            if data.get("success"):
                                chart_config = data.get("chart_config", {})
                                chart_type = chart_config.get("chart_type", "unknown")
                                data_points = data.get("data_points", 0)
                                
                                print(f"   ✅ 生成成功: {chart_type}图表，{data_points}个数据点")
                                success_count += 1
                            else:
                                error = data.get("error", "未知错误")
                                print(f"   ❌ 生成失败: {error}")
                        else:
                            print(f"   ❌ 请求失败，状态码: {response.status}")
            
            success_rate = success_count / len(test_questions)
            print(f"📊 图表生成成功率: {success_rate:.1%}")
            
            return success_rate >= 0.8  # 80%成功率
            
        except Exception as e:
            print(f"❌ 图表生成测试异常: {e}")
            return False
    
    async def test_examples_endpoint(self) -> bool:
        """测试示例问题端点"""
        print("🔍 测试示例问题端点...")
        
        import aiohttp
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}{self.api_prefix}/examples") as response:
                    
                    if response.status == 200:
                        data = await response.json()
                        
                        examples = data.get("examples", [])
                        tips = data.get("tips", [])
                        
                        if examples and tips:
                            print(f"✅ 示例端点正常，返回{len(examples)}个示例和{len(tips)}个提示")
                            return True
                        else:
                            print("❌ 示例端点数据不完整")
                            return False
                    else:
                        print(f"❌ 示例端点失败，状态码: {response.status}")
                        return False
                        
        except Exception as e:
            print(f"❌ 示例端点测试异常: {e}")
            return False
    
    async def test_schema_endpoint(self) -> bool:
        """测试Schema端点"""
        print("🔍 测试Schema端点...")
        
        import aiohttp
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}{self.api_prefix}/schema") as response:
                    
                    if response.status == 200:
                        data = await response.json()
                        
                        if data.get("success"):
                            print("✅ Schema端点正常")
                            return True
                        else:
                            error = data.get("error", "未知错误")
                            print(f"❌ Schema查询失败: {error}")
                            return False
                    else:
                        print(f"❌ Schema端点失败，状态码: {response.status}")
                        return False
                        
        except Exception as e:
            print(f"❌ Schema端点测试异常: {e}")
            return False
    
    async def run_full_test(self) -> Dict[str, bool]:
        """运行完整的API测试"""
        print("=" * 50)
        print("🧪 MCP API端点测试套件")
        print("=" * 50)
        
        results = {}
        
        # 1. 健康检查测试
        results["health"] = await self.test_health_endpoint()
        
        if not results["health"]:
            print("❌ 健康检查失败，跳过后续测试")
            return results
        
        # 2. 图表生成测试
        results["chart_generation"] = await self.test_chart_generation()
        
        # 3. 示例端点测试
        results["examples"] = await self.test_examples_endpoint()
        
        # 4. Schema端点测试
        results["schema"] = await self.test_schema_endpoint()
        
        # 输出测试结果
        print("\n" + "=" * 50)
        print("📊 测试结果汇总:")
        print("=" * 50)
        
        for test_name, passed in results.items():
            status = "✅ 通过" if passed else "❌ 失败"
            print(f"{test_name:18}: {status}")
        
        overall_success = all(results.values())
        print(f"\n整体状态: {'✅ 全部通过' if overall_success else '❌ 存在失败'}")
        
        return results

# 独立测试脚本
async def main():
    """独立测试入口"""
    print("请先启动FastAPI服务器...")
    print("运行命令: uvicorn app.main:app --reload --port 8000")
    input("按Enter键开始测试...")
    
    tester = MCPAPITester()
    results = await tester.run_full_test()
    
    if all(results.values()):
        print("\n🎉 MCP API端点测试完成，可以进入下一步！")
        exit(0)
    else:
        print("\n❌ API端点测试中存在问题，请检查错误信息后重试")
        exit(1)

if __name__ == "__main__":
    asyncio.run(main())