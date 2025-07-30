#!/usr/bin/env python3
"""
Wise数据检查工具
用于检查Wise汇率数据的同步状态和健康状况
"""

import os
import sys

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    """主函数"""
    try:
        from app.utils.wise_data_manager import WiseDataManager
        
        # 创建数据管理器
        manager = WiseDataManager()
        
        print("🔍 Wise汇率数据检查工具")
        print("=" * 50)
        
        # 检查数据状态
        status_ok = manager.check_data_status()
        
        if status_ok:
            print("\n✅ 数据状态正常")
            sys.exit(0)
        else:
            print("\n❌ 数据状态异常")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ 检查失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 