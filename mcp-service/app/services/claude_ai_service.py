"""Claude AI服务 - 支持MCP工具调用"""

import json
import logging
import httpx
import asyncio
from typing import Dict, Any, Optional, List
import os

logger = logging.getLogger(__name__)

class ClaudeAIService:
    """Claude AI服务 - 支持MCP工具调用"""
    
    def __init__(self, mcp_tools):
        self.api_key = os.getenv("CLAUDE_API_KEY")
        self.model = "claude-3-5-sonnet-20241022"
        self.max_tokens = 4000
        self.mcp_tools = mcp_tools
        self.tools = self._build_tools_definition()
        
        if not self.api_key:
            logger.warning("Claude API Key未配置")
    
    def _build_tools_definition(self) -> List[Dict[str, Any]]:
        """构建MCP工具定义"""
        tools = self.mcp_tools.get_tools()
        
        # 转换为Claude工具格式
        claude_tools = []
        for tool in tools:
            claude_tool = {
                "name": tool["name"],
                "description": tool["description"],
                "input_schema": tool["parameters"]
            }
            claude_tools.append(claude_tool)
        
        return claude_tools
    
    async def analyze_with_tools(self, question: str) -> Dict[str, Any]:
        """使用工具分析问题"""
        try:
            if not self.api_key:
                return {"error": "Claude API Key未配置"}
            
            # 构建系统提示词
            system_prompt = self._build_system_prompt()
            
            # 构建消息
            messages = [{"role": "user", "content": question}]
            
            # 构建请求体
            request_body = {
                "model": self.model,
                "max_tokens": self.max_tokens,
                "system": system_prompt,
                "messages": messages,
                "tools": self.tools
            }
            
            # 发送API请求
            response = await self._send_request(request_body)
            
            # 处理工具调用结果
            return await self._process_tool_calls(response, question)
            
        except Exception as e:
            logger.error(f"Claude AI分析失败: {e}")
            return {"error": f"AI分析失败: {str(e)}"}
    
    def _build_system_prompt(self) -> str:
        """构建系统提示词"""
        # 获取Resources和Prompts
        resources = self.mcp_tools.get_resources()
        prompts = self.mcp_tools.get_prompts()
        
        # 构建schema总览
        schema_overview = resources.get("db://schema/overview.md", "")
        
        # 构建SQL编写规范
        sql_style_guide = prompts.get("sql_style_guide", "")
        
        # 构建财务分析指南
        financial_guide = prompts.get("financial_analysis_guide", "")
        
        # 构建工具定义
        tools_definition = json.dumps(self.tools, ensure_ascii=False, indent=2)

        # 构建系统提示词
        system_prompt = f"""你是一个专业的财务数据分析AI助手，专门帮助用户分析个人财务数据。

## 数据库结构
{schema_overview}

## SQL编写规范
{sql_style_guide}

## 财务分析指南
{financial_guide}

## ⚠️ 重要：PostgreSQL语法规则
生成SQL时必须严格遵循PostgreSQL语法规则！
- 使用GROUP BY时，避免在SELECT中使用窗口函数OVER()
- 优先使用子查询结构来分离聚合和窗口计算
- 确保所有非聚合字段都在GROUP BY中，或使用聚合函数包装
- 使用CTE (WITH语句) 来组织复杂查询
- 复杂计算使用子查询或CTE结构

## 工作流程
1. 理解用户需求
2. 分析数据库结构
3. 设计查询逻辑
4. 生成符合PostgreSQL规范的SQL
5. 验证SQL语法正确性

## 重要原则
- 始终使用COALESCE处理NULL值
- 避免SELECT *，明确指定需要的字段
- 使用LIMIT限制返回行数
- 优先使用聚合函数而非窗口函数在GROUP BY查询中
- 复杂计算使用子查询或CTE结构

## 可用工具
你可以使用以下工具来完成任务：
{tools_definition}

请根据用户的问题，使用合适的工具进行分析，并生成符合PostgreSQL规范的SQL查询。"""
        return system_prompt
    
    async def _send_request(self, request_body: Dict[str, Any]) -> Dict[str, Any]:
        """发送API请求"""
        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                "https://api.anthropic.com/v1/messages",
                headers=headers,
                json=request_body
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Claude API请求失败: {response.status_code} - {response.text}")
                return {"error": f"API请求失败: {response.status_code}"}
    
    async def _process_tool_calls(self, result: Dict[str, Any], original_question: str) -> Dict[str, Any]:
        """处理工具调用结果"""
        try:
            # 检查是否有工具调用
            if "content" in result and isinstance(result["content"], list):
                for content_item in result["content"]:
                    if content_item.get("type") == "tool_use":
                        tool_call = content_item
                        
                        # 执行工具调用
                        tool_name = tool_call["name"]
                        tool_args = tool_call["input"]
                        
                        logger.info(f"🔧 执行工具调用: {tool_name} with args: {tool_args}")
                        
                        # 调用MCP工具
                        tool_result = self.mcp_tools.execute_tool(tool_name, tool_args)
                        
                        # 将工具结果返回给Claude进行进一步分析
                        return await self._continue_analysis_with_tool_result(
                            original_question, tool_result, tool_name
                        )
            
            # 如果没有工具调用，直接返回结果
            return {"response": result.get("content", "无响应")}
            
        except Exception as e:
            logger.error(f"处理工具调用失败: {e}")
            return {"error": f"工具调用处理失败: {str(e)}"}
    
    async def _continue_analysis_with_tool_result(
        self, 
        original_question: str, 
        tool_result: Dict[str, Any],
        tool_name: str
    ) -> Dict[str, Any]:
        """使用工具结果继续分析"""
        try:
            # 构建包含工具结果的提示词
            follow_up_prompt = f"""
基于以下工具执行结果，请继续分析用户问题："{original_question}"

工具名称：{tool_name}
工具结果：{json.dumps(tool_result, ensure_ascii=False, indent=2)}

请根据工具结果，生成最终的SQL查询并执行，或者提供进一步的分析建议。
"""
            
            # 构建消息
            messages = [
                {"role": "user", "content": original_question},
                {"role": "assistant", "content": f"我执行了工具 {tool_name}，结果如下：{json.dumps(tool_result, ensure_ascii=False)}"},
                {"role": "user", "content": follow_up_prompt}
            ]
            
            # 构建请求体
            request_body = {
                "model": self.model,
                "max_tokens": self.max_tokens,
                "system": self._build_system_prompt(),
                "messages": messages,
                "tools": self.tools
            }
            
            # 发送后续请求
            response = await self._send_request(request_body)
            
            # 处理最终结果
            return self._extract_final_result(response)
            
        except Exception as e:
            logger.error(f"继续分析失败: {e}")
            return {"error": f"继续分析失败: {str(e)}"}
    
    def _extract_final_result(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """提取最终结果"""
        try:
            if "content" in response and isinstance(response["content"], list):
                for content_item in response["content"]:
                    if content_item.get("type") == "text":
                        return {
                            "response": content_item["text"],
                            "method": "claude_ai_with_tools"
                        }
            
            return {"response": "无法提取响应内容", "method": "claude_ai_with_tools"}
            
        except Exception as e:
            logger.error(f"提取最终结果失败: {e}")
            return {"error": f"提取最终结果失败: {str(e)}"}
    
    async def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        try:
            if not self.api_key:
                return {"status": "unhealthy", "error": "API Key未配置"}
            
            # 简单的健康检查
            test_result = await self.analyze_with_tools("测试连接")
            
            if "error" in test_result:
                return {"status": "unhealthy", "error": test_result["error"]}
            else:
                return {"status": "healthy", "model": self.model}
                
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}
