"""
AI聊天API

提供文本聊天功能，使用DeepSeek AI生成回复
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from app.services.deepseek_ai_service import DeepSeekAIService
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

class ChatRequest(BaseModel):
    question: str
    context: Optional[str] = None

class ChatResponse(BaseModel):
    success: bool
    response: str
    error: Optional[str] = None

@router.post("/text", response_model=ChatResponse)
async def chat_text(request: ChatRequest):
    """AI文本聊天"""
    try:
        logger.info(f"收到聊天请求: {request.question}")
        
        # 创建DeepSeek AI服务实例
        ai_service = DeepSeekAIService()
        
        # 构建聊天提示词
        system_prompt = """你是一个专业的AI财务助手，专门帮助用户分析个人财务状况。

你的职责：
1. 回答用户的财务相关问题
2. 提供专业的财务建议
3. 解释财务概念
4. 帮助用户理解投资策略

数据库信息（用于提供准确建议）：
- 主要数据表：asset_snapshot（资产快照）、user_operations（交易记录）、asset_positions（持仓信息）
- 支持的平台：支付宝、Wise、IBKR、OKX、Web3
- 资产类型：基金、外汇、股票、数字货币、现金、储蓄
- 主要分析字段：balance_cny（人民币余额）、snapshot_time（快照时间）

回答要求：
- 专业准确：基于实际的数据库结构提供建议
- 通俗易懂：用简单语言解释复杂概念
- 有实际价值：结合用户的具体情况给出建议
- 鼓励深入：如果涉及数据分析，建议用户使用图表功能

当用户询问具体数据时，可以建议：
- "我可以为您生成资产分布图表"
- "让我为您分析投资组合表现"
- "我可以展示各平台的资产对比"
- "让我为您生成收益趋势分析" """

        # 调用DeepSeek AI
        messages = [
            {"role": "user", "content": request.question}
        ]
        
        result = await ai_service.chat_completion(messages, system_prompt, temperature=0.7)
        
        if result and 'choices' in result:
            content = result['choices'][0]['message']['content']
            logger.info(f"AI回复生成成功: {content[:100]}...")
            
            return ChatResponse(
                success=True,
                response=content
            )
        else:
            logger.warning("DeepSeek AI未返回有效回复")
            return ChatResponse(
                success=True,
                response="抱歉，我现在无法生成回复。请尝试询问具体的财务数据，我可以为您生成图表分析。"
            )
            
    except Exception as e:
        logger.error(f"AI聊天异常: {e}")
        return ChatResponse(
            success=False,
            response="抱歉，AI服务暂时不可用。",
            error=str(e)
        )

@router.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy", "service": "ai-chat"}
