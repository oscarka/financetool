# 🛠️ Railway数据持久化解决方案

## 🔍 问题分析

### 根本原因
Railway上每次重新部署时IBKR数据丢失的根本原因是**容器化部署的数据持久化问题**：

1. **SQLite数据库存储在容器内部**
   - 数据库文件位置：`./data/personalfinance.db`
   - 在Docker容器中，这个路径是容器内的临时文件系统
   - 每次容器重启或重新部署时，容器内的文件系统会被重置

2. **缺少数据卷配置**
   - 当前的`railway.toml`配置中没有配置持久化数据卷
   - 没有将数据库文件挂载到Railway的持久化存储中

3. **容器重启机制**
   - Railway使用`restartPolicyType = "on_failure"`配置
   - 每次代码更新都会触发新的容器部署
   - 新容器启动时会重新创建空的数据库文件

### 影响范围
- ✅ IBKR账户数据 (`ibkr_accounts`)
- ✅ IBKR余额数据 (`ibkr_balances`)
- ✅ IBKR持仓数据 (`ibkr_positions`)
- ✅ IBKR同步日志 (`ibkr_sync_logs`)
- ✅ Wise交易记录 (`wise_transactions`)
- ✅ Wise余额数据 (`wise_balances`)
- ✅ 用户操作记录 (`user_operations`)
- ✅ 资产持仓数据 (`asset_positions`)
- ✅ 基金信息 (`fund_info`)
- ✅ 定投计划 (`dca_plans`)

## 🛠️ 解决方案

### 方案1：配置Railway数据卷（推荐）

#### 1.1 修改Railway配置
已更新 `backend/railway.toml`：

```toml
[build]
builder = "dockerfile"
dockerfilePath = "backend/Dockerfile"

[deploy]
startCommand = "python run.py"
healthcheckPath = "/health"
healthcheckTimeout = 300
restartPolicyType = "on_failure"

[deploy.environment]
PORT = "8000"
DEBUG = "false"
WORKERS = "2"
APP_ENV = "prod"

# 添加数据卷配置
[[deploy.volumes]]
source = "database"
target = "/app/data"
```

#### 1.2 在Railway控制台配置
1. 登录Railway Dashboard
2. 进入你的后端项目
3. 点击 "Settings" → "Volumes"
4. 创建新的数据卷：
   - **Name**: `database`
   - **Path**: `/app/data`
   - **Size**: 根据需要设置（建议至少1GB）

#### 1.3 验证配置
部署后检查数据卷是否正确挂载：
```bash
# 在Railway控制台的终端中运行
ls -la /app/data/
```

### 方案2：使用外部数据库（长期方案）

#### 2.1 配置PostgreSQL数据库
1. 在Railway中创建PostgreSQL服务
2. 获取数据库连接URL
3. 设置环境变量：
```bash
DATABASE_URL=postgresql://username:password@host:port/database
```

#### 2.2 更新数据库配置
修改 `backend/app/settings/prod.py`：
```python
# 优先使用环境变量中的DATABASE_URL
database_url: str = os.getenv("DATABASE_URL", "sqlite:///./data/personalfinance.db")
```

### 方案3：自动备份和恢复

#### 3.1 部署前备份脚本
已创建 `backend/pre_deploy_backup.py`：
```bash
# 在部署前运行
python pre_deploy_backup.py
```

#### 3.2 数据库备份工具
已创建 `backend/backup_database.py`：
```bash
# 创建备份
python backup_database.py backup

# 列出备份
python backup_database.py list

# 恢复备份
python backup_database.py restore backups/personalfinance_backup_20241219_120000.db
```

#### 3.3 集成到GitHub Actions
在 `.github/workflows/deploy.yml` 中添加备份步骤：

```yaml
- name: Backup data before deployment
  run: |
    cd backend
    python pre_deploy_backup.py
  env:
    RAILWAY_SERVICE_URL: ${{ secrets.RAILWAY_SERVICE_URL }}
```

## 🔧 实施步骤

### 步骤1：立即备份现有数据
```bash
# 1. 连接到Railway服务
railway login
railway link

# 2. 备份当前数据
railway run python backup_database.py backup
```

### 步骤2：配置数据卷
1. 在Railway Dashboard中创建数据卷
2. 更新 `railway.toml` 配置
3. 重新部署服务

### 步骤3：验证数据持久化
```bash
# 1. 检查数据卷挂载
railway run ls -la /app/data/

# 2. 验证数据库文件存在
railway run python -c "import sqlite3; conn = sqlite3.connect('./data/personalfinance.db'); print('Database exists')"

# 3. 检查IBKR数据
railway run python -c "
from app.utils.database import get_db
from app.models.database import IBKRAccount, IBKRBalance, IBKRPosition
with next(get_db()) as db:
    accounts = db.query(IBKRAccount).count()
    balances = db.query(IBKRBalance).count()
    positions = db.query(IBKRPosition).count()
    print(f'IBKR数据: {accounts}个账户, {balances}条余额, {positions}条持仓')
"
```

### 步骤4：测试部署流程
1. 修改代码并推送
2. 观察GitHub Actions部署过程
3. 验证数据是否保留

## 📊 监控和维护

### 数据完整性检查
创建定期检查脚本 `backend/check_data_integrity.py`：

```python
#!/usr/bin/env python3
"""
数据完整性检查脚本
"""

from app.utils.database import get_db
from app.models.database import IBKRAccount, IBKRBalance, IBKRPosition
from datetime import datetime, timedelta

def check_ibkr_data_integrity():
    """检查IBKR数据完整性"""
    with next(get_db()) as db:
        # 检查账户数据
        accounts = db.query(IBKRAccount).all()
        print(f"IBKR账户数量: {len(accounts)}")
        
        # 检查最近24小时的余额数据
        yesterday = datetime.now() - timedelta(days=1)
        recent_balances = db.query(IBKRBalance).filter(
            IBKRBalance.created_at >= yesterday
        ).count()
        print(f"最近24小时余额记录: {recent_balances}")
        
        # 检查最近24小时的持仓数据
        recent_positions = db.query(IBKRPosition).filter(
            IBKRPosition.created_at >= yesterday
        ).count()
        print(f"最近24小时持仓记录: {recent_positions}")
        
        return len(accounts) > 0 and recent_balances > 0

if __name__ == "__main__":
    check_ibkr_data_integrity()
```

### 自动化监控
在Railway中设置健康检查端点：

```python
# 在 app/main.py 中添加
@app.get("/health/data")
async def health_check_data():
    """数据健康检查"""
    try:
        with next(get_db()) as db:
            # 检查关键表是否有数据
            ibkr_accounts = db.query(IBKRAccount).count()
            ibkr_balances = db.query(IBKRBalance).count()
            
            return {
                "status": "healthy",
                "data_integrity": {
                    "ibkr_accounts": ibkr_accounts,
                    "ibkr_balances": ibkr_balances,
                    "has_data": ibkr_accounts > 0 and ibkr_balances > 0
                }
            }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }
```

## 🚨 应急处理

### 数据丢失时的恢复流程
1. **立即停止部署**
   ```bash
   # 在GitHub Actions中取消正在进行的部署
   ```

2. **检查备份**
   ```bash
   python backup_database.py list
   ```

3. **恢复最新备份**
   ```bash
   python backup_database.py restore backups/latest_backup.db
   ```

4. **验证数据**
   ```bash
   python check_data_integrity.py
   ```

5. **重新配置数据卷**
   - 确保Railway数据卷正确配置
   - 重新部署服务

### 预防措施
1. **定期备份**
   - 每天自动备份重要数据
   - 保留多个备份版本

2. **部署前检查**
   - 确保数据卷配置正确
   - 验证备份文件完整性

3. **监控告警**
   - 设置数据完整性监控
   - 异常时及时通知

## 📋 检查清单

### 部署前检查
- [ ] 数据卷已正确配置
- [ ] 最新数据已备份
- [ ] 数据库连接正常
- [ ] 所有API端点可访问

### 部署后验证
- [ ] 数据卷正确挂载
- [ ] 数据库文件存在
- [ ] IBKR数据完整
- [ ] 其他数据完整
- [ ] 健康检查通过

### 定期维护
- [ ] 检查数据完整性
- [ ] 清理旧备份文件
- [ ] 监控磁盘空间
- [ ] 更新备份策略

## 🎯 预期效果

实施这些解决方案后：

1. **数据持久化**：IBKR数据在部署后不会丢失
2. **自动备份**：重要数据定期自动备份
3. **快速恢复**：数据丢失时可快速恢复
4. **监控告警**：及时发现数据问题
5. **部署安全**：部署过程不会影响现有数据

---

**最后更新**: 2024-12-19  
**状态**: ✅ 解决方案就绪  
**下一步**: 按照实施步骤逐步执行