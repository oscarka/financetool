"""
DeepSeek AI API集成服务

提供自然语言处理、智能分析等功能
"""

import httpx
import json
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime
from app.settings import settings

logger = logging.getLogger(__name__)

class DeepSeekAIService:
    """DeepSeek AI API集成服务"""
    
    def __init__(self):
        self.api_key = settings.deepseek_api_key
        self.base_url = settings.deepseek_api_base_url
        self.model = settings.deepseek_model
        self.max_tokens = settings.deepseek_max_tokens
        self.temperature = settings.deepseek_temperature
        
        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        logger.info(f"DeepSeek AI服务初始化: model={self.model}, base_url={self.base_url}")
    
    def _validate_config(self) -> bool:
        """验证API配置是否完整"""
        if not self.api_key:
            logger.error("DeepSeek API Key未配置，请检查环境变量")
            return False
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
                    logger.error(f"DeepSeek API请求失败: {response.status_code} - {response.text}")
                    return None
                    
        except Exception as e:
            logger.error(f"DeepSeek API请求异常: {e}")
            return None
    
    async def analyze_financial_question(
        self, 
        question: str, 
        context: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        分析金融相关问题，生成SQL查询
        
        Args:
            question: 用户问题
            context: 数据库上下文信息
        
        Returns:
            分析结果，包含SQL查询和图表建议
        """
        system_prompt = """你是一个专业的金融数据分析师。根据用户的问题，分析数据需求并生成相应的SQL查询。

数据库表结构：
- asset_snapshot: 资产快照表
  - platform: 平台名称
  - asset_type: 资产类型
  - asset_name: 资产名称
  - balance_cny: 人民币余额
  - snapshot_time: 快照时间

请根据问题生成合适的SQL查询，并建议图表类型。返回JSON格式：
{
    "sql": "SQL查询语句",
    "chart_type": "图表类型(pie/bar/line/table)",
    "description": "图表描述",
    "analysis": "数据分析说明"
}"""

        messages = [
            {"role": "user", "content": f"问题：{question}\n\n数据库上下文：{context or '无特殊上下文'}"}
        ]
        
        try:
            result = await self.chat_completion(messages, system_prompt, temperature=0.3)
            
            if result and 'choices' in result:
                content = result['choices'][0]['message']['content']
                
                # 尝试解析JSON响应
                try:
                    analysis_result = json.loads(content)
                    logger.info(f"DeepSeek分析结果: {analysis_result}")
                    return analysis_result
                except json.JSONDecodeError:
                    logger.warning(f"DeepSeek返回内容不是有效JSON: {content}")
                    # 尝试提取SQL和图表类型
                    return self._extract_from_text(content, question)
            
            return None
            
        except Exception as e:
            logger.error(f"DeepSeek分析异常: {e}")
            return None
    
    def _extract_from_text(self, text: str, question: str) -> Dict[str, Any]:
        """从文本中提取SQL和图表类型"""
        # 简单的关键词匹配作为备选方案
        chart_type = "bar"  # 默认柱状图
        
        if any(word in question.lower() for word in ["分布", "占比", "比例"]):
            chart_type = "pie"
        elif any(word in question.lower() for word in ["趋势", "变化", "时间"]):
            chart_type = "line"
        elif any(word in question.lower() for word in ["排行", "对比", "比较"]):
            chart_type = "bar"
        
        return {
            "sql": "SELECT platform, SUM(balance_cny) as total_value, COUNT(*) as asset_count FROM asset_snapshot WHERE snapshot_time = (SELECT MAX(snapshot_time) FROM asset_snapshot) GROUP BY platform ORDER BY total_value DESC",
            "chart_type": chart_type,
            "description": f"基于'{question}'的数据分析",
            "analysis": "使用DeepSeek AI分析生成"
        }
    
    async def health_check(self) -> bool:
        """健康检查"""
        try:
            messages = [{"role": "user", "content": "Hello"}]
            result = await self.chat_completion(messages, temperature=0.1)
            return result is not None
        except Exception as e:
            logger.error(f"DeepSeek健康检查失败: {e}")
            return False
