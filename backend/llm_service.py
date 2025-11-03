# ============================================================================
# LLM 服务层 - DeepSeek 集成
# ============================================================================

import os
import json
import requests
from typing import Dict, List, Any, Optional, Generator
import time

class DeepSeekLLM:
    """DeepSeek LLM 服务"""
    
    def __init__(self, api_key: Optional[str] = None, base_url: str = "https://api.deepseek.com/v1"):
        """
        初始化DeepSeek LLM
        
        Args:
            api_key: DeepSeek API Key
            base_url: API基础URL
        """
        self._api_key = api_key or os.environ.get('DEEPSEEK_API_KEY', '')
        self.base_url = base_url
        self.model = "deepseek-chat"  # 默认使用deepseek-chat模型
        self._db = None
        
    def set_database(self, db):
        """设置数据库实例"""
        self._db = db
        
    @property
    def api_key(self):
        """获取API Key（优先从数据库读取）"""
        if self._db:
            try:
                from backend.database import Database
                with self._db.session_scope() as session:
                    key = self._db.get_secret_key(session, 'deepseek_api_key')
                    if key:
                        return key
            except:
                pass
        return self._api_key
    
    def set_api_key(self, api_key: str, persist: bool = False):
        """
        设置API Key
        
        Args:
            api_key: API Key值
            persist: 是否持久化到数据库
        """
        self._api_key = api_key
        
        if persist and self._db:
            try:
                with self._db.session_scope() as session:
                    self._db.set_secret_key(session, 'deepseek_api_key', api_key)
            except Exception as e:
                print(f"保存API Key失败: {e}")
        
    def is_configured(self) -> bool:
        """检查是否已配置API Key"""
        return bool(self.api_key)
    
    def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2000,
        stream: bool = False,
        tools: Optional[List[Dict]] = None,
        tool_choice: str = "auto"
    ) -> Dict[str, Any]:
        """
        发送聊天请求
        
        Args:
            messages: 消息列表 [{"role": "user/assistant/system", "content": "..."}]
            temperature: 温度参数 (0-1)
            max_tokens: 最大token数
            stream: 是否流式输出
            
        Returns:
            响应数据
        """
        if not self.is_configured():
            return {
                'success': False,
                'error': '未配置DeepSeek API Key，请在设置中配置'
            }
        
        try:
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            data = {
                'model': self.model,
                'messages': messages,
                'temperature': temperature,
                'max_tokens': max_tokens,
                'stream': stream
            }
            
            # 添加工具参数（如果提供）
            if tools:
                data['tools'] = tools
                data['tool_choice'] = tool_choice
            
            # 增加超时时间到60秒，并添加连接超时设置
            # 关键：如果是流式请求，requests也要设置stream=True
            response = requests.post(
                f'{self.base_url}/chat/completions',
                headers=headers,
                json=data,
                stream=stream,  # 这个参数很关键！
                timeout=(10, 60)  # (连接超时, 读取超时)
            )
            
            if response.status_code == 200:
                # 流式输出
                if stream:
                    def generate():
                        for line in response.iter_lines():
                            if line:
                                line_str = line.decode('utf-8')
                                if line_str.startswith('data: '):
                                    data_str = line_str[6:]
                                    if data_str == '[DONE]':
                                        break
                                    try:
                                        data = json.loads(data_str)
                                        if 'choices' in data and len(data['choices']) > 0:
                                            delta = data['choices'][0].get('delta', {})
                                            content = delta.get('content', '')
                                            if content:
                                                yield content
                                    except json.JSONDecodeError:
                                        continue
                    return {
                        'success': True,
                        'stream': generate(),
                        'is_stream': True
                    }
                else:
                    # 非流式输出
                    result = response.json()
                    message = result['choices'][0]['message']
                    
                    response_data = {
                        'success': True,
                        'message': message,
                        'usage': result.get('usage', {}),
                        'model': result.get('model', self.model)
                    }
                    
                    # 检查是否有工具调用
                    if 'tool_calls' in message and message['tool_calls']:
                        response_data['tool_calls'] = message['tool_calls']
                    else:
                        response_data['content'] = message.get('content', '')
                    
                    return response_data
            elif response.status_code == 401:
                return {
                    'success': False,
                    'error': 'API Key 无效或已过期，请重新配置',
                    'error_type': 'auth_error'
                }
            elif response.status_code == 429:
                return {
                    'success': False,
                    'error': 'API 请求频率过高，请稍后再试',
                    'error_type': 'rate_limit'
                }
            else:
                return {
                    'success': False,
                    'error': f'API请求失败: {response.status_code} - {response.text}',
                    'error_type': 'api_error'
                }
                
        except requests.exceptions.Timeout:
            return {
                'success': False,
                'error': 'DeepSeek API 响应超时（60秒）\n\n可能原因：\n1. 网络连接不稳定\n2. DeepSeek 服务器响应慢\n3. 需要配置代理\n\n建议：\n- 检查网络连接\n- 稍后重试\n- 如在国内，可能需要配置代理',
                'error_type': 'timeout'
            }
        except requests.exceptions.ConnectionError:
            return {
                'success': False,
                'error': '无法连接到 DeepSeek API\n\n可能原因：\n1. 网络未连接\n2. 防火墙拦截\n3. DNS 解析失败\n4. 需要配置代理\n\n建议：\n- 检查网络连接\n- 关闭防火墙/VPN 试试\n- 配置系统代理',
                'error_type': 'connection_error'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'请求异常: {str(e)}',
                'error_type': 'unknown_error'
            }
    
    def chat_stream(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> Generator[str, None, None]:
        """
        流式聊天 - 逐字输出
        
        Yields:
            str: 每次生成的文本片段
        """
        if not self.is_configured():
            yield json.dumps({
                'success': False,
                'error': '未配置DeepSeek API Key'
            })
            return
        
        try:
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            data = {
                'model': self.model,
                'messages': messages,
                'temperature': temperature,
                'max_tokens': max_tokens,
                'stream': True
            }
            
            response = requests.post(
                f'{self.base_url}/chat/completions',
                headers=headers,
                json=data,
                stream=True,
                timeout=60
            )
            
            if response.status_code == 200:
                for line in response.iter_lines():
                    if line:
                        line = line.decode('utf-8')
                        if line.startswith('data: '):
                            line = line[6:]
                            if line == '[DONE]':
                                break
                            try:
                                chunk = json.loads(line)
                                if 'choices' in chunk and len(chunk['choices']) > 0:
                                    delta = chunk['choices'][0].get('delta', {})
                                    content = delta.get('content', '')
                                    if content:
                                        yield content
                            except json.JSONDecodeError:
                                continue
            else:
                yield json.dumps({
                    'success': False,
                    'error': f'API请求失败: {response.status_code}'
                })
                
        except Exception as e:
            yield json.dumps({
                'success': False,
                'error': f'请求异常: {str(e)}'
            })
    
    def generate_agent_code(
        self,
        description: str,
        agent_type: str = 'processor'
    ) -> Dict[str, Any]:
        """
        使用AI生成Agent代码
        
        Args:
            description: Agent功能描述
            agent_type: Agent类型
            
        Returns:
            生成的代码和元信息
        """
        system_prompt = """你是一个专业的Python Agent代码生成助手。
根据用户描述，生成符合规范的Agent函数代码。

要求：
1. 函数必须包含详细的docstring
2. 参数需要类型注解
3. 包含错误处理
4. 返回格式化的结果字典
5. 代码简洁高效

示例格式：
```python
def my_agent(param1: str, param2: int = 10) -> Dict[str, Any]:
    \"\"\"
    Agent功能描述
    
    Args:
        param1: 参数1说明
        param2: 参数2说明
        
    Returns:
        Dict: 包含处理结果的字典
    \"\"\"
    try:
        # 处理逻辑
        result = ...
        
        return {
            'success': True,
            'result': result
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }
```

只返回代码，不要额外说明。"""
        
        messages = [
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': f'请生成一个{agent_type}类型的Agent：{description}'}
        ]
        
        result = self.chat(messages, temperature=0.3)
        
        if result['success']:
            code = result['content']
            # 提取代码块
            if '```python' in code:
                code = code.split('```python')[1].split('```')[0].strip()
            elif '```' in code:
                code = code.split('```')[1].split('```')[0].strip()
                
            return {
                'success': True,
                'code': code,
                'usage': result.get('usage', {})
            }
        else:
            return result


# 全局LLM实例
deepseek_llm = DeepSeekLLM()


def get_llm_service() -> DeepSeekLLM:
    """获取LLM服务实例"""
    return deepseek_llm

