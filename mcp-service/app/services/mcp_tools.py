"""MCP工具定义 - 让AI能够调用数据库工具"""

import json
import logging
from typing import Dict, Any, List, Optional
import psycopg2
from psycopg2.extras import RealDictCursor
from .mcp_resources import MCPResourcesManager
from .mcp_prompts import MCPPromptsManager

logger = logging.getLogger(__name__)

class MCPTools:
    """MCP工具集合 - 提供数据库查询能力"""
    
    def __init__(self, db_config: Dict[str, Any]):
        self.db_config = db_config
        self.resources_manager = MCPResourcesManager(db_config)
        self.prompts_manager = MCPPromptsManager()
        self.tools = self._define_tools()
    
    def _define_tools(self) -> List[Dict[str, Any]]:
        """定义可用的MCP工具"""
        return [
            {
                "name": "get_table_schema",
                "description": "获取指定表的完整结构信息，包括字段名、类型、描述等",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "table_name": {
                            "type": "string",
                            "description": "要查询的表名"
                        }
                    },
                    "required": ["table_name"]
                }
            },
            {
                "name": "list_tables",
                "description": "列出数据库中所有可用的表",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },
            {
                "name": "query_database",
                "description": "执行SQL查询并返回结果",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "sql": {
                            "type": "string",
                            "description": "要执行的SQL查询语句"
                        },
                        "max_rows": {
                            "type": "integer",
                            "description": "最大返回行数，默认200"
                        }
                    },
                    "required": ["sql"]
                }
            },
            {
                "name": "explore_table_data",
                "description": "探索表的数据样本，了解数据结构和内容",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "table_name": {
                            "type": "string",
                            "description": "要探索的表名"
                        },
                        "sample_size": {
                            "type": "integer",
                            "description": "样本大小，默认5行"
                        }
                    },
                    "required": ["table_name"]
                }
            },
            {
                "name": "get_schema_overview",
                "description": "获取数据库schema总览，了解业务域和表关系",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },
            {
                "name": "get_example_queries",
                "description": "获取高质量示例查询，学习最佳实践",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },
            {
                "name": "get_analysis_patterns",
                "description": "获取财务分析模式指南，学习标准分析方法",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },
            {
                "name": "get_sql_style_guide",
                "description": "获取SQL编写规范指南，学习最佳实践",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },
            {
                "name": "get_financial_analysis_guide",
                "description": "获取财务分析专用指南，学习专业分析方法",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },
            {
                "name": "explain_sql",
                "description": "分析SQL查询的执行计划和性能",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "sql": {
                            "type": "string",
                            "description": "要分析的SQL查询语句"
                        }
                    },
                    "required": ["sql"]
                }
            },
            {
                "name": "get_postgresql_syntax_rules",
                "description": "获取PostgreSQL特定的语法规则和约束，确保生成的SQL符合PostgreSQL要求",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },
            {
                "name": "get_resources",
                "description": "获取所有可用的MCP资源",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },
            {
                "name": "get_prompts",
                "description": "获取所有可用的MCP提示和指南",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            }
        ]
    
    def get_tools(self) -> List[Dict[str, Any]]:
        """返回可用工具列表"""
        return self.tools
    
    def get_resources(self) -> Dict[str, str]:
        """返回可用的Resources"""
        return self.resources_manager.get_all_resources()
    
    def get_prompts(self) -> Dict[str, str]:
        """返回可用的Prompts"""
        return self.prompts_manager.get_all_prompts()
    
    def execute_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """执行指定的工具"""
        try:
            if tool_name == "get_table_schema":
                return self._get_table_schema(parameters["table_name"])
            elif tool_name == "list_tables":
                return self._list_tables()
            elif tool_name == "query_database":
                return self._query_database(parameters["sql"], parameters.get("max_rows", 200))
            elif tool_name == "explore_table_data":
                return self._explore_table_data(parameters["table_name"], parameters.get("sample_size", 5))
            elif tool_name == "get_schema_overview":
                return self._get_schema_overview()
            elif tool_name == "get_example_queries":
                return self._get_example_queries()
            elif tool_name == "get_analysis_patterns":
                return self._get_analysis_patterns()
            elif tool_name == "get_sql_style_guide":
                return self._get_sql_style_guide()
            elif tool_name == "get_financial_analysis_guide":
                return self._get_financial_analysis_guide()
            elif tool_name == "explain_sql":
                return self._explain_sql(parameters["sql"])
            elif tool_name == "get_postgresql_syntax_rules":
                return self._get_postgresql_syntax_rules()
            elif tool_name == "get_resources":
                return self.get_resources()
            elif tool_name == "get_prompts":
                return self.get_prompts()
            else:
                return {"error": f"未知工具: {tool_name}"}
        except Exception as e:
            logger.error(f"工具执行失败: {e}")
            return {"error": f"工具执行失败: {str(e)}"}
    
    def _get_table_schema(self, table_name: str) -> Dict[str, Any]:
        """获取表结构"""
        try:
            with psycopg2.connect(**self.db_config) as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                    # 获取字段信息
                    cursor.execute("""
                        SELECT column_name, data_type, is_nullable, column_default, 
                               character_maximum_length, numeric_precision, numeric_scale
                        FROM information_schema.columns 
                        WHERE table_name = %s 
                        ORDER BY ordinal_position
                    """, (table_name,))
                    
                    columns = cursor.fetchall()
                    
                    # 获取表描述
                    cursor.execute("""
                        SELECT obj_description(c.oid) as table_comment
                        FROM pg_class c
                        JOIN pg_namespace n ON n.oid = c.relnamespace
                        WHERE c.relname = %s AND n.nspname = 'public'
                    """, (table_name,))
                    
                    table_comment = cursor.fetchone()
                    
                    return {
                        "table_name": table_name,
                        "table_comment": table_comment["table_comment"] if table_comment else None,
                        "columns": [
                            {
                                "name": col["column_name"],
                                "type": col["data_type"],
                                "nullable": col["is_nullable"] == "YES",
                                "default": col["column_default"],
                                "max_length": col["character_maximum_length"],
                                "precision": col["numeric_precision"],
                                "scale": col["numeric_scale"]
                            }
                            for col in columns
                        ],
                        "total_columns": len(columns)
                    }
        except Exception as e:
            logger.error(f"获取表结构失败: {e}")
            return {"error": f"获取表结构失败: {str(e)}"}
    
    def _list_tables(self) -> Dict[str, Any]:
        """列出所有表"""
        try:
            with psycopg2.connect(**self.db_config) as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                    cursor.execute("""
                        SELECT table_name, 
                               (SELECT COUNT(*) FROM information_schema.columns WHERE table_name = t.table_name) as column_count
                        FROM information_schema.tables t
                        WHERE table_schema = 'public'
                        ORDER BY table_name
                    """)
                    
                    tables = cursor.fetchall()
                    
                    return {
                        "tables": [
                            {
                                "name": table["table_name"],
                                "column_count": table["column_count"]
                            }
                            for table in tables
                        ],
                        "total_tables": len(tables)
                    }
        except Exception as e:
            logger.error(f"列出表失败: {e}")
            return {"error": f"列出表失败: {str(e)}"}
    
    def _query_database(self, sql: str, max_rows: int = 200) -> Dict[str, Any]:
        """执行SQL查询"""
        try:
            # 安全检查
            if not self._security_check(sql):
                return {"error": "SQL安全检查失败", "success": False}
            
            with psycopg2.connect(**self.db_config) as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                    # 强制添加LIMIT子句
                    if "LIMIT" not in sql.upper():
                        sql = f"{sql} LIMIT {max_rows}"
                    else:
                        # 检查LIMIT值是否过大
                        import re
                        limit_match = re.search(r'LIMIT\s+(\d+)', sql.upper())
                        if limit_match:
                            limit_value = int(limit_match.group(1))
                            if limit_value > max_rows:
                                # 替换过大的LIMIT值
                                sql = re.sub(r'LIMIT\s+\d+', f'LIMIT {max_rows}', sql.upper())
                    
                    cursor.execute(sql)
                    rows = cursor.fetchall()
                    
                    # 转换为字典列表
                    result = [dict(row) for row in rows]
                    
                    return {
                        "success": True,
                        "sql": sql,
                        "data": result,
                        "row_count": len(result),
                        "max_rows": max_rows
                    }
        except Exception as e:
            logger.error(f"SQL查询失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "sql": sql
            }
    
    def _security_check(self, sql: str) -> bool:
        """SQL安全检查"""
        sql_upper = sql.upper().strip()
        
        # 检查危险关键字
        dangerous_keywords = [
            'DROP', 'DELETE', 'TRUNCATE', 'ALTER', 'CREATE', 'GRANT', 'REVOKE',
            'EXECUTE', 'EXEC', 'xp_', 'sp_', '--', '/*', '*/', 'INSERT', 'UPDATE'
        ]
        
        for keyword in dangerous_keywords:
            if keyword in sql_upper:
                logger.warning(f"检测到危险SQL关键字: {keyword}")
                return False
        
        # 检查是否是多语句查询
        if ';' in sql and sql.count(';') > 1:
            logger.warning("检测到多语句查询")
            return False
        
        # 检查是否包含注释
        if '--' in sql or '/*' in sql:
            logger.warning("检测到SQL注释")
            return False
        
        # 检查是否包含存储过程调用
        if 'CALL' in sql_upper or 'EXEC' in sql_upper:
            logger.warning("检测到存储过程调用")
            return False
        
        return True
    
    def _explore_table_data(self, table_name: str, sample_size: int = 5) -> Dict[str, Any]:
        """探索表数据样本"""
        try:
            with psycopg2.connect(**self.db_config) as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                    # 获取样本数据
                    cursor.execute(f"SELECT * FROM {table_name} LIMIT {sample_size}")
                    sample_rows = cursor.fetchall()
                    
                    # 获取总行数
                    cursor.execute(f"SELECT COUNT(*) as total_count FROM {table_name}")
                    total_count = cursor.fetchone()["total_count"]
                    
                    # 获取字段信息
                    cursor.execute("""
                        SELECT column_name, data_type
                        FROM information_schema.columns 
                        WHERE table_name = %s 
                        ORDER BY ordinal_position
                    """, (table_name,))
                    
                    columns = cursor.fetchall()
                    
                    return {
                        "table_name": table_name,
                        "total_rows": total_count,
                        "sample_size": sample_size,
                        "columns": [{"name": col["column_name"], "type": col["data_type"]} for col in columns],
                        "sample_data": [dict(row) for row in sample_rows]
                    }
        except Exception as e:
            logger.error(f"探索表数据失败: {e}")
            return {"error": f"探索表数据失败: {str(e)}"}
    
    def _get_schema_overview(self) -> Dict[str, Any]:
        """获取schema总览"""
        try:
            overview = self.resources_manager.get_resource("db://schema/overview.md")
            return {
                "success": True,
                "resource_type": "schema_overview",
                "content": overview,
                "format": "markdown"
            }
        except Exception as e:
            logger.error(f"获取schema总览失败: {e}")
            return {"error": f"获取schema总览失败: {str(e)}"}
    
    def _get_example_queries(self) -> Dict[str, Any]:
        """获取示例查询"""
        try:
            queries = self.resources_manager.get_resource("db://examples/queries.sql")
            return {
                "success": True,
                "resource_type": "example_queries",
                "content": queries,
                "format": "sql"
            }
        except Exception as e:
            logger.error(f"获取示例查询失败: {e}")
            return {"error": f"获取示例查询失败: {str(e)}"}
    
    def _get_analysis_patterns(self) -> Dict[str, Any]:
        """获取分析模式指南"""
        try:
            patterns = self.resources_manager.get_resource("db://examples/analysis_patterns.md")
            return {
                "success": True,
                "resource_type": "analysis_patterns",
                "content": patterns,
                "format": "markdown"
            }
        except Exception as e:
            logger.error(f"获取分析模式指南失败: {e}")
            return {"error": f"获取分析模式指南失败: {str(e)}"}
    
    def _get_sql_style_guide(self) -> Dict[str, Any]:
        """获取SQL编写规范指南"""
        try:
            guide = self.prompts_manager.get_prompt("sql_style_guide")
            return {
                "success": True,
                "prompt_type": "sql_style_guide",
                "content": guide,
                "format": "markdown"
            }
        except Exception as e:
            logger.error(f"获取SQL编写规范指南失败: {e}")
            return {"error": f"获取SQL编写规范指南失败: {str(e)}"}
    
    def _get_financial_analysis_guide(self) -> Dict[str, Any]:
        """获取财务分析专用指南"""
        try:
            guide = self.prompts_manager.get_prompt("financial_analysis_guide")
            return {
                "success": True,
                "prompt_type": "financial_analysis_guide",
                "content": guide,
                "format": "markdown"
            }
        except Exception as e:
            logger.error(f"获取财务分析专用指南失败: {e}")
            return {"error": f"获取财务分析专用指南失败: {str(e)}"}
    
    def _explain_sql(self, sql: str) -> dict:
        """分析SQL查询的执行计划和性能"""
        try:
            # 清理SQL语句
            clean_sql = self._clean_sql(sql)
            
            # 执行EXPLAIN
            explain_sql = f"EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON) {clean_sql}"
            
            with self.get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(explain_sql)
                    result = cursor.fetchone()
                    
                    if result and result[0]:
                        plan = result[0]
                        return {
                            "success": True,
                            "explain_plan": plan,
                            "sql": clean_sql,
                            "message": "SQL执行计划分析完成"
                        }
                    else:
                        return {
                            "success": False,
                            "error": "无法获取执行计划"
                        }
                        
        except Exception as e:
            return {
                "success": False,
                "error": f"SQL分析失败: {str(e)}",
                "sql": sql
            }

    def _get_postgresql_syntax_rules(self) -> dict:
        """获取PostgreSQL特定的语法规则和约束"""
        try:
            rules = self.prompts_manager.get_prompt("postgresql_syntax_rules")
            return {
                "success": True,
                "rules": rules,
                "message": "PostgreSQL语法规则获取成功"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"获取PostgreSQL语法规则失败: {str(e)}"
            }

    def get_resources(self) -> Dict[str, Any]:
        """获取所有可用的MCP资源"""
        try:
            return self.resources_manager.get_all_resources()
        except Exception as e:
            logger.error(f"获取MCP资源失败: {e}")
            return {"error": f"获取MCP资源失败: {str(e)}"}

    def get_prompts(self) -> Dict[str, Any]:
        """获取所有可用的MCP提示和指南"""
        try:
            return self.prompts_manager.get_all_prompts()
        except Exception as e:
            logger.error(f"获取MCP提示失败: {e}")
            return {"error": f"获取MCP提示失败: {str(e)}"}
