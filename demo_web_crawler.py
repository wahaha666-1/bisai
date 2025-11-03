# ============================================================================
# 竞品分析自动化 Demo - 比赛演示案例 (三层架构版)
# ============================================================================

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 从 app 导入系统组件
from app import db, registry, executor, engine

print("="*60)
print("竞品分析自动化工作流 Demo")
print("="*60)

# ============================================================================
# 注册 Agent
# ============================================================================

# Agent 1: 网页爬虫
@registry.register(
    name="网页爬虫",
    agent_type="data_collector",
    tools=["requests", "beautifulsoup4"],
    description="爬取指定URL的网页内容",
    category="数据处理",
    icon="spider"
)
def web_crawler(url: str, timeout: int = 30) -> dict:
    """
    爬取网页内容
    
    注意：这是演示版本，实际使用需要安装 requests 和 beautifulsoup4
    """
    try:
        import requests
        from bs4 import BeautifulSoup
        
        print(f"  → 正在爬取: {url}")
        response = requests.get(url, timeout=timeout)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # 提取内容
        title = soup.title.string if soup.title else ''
        text = soup.get_text()
        
        # 清理文本
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text_clean = '\n'.join(chunk for chunk in chunks if chunk)
        
        print(f"  ✓ 爬取成功，获取了 {len(text_clean)} 字符")
        
        return {
            'url': url,
            'title': title,
            'content': text_clean[:2000],  # 限制长度
            'content_length': len(text_clean),
            'status': response.status_code,
            'success': True
        }
    
    except ImportError:
        # 模拟数据（用于演示）
        print(f"  → 模拟爬取: {url}")
        return {
            'url': url,
            'title': '示例网站标题',
            'content': '这是一个模拟的网页内容。产品特点：功能强大、价格合理、用户体验好。',
            'content_length': 100,
            'status': 200,
            'success': True
        }
    
    except Exception as e:
        print(f"  ✗ 爬取失败: {e}")
        return {
            'url': url,
            'error': str(e),
            'success': False
        }


# Agent 2: 内容分析师
@registry.register(
    name="内容分析师",
    agent_type="ai_analyzer",
    llm_model="gpt-4",
    description="AI 分析网页内容",
    category="AI分析",
    icon="brain",
    prompt_template="""
请分析以下竞品网站内容：

网站：{url}
标题：{title}
内容摘要：{content}

请提供：
1. 内容摘要（100字以内）
2. 3个关键产品特点
3. 竞品优势分析
4. 建议我们应该注意的方面
"""
)
def content_analyzer(url: str, title: str, content: str) -> dict:
    """
    AI 分析内容
    
    注意：需要配置 OpenAI API Key 才能真正调用 LLM
    """
    # 模拟 AI 分析结果（用于演示）
    print(f"  → 正在分析内容...")
    
    return {
        'summary': f'分析了来自 {url} 的内容，标题为：{title}',
        'key_features': [
            '功能强大：产品功能完善',
            '用户体验：界面友好',
            '价格合理：性价比高'
        ],
        'advantages': '该竞品在用户体验和功能完整性方面表现突出',
        'suggestions': [
            '建议关注其用户界面设计',
            '学习其功能模块划分',
            '研究其定价策略'
        ],
        'analyzed': True
    }


# Agent 3: 报告生成器
@registry.register(
    name="报告生成器",
    agent_type="content_generator",
    description="生成分析报告",
    category="内容生成",
    icon="document"
)
def report_generator(url: str, analysis: dict) -> dict:
    """生成分析报告"""
    print(f"  → 正在生成报告...")
    
    report = f"""
# 竞品分析报告

## 基本信息
- 网站URL: {url}
- 分析时间: 2024-12-05

## 内容摘要
{analysis.get('summary', 'N/A')}

## 关键特点
{chr(10).join('- ' + f for f in analysis.get('key_features', []))}

## 优势分析
{analysis.get('advantages', 'N/A')}

## 建议
{chr(10).join('- ' + s for s in analysis.get('suggestions', []))}

---
报告由 AgentFlow 自动生成
"""
    
    print(f"  ✓ 报告生成完成")
    
    return {
        'report': report,
        'report_length': len(report),
        'format': 'markdown',
        'generated': True
    }


# Agent 4: 结果输出
@registry.register(
    name="结果输出",
    agent_type="action_executor",
    description="输出最终结果",
    category="自动化操作",
    icon="output"
)
def result_output(report: dict) -> dict:
    """输出结果"""
    print(f"\n{'='*60}")
    print("最终生成的报告：")
    print('='*60)
    print(report.get('report', 'N/A'))
    print('='*60 + "\n")
    
    return {
        'output_success': True,
        'message': '报告已输出'
    }


# ============================================================================
# 创建并执行工作流
# ============================================================================

print("\n创建工作流...")

workflow_def = {
    'nodes': [
        {
            'id': '1',
            'agent': '网页爬虫',
            'params': {
                'url': 'https://example.com',
                'timeout': 30
            }
        },
        {
            'id': '2',
            'agent': '内容分析师',
            'params': {
                'url': '$网页爬虫_result.url',
                'title': '$网页爬虫_result.title',
                'content': '$网页爬虫_result.content'
            }
        },
        {
            'id': '3',
            'agent': '报告生成器',
            'params': {
                'url': '$网页爬虫_result.url',
                'analysis': '$内容分析师_result'
            }
        },
        {
            'id': '4',
            'agent': '结果输出',
            'params': {
                'report': '$报告生成器_result'
            }
        }
    ],
    'edges': [
        {'from': '1', 'to': '2'},
        {'from': '2', 'to': '3'},
        {'from': '3', 'to': '4'}
    ]
}

with db.session_scope() as session:
    workflow_id = db.create_workflow(
        session=session,
        name='竞品分析自动化',
        description='网页爬虫 → AI分析 → 报告生成 → 结果输出',
        workflow_definition=workflow_def,
        category='数据分析'
    )

print(f"✓ 工作流创建成功！ID: {workflow_id}")

print("\n开始执行工作流...\n")

# 执行工作流
result = engine.execute_workflow(
    workflow_id=workflow_id,
    input_data={'target_url': 'https://example.com'}
)

# 显示结果
print("\n" + "="*60)
print("工作流执行结果")
print("="*60)
print(f"执行状态: {'✓ 成功' if result['success'] else '✗ 失败'}")
print(f"执行ID: {result['execution_id']}")
print(f"总耗时: {result['execution_time']:.2f}秒")

if not result['success']:
    print(f"错误信息: {result['error']}")

print("\n" + "="*60)
print("查看执行记录")
print("="*60)

with db.session_scope() as session:
    execution = db.get_workflow_execution(session, result['execution_id'])
    if execution:
        print(f"工作流名称: {workflow_def['nodes'][0]['agent']}")
        print(f"执行时间: {execution['started_at']} 至 {execution['completed_at']}")
        print(f"状态: {execution['status']}")
        
        if execution['execution_graph']:
            print(f"\n执行详情:")
            for step in execution['execution_graph']:
                status_icon = '✓' if step['status'] == 'completed' else '✗'
                print(f"  {status_icon} {step['agent']}: {step['execution_time']:.2f}秒")

print("\n✓ Demo 完成！")
print("\n提示：")
print("  1. 这是简化的演示版本")
print("  2. 实际使用需要安装 requests 和 beautifulsoup4")
print("  3. AI 分析需要配置 OpenAI API Key")
print("  4. 可以修改 workflow_def 中的 URL 来分析其他网站")

