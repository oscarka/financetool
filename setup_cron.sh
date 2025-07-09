#!/bin/bash
# IBKR数据同步定时任务设置脚本

echo "🔧 设置IBKR数据同步定时任务..."

# 创建日志目录
sudo mkdir -p /var/log
sudo touch /var/log/ibkr_sync.log
sudo chmod 666 /var/log/ibkr_sync.log

# 创建脚本目录
mkdir -p ~/ibkr_scripts
cp ibkr_data_sync.py ~/ibkr_scripts/
cp test_ibkr_connection.py ~/ibkr_scripts/
chmod +x ~/ibkr_scripts/*.py

# 设置定时任务
echo "📅 添加cron任务 (每日8:00和18:00执行)..."

# 备份现有crontab
crontab -l > /tmp/crontab_backup 2>/dev/null || touch /tmp/crontab_backup

# 添加新的定时任务
echo "# IBKR数据同步任务" >> /tmp/crontab_backup
echo "0 8 * * * /usr/bin/python3 ~/ibkr_scripts/ibkr_data_sync.py >> /var/log/ibkr_sync.log 2>&1" >> /tmp/crontab_backup
echo "0 18 * * * /usr/bin/python3 ~/ibkr_scripts/ibkr_data_sync.py >> /var/log/ibkr_sync.log 2>&1" >> /tmp/crontab_backup

# 应用新的crontab
crontab /tmp/crontab_backup

echo "✅ 定时任务设置完成！"
echo ""
echo "📋 任务列表:"
crontab -l | grep -A 3 "IBKR"

echo ""
echo "🧪 现在可以运行测试:"
echo "   python3 ~/ibkr_scripts/test_ibkr_connection.py"
echo ""
echo "📝 查看日志:"
echo "   tail -f /var/log/ibkr_sync.log"
echo ""
echo "⏰ 手动执行同步:"
echo "   python3 ~/ibkr_scripts/ibkr_data_sync.py"