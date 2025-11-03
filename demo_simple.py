# ============================================================================
# AgentFlow - 简单示例 (三层架构版)
# ============================================================================

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 从 app 导入系统组件
from app import db, registry, executor

# ============================================================================
# 1. 注册 Agent
# ============================================================================

print("\n" + "="*60)
print("AgentFlow 简单示例 - 注册 Agent")
print("="*60 + "\n")

# Agent 1: 文本处理
@registry.register(
    name="text_processor",
    agent_type="processor",
    category="文本处理",
    icon="📝",
    description="处理和分析文本数据"
)
def text_processor(text: str) -> dict:
    """处理文本"""
    return {
        'length': len(text),
        'words': len(text.split()),
        'upper': text.upper(),
        'lower': text.lower()
    }

# Agent 2: 数学计算
@registry.register(
    name="calculator",
    agent_type="calculator",
    category="数学计算",
    icon="🔢",
    description="执行基本数学运算"
)
def calculator(a: float, b: float, operation: str = 'add') -> float:
    """计算器"""
    ops = {
        'add': a + b,
        'subtract': a - b,
        'multiply': a * b,
        'divide': a / b if b != 0 else None
    }
    return ops.get(operation, 0)

# Agent 3: 数据格式化
@registry.register(
    name="formatter",
    agent_type="formatter",
    category="数据处理",
    icon="💅",
    description="格式化数据输出"
)
def formatter(data: dict) -> str:
    """格式化数据"""
    lines = ["格式化结果:"]
    for key, value in data.items():
        lines.append(f"  {key}: {value}")
    return "\n".join(lines)

# ============================================================================
# 2. 测试 Agent
# ============================================================================

print("\n" + "="*60)
print("测试 Agent 执行")
print("="*60 + "\n")

# 测试 1: 文本处理
print("[测试 1] text_processor")
result1 = executor.execute(
    agent_name="text_processor",
    params={"text": "Hello AgentFlow System"}
)
print(f"结果: {result1['output']}\n")

# 测试 2: 计算器
print("[测试 2] calculator")
result2 = executor.execute(
    agent_name="calculator",
    params={"a": 10, "b": 5, "operation": "multiply"}
)
print(f"结果: {result2['output']}\n")

# 测试 3: 格式化
print("[测试 3] formatter")
result3 = executor.execute(
    agent_name="formatter",
    params={"data": {"name": "AgentFlow", "version": "1.0", "status": "running"}}
)
print(f"结果:\n{result3['output']}\n")

# ============================================================================
# 3. 查看注册的 Agent
# ============================================================================

print("="*60)
print("已注册的 Agent:")
print("="*60)

with db.session_scope() as session:
    agents = db.get_all_agents(session)
    for agent in agents:
        print(f"\n{agent['icon']} {agent['name']}")
        print(f"  类型: {agent['agent_type']}")
        print(f"  分类: {agent['category']}")
        print(f"  描述: {agent['description']}")

print("\n" + "="*60)
print("✓ 所有测试完成！")
print("="*60)
print("\n提示: 运行 app.py 启动 Web 界面查看数据\n")

