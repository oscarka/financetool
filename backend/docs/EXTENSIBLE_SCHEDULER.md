# 可扩展定时任务系统

## 概述

新的可扩展定时任务系统提供了更灵活、更强大的任务管理能力，支持插件化架构、事件驱动、动态配置等特性。

## 核心特性

### 1. 插件化架构
- **动态加载**: 支持热插拔插件，无需重启服务
- **标准化接口**: 统一的插件和任务接口规范
- **依赖管理**: 自动处理插件间的依赖关系

### 2. 事件驱动
- **事件总线**: 任务间通过事件通信
- **事件历史**: 记录和查询事件历史
- **异步处理**: 全异步架构，提高并发性能

### 3. 灵活调度
- **多种调度方式**: Cron、间隔、一次性任务
- **动态配置**: 支持运行时修改任务配置
- **条件执行**: 支持基于条件的任务执行

### 4. 集成服务
- **基金服务**: 净值更新、定投执行、持仓同步
- **Wise服务**: 余额同步、交易同步、汇率同步
- **OKX服务**: 余额同步、持仓同步、市场数据
- **IBKR服务**: 余额同步、持仓同步

## 系统架构

```
可扩展调度器系统
├── PluginManager (插件管理器)
│   ├── 插件注册/注销
│   ├── 插件生命周期管理
│   └── 插件依赖解析
├── TaskEngine (任务引擎)
│   ├── 任务调度器
│   ├── 任务执行器
│   └── 任务状态管理
├── EventBus (事件总线)
│   ├── 事件发布/订阅
│   ├── 事件路由
│   └── 事件持久化
└── StorageLayer (存储层)
    ├── 任务定义存储
    ├── 执行记录存储
    └── 事件日志存储
```

## 使用方法

### 1. API接口

#### 获取调度器状态
```bash
GET /api/v1/scheduler/status
```

#### 获取插件列表
```bash
GET /api/v1/scheduler/plugins
```

#### 获取任务定义
```bash
GET /api/v1/scheduler/tasks
```

#### 获取定时任务
```bash
GET /api/v1/scheduler/jobs
```

#### 创建定时任务
```bash
POST /api/v1/scheduler/jobs
Content-Type: application/json

{
    "job_id": "fund_nav_daily_update",
    "name": "每日基金净值更新",
    "task_id": "fund_nav_update",
    "schedule": {
        "type": "cron",
        "hour": 15,
        "minute": 30,
        "second": 0
    },
    "config": {
        "update_all": true,
        "data_source": "tiantian",
        "retry_times": 3
    }
}
```

#### 立即执行任务
```bash
POST /api/v1/scheduler/jobs/fund_nav_update/execute
Content-Type: application/json

{
    "update_all": false,
    "fund_codes": ["000001", "000002"]
}
```

#### 暂停/恢复任务
```bash
POST /api/v1/scheduler/jobs/{job_id}/pause
POST /api/v1/scheduler/jobs/{job_id}/resume
```

#### 删除任务
```bash
DELETE /api/v1/scheduler/jobs/{job_id}
```

### 2. 任务配置示例

#### Cron调度
```python
{
    "type": "cron",
    "hour": 15,
    "minute": 30,
    "second": 0
}
```

#### 间隔调度
```python
{
    "type": "interval",
    "hours": 1
}
```

#### 一次性任务
```python
{
    "type": "date",
    "run_date": "2024-12-31 23:59:59"
}
```

### 3. 可用任务

#### 基金相关任务
- `fund_nav_update`: 基金净值更新
- `dca_execute`: 定投计划执行
- `fund_position_sync`: 基金持仓同步

#### Wise相关任务
- `wise_balance_sync`: Wise余额同步
- `wise_transaction_sync`: Wise交易同步
- `wise_exchange_rate_sync`: Wise汇率同步

#### OKX相关任务
- `okx_balance_sync`: OKX余额同步
- `okx_position_sync`: OKX持仓同步
- `okx_market_data_sync`: OKX市场数据同步

#### IBKR相关任务
- `ibkr_balance_sync`: IBKR余额同步
- `ibkr_position_sync`: IBKR持仓同步

#### 数据处理任务
- `data_cleanup`: 数据清理
- `data_backup`: 数据备份
- `report_generation`: 报表生成

## 开发指南

### 1. 创建新插件

```python
from app.core.base_plugin import BaseTaskPlugin
from typing import Dict, Any, List

class MyPlugin(BaseTaskPlugin):
    def __init__(self):
        super().__init__()
        self.plugin_id = "my_plugin"
        self.plugin_name = "我的插件"
        self.version = "1.0.0"
        self.description = "我的自定义插件"
        
    async def register_tasks(self) -> List[Dict[str, Any]]:
        return [
            {
                "task_id": "my_task",
                "name": "我的任务",
                "description": "自定义任务描述",
                "class": "app.plugins.my_plugin.tasks.my_task.MyTask"
            }
        ]
```

### 2. 创建新任务

```python
from app.core.base_task import BaseTask
from app.core.context import TaskContext, TaskResult

class MyTask(BaseTask):
    async def execute(self, context: TaskContext) -> TaskResult:
        try:
            # 任务执行逻辑
            context.log("开始执行我的任务")
            
            # 获取配置
            param = context.get_config('param', 'default')
            
            # 执行操作
            result_data = {"processed": True, "param": param}
            
            # 发布事件
            if context.event_bus:
                await context.event_bus.publish('my.task.completed', result_data)
            
            return TaskResult(success=True, data=result_data)
            
        except Exception as e:
            return TaskResult(success=False, error=str(e))
```

### 3. 事件处理

```python
# 订阅事件
event_bus.subscribe('my.task.completed', handle_task_completed)

async def handle_task_completed(event):
    print(f"任务完成: {event['data']}")
```

## 测试

运行测试脚本：
```bash
cd backend
python test_extensible_scheduler.py
```

## 配置说明

### 环境变量
- `ENABLE_SCHEDULER`: 是否启用调度器 (默认: true)
- `SCHEDULER_TIMEZONE`: 调度器时区 (默认: Asia/Shanghai)

### 默认任务配置
系统启动时会自动创建以下默认任务：
- 基金净值更新 (每天15:30)
- Wise余额同步 (每天16:30)
- OKX余额同步 (每小时)
- IBKR余额同步 (每天17:00)
- 数据清理 (每周日2:00)
- 报表生成 (每月1日6:00)

## 监控和日志

### 事件监控
- 任务开始/完成/失败事件
- 业务事件 (基金更新、余额同步等)
- 系统事件 (插件加载、调度器状态等)

### 日志记录
- 任务执行日志
- 错误和异常日志
- 性能监控日志

## 故障排除

### 常见问题

1. **任务执行失败**
   - 检查任务配置是否正确
   - 查看错误日志
   - 验证依赖服务是否可用

2. **插件加载失败**
   - 检查插件路径是否正确
   - 验证插件类是否继承自BaseTaskPlugin
   - 查看插件初始化日志

3. **调度器不启动**
   - 检查ENABLE_SCHEDULER环境变量
   - 验证时区配置
   - 查看启动日志

### 调试模式
设置环境变量启用调试模式：
```bash
export DEBUG=true
export LOG_LEVEL=DEBUG
```

## 性能优化

1. **任务并发控制**
   - 设置合适的max_instances
   - 使用coalesce避免任务堆积

2. **事件处理优化**
   - 异步处理事件
   - 限制事件历史记录数量

3. **数据库优化**
   - 使用连接池
   - 定期清理历史数据

## 扩展计划

1. **工作流引擎**
   - 支持任务链和条件分支
   - 可视化工作流设计

2. **分布式支持**
   - 多节点任务调度
   - 任务负载均衡

3. **监控面板**
   - Web界面管理
   - 实时监控和告警

4. **更多插件**
   - 邮件通知插件
   - 数据导出插件
   - 第三方集成插件 