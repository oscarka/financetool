"""MCP工具定义 - 让AI能够调用数据库工具"""

import json
import logging
from typing import Dict, Any, List, Optional
import psycopg2
from psycopg2.extras import RealDictCursor

logger = logging.getLogger(__name__)

class MCPTools:
    """MCP工具集合 - 提供数据库查询能力"""
    
    def __init__(self, db_config: Dict[str, Any]):
        self.db_config = db_config
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
                            "description": "最大返回行数，默认1000"
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
            }
        ]
    
    def get_tools(self) -> List[Dict[str, Any]]:
        """返回可用工具列表"""
        return self.tools
    
    def execute_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """执行指定的工具"""
        try:
            if tool_name == "get_table_schema":
                return self._get_table_schema(parameters["table_name"])
            elif tool_name == "list_tables":
                return self._list_tables()
            elif tool_name == "query_database":
                return self._query_database(parameters["sql"], parameters.get("max_rows", 1000))
            elif tool_name == "explore_table_data":
                return self._explore_table_data(parameters["table_name"], parameters.get("sample_size", 5))
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
    
    def _query_database(self, sql: str, max_rows: int = 1000) -> Dict[str, Any]:
        """执行SQL查询"""
        try:
            with psycopg2.connect(**self.db_config) as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                    # 添加LIMIT子句
                    if "LIMIT" not in sql.upper():
                        sql = f"{sql} LIMIT {max_rows}"
                    
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
