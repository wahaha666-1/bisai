#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智链编排平台 - 完整演示脚本
展示从创建 Agent 到执行工作流的完整流程
"""

from app import db, registry, executor, engine
from datetime import datetime

print("=" * 80)
print("🚀 智链编排平台 - 完整演示")
print("=" * 80)
print()

# ============================================================================
# 步骤 1: 注册基础 Agent
# ============================================================================

print("📦 步骤 1: 注册基础 Agent")
print("-" * 80)

@registry.register(
    name='text_processor',
    agent_type='processor',
    description='处理和分析文本数据',
    category='文本处理'
)
def text_processor(text: str) -> dict:
    """文本处理器 - 转大写并统计"""
    processed = text.upper()
    words = text.split()
    
    return {
        '原文': text,
        '处理后': processed,
        '字符数': len(text),
        '单词数': len(words)
    }

@registry.register(
    name='number_calculator',
    agent_type='processor',
    description='数学计算器',
    category='数据处理'
)
def number_calculator(operation: str, a: float, b: float) -> dict:
    """计算器"""
    operations = {
        'add': a + b,
        'subtract': a - b,
        'multiply': a * b,
        'divide': a / b if b != 0 else None
    }
    
    result = operations.get(operation)
    
    return {
        '操作': operation,
        'A': a,
        'B': b,
        '结果': result
    }

@registry.register(
    name='data_formatter',
    agent_type='processor',
    description='格式化数据输出',
    category='数据处理'
)
def data_formatter(data: dict) -> str:
    """数据格式化器"""
    lines = []
    for key, value in data.items():
        lines.append(f"{key}: {value}")
    return "\n".join(lines)

@registry.register(
    name='list_processor',
    agent_type='processor',
    description='处理列表数据',
    category='数据处理'
)
def list_processor(items: list) -> dict:
    """列表处理器"""
    return {
        '项目数': len(items),
        '第一项': items[0] if items else None,
        '最后一项': items[-1] if items else None,
        '所有项': items
    }

@registry.register(
    name='json_parser',
    agent_type='processor',
    description='解析 JSON 数据',
    category='数据处理'
)
def json_parser(json_str: str) -> dict:
    """JSON 解析器"""
    import json
    try:
        data = json.loads(json_str)
        return {
            '状态': '成功',
            '数据': data,
            '类型': type(data).__name__
        }
    except Exception as e:
        return {
            '状态': '失败',
            '错误': str(e)
        }

print(f"✅ 已注册 {len(registry.list_agents())} 个 Agent")
print()

# ============================================================================
# 步骤 2: 创建工作流
# ============================================================================

print("🔄 步骤 2: 创建工作流")
print("-" * 80)

# 工作流 1: 简单文本处理
with db.session_scope() as session:
    workflow_id_1 = db.create_workflow(
        session=session,
        name='文本处理演示',
        description='演示文本处理流程',
        category='演示',
        workflow_definition={
            "agents": ["text_processor"],
            "sequence": [
                {"agent": "text_processor", "params": {}}
            ]
        }
    )
    print(f"✅ 创建工作流: 文本处理演示 (ID: {workflow_id_1})")

# 工作流 2: 计算器演示
with db.session_scope() as session:
    workflow_id_2 = db.create_workflow(
        session=session,
        name='计算器演示',
        description='演示数学计算',
        category='演示',
        workflow_definition={
            "agents": ["number_calculator"],
            "sequence": [
                {"agent": "number_calculator", "params": {}}
            ]
        }
    )
    print(f"✅ 创建工作流: 计算器演示 (ID: {workflow_id_2})")

# 工作流 3: 多步骤流程
with db.session_scope() as session:
    workflow_id_3 = db.create_workflow(
        session=session,
        name='多步骤处理流程',
        description='文本处理 → 数据格式化',
        category='演示',
        workflow_definition={
            "agents": ["text_processor", "data_formatter"],
            "sequence": [
                {"agent": "text_processor", "params": {}},
                {"agent": "data_formatter", "params": {}}
            ]
        }
    )
    print(f"✅ 创建工作流: 多步骤处理流程 (ID: {workflow_id_3})")

print()

# ============================================================================
# 步骤 3: 执行工作流
# ============================================================================

print("▶️  步骤 3: 执行工作流")
print("-" * 80)
print()

# 执行 1: 文本处理
print("【演示 1】文本处理")
print("-" * 40)
result_1 = engine.execute_workflow(
    workflow_id=workflow_id_1,
    input_data={'text': 'Hello World! This is a test.'}
)

if result_1['success']:
    print("✅ 执行成功！")
    print(f"耗时: {result_1['execution_time']:.2f}秒")
    print(f"输出: {result_1['output']}")
else:
    print(f"❌ 执行失败: {result_1['error']}")
print()

# 执行 2: 计算器
print("【演示 2】计算器")
print("-" * 40)
result_2 = engine.execute_workflow(
    workflow_id=workflow_id_2,
    input_data={'operation': 'add', 'a': 10, 'b': 20}
)

if result_2['success']:
    print("✅ 执行成功！")
    print(f"耗时: {result_2['execution_time']:.2f}秒")
    print(f"输出: {result_2['output']}")
else:
    print(f"❌ 执行失败: {result_2['error']}")
print()

# 执行 3: 多步骤
print("【演示 3】多步骤流程")
print("-" * 40)
result_3 = engine.execute_workflow(
    workflow_id=workflow_id_3,
    input_data={'text': 'Python is awesome'}
)

if result_3['success']:
    print("✅ 执行成功！")
    print(f"耗时: {result_3['execution_time']:.2f}秒")
    print(f"输出: {result_3['output']}")
else:
    print(f"❌ 执行失败: {result_3['error']}")
print()

# ============================================================================
# 步骤 4: 查看统计数据
# ============================================================================

print("📊 步骤 4: 查看统计数据")
print("-" * 80)

# Agent 统计
agents = registry.list_agents()
print(f"📦 Agent 总数: {len(agents)}")

# 工作流和执行统计
with db.session_scope() as session:
    # 工作流统计
    workflows = db.get_all_workflows(session)
    print(f"🔄 工作流总数: {len(workflows)}")
    
    # 执行统计
    from backend.models import WorkflowExecution
    executions = session.query(WorkflowExecution).all()
    print(f"▶️  总执行次数: {len(executions)}")
    
    # 成功率
    successful = sum(1 for e in executions if e.status == 'completed')
    success_rate = (successful / len(executions) * 100) if executions else 0
    print(f"✅ 成功率: {success_rate:.1f}%")
    
    # 日志统计
    from backend.models import Log
    logs = session.query(Log).all()
    print(f"📝 日志总数: {len(logs)}")

print()

# ============================================================================
# 步骤 5: Agent 详细信息
# ============================================================================

print("🔍 步骤 5: Agent 详细信息")
print("-" * 80)

for agent in registry.list_agents():
    print(f"\n📦 {agent['name']}")
    print(f"   类型: {agent['agent_type']}")
    print(f"   分类: {agent['category']}")
    print(f"   描述: {agent['description']}")
    
    # 输入参数
    if agent['input_parameters']:
        print(f"   输入:")
        for param in agent['input_parameters']:
            print(f"      - {param['name']}: {param['type']}")
    
    # 输出参数
    if agent['output_parameters']:
        print(f"   输出:")
        for param in agent['output_parameters']:
            print(f"      - {param['name']}: {param['type']}")

print()

# ============================================================================
# 完成
# ============================================================================

print("=" * 80)
print("🎉 演示完成！")
print("=" * 80)
print()
print("📝 总结:")
print(f"   • 注册了 {len(registry.list_agents())} 个 Agent")
print(f"   • 创建了 3 个工作流")
print(f"   • 执行了 3 次工作流")
print(f"   • 所有演示都成功完成！")
print()
print("💡 接下来你可以:")
print("   1. 访问 http://localhost:5000/workspace 查看工作台")
print("   2. 访问 http://localhost:5000/dashboard 查看数据看板")
print("   3. 刷新页面看到统计数字更新")
print("   4. 点击「执行」按钮测试工作流")
print()
print("=" * 80)

