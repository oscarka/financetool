# IBKR 集成实施方案

## 📊 概览

为多资产投资系统增加 **Interactive Brokers (IBKR)** API 集成，支持股票、期权、期货等传统金融产品的交易和数据获取。

## 🎯 技术方案

### API 选择：Client Portal REST API
- **认证方式**：Gateway + OAuth（推荐使用社区工具）
- **数据格式**：JSON REST API
- **实时数据**：REST + WebSocket
- **部署方式**：Docker 容器化

### 社区工具集成
使用成熟的开源工具简化集成：

1. **IBeam** (688⭐) - Gateway 认证和维护
   - 自动化登录和会话管理
   - Docker 容器化部署
   - 无头模式运行

2. **IBind** (257⭐) - Python 客户端库
   - REST 和 WebSocket 支持
   - 自动错误处理和重试
   - 完整的 API 覆盖

## 🏗️ 架构设计

### 1. 新增文件结构

```
backend/
├── docker-compose.ibkr.yml     # IBKR 服务编排
├── app/
│   ├── services/
│   │   └── ibkr_api_service.py   # IBKR API 服务层
│   ├── api/v1/
│   │   └── ibkr.py               # IBKR REST 接口
│   ├── models/
│   │   └── ibkr_models.py        # IBKR 数据模型
│   └── utils/
│       └── ibkr_client.py        # IBKR 客户端封装
├── config/
│   └── ibkr.env                  # IBKR 环境配置
└── requirements.txt              # 更新依赖
```

### 2. 数据模型扩展

新增 IBKR 相关数据表：
- `ibkr_accounts` - IBKR 账户信息
- `ibkr_positions` - 持仓数据
- `ibkr_orders` - 订单记录
- `ibkr_executions` - 成交记录
- `ibkr_market_data` - 市场数据
- `ibkr_pnl` - 盈亏数据

### 3. 服务层设计

#### IbkrApiService 主要功能：
```python
class IbkrApiService:
    # 账户管理
    async def get_accounts()
    async def get_account_summary()
    async def get_positions()
    async def get_pnl()
    
    # 市场数据
    async def get_market_data()
    async def get_historical_data()
    async def search_contracts()
    
    # 交易功能
    async def place_order()
    async def modify_order()
    async def cancel_order()
    async def get_order_status()
    
    # 实时数据
    async def subscribe_market_data()
    async def subscribe_pnl_updates()
```

### 4. API 接口设计

按照现有模式设计 REST 接口：

```python
# /api/v1/ibkr/accounts
# /api/v1/ibkr/positions  
# /api/v1/ibkr/orders
# /api/v1/ibkr/market-data
# /api/v1/ibkr/historical-data
# /api/v1/ibkr/contracts/search
```

## 🔧 实施步骤

### Phase 1: 基础设施搭建 (1-2周)

1. **环境配置**
   ```bash
   # 新增依赖
   pip install ibeam ibind requests-oauthlib
   ```

2. **Docker 服务**
   ```yaml
   # docker-compose.ibkr.yml
   services:
     ibeam:
       image: voyz/ibeam
       environment:
         - IBEAM_ACCOUNT=${IBKR_ACCOUNT}
         - IBEAM_PASSWORD=${IBKR_PASSWORD}
       ports:
         - "5000:5000"
   ```

3. **基础服务类**
   - 创建 `IbkrApiService`
   - 实现基础认证和连接
   - 添加配置管理

### Phase 2: 核心功能开发 (2-3周)

1. **账户数据集成**
   - 账户信息同步
   - 持仓数据获取
   - 盈亏计算

2. **市场数据功能**
   - 实时价格订阅
   - 历史数据获取
   - 合约搜索

3. **交易功能**
   - 下单接口
   - 订单管理
   - 成交回报

### Phase 3: 高级功能 (1-2周)

1. **实时数据流**
   - WebSocket 集成
   - 数据推送
   - 订阅管理

2. **风险管理**
   - 仓位限制
   - 风险指标
   - 报警机制

### Phase 4: 集成测试 (1周)

1. **功能测试**
   - API 接口测试
   - 数据一致性验证
   - 错误处理测试

2. **性能优化**
   - 请求限频
   - 缓存策略
   - 连接池优化

## 💻 代码示例

### 服务层实现示例

```python
# app/services/ibkr_api_service.py
from ibind import IbkrClient
from typing import Optional, Dict, Any, List
import asyncio
from app.config import settings

class IbkrApiService:
    def __init__(self):
        self.client = IbkrClient(
            base_url=settings.ibkr_gateway_url,
            cacert=settings.ibkr_cacert_path
        )
    
    async def get_accounts(self) -> List[Dict[str, Any]]:
        """获取账户列表"""
        try:
            response = self.client.portfolio_accounts()
            return response.data if response.success else []
        except Exception as e:
            logger.error(f"获取IBKR账户失败: {e}")
            return []
    
    async def get_positions(self, account_id: str) -> List[Dict[str, Any]]:
        """获取持仓信息"""
        try:
            response = self.client.portfolio_positions(account_id)
            return response.data if response.success else []
        except Exception as e:
            logger.error(f"获取IBKR持仓失败: {e}")
            return []
```

### API 路由实现示例

```python
# app/api/v1/ibkr.py
from fastapi import APIRouter, HTTPException
from app.services.ibkr_api_service import IbkrApiService

router = APIRouter(prefix="/ibkr", tags=["IBKR API"])
ibkr_service = IbkrApiService()

@router.get("/accounts")
async def get_ibkr_accounts():
    """获取IBKR账户列表"""
    try:
        accounts = await ibkr_service.get_accounts()
        return {
            "success": True,
            "data": accounts,
            "count": len(accounts)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取账户失败: {str(e)}")

@router.get("/positions/{account_id}")
async def get_ibkr_positions(account_id: str):
    """获取指定账户持仓"""
    try:
        positions = await ibkr_service.get_positions(account_id)
        return {
            "success": True,
            "data": positions,
            "count": len(positions)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取持仓失败: {str(e)}")
```

## 🔒 安全考虑

1. **认证安全**
   - 使用环境变量存储敏感信息
   - 考虑使用 Docker Secrets
   - 定期轮换认证令牌

2. **网络安全**
   - HTTPS 通信
   - IP 白名单限制
   - API 限频保护

3. **数据安全**
   - 敏感数据加密存储
   - 审计日志记录
   - 访问权限控制

## 📈 监控和维护

1. **健康检查**
   - Gateway 连接状态
   - API 响应时间
   - 错误率监控

2. **日志管理**
   - 结构化日志记录
   - 错误告警机制
   - 性能指标追踪

3. **定期维护**
   - Gateway 重启策略
   - 数据清理任务
   - 性能优化

## 🚀 部署方案

### 开发环境
```bash
# 启动 IBKR Gateway
docker-compose -f docker-compose.ibkr.yml up -d

# 启动后端服务
python -m app.main
```

### 生产环境
```bash
# 完整服务栈
docker-compose up -d
```

## 📋 注意事项

1. **IBKR 账户要求**
   - 需要 IBKR Pro 账户（不支持 Lite）
   - 需要启用 API 权限
   - 建议先用纸交易测试

2. **技术限制**
   - 24小时认证过期需要重新登录
   - 并发连接数限制
   - 市场数据订阅费用

3. **合规要求**
   - 遵守 IBKR 使用条款
   - 注意交易监管要求
   - 保留审计追踪

## 🔗 有用资源

- [IBKR Web API 文档](https://www.interactivebrokers.com/campus/ibkr-api-page/cpapi/)
- [IBeam 项目](https://github.com/Voyz/ibeam)
- [IBind 项目](https://github.com/Voyz/ibind)
- [IBKR 开发者论坛](https://groups.io/g/twsapi)

---

**预估开发时间：4-6周**  
**技术难度：中等**  
**投资回报：高** (传统金融市场全覆盖)