# Adam 计算器 MCP 工具

## 项目概述
`adam-calculator-mcp` 是一个功能完整的计算器 MCP 工具，提供多种数学运算功能，版本为 `0.1.1`。

## 功能特性
- 基础运算：加法、减法、乘法、除法
- 高级运算：幂运算、平方根
- 统计分析：平均值、最大值、最小值、方差、标准差
- 错误处理：完善的输入验证和异常处理

## 依赖要求
- Python 版本需 `>=3.10`
- 依赖的 Python 包：
  - `httpx>=0.28.1`
  - `mcp[cli]>=1.21.0`

## 安装方法

### 使用 pip 安装
```bash
pip install adam-calculator-mcp
```

### 使用 uvx 运行（无需安装）
```bash
uvx adam-calculator-mcp
```

## 使用方法

### 作为 MCP 服务器运行
```bash
# 直接运行
adam-calculator-mcp

# 使用 uvx 运行
uvx adam-calculator-mcp
```

### 在 Claude Desktop 中配置
在 `claude_desktop_config.json` 中添加：
```json
{
  "mcpServers": {
    "adam-calculator": {
      "command": "adam-calculator-mcp",
      "args": []
    }
  }
}
```

### 可用的工具函数
- `add(a, b)` - 加法运算
- `subtract(a, b)` - 减法运算
- `multiply(a, b)` - 乘法运算
- `divide(a, b)` - 除法运算（支持除零检查）
- `power(base, exponent)` - 幂运算
- `sqrt(value)` - 平方根（支持负数检查）
- `average(values)` - 计算平均值
- `stats(values)` - 统计分析（返回完整统计信息）

## 开发和使用示例

### Python 代码中使用
```python
from adam_calculator_mcp import add, multiply, stats

# 基础运算
result = add(10, 5)
print(f"10 + 5 = {result}")

# 统计分析
data = [1, 2, 3, 4, 5]
statistics = stats(data)
print(f"统计数据: {statistics}")
```

### MCP 客户端调用
安装后，你的 MCP 客户端可以自动发现并调用这些计算器工具。

## 配置要求
- 确保 Python 3.10+ 环境
- 网络连接正常（用于下载依赖）

## 错误处理
所有函数都包含完善的错误处理：
- 除法运算自动检查除零错误
- 平方根运算自动检查负数输入
- 统计函数自动检查空列表
- 提供清晰的错误信息

## 许可证
MIT License

## 作者信息
adam <adam@example.com>

## 项目地址
- 主页: https://github.com/adam/adam-calculator-mcp
- 问题反馈: https://github.com/adam/adam-calculator-mcp/issues

## 发布和安装

### 开发者发布流程
```bash
# 构建包
uv build

# 发布到 PyPI (需要配置认证)
uv publish

# 测试发布
uv publish --dry-run
```

### 用户安装和使用
```bash
# 使用 pip 安装
pip install adam-calculator-mcp

# 使用 uvx 直接运行 (无需安装)
uvx adam-calculator-mcp
