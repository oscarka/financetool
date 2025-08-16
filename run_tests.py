#!/usr/bin/env python3
"""
快速启动MCP智能图表系统测试
"""

import subprocess
import webbrowser
import os
import sys
import time
from pathlib import Path

def main():
    print("🚀 MCP智能图表系统 - 快速测试启动器")
    print("=" * 50)
    
    # 当前目录
    current_dir = Path(__file__).parent
    
    print("📋 可用的测试选项:")
    print("1. 📊 图表配置生成器测试 (已验证)")
    print("2. 🖥️  打开Mock测试界面 (浏览器)")
    print("3. 🧪 运行所有独立测试")
    print("4. 📖 查看使用指南")
    
    choice = input("\n请选择测试选项 (1-4): ").strip()
    
    if choice == "1":
        print("\n🔍 运行图表配置生成器测试...")
        result = subprocess.run([sys.executable, "test_chart_generator_standalone.py"], 
                              cwd=current_dir)
        if result.returncode == 0:
            print("\n✅ 图表配置生成器测试完成！")
        else:
            print("\n❌ 测试失败，请检查错误信息")
            
    elif choice == "2":
        print("\n🖥️  打开Mock测试界面...")
        html_file = current_dir / "mock_test_interface.html"
        
        if html_file.exists():
            # 在浏览器中打开HTML文件
            file_url = f"file://{html_file.absolute()}"
            print(f"📂 打开文件: {file_url}")
            
            try:
                webbrowser.open(file_url)
                print("✅ 测试界面已在浏览器中打开！")
                print("\n📋 测试界面功能:")
                print("   - MCP客户端模拟测试")
                print("   - API端点模拟测试") 
                print("   - LLM集成测试 (可输入真实API密钥)")
                print("   - 端到端流程测试")
                print("\n💡 提示: 可以在LLM集成标签页中输入真实的API密钥进行测试")
                
            except Exception as e:
                print(f"❌ 无法打开浏览器: {e}")
                print(f"请手动在浏览器中打开: {file_url}")
        else:
            print("❌ 找不到测试界面文件")
            
    elif choice == "3":
        print("\n🧪 运行所有独立测试...")
        
        # 只运行可以独立运行的测试
        tests = [
            ("图表配置生成器", "test_chart_generator_standalone.py"),
        ]
        
        results = []
        for test_name, test_file in tests:
            print(f"\n📋 运行: {test_name}")
            result = subprocess.run([sys.executable, test_file], 
                                  cwd=current_dir,
                                  capture_output=True,
                                  text=True)
            
            if result.returncode == 0:
                print(f"✅ {test_name} - 通过")
                results.append(True)
            else:
                print(f"❌ {test_name} - 失败")
                print(f"错误信息: {result.stderr}")
                results.append(False)
        
        # 总结
        passed = sum(results)
        total = len(results)
        print(f"\n📊 测试总结: {passed}/{total} 通过")
        
        if passed == total:
            print("🎉 所有独立测试通过！")
        else:
            print("⚠️  部分测试失败，请检查错误信息")
            
    elif choice == "4":
        print("\n📖 查看使用指南...")
        guide_file = current_dir / "MCP_SMART_CHART_GUIDE.md"
        
        if guide_file.exists():
            try:
                # 尝试用默认程序打开Markdown文件
                if sys.platform == "win32":
                    os.startfile(guide_file)
                elif sys.platform == "darwin":  # macOS
                    subprocess.run(["open", guide_file])
                else:  # Linux
                    subprocess.run(["xdg-open", guide_file])
                    
                print("✅ 使用指南已打开！")
            except Exception as e:
                print(f"❌ 无法打开文件: {e}")
                print(f"请手动打开: {guide_file}")
        else:
            print("❌ 找不到使用指南文件")
    
    else:
        print("❌ 无效选择")
        return
    
    print(f"\n{'='*50}")
    print("📋 下一步建议:")
    print("1. 如果独立测试通过，可以开始集成到你的项目")
    print("2. 查看 MCP_SMART_CHART_GUIDE.md 了解详细实施步骤")
    print("3. 使用Mock测试界面验证LLM集成")
    print("4. 开始Flutter端的集成工作")

if __name__ == "__main__":
    main()