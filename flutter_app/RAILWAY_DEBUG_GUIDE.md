# Railway Flutter部署调试指南

## 问题分析

Railway部署失败，错误信息：`/start.sh: not found`

## 解决方案

### 1. 修复的问题

1. **Dockerfile路径问题**：确保Railway使用正确的Dockerfile
2. **nginx配置冲突**：原配置包含完整http块，与nginx Alpine默认配置冲突
3. **启动脚本权限**：确保脚本有执行权限
4. **调试信息**：添加详细日志帮助诊断

### 2. 主要修改

#### Dockerfile增强
- 添加详细的构建和运行时调试信息
- 确保所有文件正确复制
- 添加健康检查功能
- 改用只包含server块的nginx配置

#### nginx配置优化
- 创建`nginx.conf.server`，只包含server块配置
- 避免与nginx默认配置冲突
- 保留健康检查和调试端点

#### Railway配置
- 明确指定`dockerfilePath = "Dockerfile"`
- 增加重试次数配置

### 3. 部署选项

#### 选项A：使用增强版Dockerfile
```bash
# 使用默认Dockerfile（已增强）
railway up --detach
```

#### 选项B：使用简化版Dockerfile
如果主Dockerfile仍有问题，可以使用简化版：
```bash
# 重命名文件
mv Dockerfile Dockerfile.enhanced
mv Dockerfile.simple Dockerfile
railway up --detach
```

### 4. 调试步骤

1. **检查构建日志**：查看Docker构建过程中的调试输出
2. **检查启动日志**：查看容器启动时的详细信息
3. **访问调试端点**：
   - `/health` - 健康检查
   - `/debug` - 详细调试信息
   - `/simple.html` - 备用页面

### 5. 常见问题

1. **文件权限**：已在Dockerfile中设置正确权限
2. **路径问题**：使用绝对路径避免相对路径问题
3. **环境变量**：确保PORT变量正确传递

### 6. 验证部署

部署成功后，应该能看到：
- 主页面显示Flutter应用
- `/health`返回"healthy"
- `/debug`显示详细调试信息
- 日志显示详细的启动过程

## 下一步

1. 推送更改到Railway
2. 监控部署日志
3. 检查应用是否正常运行
4. 如有问题，查看调试端点获取更多信息
