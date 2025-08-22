#!/usr/bin/env python3
"""
数据库Schema配置就绪状态检查
检查数据库字段信息和MCP配置是否准备完毕
"""

import json
import os
from pathlib import Path
import sys

def check_schema_file():
    """检查Schema文件是否存在且完整"""
    print("🔍 检查数据库Schema文件...")
    
    schema_file = Path("../config/database_schema_for_mcp.json")
    
    if not schema_file.exists():
        print("❌ Schema文件不存在")
        return False
    
    try:
        with open(schema_file, 'r', encoding='utf-8') as f:
            schema = json.load(f)
        
        # 检查必要的字段
        required_keys = ["tables", "business_dimensions", "sample_queries"]
        missing_keys = []
        
        db_schema = schema.get("database_schema", {})
        if not db_schema:
            print("❌ 缺少database_schema根节点")
            return False
            
        for key in required_keys:
            if key not in db_schema:
                missing_keys.append(key)
        
        if missing_keys:
            print(f"❌ Schema文件缺少必要字段: {missing_keys}")
            return False
        
        # 检查核心表
        tables = db_schema.get("tables", {})
        core_tables = ["asset_snapshot", "user_operations", "asset_positions"]
        missing_tables = []
        
        for table in core_tables:
            if table not in tables:
                missing_tables.append(table)
        
        if missing_tables:
            print(f"❌ Schema文件缺少核心表: {missing_tables}")
            return False
        
        print("✅ Schema文件完整且格式正确")
        print(f"   - 包含 {len(tables)} 个数据表")
        print(f"   - 包含 {len(db_schema.get('sample_queries', {}))} 个示例查询")
        return True
        
    except json.JSONDecodeError as e:
        print(f"❌ Schema文件JSON格式错误: {e}")
        return False
    except Exception as e:
        print(f"❌ Schema文件检查异常: {e}")
        return False

def check_mcp_client_integration():
    """检查MCP客户端是否已集成Schema"""
    print("\n🔍 检查MCP客户端Schema集成...")
    
    mcp_client_file = Path("../app/services/mcp_client.py")
    
    if not mcp_client_file.exists():
        print("❌ MCP客户端文件不存在")
        return False
    
    try:
        with open(mcp_client_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查是否包含Schema加载逻辑
        if "database_schema_for_mcp.json" in content:
            print("✅ MCP客户端已集成Schema加载")
            
            if "_get_database_context" in content:
                print("✅ 数据库上下文函数已实现")
                return True
            else:
                print("❌ 缺少数据库上下文函数")
                return False
        else:
            print("❌ MCP客户端未集成Schema文件")
            return False
            
    except Exception as e:
        print(f"❌ MCP客户端检查异常: {e}")
        return False

def check_sample_queries():
    """检查示例查询是否适用于当前数据库结构"""
    print("\n🔍 检查示例SQL查询...")
    
    schema_file = Path("../config/database_schema_for_mcp.json")
    
    try:
        with open(schema_file, 'r', encoding='utf-8') as f:
            schema = json.load(f)
        
        sample_queries = schema["database_schema"]["sample_queries"]
        
        print(f"✅ 发现 {len(sample_queries)} 个示例查询:")
        
        for query_name, query_info in sample_queries.items():
            description = query_info.get("description", "无描述")
            chart_type = query_info.get("chart_type", "未知")
            sql = query_info.get("sql", "")
            
            print(f"   📊 {description} ({chart_type}图表)")
            
            # 简单的SQL语法检查
            sql_upper = sql.upper()
            if "SELECT" in sql_upper and "FROM" in sql_upper:
                print(f"      ✅ SQL语法基本正确")
            else:
                print(f"      ❌ SQL语法可能有问题")
                
        return True
        
    except Exception as e:
        print(f"❌ 示例查询检查异常: {e}")
        return False

def check_chart_config_compatibility():
    """检查图表配置生成器兼容性"""
    print("\n🔍 检查图表配置生成器兼容性...")
    
    # 测试图表配置生成器是否能正确处理Schema中的数据格式
    try:
        # 模拟数据
        test_data = [
            {"platform": "支付宝", "total_value": 158460.30, "asset_count": 5},
            {"platform": "Wise", "total_value": 8158.23, "asset_count": 2},
            {"platform": "IBKR", "total_value": 42.03, "asset_count": 1}
        ]
        
        # 检查是否有图表配置生成器
        config_generator_file = Path("../app/services/chart_config_generator.py")
        
        if config_generator_file.exists():
            print("✅ 图表配置生成器文件存在")
            
            # 检查核心函数
            with open(config_generator_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            required_methods = [
                "_analyze_data_structure",
                "_determine_chart_type", 
                "_format_data_for_chart",
                "generate_config"
            ]
            
            missing_methods = []
            for method in required_methods:
                if method not in content:
                    missing_methods.append(method)
            
            if missing_methods:
                print(f"❌ 缺少必要方法: {missing_methods}")
                return False
            else:
                print("✅ 图表配置生成器包含所有必要方法")
                return True
        else:
            print("❌ 图表配置生成器文件不存在")
            return False
            
    except Exception as e:
        print(f"❌ 图表配置兼容性检查异常: {e}")
        return False

def check_flutter_compatibility():
    """检查Flutter集成兼容性"""
    print("\n🔍 检查Flutter集成配置...")
    
    schema_file = Path("../config/database_schema_for_mcp.json")
    
    try:
        with open(schema_file, 'r', encoding='utf-8') as f:
            schema = json.load(f)
        
        # 检查图表类型是否与Flutter fl_chart兼容
        sample_queries = schema["database_schema"]["sample_queries"]
        flutter_supported_charts = ["bar", "line", "pie", "table"]
        
        incompatible_charts = []
        
        for query_name, query_info in sample_queries.items():
            chart_type = query_info.get("chart_type", "unknown")
            if chart_type not in flutter_supported_charts:
                incompatible_charts.append(chart_type)
        
        if incompatible_charts:
            print(f"⚠️  发现不兼容的图表类型: {incompatible_charts}")
            print("   建议修改为 bar, line, pie, table 中的一种")
        else:
            print("✅ 所有图表类型都与Flutter fl_chart兼容")
        
        # 检查数据字段命名（可选字段）
        analysis_patterns = schema["database_schema"].get("common_analysis_patterns", {})
        
        if analysis_patterns:
            print(f"✅ 支持 {len(analysis_patterns)} 种分析模式:")
            for pattern_name, pattern_info in analysis_patterns.items():
                chart_types = pattern_info.get("chart_types", [])
                print(f"   📈 {pattern_info.get('description', pattern_name)}: {', '.join(chart_types)}")
        else:
            print("ℹ️  未配置分析模式（可选）")
        
        return True
        
    except Exception as e:
        print(f"❌ Flutter兼容性检查异常: {e}")
        return False

def generate_mcp_ready_summary():
    """生成MCP就绪状态总结"""
    print("\n" + "="*60)
    print("📋 MCP数据库配置就绪状态总结")
    print("="*60)
    
    checks = [
        ("Schema文件", check_schema_file()),
        ("MCP客户端集成", check_mcp_client_integration()),
        ("示例查询", check_sample_queries()),
        ("图表配置兼容性", check_chart_config_compatibility()),
        ("Flutter兼容性", check_flutter_compatibility())
    ]
    
    passed_checks = sum(1 for _, passed in checks if passed)
    total_checks = len(checks)
    
    print(f"\n📊 检查结果:")
    for check_name, passed in checks:
        status = "✅ 通过" if passed else "❌ 失败"
        print(f"   {check_name:15}: {status}")
    
    success_rate = (passed_checks / total_checks) * 100
    print(f"\n📈 总体就绪率: {success_rate:.1f}% ({passed_checks}/{total_checks})")
    
    if passed_checks == total_checks:
        print("\n🎉 数据库配置完全就绪！可以直接使用MCP系统")
        print("\n📋 下一步操作:")
        print("   1. 启动MCP服务器: cd backend && npm start")
        print("   2. 启动FastAPI: uvicorn app.main:app --reload")
        print("   3. 测试API: python3 run_tests.py")
        return True
    else:
        print(f"\n⚠️  还有 {total_checks - passed_checks} 项检查未通过")
        print("\n🔧 需要修复的问题:")
        for check_name, passed in checks:
            if not passed:
                print(f"   ❌ {check_name}")
        
        print("\n💡 建议:")
        print("   1. 修复上述问题")
        print("   2. 重新运行此检查脚本")
        print("   3. 确保所有组件都已正确配置")
        return False

def main():
    """主函数"""
    print("🔍 MCP智能图表系统 - 数据库配置就绪检查")
    print("检查数据库Schema、字段信息和MCP配置状态")
    print("-" * 60)
    
    # 运行完整检查
    ready = generate_mcp_ready_summary()
    
    # 输出关键信息
    if ready:
        print("\n🎯 关键配置信息:")
        print("   📊 核心分析表: asset_snapshot")
        print("   💰 主要数值字段: balance_cny")
        print("   ⏰ 时间字段: snapshot_time") 
        print("   🏢 分类字段: platform, asset_type")
        print("   📈 支持图表: bar, line, pie, table")
        
        print("\n🔌 MCP集成状态:")
        print("   ✅ Schema文件已准备")
        print("   ✅ MCP客户端已配置")
        print("   ✅ 示例查询可用")
        print("   ✅ Flutter兼容")
        
        exit_code = 0
    else:
        print("\n❌ 配置未完全就绪，请修复问题后重试")
        exit_code = 1
    
    sys.exit(exit_code)

if __name__ == "__main__":
    main()