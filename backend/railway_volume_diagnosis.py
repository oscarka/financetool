#!/usr/bin/env python3
"""
Railway Volume诊断脚本
快速检查数据持久化问题
"""
import os
import sys
import sqlite3
from pathlib import Path
from datetime import datetime
import json

def print_header(title):
    """打印标题"""
    print(f"\n{'='*60}")
    print(f"🔍 {title}")
    print(f"{'='*60}")

def print_section(title):
    """打印章节标题"""
    print(f"\n📋 {title}")
    print("-" * 40)

def check_environment():
    """检查环境变量"""
    print_section("环境变量检查")
    
    env_vars = {
        "RAILWAY_ENVIRONMENT": os.getenv("RAILWAY_ENVIRONMENT"),
        "RAILWAY_PROJECT_ID": os.getenv("RAILWAY_PROJECT_ID"),
        "DATABASE_PERSISTENT_PATH": os.getenv("DATABASE_PERSISTENT_PATH"),
        "DATABASE_URL": os.getenv("DATABASE_URL"),
        "PORT": os.getenv("PORT"),
        "APP_ENV": os.getenv("APP_ENV")
    }
    
    is_railway = env_vars["RAILWAY_ENVIRONMENT"] is not None
    
    for key, value in env_vars.items():
        status = "✅" if value else "❌"
        print(f"  {status} {key}: {value or '未设置'}")
    
    print(f"\n📍 运行环境: {'Railway' if is_railway else '本地/其他'}")
    return is_railway

def check_volume_mount():
    """检查volume挂载"""
    print_section("Volume挂载检查")
    
    data_path = os.getenv("DATABASE_PERSISTENT_PATH", "/app/data")
    print(f"  数据目录路径: {data_path}")
    
    # 检查目录是否存在
    data_dir = Path(data_path)
    print(f"  目录存在: {'✅' if data_dir.exists() else '❌'}")
    
    if data_dir.exists():
        # 检查权限
        try:
            stat = data_dir.stat()
            print(f"  目录权限: {oct(stat.st_mode)[-3:]}")
            print(f"  所有者: {stat.st_uid}")
        except Exception as e:
            print(f"  权限检查失败: {e}")
        
        # 列出目录内容
        try:
            files = list(data_dir.glob("*"))
            print(f"  目录内容: {len(files)} 个文件/目录")
            for file in files:
                if file.is_file():
                    size = file.stat().st_size
                    size_mb = size / (1024 * 1024)
                    print(f"    📄 {file.name} ({size_mb:.2f}MB)")
                else:
                    print(f"    📁 {file.name}/")
        except Exception as e:
            print(f"  目录内容检查失败: {e}")
        
        # 测试写入权限
        try:
            test_file = data_dir / "volume_test.txt"
            test_file.write_text(f"Volume test at {datetime.now()}")
            content = test_file.read_text()
            test_file.unlink()
            print("  ✅ Volume写入测试通过")
            return True
        except Exception as e:
            print(f"  ❌ Volume写入测试失败: {e}")
            return False
    else:
        print("  ❌ 数据目录不存在")
        return False

def check_database():
    """检查数据库文件"""
    print_section("数据库文件检查")
    
    data_path = os.getenv("DATABASE_PERSISTENT_PATH", "/app/data")
    db_path = os.path.join(data_path, "personalfinance.db")
    
    print(f"  数据库路径: {db_path}")
    print(f"  文件存在: {'✅' if os.path.exists(db_path) else '❌'}")
    
    if os.path.exists(db_path):
        try:
            size = os.path.getsize(db_path)
            size_mb = size / (1024 * 1024)
            print(f"  文件大小: {size_mb:.2f}MB")
            
            # 检查数据库连接
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # 获取表列表
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            print(f"  数据库表数量: {len(tables)}")
            
            # 检查关键表
            key_tables = ['fund_nav', 'user_operations', 'fund_info', 'asset_positions']
            for table in key_tables:
                try:
                    cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    count = cursor.fetchone()[0]
                    print(f"    📋 {table}: {count} 条记录")
                except Exception:
                    print(f"    📋 {table}: 表不存在")
            
            conn.close()
            print("  ✅ 数据库连接正常")
            return True
            
        except Exception as e:
            print(f"  ❌ 数据库检查失败: {e}")
            return False
    else:
        print("  ⚠️  数据库文件不存在，将在首次运行时创建")
        return False

def check_railway_config():
    """检查Railway配置"""
    print_section("Railway配置检查")
    
    # 检查railway.toml
    railway_toml = Path("railway.toml")
    if railway_toml.exists():
        print("  ✅ railway.toml 文件存在")
        
        # 读取并检查volume配置
        content = railway_toml.read_text()
        if "[[deploy.volumes]]" in content:
            print("  ✅ volume配置已设置")
            
            # 提取volume配置
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if 'source = "database"' in line:
                    print("    📍 source: database")
                elif 'target = "/app/data"' in line:
                    print("    📍 target: /app/data")
        else:
            print("  ❌ volume配置缺失")
    else:
        print("  ❌ railway.toml 文件不存在")
    
    # 检查Dockerfile
    dockerfile = Path("Dockerfile")
    if dockerfile.exists():
        print("  ✅ Dockerfile 文件存在")
        
        content = dockerfile.read_text()
        if "DATABASE_PERSISTENT_PATH" in content:
            print("  ✅ 数据持久化环境变量已设置")
        else:
            print("  ❌ 数据持久化环境变量缺失")
    else:
        print("  ❌ Dockerfile 文件不存在")

def check_service_health():
    """检查服务健康状态"""
    print_section("服务健康检查")
    
    try:
        import requests
        
        # 获取服务URL
        port = os.getenv("PORT", "8000")
        service_url = f"http://localhost:{port}"
        
        # 检查健康状态
        response = requests.get(f"{service_url}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("  ✅ 服务健康检查通过")
            print(f"    状态: {data.get('status')}")
            print(f"    环境: {data.get('environment')}")
            
            # 检查数据库信息
            if 'database' in data:
                db_info = data['database']
                print(f"    数据库路径: {db_info.get('path')}")
                print(f"    数据库存在: {db_info.get('exists')}")
                if db_info.get('size_bytes'):
                    size_mb = db_info.get('size_bytes', 0) / (1024 * 1024)
                    print(f"    数据库大小: {size_mb:.2f}MB")
            
            return True
        else:
            print(f"  ❌ 服务健康检查失败: {response.status_code}")
            return False
            
    except ImportError:
        print("  ⚠️  requests库未安装，跳过服务健康检查")
        return False
    except Exception as e:
        print(f"  ❌ 服务健康检查异常: {e}")
        return False

def generate_diagnosis_report():
    """生成诊断报告"""
    print_header("Railway Volume诊断报告")
    
    # 执行检查
    is_railway = check_environment()
    volume_ok = check_volume_mount()
    db_ok = check_database()
    check_railway_config()
    service_ok = check_service_health()
    
    # 总结
    print_section("诊断总结")
    
    print(f"  📍 运行环境: {'Railway' if is_railway else '本地/其他'}")
    print(f"  🔗 Volume挂载: {'✅ 正常' if volume_ok else '❌ 异常'}")
    print(f"  📊 数据库文件: {'✅ 正常' if db_ok else '❌ 异常'}")
    print(f"  🏥 服务健康: {'✅ 正常' if service_ok else '❌ 异常'}")
    
    # 问题诊断
    print_section("问题诊断")
    
    if not is_railway:
        print("  ⚠️  不在Railway环境中，无法测试volume挂载")
        print("  💡 建议：在Railway控制台运行此脚本")
    
    if not volume_ok:
        print("  ❌ Volume挂载失败")
        print("  💡 解决方案：")
        print("     1. 在Railway控制台创建名为'database'的volume")
        print("     2. 设置挂载路径为'/app/data'")
        print("     3. 确保volume状态为'Active'")
    
    if not db_ok:
        print("  ❌ 数据库文件异常")
        print("  💡 解决方案：")
        print("     1. 检查volume是否正确挂载")
        print("     2. 确认数据目录权限")
        print("     3. 重新部署服务")
    
    if not service_ok:
        print("  ❌ 服务健康检查失败")
        print("  💡 解决方案：")
        print("     1. 检查服务是否正常启动")
        print("     2. 查看部署日志")
        print("     3. 确认环境变量配置")
    
    # 保存报告
    report = {
        "timestamp": datetime.now().isoformat(),
        "is_railway": is_railway,
        "volume_ok": volume_ok,
        "db_ok": db_ok,
        "service_ok": service_ok,
        "environment_vars": {
            "RAILWAY_ENVIRONMENT": os.getenv("RAILWAY_ENVIRONMENT"),
            "DATABASE_PERSISTENT_PATH": os.getenv("DATABASE_PERSISTENT_PATH"),
            "DATABASE_URL": os.getenv("DATABASE_URL")
        }
    }
    
    report_file = "railway_volume_diagnosis_report.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f"\n📄 诊断报告已保存: {report_file}")

if __name__ == "__main__":
    generate_diagnosis_report()
    
    print("\n✅ 诊断完成！")
    print("\n💡 如果发现问题，请按照上述建议进行修复。")