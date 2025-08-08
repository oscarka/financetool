# 个人金融仪表板 Flutter Web版

这是一个基于Flutter Web的个人金融仪表板应用，提供资产分布、实时数据展示等功能。

## 功能特性

- 📊 实时资产分布展示
- 💰 多货币支持 (USD, CNY, USDT, BTC)
- 📈 24小时资产变化趋势
- 🎯 风险等级评估
- 📱 响应式设计

## 本地开发

### 环境要求
- Flutter SDK 3.1.5+
- Dart SDK 3.1.5+

### 运行步骤
1. 安装依赖：
```bash
flutter pub get
```

2. 启动后端服务：
```bash
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

3. 运行Flutter Web应用：
```bash
flutter run -d web-server --web-port=8080 --web-hostname=0.0.0.0
```

## Railway部署

### 自动部署
1. 将代码推送到GitHub仓库
2. 在Railway中连接GitHub仓库
3. Railway会自动检测Flutter项目并部署

### 环境变量配置
在Railway中设置以下环境变量：
- `DATABASE_URL`: PostgreSQL连接字符串
- `DATABASE_PERSISTENT_PATH`: 数据持久化路径

### 部署配置
- 使用Nixpacks构建器
- 自动安装Flutter和Dart
- 构建Web版本并启动服务器

## 项目结构

```
lib/
├── main.dart              # 主应用入口
├── models/                # 数据模型
│   ├── asset_stats.dart   # 资产统计模型
│   └── trend_data.dart    # 趋势数据模型
├── services/              # 服务层
│   └── api_client.dart    # API客户端
└── widgets/               # 自定义组件
```

## API接口

应用依赖以下后端API：
- `/api/v1/aggregation/stats` - 聚合统计数据
- `/api/v1/aggregation/trend` - 趋势数据
- `/api/v1/snapshot/assets` - 资产快照数据

## 技术栈

- **前端**: Flutter Web
- **状态管理**: Flutter内置状态管理
- **图表**: fl_chart
- **HTTP客户端**: http package
- **部署**: Railway + Nixpacks

## 许可证

MIT License
