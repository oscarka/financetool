# 一行命令快速调试

如果你不想使用脚本，可以直接使用这些一行命令：

## 快速获取错误日志
```bash
echo "=== Railway Debug Report ===" && echo "Time: $(date)" && echo "Project: $(railway status 2>/dev/null | grep -o 'Project: .*' || echo 'Unknown')" && echo "=== ERROR LOGS ===" && railway logs | grep -i "error\|exception\|fail\|panic" | tail -20 && echo -e "\n=== LATEST LOGS ===" && railway logs | tail -15
```

## 更简洁版本
```bash
railway logs | grep -E "(error|ERROR|Error|exception|Exception|fail|FAIL|Fail)" | tail -20
```

## 获取最新日志并格式化
```bash
echo "Latest Railway logs:" && railway logs | tail -30
```

## 保存到文件一行命令
```bash
(echo "Railway Debug Report - $(date)" && echo "Project: $(railway status 2>/dev/null | grep 'Project:' || echo 'Unknown')" && echo "=== ERRORS ===" && railway logs | grep -i error | tail -20 && echo -e "\n=== LATEST ===" && railway logs | tail -20) > debug_$(date +%Y%m%d_%H%M%S).log
```

复制任何一个命令的输出，然后发送给AI助手进行调试。