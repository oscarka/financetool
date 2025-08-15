# 🚀 MCP智能图表系统 - 完整实施指南

## 📋 系统概述

基于MCP (Model Context Protocol) 的智能图表生成系统，通过自然语言查询生成交互式图表。

### 🏗️ 系统架构

```
用户自然语言问题
        ↓
FastAPI Backend (Railway)
        ↓
MCP Database Server
        ↓
PostgreSQL Database (Railway)
        ↓
智能图表配置生成
        ↓
Flutter前端渲染
```

## 🛠️ 分步实施指南

### 第一步: 环境准备

```bash
# 1. 克隆项目
cd /workspace

# 2. 设置环境变量
export DATABASE_URL="postgresql://user:pass@railway.app:5432/railway"

# 3. 安装后端依赖
cd backend
pip install aiohttp fastapi uvicorn

# 4. 安装Node.js依赖（用于MCP服务器）
npm install
```

### 第二步: 运行测试验证

```bash
# 完整测试套件
python3 run_all_tests.py

# 或者分步测试
python3 run_all_tests.py --quick mcp-server
python3 run_all_tests.py --quick mcp-client  
python3 run_all_tests.py --quick chart-generator

# 保存测试报告
python3 run_all_tests.py --save-report
```

### 第三步: 启动服务

```bash
# 1. 启动MCP数据库服务器（后台运行）
cd backend
npx @anthropic-ai/mcp-server-postgres \
  --database-url $DATABASE_URL \
  --port 3001 &

# 2. 启动FastAPI后端
uvicorn app.main:app --reload --port 8000

# 3. 验证服务
curl http://localhost:8000/api/v1/mcp-smart-chart/health
```

### 第四步: API测试

```bash
# 测试图表生成
curl -X POST "http://localhost:8000/api/v1/mcp-smart-chart/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "显示各平台的资产分布",
    "base_currency": "CNY"
  }'

# 获取示例问题
curl http://localhost:8000/api/v1/mcp-smart-chart/examples
```

## 📱 Flutter集成

### 添加依赖

```yaml
# pubspec.yaml
dependencies:
  http: ^1.1.0
  fl_chart: ^0.69.0  # 已有
  shared_preferences: ^2.0.10  # 图表保存
```

### 服务类实现

```dart
// lib/services/mcp_chart_service.dart
class MCPChartService {
  static const String baseUrl = 'https://backend-production-2750.up.railway.app';
  
  Future<ChartResult> generateChart(String question) async {
    final response = await http.post(
      Uri.parse('$baseUrl/api/v1/mcp-smart-chart/generate'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'question': question,
        'base_currency': 'CNY'
      }),
    );
    
    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      return ChartResult.fromJson(data);
    } else {
      throw Exception('图表生成失败');
    }
  }
}
```

### UI集成

```dart
// 在AI对话页面中集成
class AIChatPage extends StatefulWidget {
  final MCPChartService _chartService = MCPChartService();
  
  void _handleUserMessage(String message) async {
    if (_isChartRequest(message)) {
      try {
        final chartResult = await _chartService.generateChart(message);
        
        // 显示图表
        setState(() {
          _messages.add(ChatMessage(
            text: "📊 ${chartResult.title}",
            isUser: false,
            chartWidget: _buildChartWidget(chartResult),
          ));
        });
        
        // 保存到深度分析页面
        await _saveToAnalysisPage(chartResult);
        
      } catch (e) {
        _showError(e.toString());
      }
    }
  }
  
  Widget _buildChartWidget(ChartResult result) {
    switch (result.chartType) {
      case 'bar':
        return BarChart(/* fl_chart配置 */);
      case 'line':
        return LineChart(/* fl_chart配置 */);
      case 'pie':
        return PieChart(/* fl_chart配置 */);
      default:
        return DataTable(/* 表格配置 */);
    }
  }
}
```

## 🔧 系统配置

### 环境变量

```bash
# .env 文件
DATABASE_URL=postgresql://user:pass@railway.app:5432/railway
MCP_SERVER_PORT=3001
API_BASE_URL=https://backend-production-2750.up.railway.app
```

### MCP服务器配置

```json
// backend/package.json
{
  "dependencies": {
    "@anthropic-ai/mcp-server-postgres": "^0.4.0"
  },
  "scripts": {
    "start-mcp": "mcp-server-postgres --database-url $DATABASE_URL --port 3001"
  }
}
```

## 📊 支持的查询类型

### 平台分析
- "显示各平台的资产分布"
- "对比不同平台的收益"
- "哪个平台资产最多"

### 资产类型分析
- "各资产类型的占比"
- "投资组合的结构分析"
- "基金和股票的比例"

### 趋势分析
- "最近30天的资产变化趋势"
- "资产价值走势图"
- "历史收益变化"

### 详细查询
- "详细的交易记录"
- "投资明细表"
- "资产详情列表"

## 🐛 故障排除

### 常见问题

#### 1. MCP服务器连接失败
```bash
# 检查服务器状态
curl http://localhost:3001/health

# 重启MCP服务器
pkill -f mcp-server-postgres
npx @anthropic-ai/mcp-server-postgres --database-url $DATABASE_URL --port 3001
```

#### 2. 数据库连接问题
```bash
# 验证数据库连接
psql $DATABASE_URL -c "SELECT COUNT(*) FROM asset_snapshot;"

# 检查表结构
psql $DATABASE_URL -c "\dt"
```

#### 3. API响应超时
```python
# 在MCP客户端中增加超时设置
self.timeout = aiohttp.ClientTimeout(total=60)  # 增加到60秒
```

#### 4. 图表数据为空
```sql
-- 检查数据是否存在
SELECT COUNT(*) FROM asset_snapshot WHERE snapshot_time >= NOW() - INTERVAL '30 days';

-- 检查最新快照时间
SELECT MAX(snapshot_time) FROM asset_snapshot;
```

### 日志调试

```python
# 启用详细日志
import logging
logging.basicConfig(level=logging.DEBUG)

# 检查MCP服务器日志
tail -f /var/log/mcp-server.log
```

## 📈 性能优化

### 数据库优化
```sql
-- 添加索引
CREATE INDEX IF NOT EXISTS idx_asset_snapshot_time ON asset_snapshot(snapshot_time);
CREATE INDEX IF NOT EXISTS idx_asset_snapshot_platform ON asset_snapshot(platform);
```

### 缓存策略
```python
# 在MCP客户端中添加缓存
from functools import lru_cache

@lru_cache(maxsize=128)
def cached_query(question: str, base_currency: str):
    # 缓存常见查询结果
    pass
```

## 🚀 部署到生产环境

### Railway部署

```bash
# 1. 添加MCP服务器启动脚本
echo "npm start &" >> Procfile
echo "uvicorn app.main:app --host 0.0.0.0 --port \$PORT" >> Procfile

# 2. 设置环境变量
railway variables set MCP_SERVER_PORT=3001
railway variables set NODE_ENV=production

# 3. 部署
railway up
```

### 健康检查

```bash
# 创建健康检查脚本
cat > health_check.sh << 'EOF'
#!/bin/bash
curl -f http://localhost:8000/api/v1/mcp-smart-chart/health || exit 1
curl -f http://localhost:3001/health || exit 1
echo "所有服务正常运行"
EOF

chmod +x health_check.sh
```

## 📋 下一步扩展

### 功能增强
1. **语音输入** - 集成语音识别
2. **图表导出** - 支持PNG/PDF导出
3. **实时更新** - WebSocket实时数据
4. **高级分析** - 机器学习预测

### 技术升级
1. **缓存层** - Redis缓存热点查询
2. **消息队列** - 异步处理复杂查询
3. **监控告警** - Prometheus + Grafana
4. **A/B测试** - 不同图表算法对比

## 🎯 成功验收标准

- [ ] MCP服务器稳定运行
- [ ] API响应时间 < 5秒
- [ ] 图表生成成功率 > 90%
- [ ] Flutter集成无错误
- [ ] 用户体验流畅

## 📞 技术支持

遇到问题时，请按以下顺序排查：
1. 运行测试套件确认各组件状态
2. 检查日志文件定位具体错误
3. 参考故障排除章节
4. 查看API文档确认请求格式
5. 验证数据库数据完整性

---

**🎉 恭喜！现在你有了一个完整的MCP驱动的智能图表系统！**