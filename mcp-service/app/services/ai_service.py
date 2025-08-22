"""
DeepSeek AI API集成服务
MCP服务专用版本
"""

import httpx
import json
import logging
import os
from typing import Optional, Dict, Any, List
from datetime import datetime

logger = logging.getLogger(__name__)

class DeepSeekAIService:
    """DeepSeek AI API集成服务"""
    
    def __init__(self):
        self.api_key = os.getenv("DEEPSEEK_API_KEY")
        self.base_url = os.getenv("DEEPSEEK_API_BASE_URL", "https://api.deepseek.com")
        self.model = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
        self.max_tokens = int(os.getenv("DEEPSEEK_MAX_TOKENS", "4000"))
        self.temperature = float(os.getenv("DEEPSEEK_TEMPERATURE", "0.7"))
        
        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        # 加载数据库结构文件
        self.db_schema = self._load_database_schema()
        
        logger.info(f"DeepSeek AI服务初始化: model={self.model}, base_url={self.base_url}")
        if self.db_schema:
            logger.info("✅ 数据库结构文件加载成功")
        else:
            logger.warning("⚠️ 数据库结构文件加载失败，将使用默认提示词")
    
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
    
    async def chat_completion(
        self, 
        messages: List[Dict[str, str]], 
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None
    ) -> Optional[Dict[str, Any]]:
        """
        发送聊天完成请求
        
        Args:
            messages: 消息列表，格式为 [{"role": "user", "content": "..."}]
            system_prompt: 系统提示词
            temperature: 温度参数，控制随机性
        
        Returns:
            API响应数据或None
        """
        if not self._validate_config():
            return None
        
        try:
            # 构建请求体
            request_data = {
                "model": self.model,
                "messages": messages,
                "max_tokens": self.max_tokens,
                "temperature": temperature or self.temperature,
                "stream": False
            }
            
            # 如果有系统提示词，添加到消息开头
            if system_prompt:
                request_data["messages"].insert(0, {
                    "role": "system", 
                    "content": system_prompt
                })
            
            logger.info(f"发送DeepSeek API请求: model={self.model}, messages_count={len(messages)}")
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.base_url}/v1/chat/completions",
                    headers=self.headers,
                    json=request_data
                )
                
                if response.status_code == 200:
                    result = response.json()
                    logger.info(f"DeepSeek API请求成功: tokens_used={result.get('usage', {}).get('total_tokens', 0)}")
                    return result
                else:
                    logger.error(f"DeepSeek API请求失败: status={response.status_code}, response={response.text}")
                    return None
                    
        except Exception as e:
            logger.error(f"DeepSeek API请求异常: {e}")
            return None
    
    async def analyze_financial_question(self, question: str) -> Optional[Dict[str, Any]]:
        """
        分析财务问题并生成SQL查询
        
        Args:
            question: 用户问题
        
        Returns:
            分析结果，包含SQL和解释
        """
        if not self._validate_config():
            return None
        
        try:
            # 构建系统提示词
            system_prompt = self._build_system_prompt()
            
            # 构建用户消息
            user_message = f"请分析以下问题并生成SQL查询：{question}"
            
            # 发送请求
            result = await self.chat_completion(
                messages=[{"role": "user", "content": user_message}],
                system_prompt=system_prompt,
                temperature=0.3  # 降低随机性，提高一致性
            )
            
            if result and "choices" in result:
                content = result["choices"][0]["message"]["content"]
                
                # 尝试解析JSON响应
                try:
                    # 查找JSON内容
                    start_idx = content.find('{')
                    end_idx = content.rfind('}') + 1
                    
                    if start_idx != -1 and end_idx != 0:
                        json_content = content[start_idx:end_idx]
                        parsed_result = json.loads(json_content)
                        
                        logger.info(f"AI分析成功: {parsed_result}")
                        return parsed_result
                    else:
                        logger.warning(f"AI响应中未找到JSON内容: {content}")
                        return None
                        
                except json.JSONDecodeError as e:
                    logger.error(f"AI响应JSON解析失败: {e}, content: {content}")
                    return None
            else:
                logger.error("AI响应格式异常")
                return None
                
        except Exception as e:
            logger.error(f"财务问题分析失败: {e}")
            return None
