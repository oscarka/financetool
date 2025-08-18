#!/usr/bin/env python3
"""
简单的MCP服务器实现
用于测试MCP客户端连接
"""

import asyncio
import json
import logging
import psycopg2
from aiohttp import web
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SimpleMCPServer:
    def __init__(self, db_url: str):
        self.db_url = db_url
        self.app = web.Application()
        self.setup_routes()
    
    def setup_routes(self):
        """设置路由"""
        self.app.router.add_get('/health', self.health_check)
        self.app.router.add_post('/query', self.execute_sql)
        self.app.router.add_post('/nl-query', self.natural_language_query)
    
    async def health_check(self, request):
        """健康检查端点"""
        try:
            # 测试数据库连接
            conn = psycopg2.connect(self.db_url)
            conn.close()
            
            return web.json_response({
                "status": "healthy",
                "database": "connected",
                "timestamp": datetime.now().isoformat()
            })
        except Exception as e:
            logger.error(f"健康检查失败: {e}")
            return web.json_response({
                "status": "unhealthy",
                "database": "disconnected",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }, status=500)
    
    async def execute_sql(self, request):
        """执行SQL查询"""
        try:
            data = await request.json()
            sql = data.get("params", {}).get("sql")
            max_rows = data.get("params", {}).get("max_rows", 100)
            
            if not sql:
                return web.json_response({
                    "error": "Missing SQL query"
                }, status=400)
            
            logger.info(f"执行SQL: {sql}")
            
            # 执行SQL查询
            conn = psycopg2.connect(self.db_url)
            cur = conn.cursor()
            
            cur.execute(sql)
            
            # 获取列名
            columns = [desc[0] for desc in cur.description]
            
            # 获取数据
            rows = cur.fetchall()
            
            # 转换为字典格式
            result_data = []
            for row in rows[:max_rows]:
                row_dict = {}
                for i, value in enumerate(row):
                    if isinstance(value, datetime):
                        row_dict[columns[i]] = value.isoformat()
                    elif hasattr(value, '__float__'):  # 处理Decimal等数值类型
                        row_dict[columns[i]] = float(value)
                    else:
                        row_dict[columns[i]] = value
                result_data.append(row_dict)
            
            cur.close()
            conn.close()
            
            return web.json_response({
                "success": True,
                "data": result_data,
                "row_count": len(result_data),
                "columns": columns
            })
            
        except Exception as e:
            logger.error(f"SQL执行失败: {e}")
            return web.json_response({
                "success": False,
                "error": str(e)
            }, status=500)
    
    async def natural_language_query(self, request):
        """自然语言查询处理"""
        try:
            data = await request.json()
            question = data.get("params", {}).get("question")
            
            if not question:
                return web.json_response({
                    "error": "Missing question"
                }, status=400)
            
            logger.info(f"自然语言查询: {question}")
            
            # 简单的关键词匹配
            sql = self._generate_sql_from_question(question)
            
            return web.json_response({
                "success": True,
                "sql": sql,
                "question": question
            })
            
        except Exception as e:
            logger.error(f"自然语言查询失败: {e}")
            return web.json_response({
                "success": False,
                "error": str(e)
            }, status=500)
    
    def _generate_sql_from_question(self, question: str) -> str:
        """根据问题生成SQL"""
        question_lower = question.lower()
        
        if any(word in question_lower for word in ['平台', '分布', 'platform']):
            return """
                SELECT platform, SUM(balance_cny) as total_value, COUNT(*) as asset_count
                FROM asset_snapshot 
                WHERE snapshot_time = (SELECT MAX(snapshot_time) FROM asset_snapshot)
                GROUP BY platform 
                ORDER BY total_value DESC
            """
        elif any(word in question_lower for word in ['类型', '种类', '占比', '比例']):
            return """
                SELECT asset_type, SUM(balance_cny) as total_value, COUNT(*) as asset_count
                FROM asset_snapshot 
                WHERE snapshot_time = (SELECT MAX(snapshot_time) FROM asset_snapshot)
                GROUP BY asset_type 
                ORDER BY total_value DESC
            """
        else:
            return """
                SELECT platform, asset_type, asset_name, balance_cny, snapshot_time
                FROM asset_snapshot 
                WHERE snapshot_time = (SELECT MAX(snapshot_time) FROM asset_snapshot)
                ORDER BY balance_cny DESC 
                LIMIT 20
            """
    
    def run(self, host='localhost', port=3001):
        """启动服务器"""
        logger.info(f"启动简单MCP服务器在 {host}:{port}")
        web.run_app(self.app, host=host, port=port)

if __name__ == "__main__":
    # 数据库连接URL
    db_url = "postgresql://financetool_user:financetool_pass@localhost:5432/financetool_test"
    
    # 创建并启动服务器
    server = SimpleMCPServer(db_url)
    server.run()
