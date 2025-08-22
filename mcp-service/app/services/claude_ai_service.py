"""Claude AI服务 - 支持MCP工具调用"""

import os
import json
import logging
from typing import Dict, Any, Optional, List
import httpx
from .mcp_tools import MCPTools

logger = logging.getLogger(__name__)

class ClaudeAIService:
    """Claude AI服务 - 支持MCP工具调用"""
    
    def __init__(self, mcp_tools: MCPTools):
        self.api_key = os.getenv("CLAUDE_API_KEY")
        self.base_url = os.getenv("CLAUDE_API_BASE_URL", "https://api.anthropic.com")
        self.model = os.getenv("CLAUDE_MODEL", "claude-3-5-sonnet-20241022")
        self.max_tokens = int(os.getenv("CLAUDE_MAX_TOKENS", "4000"))
        
        self.mcp_tools = mcp_tools
        self.tools = mcp_tools.get_tools()
        
        self.headers = {
            'x-api-key': self.api_key,
            'anthropic-version': '2023-06-01',
            'Content-Type': 'application/json'
        }
        
        logger.info(f"Claude AI服务初始化: model={self.model}, base_url={self.base_url}")
        logger.info(f"可用工具数量: {len(self.tools)}")
    
    def analyze_with_tools(self, question: str) -> Dict[str, Any]:
        """使用工具分析问题"""
        try:
            # 构建系统提示词
            system_prompt = self._build_system_prompt()
            
            # 构建消息
            messages = [
                {
                    "role": "user",
                    "content": question
                }
            ]
            
            # 构建请求体
            request_body = {
                "model": self.model,
                "max_tokens": self.max_tokens,
                "system": system_prompt,
                "messages": messages,
                "tools": self.tools
            }
            
            logger.info(f"发送Claude API请求: model={self.model}, tools_count={len(self.tools)}")
            
            # 发送请求
            with httpx.Client() as client:
                response = client.post(
                    f"{self.base_url}/v1/messages",
                    headers=self.headers,
                    json=request_body,
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    result = response.json()
                    logger.info(f"Claude API请求成功: tokens_used={result.get('usage', {}).get('input_tokens', 0)}")
                    
                    # 处理工具调用
                    return self._process_tool_calls(result, question)
                else:
                    logger.error(f"Claude API请求失败: {response.status_code} - {response.text}")
                    return {"error": f"API请求失败: {response.status_code}"}
                    
        except Exception as e:
            logger.error(f"Claude AI分析失败: {e}")
            return {"error": f"AI分析失败: {str(e)}"}
    
    def _build_system_prompt(self) -> str:
        """构建系统提示词"""
        return f"""你是一个专业的财务数据分析师，擅长使用数据库工具分析财务数据。

## 可用工具
你有以下工具可以使用：

{json.dumps(self.tools, ensure_ascii=False, indent=2)}

## 工作流程
1. 首先了解用户需求
2. 使用 list_tables 查看可用的表
3. 使用 get_table_schema 了解表结构
4. 使用 explore_table_data 查看数据样本
5. 最后使用 query_database 执行查询

## 重要原则
- 总是先了解数据结构，再生成查询
- 使用正确的字段名和表名
- 生成可执行的SQL语句
- 返回清晰的解释和图表建议

## 图表类型建议
- bar: 柱状图，适合比较不同类别的数值
- pie: 饼图，适合显示占比关系
- line: 折线图，适合显示趋势变化
- table: 表格，适合显示详细数据

请根据用户问题，使用合适的工具进行分析。"""
    
    def _process_tool_calls(self, api_response: Dict[str, Any], original_question: str) -> Dict[str, Any]:
        """处理工具调用"""
        try:
            content = api_response.get("content", [])
            
            # 查找工具调用
            tool_calls = []
            for item in content:
                if item.get("type") == "tool_use":
                    tool_calls.append(item)
            
            if not tool_calls:
                # 没有工具调用，直接返回AI的回答
                return self._extract_final_answer(api_response)
            
            # 执行工具调用
            tool_results = []
            for tool_call in tool_calls:
                tool_name = tool_call["name"]
                tool_input = tool_call["input"]
                
                logger.info(f"执行工具: {tool_name}, 参数: {tool_input}")
                
                # 执行工具
                result = self.mcp_tools.execute_tool(tool_name, tool_input)
                tool_results.append({
                    "tool_name": tool_name,
                    "input": tool_input,
                    "output": result
                })
            
            # 将工具结果发送给AI，获取最终答案
            return self._get_final_answer_with_tools(original_question, tool_results)
            
        except Exception as e:
            logger.error(f"处理工具调用失败: {e}")
            return {"error": f"工具调用处理失败: {str(e)}"}
    
    def _extract_final_answer(self, api_response: Dict[str, Any]) -> Dict[str, Any]:
        """提取AI的最终答案"""
        try:
            content = api_response.get("content", [])
            
            # 查找文本内容
            text_content = ""
            for item in content:
                if item.get("type") == "text":
                    text_content += item.get("text", "")
            
            # 尝试解析JSON格式的回答
            try:
                # 查找JSON代码块
                if "```json" in text_content:
                    json_start = text_content.find("```json") + 7
                    json_end = text_content.find("```", json_start)
                    json_str = text_content[json_start:json_end].strip()
                    
                    parsed = json.loads(json_str)
                    return {
                        "success": True,
                        "sql": parsed.get("sql"),
                        "explanation": parsed.get("explanation"),
                        "chart_type": parsed.get("chart_type"),
                        "method": "claude_ai"
                    }
            except:
                pass
            
            # 如果没有JSON，返回文本解释
            return {
                "success": True,
                "explanation": text_content,
                "method": "claude_ai"
            }
            
        except Exception as e:
            logger.error(f"提取最终答案失败: {e}")
            return {"error": f"提取答案失败: {str(e)}"}
    
    def _get_final_answer_with_tools(self, question: str, tool_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """使用工具结果获取最终答案"""
        try:
            # 构建包含工具结果的提示
            tools_summary = "\n\n## 工具执行结果\n"
            for result in tool_results:
                tools_summary += f"\n### {result['tool_name']}\n"
                tools_summary += f"输入: {result['input']}\n"
                tools_summary += f"输出: {json.dumps(result['output'], ensure_ascii=False, indent=2)}\n"
            
            follow_up_prompt = f"""
基于以上工具执行结果，请回答用户问题：{question}

请生成最终的SQL查询、解释和图表建议，格式如下：
```json
{{
    "sql": "你的SQL查询",
    "explanation": "查询解释",
    "chart_type": "建议的图表类型"
}}
```
"""
            
            # 发送后续请求
            messages = [
                {
                    "role": "user",
                    "content": follow_up_prompt + tools_summary
                }
            ]
            
            request_body = {
                "model": self.model,
                "max_tokens": self.max_tokens,
                "messages": messages
            }
            
            with httpx.Client() as client:
                response = client.post(
                    f"{self.base_url}/v1/messages",
                    headers=self.headers,
                    json=request_body,
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return self._extract_final_answer(result)
                else:
                    return {"error": f"后续请求失败: {response.status_code}"}
                    
        except Exception as e:
            logger.error(f"获取最终答案失败: {e}")
            return {"error": f"获取最终答案失败: {str(e)}"}
