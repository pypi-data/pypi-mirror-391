from mcp.server.fastmcp import FastMCP
import math
from typing import List

# ==================================
# 创建 MCP 服务
# ==================================
mcp = FastMCP("calculatorTools")


# ==================================
# 工具 1：加法
# ==================================
@mcp.tool(description="执行两个数的加法运算")
def add(a: float, b: float) -> float:
    """
    功能说明：
        将两个数相加并返回结果。

    参数说明：
        - a (float): 第一个加数
        - b (float): 第二个加数

    返回：
        float: 两个数的和
    """
    return a + b


# ==================================
# 工具 2：减法
# ==================================
@mcp.tool(description="执行两个数的减法运算")
def subtract(a: float, b: float) -> float:
    """
    功能说明：
        返回 a - b 的结果。
    """
    return a - b


# ==================================
# 工具 3：乘法
# ==================================
@mcp.tool(description="执行两个数的乘法运算")
def multiply(a: float, b: float) -> float:
    """
    功能说明：
        返回两个数相乘的结果。
    """
    return a * b


# ==================================
# 工具 4：除法
# ==================================
@mcp.tool(description="执行两个数的除法运算，检查除数是否为零")
def divide(a: float, b: float) -> float:
    """
    功能说明：
        返回 a / b 的结果。
        如果 b 为 0，将抛出异常。

    异常：
        ValueError: 当 b == 0 时抛出。
    """
    if b == 0:
        raise ValueError("除数不能为 0")
    return a / b


# ==================================
# 工具 5：幂运算
# ==================================
@mcp.tool(description="执行幂次方运算")
def power(base: float, exponent: float) -> float:
    """
    功能说明：
        计算 base 的 exponent 次幂。
    """
    return math.pow(base, exponent)


# ==================================
# 工具 6：平方根
# ==================================
@mcp.tool(description="计算平方根")
def sqrt(value: float) -> float:
    """
    功能说明：
        计算输入值的平方根。
        如果输入为负数，抛出异常。
    """
    if value < 0:
        raise ValueError("不能对负数开平方")
    return math.sqrt(value)


# ==================================
# 工具 7：平均值
# ==================================
@mcp.tool(description="计算一组数字的平均值")
def average(values: List[float]) -> float:
    """
    功能说明：
        计算一组数的平均值。
        如果列表为空，则抛出异常。
    """
    if not values:
        raise ValueError("输入列表不能为空")
    return sum(values) / len(values)


# ==================================
# 工具 8：统计分析
# ==================================
@mcp.tool(description="获取一组数的统计指标，包括最大值、最小值、平均值、方差、标准差")
def stats(values: List[float]) -> dict:
    """
    功能说明：
        对输入的数字列表进行统计分析，返回结果包含：
        - count: 元素数量
        - max: 最大值
        - min: 最小值
        - avg: 平均值
        - variance: 方差
        - std_dev: 标准差

    参数：
        values (List[float]): 数字列表

    返回：
        dict: 统计结果字典
    """
    if not values:
        raise ValueError("输入列表不能为空")

    avg = sum(values) / len(values)
    variance = sum((x - avg) ** 2 for x in values) / len(values)
    std_dev = math.sqrt(variance)

    return {
        "count": len(values),
        "max": max(values),
        "min": min(values),
        "avg": avg,
        "variance": variance,
        "std_dev": std_dev
    }


# ==================================
# 启动 MCP 服务
# ==================================
if __name__ == "__main__":
    mcp.run(transport="stdio")
    # mcp.run(transport="sse")
