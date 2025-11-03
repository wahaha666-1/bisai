"""
工具系统 - AgentFlow Tool System
支持外部API调用、数据处理等工具
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Callable
import json
import requests
from datetime import datetime


class Tool(ABC):
    """工具基类"""
    
    def __init__(self, name: str, description: str, parameters: Dict[str, Any]):
        self.name = name
        self.description = description
        self.parameters = parameters  # JSON Schema格式的参数定义
        
    @abstractmethod
    def execute(self, **kwargs) -> Dict[str, Any]:
        """执行工具，返回结果"""
        pass
    
    def to_function_schema(self) -> Dict[str, Any]:
        """转换为DeepSeek Function Calling格式"""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters
            }
        }


class ToolRegistry:
    """工具注册中心"""
    
    def __init__(self):
        self.tools: Dict[str, Tool] = {}
        
    def register(self, tool: Tool):
        """注册工具"""
        self.tools[tool.name] = tool
        print(f"[工具系统] 注册工具: {tool.name}")
        
    def get_tool(self, name: str) -> Optional[Tool]:
        """获取工具"""
        return self.tools.get(name)
    
    def list_tools(self) -> List[str]:
        """列出所有工具"""
        return list(self.tools.keys())
    
    def get_function_schemas(self) -> List[Dict[str, Any]]:
        """获取所有工具的Function Schema（用于DeepSeek）"""
        return [tool.to_function_schema() for tool in self.tools.values()]
    
    def execute_tool(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """执行工具"""
        tool = self.get_tool(name)
        if not tool:
            return {"success": False, "error": f"工具不存在: {name}"}
        
        try:
            result = tool.execute(**arguments)
            return {"success": True, "result": result}
        except Exception as e:
            import traceback
            return {
                "success": False, 
                "error": str(e),
                "traceback": traceback.format_exc()
            }


# ============================================================================
# 内置工具实现
# ============================================================================

class WeatherTool(Tool):
    """天气查询工具"""
    
    def __init__(self, api_key: Optional[str] = None):
        super().__init__(
            name="get_weather",
            description="查询指定城市的实时天气信息，包括温度、湿度、天气状况等",
            parameters={
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "城市名称，例如：北京、上海、New York"
                    },
                    "unit": {
                        "type": "string",
                        "enum": ["celsius", "fahrenheit"],
                        "description": "温度单位，celsius(摄氏度)或fahrenheit(华氏度)",
                        "default": "celsius"
                    }
                },
                "required": ["city"]
            }
        )
        self.api_key = api_key or "demo_key"  # 使用免费的wttr.in服务
        
    def execute(self, city: str, unit: str = "celsius") -> Dict[str, Any]:
        """查询天气"""
        try:
            # 使用wttr.in免费服务（无需API Key）
            url = f"https://wttr.in/{city}?format=j1"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                current = data['current_condition'][0]
                
                # 解析数据
                temp_c = current['temp_C']
                temp_f = current['temp_F']
                
                return {
                    "city": city,
                    "temperature": temp_c if unit == "celsius" else temp_f,
                    "unit": "°C" if unit == "celsius" else "°F",
                    "description": current['weatherDesc'][0]['value'],
                    "humidity": current['humidity'] + "%",
                    "wind_speed": current['windspeedKmph'] + " km/h",
                    "feels_like": current['FeelsLikeC'] + "°C" if unit == "celsius" else current['FeelsLikeF'] + "°F",
                    "query_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
            else:
                return {"error": f"无法获取天气信息，状态码: {response.status_code}"}
                
        except Exception as e:
            return {"error": f"天气查询失败: {str(e)}"}


class WebSearchTool(Tool):
    """网络搜索工具（使用DuckDuckGo，免费无需API Key）"""
    
    def __init__(self):
        super().__init__(
            name="web_search",
            description="在互联网上搜索信息，返回相关网页摘要和链接",
            parameters={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "搜索关键词或问题"
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "返回结果数量",
                        "default": 5
                    }
                },
                "required": ["query"]
            }
        )
        
    def execute(self, query: str, max_results: int = 5) -> Dict[str, Any]:
        """执行搜索"""
        try:
            # 使用DuckDuckGo的HTML接口（简单版本）
            url = f"https://html.duckduckgo.com/html/"
            params = {"q": query}
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
            
            response = requests.post(url, data=params, headers=headers, timeout=10)
            
            if response.status_code == 200:
                # 简化版：返回搜索建议
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(response.text, 'html.parser')
                results = []
                
                for result in soup.find_all('div', class_='result', limit=max_results):
                    title_tag = result.find('a', class_='result__a')
                    snippet_tag = result.find('a', class_='result__snippet')
                    
                    if title_tag:
                        results.append({
                            "title": title_tag.get_text(strip=True),
                            "url": title_tag.get('href', ''),
                            "snippet": snippet_tag.get_text(strip=True) if snippet_tag else ""
                        })
                
                return {
                    "query": query,
                    "results": results,
                    "count": len(results)
                }
            else:
                return {"error": "搜索失败"}
                
        except Exception as e:
            return {"error": f"搜索出错: {str(e)}"}


class WebScraperTool(Tool):
    """网页内容抓取工具"""
    
    def __init__(self):
        super().__init__(
            name="scrape_webpage",
            description="抓取指定网页的文本内容，提取标题、正文等信息",
            parameters={
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "要抓取的网页URL"
                    },
                    "selector": {
                        "type": "string",
                        "description": "CSS选择器（可选），用于提取特定内容",
                        "default": "body"
                    }
                },
                "required": ["url"]
            }
        )
        
    def execute(self, url: str, selector: str = "body") -> Dict[str, Any]:
        """抓取网页"""
        try:
            from bs4 import BeautifulSoup
            
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
            response = requests.get(url, headers=headers, timeout=15)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # 提取标题
                title = soup.find('title')
                title_text = title.get_text(strip=True) if title else "无标题"
                
                # 提取内容
                content_elem = soup.select_one(selector)
                if content_elem:
                    # 移除脚本和样式
                    for script in content_elem(["script", "style"]):
                        script.decompose()
                    
                    content = content_elem.get_text(separator='\n', strip=True)
                    # 限制长度
                    if len(content) > 5000:
                        content = content[:5000] + "..."
                else:
                    content = "无法提取内容"
                
                return {
                    "url": url,
                    "title": title_text,
                    "content": content,
                    "length": len(content)
                }
            else:
                return {"error": f"HTTP {response.status_code}"}
                
        except Exception as e:
            return {"error": f"抓取失败: {str(e)}"}


class CalculatorTool(Tool):
    """计算器工具"""
    
    def __init__(self):
        super().__init__(
            name="calculator",
            description="执行数学计算，支持基本运算和数学函数",
            parameters={
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "数学表达式，例如：2+2、sqrt(16)、sin(30)"
                    }
                },
                "required": ["expression"]
            }
        )
        
    def execute(self, expression: str) -> Dict[str, Any]:
        """执行计算"""
        try:
            import math
            import re
            
            # 安全检查
            if re.search(r'[^0-9+\-*/().,\s]', expression.replace('sqrt', '').replace('sin', '').replace('cos', '').replace('tan', '')):
                return {"error": "表达式包含不允许的字符"}
            
            # 替换函数名
            safe_expr = expression.replace('^', '**')
            safe_expr = safe_expr.replace('sqrt', 'math.sqrt')
            safe_expr = safe_expr.replace('sin', 'math.sin')
            safe_expr = safe_expr.replace('cos', 'math.cos')
            safe_expr = safe_expr.replace('tan', 'math.tan')
            
            result = eval(safe_expr, {"__builtins__": {}, "math": math})
            
            return {
                "expression": expression,
                "result": result,
                "formatted": f"{expression} = {result}"
            }
        except Exception as e:
            return {"error": f"计算错误: {str(e)}"}


class CurrentTimeTool(Tool):
    """当前时间工具"""
    
    def __init__(self):
        super().__init__(
            name="get_current_time",
            description="获取当前日期和时间",
            parameters={
                "type": "object",
                "properties": {
                    "timezone": {
                        "type": "string",
                        "description": "时区（可选），例如：Asia/Shanghai、America/New_York",
                        "default": "local"
                    }
                },
                "required": []
            }
        )
        
    def execute(self, timezone: str = "local") -> Dict[str, Any]:
        """获取时间"""
        try:
            from datetime import datetime
            import pytz
            
            if timezone == "local":
                now = datetime.now()
            else:
                tz = pytz.timezone(timezone)
                now = datetime.now(tz)
            
            return {
                "datetime": now.strftime("%Y-%m-%d %H:%M:%S"),
                "date": now.strftime("%Y-%m-%d"),
                "time": now.strftime("%H:%M:%S"),
                "weekday": now.strftime("%A"),
                "timezone": timezone,
                "timestamp": int(now.timestamp())
            }
        except Exception as e:
            return {"error": f"获取时间失败: {str(e)}"}


# ============================================================================
# 全局工具注册中心
# ============================================================================

# 创建全局工具注册中心
global_tool_registry = ToolRegistry()

class FileReadTool(Tool):
    """文件读取工具（简化版，只读取）"""
    
    def __init__(self):
        super().__init__(
            name="read_file",
            description="读取文本文件内容",
            parameters={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "文件路径"
                    }
                },
                "required": ["file_path"]
            }
        )
        
    def execute(self, file_path: str) -> Dict[str, Any]:
        """读取文件"""
        try:
            import os
            
            if not os.path.exists(file_path):
                return {"error": f"文件不存在: {file_path}"}
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            return {
                "success": True,
                "file_path": file_path,
                "content": content[:1000] + "..." if len(content) > 1000 else content,
                "size": len(content),
                "lines": content.count('\n') + 1
            }
        except Exception as e:
            return {"error": f"文件读取失败: {str(e)}"}


def register_default_tools():
    """注册默认工具"""
    print("\n[工具系统] 开始注册默认工具...")
    
    # 注册内置工具
    global_tool_registry.register(WeatherTool())
    global_tool_registry.register(WebSearchTool())
    global_tool_registry.register(WebScraperTool())
    global_tool_registry.register(CalculatorTool())
    global_tool_registry.register(CurrentTimeTool())
    global_tool_registry.register(FileReadTool())
    
    print(f"[工具系统] ✅ 已注册 {len(global_tool_registry.tools)} 个工具")
    print(f"[工具系统] 工具列表: {', '.join(global_tool_registry.list_tools())}")

