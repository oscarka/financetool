# 移动端功能测试指南

## 快速测试步骤

### 1. 部署应用
```bash
# 在前端目录
cd frontend
npm run build

# 部署到您的服务器或本地测试
# 确保后端服务正在运行
```

### 2. 移动设备测试

#### 方法一：真实移动设备
1. 在移动设备浏览器中访问您的应用URL
2. 应用会自动检测并显示移动端界面

#### 方法二：桌面浏览器移动模拟
1. 打开Chrome浏览器
2. 按F12打开开发者工具
3. 点击设备模拟按钮（📱图标）
4. 选择移动设备型号（如iPhone 12）
5. 刷新页面

### 3. 功能测试清单

#### 持仓管理页面 (/positions)
- [ ] **数据显示**：确认持仓数据正确显示
- [ ] **刷新功能**：点击右上角刷新按钮
- [ ] **详情查看**：点击持仓卡片的"详情"按钮
- [ ] **基金信息**：点击"基金"按钮
- [ ] **买入/卖出**：点击绿色"买入"和红色"卖出"按钮
- [ ] **悬浮按钮**：点击右下角悬浮按钮组
- [ ] **持仓汇总**：查看顶部汇总卡片数据

#### 操作记录页面 (/operations)
- [ ] **记录显示**：确认操作记录正确显示
- [ ] **查看详情**：点击操作卡片的眼睛图标
- [ ] **编辑功能**：点击编辑图标（显示功能提示）
- [ ] **删除功能**：点击删除图标并确认
- [ ] **筛选功能**：点击右上角筛选按钮
- [ ] **加载更多**：滚动到底部加载更多记录

#### 仪表板页面 (/)
- [ ] **真实数据**：确认显示真实投资数据而非静态数据
- [ ] **快速操作**：点击4个快速操作卡片
- [ ] **进度条**：查看收益率进度条显示
- [ ] **盈亏分布**：查看基金盈亏分布图表

#### 基金管理页面 (/funds)
- [ ] **模块导航**：点击6个功能模块
- [ ] **快速入口**：点击底部快速入口卡片

### 4. 兼容性测试

#### 确认桌面端不受影响
1. 在桌面浏览器中访问相同URL
2. 确认显示桌面版界面
3. 测试桌面版所有功能正常

#### 响应式测试
1. 调整浏览器窗口大小
2. 确认在不同尺寸下正确切换界面

### 5. 常见问题排查

#### 数据不显示
1. 检查浏览器控制台是否有API错误
2. 确认后端服务正在运行
3. 检查网络连接

#### 按钮无响应
1. 检查浏览器控制台是否有JavaScript错误
2. 确认页面完全加载
3. 尝试刷新页面

#### 界面显示异常
1. 确认使用的是移动设备或移动模拟模式
2. 检查浏览器是否支持最新特性
3. 清除浏览器缓存

### 6. 性能测试

#### 加载速度
- [ ] 首次加载时间 < 3秒
- [ ] 页面切换流畅
- [ ] 数据刷新响应及时

#### 交互响应
- [ ] 按钮点击响应 < 300ms
- [ ] 滚动流畅无卡顿
- [ ] 弹窗打开关闭流畅

### 7. 报告问题

如果发现问题，请提供：
1. **设备信息**：操作系统、浏览器版本
2. **复现步骤**：详细操作步骤
3. **错误信息**：浏览器控制台错误截图
4. **预期行为**：预期应该发生什么
5. **实际行为**：实际发生了什么

### 8. 已知待实现功能

以下功能已建立框架，但需要进一步开发：
- 完整的买入/卖出交易逻辑
- 操作记录编辑功能
- 基金详情页面
- 高级筛选功能

## 测试结果记录模板

```
测试日期：_______
测试设备：_______
测试浏览器：_______

持仓管理页面：
□ 数据显示正常
□ 所有按钮可点击
□ 功能响应正常
□ 界面显示正确

操作记录页面：
□ 记录显示正常
□ 交互功能正常
□ 筛选功能正常

仪表板页面：
□ 真实数据显示
□ 快速操作正常
□ 图表显示正确

发现问题：
_________________
_________________
_________________

整体评价：
□ 非常满意
□ 基本满意
□ 需要改进
```

## 联系支持

如需技术支持或有任何问题，请通过以下方式联系：
- 提供详细的测试结果
- 包含浏览器控制台截图
- 说明具体的操作步骤