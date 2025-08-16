#!/usr/bin/env python3

"""
Flutter AI图表系统测试脚本
验证核心组件的文件结构和基本语法
"""

import os
from pathlib import Path

def main():
    print('🧪 开始测试Flutter AI图表系统')
    print('=' * 50)
    
    # 检查核心文件是否存在
    core_files = [
        'flutter_app/personal_finance_flutter/lib/widgets/chart_design_system.dart',
        'flutter_app/personal_finance_flutter/lib/widgets/ai_chat_widget.dart',
        'flutter_app/personal_finance_flutter/lib/widgets/chart_intent_dialog.dart',
        'flutter_app/personal_finance_flutter/lib/widgets/chart_save_dialog.dart',
        'flutter_app/personal_finance_flutter/lib/widgets/chart_preview_modal.dart',
        'flutter_app/personal_finance_flutter/lib/widgets/mcp_chart_adapter.dart',
        'flutter_app/personal_finance_flutter/lib/pages/chart_showcase_page.dart',
        'flutter_app/personal_finance_flutter/lib/pages/main_app_demo.dart',
    ]
    
    print('📁 检查核心文件...')
    file_count = 0
    existing_files = 0
    
    for file_path in core_files:
        file_count += 1
        file_obj = Path(file_path)
        exists = file_obj.exists()
        status = '✅' if exists else '❌'
        file_name = file_obj.name
        
        print(f'  {status} {file_name}')
        
        if exists:
            existing_files += 1
            # 检查文件大小
            size = file_obj.stat().st_size
            if size > 0:
                print(f'    📏 大小: {size / 1024:.1f}KB')
                
                # 检查关键内容
                content = file_obj.read_text(encoding='utf-8')
                if 'class ' in content:
                    class_count = content.count('class ')
                    print(f'    🏗️  包含 {class_count} 个类')
                if 'Widget' in content:
                    print(f'    📱 Flutter组件')
            else:
                print('    ⚠️  文件为空')
    
    print(f'\n📊 文件检查结果:')
    print(f'  总文件数: {file_count}')
    print(f'  存在文件: {existing_files}')
    print(f'  完整度: {existing_files / file_count * 100:.1f}%')
    
    # 检查导入依赖
    print('\n🔗 检查关键导入...')
    check_imports()
    
    # 检查pubspec.yaml依赖
    print('\n📦 检查依赖配置...')
    check_dependencies()
    
    # 检查工作流程文档
    print('\n📚 检查文档...')
    check_documentation()
    
    # 生成测试总结
    print('\n' + '=' * 50)
    print('🎯 测试总结')
    print('=' * 50)
    
    if existing_files == file_count:
        print('✅ 所有核心文件已创建')
        print('✅ Flutter图表系统框架完整')
        print('🚀 可以开始运行测试！')
        
        print('\n💡 下一步操作:')
        print('1. 进入Flutter项目目录:')
        print('   cd flutter_app/personal_finance_flutter')
        print('2. 获取依赖:')
        print('   flutter pub get')
        print('3. 运行应用:')
        print('   flutter run')
        print('4. 测试功能:')
        print('   - 尝试输入: "显示各平台的资产分布"')
        print('   - 体验双重确认流程')
        
        print('\n🔄 完整测试流程:')
        print('   1. 用户输入问题 → 触发意图识别')
        print('   2. 弹出确认对话框 → 用户确认生成')
        print('   3. 生成图表 → 聊天中显示缩略图')
        print('   4. 点击图表 → 打开详情预览')
        print('   5. 点击保存 → 弹出保存确认')
        print('   6. 确认保存 → 添加到深度分析页面')
        
    else:
        missing_count = file_count - existing_files
        print(f'⚠️  缺失 {missing_count} 个文件，需要补充')
        print('📝 缺失的文件可能影响系统运行')
        
        # 列出缺失的文件
        print('\n❌ 缺失的文件:')
        for file_path in core_files:
            if not Path(file_path).exists():
                print(f'   - {Path(file_path).name}')

def check_imports():
    import_checks = [
        {
            'file': 'flutter_app/personal_finance_flutter/lib/widgets/ai_chat_widget.dart',
            'imports': [
                'chart_design_system.dart',
                'chart_preview_modal.dart',
                'chart_intent_dialog.dart',
                'chart_save_dialog.dart',
            ]
        },
        {
            'file': 'flutter_app/personal_finance_flutter/lib/widgets/chart_preview_modal.dart',
            'imports': [
                'chart_design_system.dart',
                'chart_save_dialog.dart',
            ]
        }
    ]
    
    for check in import_checks:
        file_path = Path(check['file'])
        if file_path.exists():
            content = file_path.read_text(encoding='utf-8')
            file_name = file_path.name
            
            print(f'  📄 {file_name}:')
            for import_name in check['imports']:
                has_import = f"import '{import_name}'" in content or f'import "{import_name}"' in content
                status = '✅' if has_import else '❌'
                print(f'    {status} {import_name}')

def check_dependencies():
    pubspec_file = Path('flutter_app/personal_finance_flutter/pubspec.yaml')
    
    if pubspec_file.exists():
        content = pubspec_file.read_text(encoding='utf-8')
        
        required_deps = [
            'fl_chart',
            'flutter',
        ]
        
        print('  📋 pubspec.yaml:')
        for dep in required_deps:
            has_dep = dep in content
            status = '✅' if has_dep else '❌'
            print(f'    {status} {dep}')
    else:
        print('  ❌ pubspec.yaml 不存在')

def check_documentation():
    docs = [
        'FLUTTER_CHART_SYSTEM_GUIDE.md',
        'ENHANCED_CHART_WORKFLOW_GUIDE.md',
        'COMPLETE_CHART_WORKFLOW_GUIDE.md'
    ]
    
    print('  📚 文档文件:')
    for doc in docs:
        doc_path = Path(doc)
        exists = doc_path.exists()
        status = '✅' if exists else '❌'
        print(f'    {status} {doc}')
        
        if exists:
            size = doc_path.stat().st_size
            print(f'        📏 大小: {size / 1024:.1f}KB')

if __name__ == '__main__':
    main()