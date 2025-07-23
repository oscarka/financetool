#!/usr/bin/env python3
"""
汇率更新定时任务脚本
每2小时执行一次，更新Wise汇率数据
"""

import os
import sys
import logging
import asyncio
from datetime import datetime
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.services.wise_api_service import update_wise_rates_sync
from app.core.database import get_db
from app.models.exchange_rate_models import WiseAPIConfig

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/log/wise_rate_updater.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


def check_wise_config():
    """检查Wise API配置"""
    try:
        db = next(get_db())
        config = db.query(WiseAPIConfig).filter(WiseAPIConfig.is_active == True).first()
        
        if not config:
            logger.error("未找到有效的Wise API配置")
            return False
        
        if not config.api_key or not config.profile_id:
            logger.error("Wise API配置不完整")
            return False
        
        logger.info("Wise API配置检查通过")
        return True
        
    except Exception as e:
        logger.error(f"检查Wise配置失败: {e}")
        return False
    finally:
        db.close()


def main():
    """主函数"""
    logger.info("开始执行汇率更新任务...")
    
    # 检查配置
    if not check_wise_config():
        logger.error("配置检查失败，退出任务")
        return False
    
    try:
        # 执行汇率更新
        result = update_wise_rates_sync()
        
        if result:
            logger.info(f"汇率更新任务完成: {result}")
            return True
        else:
            logger.error("汇率更新任务失败")
            return False
            
    except Exception as e:
        logger.error(f"汇率更新任务异常: {e}")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)