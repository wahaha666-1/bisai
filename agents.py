#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
预置 Agent 模块
定义所有基础 Agent，会在 app.py 启动时自动注册
"""

def register_all_agents(registry):
    """注册所有预置 Agent"""
    
    print("\n[Agent 加载] 开始注册预置 Agent...")
    
    # ========================================================================
    # 文本处理类 Agent
    # ========================================================================
    
    @registry.register(
        name='text_processor',
        agent_type='processor',
        description='处理和分析文本数据',
        category='文本处理',
        icon='📝'
    )
    def text_processor(text: str = "Hello World! Welcome to AgentFlow.") -> dict:
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
        name='default_文本处理器',
        agent_type='processor',
        description='文本转大写',
        category='文本处理',
        icon='📝'
    )
    def default_text_processor(text: str = "默认文本") -> str:
        """默认文本处理器"""
        return text.upper()
    
    # ========================================================================
    # 数据处理类 Agent
    # ========================================================================
    
    @registry.register(
        name='number_calculator',
        agent_type='processor',
        description='数学计算器',
        category='数据处理',
        icon='🔢'
    )
    def number_calculator(operation: str = "add", a: float = 10.0, b: float = 20.0) -> dict:
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
        category='数据处理',
        icon='✨'
    )
    def data_formatter(data: dict = None) -> str:
        """数据格式化器"""
        if data is None:
            data = {'示例': '数据', '状态': '就绪'}
        
        lines = []
        for key, value in data.items():
            lines.append(f"{key}: {value}")
        return "\n".join(lines)
    
    @registry.register(
        name='list_processor',
        agent_type='processor',
        description='处理列表数据',
        category='数据处理',
        icon='📋'
    )
    def list_processor(items: list = None) -> dict:
        """列表处理器"""
        if items is None:
            items = ['示例1', '示例2', '示例3']
        
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
        category='数据处理',
        icon='🔧'
    )
    def json_parser(json_str: str = '{"name": "AgentFlow", "version": "1.0"}') -> dict:
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
    
    # ========================================================================
    # 字符串处理类 Agent
    # ========================================================================
    
    @registry.register(
        name='string_reverser',
        agent_type='processor',
        description='反转字符串',
        category='文本处理',
        icon='🔄'
    )
    def string_reverser(text: str = "AgentFlow") -> str:
        """反转字符串"""
        return text[::-1]
    
    @registry.register(
        name='word_counter',
        agent_type='analyzer',
        description='统计单词频率',
        category='文本分析',
        icon='📊'
    )
    def word_counter(text: str = "hello world hello python") -> dict:
        """统计单词频率"""
        words = text.lower().split()
        freq = {}
        for word in words:
            freq[word] = freq.get(word, 0) + 1
        return freq
    
    # ========================================================================
    # 数据转换类 Agent
    # ========================================================================
    
    @registry.register(
        name='csv_to_json',
        agent_type='converter',
        description='CSV 转 JSON',
        category='数据转换',
        icon='🔄'
    )
    def csv_to_json(csv_text: str = "name,age\nAlice,25\nBob,30") -> dict:
        """CSV 转 JSON"""
        import csv
        from io import StringIO
        
        reader = csv.DictReader(StringIO(csv_text))
        data = list(reader)
        
        return {
            '行数': len(data),
            '数据': data
        }
    
    @registry.register(
        name='dict_to_query_string',
        agent_type='converter',
        description='字典转 URL 查询字符串',
        category='数据转换',
        icon='🔗'
    )
    def dict_to_query_string(params: dict = None) -> str:
        """字典转 URL 查询字符串"""
        if params is None:
            params = {'page': 1, 'size': 10, 'search': 'agent'}
        
        from urllib.parse import urlencode
        return urlencode(params)
    
    # ========================================================================
    # 时间处理类 Agent
    # ========================================================================
    
    @registry.register(
        name='timestamp_formatter',
        agent_type='processor',
        description='格式化时间戳',
        category='时间处理',
        icon='⏰'
    )
    def timestamp_formatter(timestamp: float = None) -> dict:
        """格式化时间戳"""
        from datetime import datetime
        
        if timestamp is None:
            dt = datetime.now()
        else:
            dt = datetime.fromtimestamp(timestamp)
        
        return {
            'ISO格式': dt.isoformat(),
            '可读格式': dt.strftime('%Y-%m-%d %H:%M:%S'),
            '日期': dt.strftime('%Y-%m-%d'),
            '时间': dt.strftime('%H:%M:%S'),
            '时间戳': dt.timestamp()
        }
    
    print(f"[Agent 加载] ✅ 成功注册 {len(registry.list_agents())} 个预置 Agent\n")

