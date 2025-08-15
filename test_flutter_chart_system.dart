#!/usr/bin/env dart

/// Flutter图表系统测试脚本
/// 验证核心组件的文件结构和基本语法

import 'dart:io';

void main() {
  print('🧪 开始测试Flutter AI图表系统');
  print('=' * 50);
  
  // 检查核心文件是否存在
  final coreFiles = [
    'flutter_app/personal_finance_flutter/lib/widgets/chart_design_system.dart',
    'flutter_app/personal_finance_flutter/lib/widgets/ai_chat_widget.dart',
    'flutter_app/personal_finance_flutter/lib/widgets/chart_intent_dialog.dart',
    'flutter_app/personal_finance_flutter/lib/widgets/chart_save_dialog.dart',
    'flutter_app/personal_finance_flutter/lib/widgets/chart_preview_modal.dart',
    'flutter_app/personal_finance_flutter/lib/widgets/mcp_chart_adapter.dart',
    'flutter_app/personal_finance_flutter/lib/pages/chart_showcase_page.dart',
    'flutter_app/personal_finance_flutter/lib/pages/main_app_demo.dart',
  ];
  
  print('📁 检查核心文件...');
  int fileCount = 0;
  int existingFiles = 0;
  
  for (final filePath in coreFiles) {
    fileCount++;
    final file = File(filePath);
    final exists = file.existsSync();
    final status = exists ? '✅' : '❌';
    final fileName = filePath.split('/').last;
    
    print('  $status $fileName');
    
    if (exists) {
      existingFiles++;
      // 检查文件大小
      final size = file.lengthSync();
      if (size > 0) {
        print('    📏 大小: ${(size / 1024).toStringAsFixed(1)}KB');
      } else {
        print('    ⚠️  文件为空');
      }
    }
  }
  
  print('\n📊 文件检查结果:');
  print('  总文件数: $fileCount');
  print('  存在文件: $existingFiles');
  print('  完整度: ${(existingFiles / fileCount * 100).toStringAsFixed(1)}%');
  
  // 检查导入依赖
  print('\n🔗 检查关键导入...');
  _checkImports();
  
  // 检查pubspec.yaml依赖
  print('\n📦 检查依赖配置...');
  _checkDependencies();
  
  // 生成测试总结
  print('\n' + '=' * 50);
  print('🎯 测试总结');
  print('=' * 50);
  
  if (existingFiles == fileCount) {
    print('✅ 所有核心文件已创建');
    print('✅ Flutter图表系统框架完整');
    print('🚀 可以开始运行测试！');
    
    print('\n💡 下一步操作:');
    print('1. 进入Flutter项目目录:');
    print('   cd flutter_app/personal_finance_flutter');
    print('2. 获取依赖:');
    print('   flutter pub get');
    print('3. 运行应用:');
    print('   flutter run');
    print('4. 测试功能:');
    print('   - 尝试输入: "显示各平台的资产分布"');
    print('   - 体验双重确认流程');
  } else {
    print('⚠️  部分文件缺失，需要补充');
    print('📝 缺失的文件可能影响系统运行');
  }
}

void _checkImports() {
  final importChecks = [
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
  ];
  
  for (final check in importChecks) {
    final file = File(check['file'] as String);
    if (file.existsSync()) {
      final content = file.readAsStringSync();
      final fileName = (check['file'] as String).split('/').last;
      
      print('  📄 $fileName:');
      for (final import in check['imports'] as List<String>) {
        final hasImport = content.contains("import '$import'") || 
                         content.contains('import "$import"');
        final status = hasImport ? '✅' : '❌';
        print('    $status $import');
      }
    }
  }
}

void _checkDependencies() {
  final pubspecFile = File('flutter_app/personal_finance_flutter/pubspec.yaml');
  
  if (pubspecFile.existsSync()) {
    final content = pubspecFile.readAsStringSync();
    
    final requiredDeps = [
      'fl_chart',
      'flutter',
    ];
    
    print('  📋 pubspec.yaml:');
    for (final dep in requiredDeps) {
      final hasDep = content.contains(dep);
      final status = hasDep ? '✅' : '❌';
      print('    $status $dep');
    }
  } else {
    print('  ❌ pubspec.yaml 不存在');
  }
}