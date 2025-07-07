# Railway 日志调试助手设置指南

## 问题
你想让AI助手帮你调试Railway上的bug，但不想手动复制粘贴日志。

## 解决方案
我无法直接访问你的Railway账户，但提供了几个工具来简化获取日志的过程。

## 方法1：一键快速调试 (推荐)

使用 `quick_debug.sh` 脚本：

```bash
# 运行快速调试脚本
./quick_debug.sh
```

这个脚本会自动：
- 检查项目状态
- 获取错误日志 (最近50条)
- 获取警告日志 (最近20条)  
- 获取最新日志 (最近30条)

输出结果可以直接复制给AI助手分析。

## 方法2：详细日志获取

使用 `get_railway_logs.sh` 脚本：

```bash
# 获取错误日志并保存到文件
./get_railway_logs.sh -f "@level:error" -o error_logs.txt

# 获取构建日志
./get_railway_logs.sh -t build -o build_logs.txt

# 获取最近100行部署日志
./get_railway_logs.sh -t deployment -l 100
```

## 方法3：原生CLI命令

如果你想直接使用Railway CLI：

```bash
# 获取错误日志
railway logs | grep -i "error\|exception\|fail"

# 获取最新日志  
railway logs | tail -50

# 保存到文件
railway logs > logs.txt
```

## 方法4：使用Railway Web界面

1. 登录 railway.com
2. 进入你的项目
3. 点击顶部的 "Observability"
4. 使用过滤器：`@level:error` 或其他条件
5. 复制相关日志

## 设置步骤

1. **安装Railway CLI**：
   ```bash
   npm install -g @railway/cli
   ```

2. **登录并连接项目**：
   ```bash
   railway login
   railway link
   ```

3. **使用脚本**：
   ```bash
   # 给脚本执行权限
   chmod +x *.sh
   
   # 运行快速调试
   ./quick_debug.sh
   ```

## 调试工作流

1. 发现bug后，运行 `./quick_debug.sh`
2. 复制输出的日志内容
3. 发送给AI助手，说明遇到的问题
4. AI助手根据日志分析问题并提供解决方案

## 常用过滤条件

当使用详细脚本时，可以用这些过滤条件：

```bash
# 错误日志
./get_railway_logs.sh -f "@level:error"

# 特定路径的错误
./get_railway_logs.sh -f "@path:/api AND @level:error"

# 数据库相关错误
./get_railway_logs.sh -f "database OR connection"

# HTTP 500错误
./get_railway_logs.sh -f "@httpStatus:500"
```

## 提示

- 使用 `quick_debug.sh` 可以快速获取最有用的调试信息
- 如果需要更详细的日志，使用 `get_railway_logs.sh`
- 发送日志给AI时，请简要描述遇到的问题
- 可以先用过滤条件筛选相关日志，避免信息过多

这样你就能快速获取日志并让AI助手帮你调试问题了！