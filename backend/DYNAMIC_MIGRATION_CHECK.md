# 动态数据库迁移检查机制

## 🎯 问题背景

### 原有硬编码方式的问题
```python
# 每次数据库变更都需要修改这里
required_tables = {
    'okx_transactions': [
        'id', 'transaction_id', 'account_id', 'inst_type', 'inst_id', 
        'trade_id', 'order_id', 'bill_id', 'type', 'side', 'amount', 
        'currency', 'fee', 'fee_currency', 'price', 'quantity', 
        'timestamp', 'created_at', 'bal', 'bal_chg', 'ccy', 'cl_ord_id',
        # ... 40个字段全部硬编码
    ],
    # ... 25个表全部硬编码
}
```

**维护成本**:
- ❌ 每次添加新表都要修改 `run.py`
- ❌ 每次添加新字段都要修改 `run.py`
- ❌ 容易遗漏或出错
- ❌ 代码重复，违反DRY原则

---

## 🔧 解决方案

### 方案1: 动态从SQLAlchemy模型生成 (已实现)

**核心思想**: 直接从SQLAlchemy模型定义中动态生成检查规则

```python
def check_database_compatibility(conn):
    """检查数据库兼容性"""
    # 动态从SQLAlchemy模型生成检查规则
    try:
        from app.models.database import Base
        from sqlalchemy import inspect
        
        # 获取所有模型类
        inspector = inspect(Base)
        required_tables = {}
        
        # 遍历所有模型，动态生成字段列表
        for table_name in Base.metadata.tables:
            table = Base.metadata.tables[table_name]
            required_fields = [column.name for column in table.columns]
            required_tables[table_name] = required_fields
            
        print(f"📊 动态生成检查规则: {len(required_tables)} 个表")
        
    except ImportError as e:
        print(f"⚠️  无法导入模型，使用备用检查方法: {e}")
        return check_database_basic_compatibility(conn)
```

**优势**:
- ✅ **自动同步**: 模型变更自动反映到检查规则
- ✅ **零维护**: 无需手动更新检查代码
- ✅ **一致性保证**: 检查规则与模型定义100%一致
- ✅ **错误减少**: 避免人工维护导致的错误

---

## 🛡️ 备用方案

### 基础检查机制
当无法导入模型时，使用简化的检查：

```python
def check_database_basic_compatibility(conn):
    """基础数据库兼容性检查（备用方案）"""
    # 只检查关键表的存在性
    critical_tables = [
        'user_operations', 'asset_positions', 'fund_info', 
        'wise_transactions', 'okx_transactions', 'asset_snapshot'
    ]
    
    for table_name in critical_tables:
        # 检查表是否存在
        # 不检查具体字段，只确保关键表存在
```

**适用场景**:
- 🔧 模型导入失败时
- 🧪 测试环境
- 🚀 快速部署验证

---

## 📊 维护成本对比

| 方面 | 硬编码方式 | 动态生成方式 |
|------|------------|--------------|
| **新增表** | 需要修改 `run.py` | 自动同步 |
| **新增字段** | 需要修改 `run.py` | 自动同步 |
| **删除表** | 需要修改 `run.py` | 自动同步 |
| **字段重命名** | 需要修改 `run.py` | 自动同步 |
| **维护成本** | 高 | 零 |
| **错误风险** | 高 | 低 |
| **一致性** | 需要人工保证 | 自动保证 |

---

## 🚀 使用方式

### 正常情况
```python
# 自动从模型生成检查规则
check_database_compatibility(conn)
```

### 异常情况
```python
# 如果模型导入失败，自动降级到基础检查
check_database_basic_compatibility(conn)
```

---

## 🔄 未来扩展

### 方案2: 配置文件方式
```yaml
# migration_check_config.yaml
tables:
  user_operations:
    required: true
    critical_fields: ['id', 'operation_date', 'amount']
  asset_positions:
    required: true
    critical_fields: ['id', 'platform', 'asset_code']
```

### 方案3: 数据库Schema版本控制
```python
# 基于数据库Schema版本进行检查
def check_schema_version_compatibility(conn):
    schema_version = get_current_schema_version(conn)
    expected_version = get_expected_schema_version()
    return schema_version == expected_version
```

---

## ✅ 总结

**新的动态检查机制解决了以下问题**:

1. **🔄 自动同步**: 模型变更自动反映到检查规则
2. **🛡️ 零维护**: 无需手动更新检查代码
3. **📊 一致性**: 检查规则与模型定义100%一致
4. **🚀 可靠性**: 减少人工维护导致的错误
5. **🛡️ 备用方案**: 异常情况下有降级机制

**现在当你升级数据库时**:
- ✅ 只需要修改SQLAlchemy模型
- ✅ 只需要创建Alembic迁移文件
- ✅ `run.py` 中的检查逻辑自动适应
- ✅ 无需手动维护检查规则

这大大降低了维护成本，提高了系统的可靠性和一致性。 