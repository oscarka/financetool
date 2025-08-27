"""
DeepSeek AI API集成服务
MCP服务专用版本 - 支持MCP工具调用
"""

import httpx
import json
import logging
import os
from typing import Optional, Dict, Any, List
from datetime import datetime

logger = logging.getLogger(__name__)

class DeepSeekAIService:
    """DeepSeek AI API集成服务 - 支持MCP工具调用"""
    
    def __init__(self, mcp_tools=None):
        self.api_key = os.getenv("DEEPSEEK_API_KEY")
        self.base_url = os.getenv("DEEPSEEK_API_BASE_URL", "https://api.deepseek.com")
        self.model = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
        self.max_tokens = int(os.getenv("DEEPSEEK_MAX_TOKENS", "4000"))
        self.temperature = float(os.getenv("DEEPSEEK_TEMPERATURE", "0.7"))
        
        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        # MCP工具集成
        self.mcp_tools = mcp_tools
        if self.mcp_tools:
            self.tools = self._build_tools_definition()
            logger.info(f"✅ MCP工具集成成功，可用工具数量: {len(self.tools)}")
        else:
            self.tools = []
            logger.warning("⚠️ MCP工具未配置")
        
        # 加载数据库结构文件
        self.db_schema = self._load_database_schema()
        
        logger.info(f"DeepSeek AI服务初始化: model={self.model}, base_url={self.base_url}")
        if self.db_schema:
            logger.info("✅ 数据库结构文件加载成功")
        else:
            logger.warning("⚠️ 数据库结构文件加载失败，将使用默认提示词")
    
    def _build_tools_definition(self) -> List[Dict[str, Any]]:
        """构建MCP工具定义"""
        if not self.mcp_tools:
            return []
        
        try:
            tools = self.mcp_tools.get_tools()
            
            # 转换为DeepSeek工具格式
            deepseek_tools = []
            for tool in tools:
                deepseek_tool = {
                    "type": "function",
                    "function": {
                        "name": tool["name"],
                        "description": tool["description"],
                        "parameters": tool["parameters"]
                    }
                }
                deepseek_tools.append(deepseek_tool)
            
            logger.info(f"✅ 成功构建 {len(deepseek_tools)} 个DeepSeek工具")
            return deepseek_tools
            
        except Exception as e:
            logger.error(f"构建DeepSeek工具定义失败: {e}")
            return []
    
    def _load_database_schema(self) -> Optional[Dict[str, Any]]:
        """加载数据库结构文件"""
        try:
            schema_file = "database_schema_for_mcp.json"
            if os.path.exists(schema_file):
                with open(schema_file, 'r', encoding='utf-8') as f:
                    schema = json.load(f)
                    logger.info(f"数据库结构文件加载成功: {schema_file}")
                    return schema
            else:
                logger.warning(f"数据库结构文件不存在: {schema_file}")
                return None
        except Exception as e:
            logger.error(f"加载数据库结构文件失败: {e}")
            return None
    
    def _validate_config(self) -> bool:
        """验证API配置是否完整"""
        logger.info(f"验证DeepSeek配置: api_key={'*' * 10 if self.api_key else '未设置'}, base_url={self.base_url}, model={self.model}")
        
        if not self.api_key:
            logger.error("DeepSeek API Key未配置，请检查环境变量 DEEPSEEK_API_KEY")
            return False
            
        if not self.base_url:
            logger.error("DeepSeek API Base URL未配置，请检查环境变量 DEEPSEEK_API_BASE_URL")
            return False
            
        if not self.model:
            logger.error("DeepSeek Model未配置，请检查环境变量 DEEPSEEK_MODEL")
            return False
            
        logger.info("✅ DeepSeek配置验证通过")
        return True
    
    def _build_system_prompt(self) -> str:
        """构建系统提示词，集成MCP Resources和Prompts"""
        prompt_parts = []
        
        # 基础角色定义
        prompt_parts.append("""你是一个专业的财务数据分析师，擅长使用数据库工具分析财务数据。
        
## 工作流程
1. 首先分析用户问题，理解分析需求
2. 使用可用的工具获取必要信息（如数据库schema、示例查询等）
3. 基于获取的信息生成优化的SQL查询
4. 执行查询并分析结果
5. 提供专业的财务分析见解""")
        
        # 集成MCP Resources
        if self.mcp_tools:
            try:
                resources = self.mcp_tools.get_resources()
                prompts = self.mcp_tools.get_prompts()
                
                # Schema总览
                if "db://schema/overview.md" in resources:
                    prompt_parts.append(f"""
## 数据库Schema总览
{resources["db://schema/overview.md"]}""")
                
                # SQL编写规范
                if "sql_style_guide" in prompts:
                    prompt_parts.append(f"""
## SQL编写规范
{prompts["sql_style_guide"]}""")
                
                # 财务分析指南
                if "financial_analysis_guide" in prompts:
                    prompt_parts.append(f"""
## 财务分析指南
{prompts["financial_analysis_guide"]}""")
                
                # 示例查询
                if "db://examples/queries.sql" in resources:
                    prompt_parts.append(f"""
## 示例查询参考
{resources["db://examples/queries.sql"]}""")
                
                # 分析模式
                if "db://examples/analysis_patterns.md" in resources:
                    prompt_parts.append(f"""
## 分析模式指南
{resources["db://examples/analysis_patterns.md"]}""")
                
            except Exception as e:
                logger.error(f"构建系统提示词时获取MCP内容失败: {e}")
        
        # 可用工具说明
        if self.tools:
            prompt_parts.append(f"""
## 可用工具
你有以下工具可以使用，请根据需要使用：

{json.dumps(self.tools, ensure_ascii=False, indent=2)}

## ⚠️ 重要：PostgreSQL语法规则
生成SQL时必须严格遵循PostgreSQL语法规则！
- 使用GROUP BY时，避免在SELECT中使用窗口函数OVER()
- 优先使用子查询结构来分离聚合和窗口计算
- 确保所有非聚合字段都在GROUP BY中，或使用聚合函数包装
- 使用CTE (WITH语句) 来组织复杂查询
- 复杂计算使用子查询或CTE结构

## 重要原则
1. **优先使用工具获取信息**：在生成SQL前，先使用相关工具了解数据库结构和最佳实践
2. **遵循SQL规范**：严格按照SQL编写规范生成查询
3. **应用分析模式**：使用标准的财务分析模式进行分析
4. **安全第一**：确保生成的SQL安全，避免危险操作
5. **性能优化**：考虑查询性能，使用合适的索引和优化技巧
6. **PostgreSQL兼容性**：严格遵循PostgreSQL语法规则，避免GROUP BY和窗口函数冲突""")
        
        return "\n".join(prompt_parts)
    
    async def analyze_with_tools(self, question: str) -> Dict[str, Any]:
        """使用MCP工具分析问题"""
        try:
            if not self._validate_config():
                return {"error": "DeepSeek配置验证失败"}
            
            logger.info(f"🔍 DeepSeek AI开始分析问题: {question}")
            
            # 构建系统提示词
            system_prompt = self._build_system_prompt()
            
            # 构建消息
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": question}
            ]
            
            # 构建请求体
            request_data = {
                "model": self.model,
                "messages": messages,
                "max_tokens": self.max_tokens,
                "temperature": self.temperature
            }
            
            # 如果有工具，添加到请求中
            if self.tools:
                request_data["tools"] = self.tools
                request_data["tool_choice"] = "auto"
                logger.info(f"🔧 启用MCP工具，可用工具数量: {len(self.tools)}")
            
            # 发送API请求
            response = await self._send_request(request_data)
            
            if response:
                # 处理工具调用结果
                return await self._process_tool_calls(response, question)
            else:
                return {"error": "DeepSeek API请求失败"}
                
        except Exception as e:
            logger.error(f"DeepSeek AI分析失败: {e}")
            return {"error": f"AI分析失败: {str(e)}"}
    
    async def _process_tool_calls(self, response: Dict[str, Any], original_question: str) -> Dict[str, Any]:
        """处理工具调用结果"""
        try:
            # 检查是否有工具调用
            if "choices" in response and response["choices"]:
                choice = response["choices"][0]
                
                # 检查是否有工具调用
                if "message" in choice and "tool_calls" in choice["message"]:
                    tool_calls = choice["message"]["tool_calls"]
                    logger.info(f"🔧 DeepSeek AI调用了 {len(tool_calls)} 个工具")
                    
                    # 执行工具调用
                    tool_results = []
                    for tool_call in tool_calls:
                        tool_name = tool_call["function"]["name"]
                        tool_args = json.loads(tool_call["function"]["arguments"])
                        
                        logger.info(f"🔧 执行工具: {tool_name}")
                        result = await self._execute_tool(tool_name, tool_args)
                        tool_results.append({
                            "tool_name": tool_name,
                            "result": result
                        })
                    
                    # 基于工具结果生成最终SQL
                    final_sql = await self._generate_final_sql(original_question, tool_results)
                    
                    if final_sql:
                        return {
                            "sql": final_sql,
                            "tool_calls": tool_results,
                            "method": "deepseek_ai_with_tools"
                        }
                    else:
                        return {"error": "无法生成最终SQL"}
                
                # 如果没有工具调用，检查是否有直接回答
                elif "message" in choice and "content" in choice["message"]:
                    content = choice["message"]["content"]
                    logger.info(f"📝 DeepSeek AI直接回答: {content[:100]}...")
                    
                    # 尝试从回答中提取SQL
                    extracted_sql = self._extract_sql_from_content(content)
                    if extracted_sql:
                        return {
                            "sql": extracted_sql,
                            "ai_response": content,
                            "method": "deepseek_ai"
                        }
                    else:
                        return {"error": "AI回答中未找到有效SQL"}
            
            return {"error": "DeepSeek AI响应格式异常"}
            
        except Exception as e:
            logger.error(f"处理工具调用结果失败: {e}")
            return {"error": f"工具调用处理失败: {str(e)}"}
    
    async def _execute_tool(self, tool_name: str, tool_args: Dict[str, Any]) -> Any:
        """执行MCP工具"""
        if not self.mcp_tools:
            return {"error": "MCP工具未配置"}
        
        try:
            logger.info(f"🔧 执行MCP工具: {tool_name}, 参数: {tool_args}")
            result = self.mcp_tools.execute_tool(tool_name, tool_args)
            logger.info(f"✅ 工具执行成功: {tool_name}")
            return result
        except Exception as e:
            logger.error(f"❌ 工具执行失败: {tool_name}, 错误: {e}")
            return {"error": f"工具执行失败: {str(e)}"}
    
    async def _generate_final_sql(self, question: str, tool_results: List[Dict[str, Any]]) -> Optional[str]:
        """基于工具结果生成最终SQL"""
        try:
            # 构建包含工具结果的提示词
            prompt = f"""基于以下信息，为问题生成优化的SQL查询：

问题: {question}

工具执行结果:
{json.dumps(tool_results, ensure_ascii=False, indent=2)}

请生成一个安全、高效的SQL查询，遵循SQL编写规范。"""
            
            # 发送请求生成SQL
            messages = [
                {"role": "system", "content": "你是一个SQL专家，请根据提供的信息生成优化的SQL查询。"},
                {"role": "user", "content": prompt}
            ]
            
            request_data = {
                "model": self.model,
                "messages": messages,
                "max_tokens": 1000,
                "temperature": 0.3
            }
            
            response = await self._send_request(request_data)
            
            if response and "choices" in response and response["choices"]:
                choice = response["choices"][0]
                if "message" in choice and "content" in choice["message"]:
                    content = choice["message"]["content"]
                    sql = self._extract_sql_from_content(content)
                    if sql:
                        logger.info(f"✅ 基于工具结果生成SQL成功")
                        return sql
            
            return None
            
        except Exception as e:
            logger.error(f"生成最终SQL失败: {e}")
            return None
    
    def _extract_sql_from_content(self, content: str) -> Optional[str]:
        """从AI回答中提取SQL"""
        try:
            # 尝试提取SQL代码块
            if "```sql" in content and "```" in content:
                start = content.find("```sql") + 6
                end = content.find("```", start)
                if end > start:
                    sql = content[start:end].strip()
                    logger.info(f"🔍 从代码块提取SQL: {sql[:100]}...")
                    return sql
            
            # 尝试提取SQL语句
            sql_keywords = ["SELECT", "WITH", "INSERT", "UPDATE", "DELETE"]
            for keyword in sql_keywords:
                if keyword in content.upper():
                    # 找到SQL开始位置
                    start = content.upper().find(keyword)
                    # 尝试找到SQL结束位置（分号或换行）
                    end = content.find(";", start)
                    if end == -1:
                        end = content.find("\n", start)
                    if end == -1:
                        end = len(content)
                    
                    sql = content[start:end].strip()
                    if len(sql) > 10:  # 确保SQL有足够长度
                        logger.info(f"🔍 从内容提取SQL: {sql[:100]}...")
                        return sql
            
            return None
            
        except Exception as e:
            logger.error(f"提取SQL失败: {e}")
            return None

    async def _send_request(self, request_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """发送DeepSeek API请求"""
        try:
            logger.info(f"📤 发送DeepSeek API请求: model={self.model}, messages_count={len(request_data['messages'])}")
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.base_url}/v1/chat/completions",
                    headers=self.headers,
                    json=request_data
                )
                
                if response.status_code == 200:
                    result = response.json()
                    logger.info(f"✅ DeepSeek API请求成功: tokens_used={result.get('usage', {}).get('total_tokens', 0)}")
                    return result
                else:
                    logger.error(f"❌ DeepSeek API请求失败: status={response.status_code}, response={response.text}")
                    return None
                    
        except Exception as e:
            logger.error(f"❌ DeepSeek API请求异常: {e}")
            return None
    
    async def analyze_financial_question(self, question: str) -> Optional[Dict[str, Any]]:
        """分析财务问题并生成SQL查询（兼容性方法）"""
        return await self.analyze_with_tools(question)
