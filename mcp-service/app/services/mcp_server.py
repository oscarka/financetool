"""
MCP服务器核心服务
整合AI分析和图表生成功能
"""

import logging
import json
import os
from typing import Dict, List, Any, Optional
from datetime import datetime
import psycopg2
from psycopg2.extras import RealDictCursor

from .ai_service import DeepSeekAIService
from .claude_ai_service import ClaudeAIService
from .chart_service import ChartConfigGenerator
from .mcp_tools import MCPTools

logger = logging.getLogger(__name__)

class MCPServer:
    """MCP服务器核心服务"""
    
    def __init__(self, ai_service: DeepSeekAIService, chart_generator: ChartConfigGenerator):
        self.ai_service = ai_service
        self.chart_generator = chart_generator
        
        # 数据库连接配置
        self.db_config = {
            'host': os.getenv('DB_HOST', 'localhost'),
            'port': int(os.getenv('DB_PORT', '5432')),
            'database': os.getenv('DB_NAME', 'financetool_test'),
            'user': os.getenv('DB_USER', 'financetool_user'),
            'password': os.getenv('DB_PASSWORD', 'financetool_pass')
        }
        
        # 初始化MCP工具
        self.mcp_tools = MCPTools(self.db_config)
        
        # 初始化Claude AI服务（仅在API密钥配置时）
        self.claude_ai = None
        if os.getenv("CLAUDE_API_KEY"):
            self.claude_ai = ClaudeAIService(self.mcp_tools)
        
        # 打印数据库配置信息（调试用）
        logger.info(f"数据库配置: host={self.db_config['host']}, port={self.db_config['port']}, database={self.db_config['database']}, user={self.db_config['user']}")
        
        # 模拟数据（用于测试）
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
                    SELECT platform, SUM(COALESCE(balance_cny, 0)) as total_value, COUNT(*) as asset_count
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
                    SELECT asset_type, SUM(COALESCE(balance_cny, 0)) as total_value, COUNT(*) as asset_count
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
    
    async def execute_sql(self, sql: str, max_rows: int = 1000) -> Dict[str, Any]:
        """执行SQL查询"""
        start_time = datetime.now()
        
        try:
            # 尝试连接数据库执行查询
            data = await self._execute_database_query(sql, max_rows)
            
            if data is not None:
                execution_time = (datetime.now() - start_time).total_seconds()
                return {
                    "success": True,
                    "sql": sql,
                    "data": data,
                    "execution_time": execution_time,
                    "row_count": len(data),
                    "method": "database"
                }
        
        except Exception as e:
            logger.warning(f"数据库查询失败，使用模拟数据: {e}")
        
        # 如果数据库查询失败，使用模拟数据
        try:
            mock_data = self._get_mock_data_for_sql(sql)
            execution_time = (datetime.now() - start_time).total_seconds()
            
            return {
                "success": True,
                "sql": sql,
                "data": mock_data,
                "execution_time": execution_time,
                "row_count": len(mock_data),
                "method": "mock"
            }
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            logger.error(f"SQL执行异常: {e}")
            return {
                "success": False,
                "sql": sql,
                "error": str(e),
                "execution_time": execution_time,
                "method": "error"
            }
    
    async def natural_language_query(self, question: str, context: Dict[str, Any] = None, max_rows: int = 1000, ai_service: str = "auto") -> Dict[str, Any]:
        """自然语言查询处理"""
        start_time = datetime.now()
        
        # 自动选择AI服务
        if ai_service == "auto":
            # 优先使用Claude（如果配置了API key）
            if self.claude_ai.api_key:
                ai_service = "claude"
            else:
                ai_service = "deepseek"
        
        try:
            if ai_service == "claude":
                # 使用Claude AI分析问题
                if not self.claude_ai.api_key:
                    logger.warning("Claude API Key未配置，回退到DeepSeek")
                    ai_service = "deepseek"
                else:
                    logger.info(f"使用Claude AI分析问题: {question}")
                    
                    ai_analysis = await self.claude_ai.analyze_with_tools(question)
                    
                    if ai_analysis and ai_analysis.get('sql'):
                        # Claude AI成功生成SQL，直接执行
                        generated_sql = ai_analysis['sql']
                        logger.info(f"Claude AI生成的SQL: {generated_sql}")
                        
                        # 执行生成的SQL
                        sql_result = await self.execute_sql(generated_sql, max_rows)
                        
                        # 如果SQL执行成功，添加AI分析信息
                        if sql_result.get('success'):
                            sql_result['ai_analysis'] = ai_analysis
                            sql_result['method'] = "claude_ai"
                            logger.info("✅ Claude AI调用成功，使用AI生成的SQL")
                        
                        return sql_result
                    else:
                        logger.warning(f"Claude AI未返回有效SQL: {ai_analysis}")
            
            if ai_service == "deepseek":
                # 使用DeepSeek AI分析问题
                logger.info(f"使用DeepSeek AI分析问题: {question}")
                
                ai_analysis = await self.ai_service.analyze_financial_question(question)
                
                if ai_analysis and ai_analysis.get('sql'):
                    # DeepSeek AI成功生成SQL，直接执行
                    generated_sql = ai_analysis['sql']
                    logger.info(f"DeepSeek AI生成的SQL: {generated_sql}")
                    
                    # 执行生成的SQL
                    sql_result = await self.execute_sql(generated_sql, max_rows)
                    
                    # 如果SQL执行成功，添加AI分析信息
                    if sql_result.get('success'):
                        sql_result['ai_analysis'] = ai_analysis
                        sql_result['method'] = "deepseek_ai"
                        logger.info("✅ DeepSeek AI调用成功，使用AI生成的SQL")
                    
                    return sql_result
                else:
                    logger.warning(f"DeepSeek AI未返回有效SQL: {ai_analysis}")
        
        except Exception as e:
            logger.error(f"AI分析失败: {e}")
        
        # 2. 如果AI失败，使用模板匹配
        try:
            template_result = self._match_query_template(question)
            if template_result:
                logger.info(f"使用模板匹配: {template_result['description']}")
                return await self.execute_sql(template_result["sql"], max_rows)
        except Exception as e:
            logger.error(f"模板匹配失败: {e}")
        
        # 3. 最后返回通用模拟数据
        try:
            execution_time = (datetime.now() - start_time).total_seconds()
            return {
                "success": True,
                "sql": "SELECT * FROM asset_snapshot LIMIT 10",
                "data": self.mock_data["asset_snapshot"][:10],
                "execution_time": execution_time,
                "row_count": 10,
                "method": "fallback"
            }
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            return {
                "success": False,
                "error": str(e),
                "execution_time": execution_time,
                "method": "error"
            }
    
    async def get_database_schema(self, tables: List[str] = None) -> Dict[str, Any]:
        """获取数据库Schema信息"""
        try:
            if not tables:
                tables = ["asset_snapshot", "user_operations", "asset_positions"]
            
            # 尝试从数据库获取Schema
            schema = await self._get_database_schema_info(tables)
            if schema:
                return schema
        
        except Exception as e:
            logger.warning(f"数据库Schema查询失败: {e}")
        
        # 返回默认Schema
        return {
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
    
    async def generate_chart_config(self, question: str, data: List[Dict[str, Any]], chart_type: str = "auto") -> Dict[str, Any]:
        """生成图表配置"""
        try:
            if chart_type == "auto":
                chart_config = self.chart_generator.generate_config(data, question)
            else:
                # 强制指定图表类型
                chart_config = self.chart_generator.generate_config(data, question)
                chart_config.chart_type = chart_type
            
            return {
                "success": True,
                "chart_config": chart_config.to_dict(),
                "question": question,
                "data_points": len(data)
            }
            
        except Exception as e:
            logger.error(f"图表配置生成失败: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _execute_database_query(self, sql: str, max_rows: int) -> Optional[List[Dict[str, Any]]]:
        """执行数据库查询"""
        try:
            # 检查是否使用模拟模式
            if os.getenv('USE_MOCK_DATA', 'false').lower() == 'true':
                return None
            
            conn = psycopg2.connect(**self.db_config)
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            # 清理SQL语句：移除末尾分号，确保语法正确
            clean_sql = sql.strip().rstrip(';')
            
            # 限制结果行数
            if "LIMIT" not in clean_sql.upper():
                clean_sql = f"{clean_sql} LIMIT {max_rows}"
            
            cursor.execute(clean_sql)
            results = cursor.fetchall()
            
            # 转换为字典列表
            data = [dict(row) for row in results]
            
            cursor.close()
            conn.close()
            
            return data
            
        except Exception as e:
            logger.error(f"数据库查询失败: {e}")
            logger.error(f"数据库配置: {self.db_config}")
            logger.error(f"原始SQL语句: {sql}")
            logger.error(f"清理后SQL语句: {clean_sql if 'clean_sql' in locals() else 'N/A'}")
            return None
    
    async def _get_database_schema_info(self, tables: List[str]) -> Optional[Dict[str, Any]]:
        """获取数据库Schema信息"""
        try:
            if os.getenv('USE_MOCK_DATA', 'false').lower() == 'true':
                return None
            
            conn = psycopg2.connect(**self.db_config)
            cursor = conn.cursor()
            
            schema_info = {}
            
            for table in tables:
                # 获取表结构
                cursor.execute("""
                    SELECT column_name, data_type, is_nullable, column_default
                    FROM information_schema.columns 
                    WHERE table_name = %s 
                    ORDER BY ordinal_position
                """, (table,))
                
                columns = cursor.fetchall()
                schema_info[table] = {
                    "columns": {col[0]: {"type": col[1], "nullable": col[2], "default": col[3]} for col in columns}
                }
            
            cursor.close()
            conn.close()
            
            return {"tables": schema_info}
            
        except Exception as e:
            logger.error(f"获取数据库Schema失败: {e}")
            return None
    
    def _match_query_template(self, question: str) -> Optional[Dict[str, Any]]:
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
        
        # 排名关键词
        if any(word in question_lower for word in ['排名', '排行', '最多', '最少', 'top']):
            return self.query_templates["top_assets"]
        
        return None
    
    def _get_mock_data_for_sql(self, sql: str) -> List[Dict[str, Any]]:
        """根据SQL获取相应的模拟数据"""
        sql_lower = sql.lower()
        
        # 更智能的SQL分析
        logger.info(f"分析SQL生成模拟数据: {sql}")
        
        # 检查是否是支付宝内部的查询
        if "platform = '支付宝'" in sql or "platform='支付宝'" in sql:
            if "asset_type" in sql_lower:
                # 支付宝内部资产类型分布
                logger.info("返回支付宝内部资产类型分布数据")
                return [
                    {"asset_type": "基金", "total_balance": 158460.30, "asset_count": 2},
                    {"asset_type": "股票", "total_balance": 50000.00, "asset_count": 1},
                    {"asset_type": "债券", "total_balance": 25000.00, "asset_count": 1},
                    {"asset_type": "现金", "total_balance": 15000.00, "asset_count": 1}
                ]
            elif "date" in sql_lower or "snapshot_time" in sql_lower:
                # 支付宝资产变化趋势
                logger.info("返回支付宝资产变化趋势数据")
                return [
                    {"date": "2024-01-01", "daily_total": 150000.00},
                    {"date": "2024-01-02", "daily_total": 151000.00},
                    {"date": "2024-01-03", "daily_total": 152500.00},
                    {"date": "2024-01-04", "daily_total": 154000.00},
                    {"date": "2024-01-05", "daily_total": 155500.00}
                ]
            else:
                # 支付宝总体数据
                logger.info("返回支付宝总体数据")
                return [
                    {"platform": "支付宝", "total_value": 158460.30, "asset_count": 5}
                ]
        
        # 检查是否是平台分布查询
        elif "platform" in sql_lower and "group by platform" in sql_lower:
            logger.info("返回各平台资产分布数据")
            return [
                {"platform": "支付宝", "total_value": 158460.30, "asset_count": 2},
                {"platform": "Wise", "total_value": 8158.23, "asset_count": 2},
                {"platform": "IBKR", "total_value": 42.03, "asset_count": 1},
                {"platform": "OKX", "total_value": 1205.67, "asset_count": 1}
            ]
        
        # 检查是否是资产类型分布查询
        elif "asset_type" in sql_lower and "group by asset_type" in sql_lower:
            logger.info("返回各资产类型分布数据")
            return [
                {"asset_type": "基金", "total_value": 158460.30, "asset_count": 2},
                {"asset_type": "外汇", "total_value": 8158.23, "asset_count": 2},
                {"asset_type": "股票", "total_value": 42.03, "asset_count": 1},
                {"asset_type": "数字货币", "total_value": 1205.67, "asset_count": 1}
            ]
        
        # 检查是否是时间趋势查询
        elif any(word in sql_lower for word in ["date_trunc", "to_char", "snapshot_time"]) and "group by" in sql_lower:
            logger.info("返回时间趋势数据")
            return [
                {"date": "2024-01-01", "total_value": 150000.00},
                {"date": "2024-01-02", "total_value": 151000.00},
                {"date": "2024-01-03", "total_value": 152500.00},
                {"date": "2024-01-04", "total_value": 154000.00},
                {"date": "2024-01-05", "total_value": 155500.00}
            ]
        
        # 默认返回原始数据
        else:
            logger.info("返回默认模拟数据")
            return self.mock_data["asset_snapshot"]
    
    def get_available_ai_services(self) -> Dict[str, Any]:
        """获取可用的AI服务信息"""
        services = {
            "deepseek": {
                "available": bool(self.ai_service.api_key),
                "model": getattr(self.ai_service, 'model', 'unknown'),
                "description": "DeepSeek AI服务"
            }
        }
        
        # 只有在Claude服务初始化时才添加
        if self.claude_ai:
            services["claude"] = {
                "available": bool(self.claude_ai.api_key),
                "model": getattr(self.claude_ai, 'model', 'unknown'),
                "description": "Claude AI服务（支持MCP工具调用）"
            }
        
        return services
