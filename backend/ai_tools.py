# ============================================================================
# AI工具系统 - 供AI调用的工具函数
# ============================================================================

import json
from typing import Dict, List, Any, Optional

class AIToolRegistry:
    """AI工具注册表"""
    
    def __init__(self, db, registry):
        self.db = db
        self.registry = registry
        self.tools = {}
        self._register_builtin_tools()
    
    def _register_builtin_tools(self):
        """注册内置工具"""
        
        # 工具1：创建单个Agent
        self.tools['create_agent'] = {
            'name': 'create_agent',
            'description': '创建一个Agent并注册到系统',
            'parameters': {
                'type': 'object',
                'properties': {
                    'name': {'type': 'string', 'description': 'Agent名称'},
                    'code': {'type': 'string', 'description': '完整的Python函数代码'},
                    'agent_type': {'type': 'string', 'description': 'Agent类型: processor/analyzer/converter'},
                    'description': {'type': 'string', 'description': 'Agent功能描述'}
                },
                'required': ['name', 'code', 'agent_type']
            },
            'function': self.create_agent
        }
        
        # 工具2：创建工作流
        self.tools['create_workflow'] = {
            'name': 'create_workflow',
            'description': '创建一个工作流',
            'parameters': {
                'type': 'object',
                'properties': {
                    'name': {'type': 'string', 'description': '工作流名称'},
                    'description': {'type': 'string', 'description': '工作流描述'},
                    'agents': {'type': 'array', 'description': 'Agent名称列表'},
                    'definition': {'type': 'object', 'description': '工作流定义（包含nodes和edges）'}
                },
                'required': ['name', 'agents']
            },
            'function': self.create_workflow
        }
        
        # 工具3：列出已有的Agent
        self.tools['list_agents'] = {
            'name': 'list_agents',
            'description': '列出系统中已注册的所有Agent',
            'parameters': {
                'type': 'object',
                'properties': {}
            },
            'function': self.list_agents
        }
        
        # 工具4：创建复杂业务流程
        self.tools['create_business_process'] = {
            'name': 'create_business_process',
            'description': '创建复杂的业务处理流程（包含多个Agent和工作流）',
            'parameters': {
                'type': 'object',
                'properties': {
                    'process_name': {'type': 'string', 'description': '业务流程名称'},
                    'agents': {'type': 'array', 'description': 'Agent列表'},
                    'workflows': {'type': 'array', 'description': '工作流列表'},
                    'description': {'type': 'string', 'description': '流程描述'}
                },
                'required': ['process_name', 'agents']
            },
            'function': self.create_business_process
        }
    
    def create_agent(self, name: str, code: str, agent_type: str, description: str = '') -> Dict[str, Any]:
        """创建Agent"""
        try:
            # 执行代码
            exec_globals = {}
            exec(code, exec_globals)
            
            # 查找函数
            agent_func = None
            for func_name, obj in exec_globals.items():
                if callable(obj) and not func_name.startswith('_'):
                    agent_func = obj
                    break
            
            if not agent_func:
                return {'success': False, 'error': '未找到Agent函数'}
            
            # 注册Agent
            self.registry.register_agent(
                name=name,
                func=agent_func,
                agent_type=agent_type,
                description=description
            )
            
            return {
                'success': True,
                'message': f'Agent "{name}" 创建成功',
                'agent_name': name,
                'agent_type': agent_type
            }
        except Exception as e:
            return {'success': False, 'error': f'创建Agent失败: {str(e)}'}
    
    def create_workflow(self, name: str, agents: List[str], description: str = '', 
                       definition: Optional[Dict] = None) -> Dict[str, Any]:
        """创建工作流"""
        try:
            # 构建工作流定义
            if not definition:
                definition = {
                    'agents': agents,
                    'sequence': list(range(len(agents)))
                }
            
            with self.db.session_scope() as session:
                workflow_id = self.db.create_workflow(
                    session,
                    name=name,
                    description=description or f'包含 {len(agents)} 个Agent的工作流',
                    definition=definition
                )
            
            return {
                'success': True,
                'message': f'工作流 "{name}" 创建成功',
                'workflow_id': workflow_id,
                'workflow_name': name,
                'agents': agents
            }
        except Exception as e:
            return {'success': False, 'error': f'创建工作流失败: {str(e)}'}
    
    def list_agents(self) -> Dict[str, Any]:
        """列出所有Agent"""
        try:
            agents = self.registry.list_agents()
            return {
                'success': True,
                'agents': [
                    {
                        'name': agent['name'],
                        'type': agent['type'],
                        'description': agent.get('description', '')
                    }
                    for agent in agents
                ],
                'count': len(agents)
            }
        except Exception as e:
            return {'success': False, 'error': f'获取Agent列表失败: {str(e)}'}
    
    def create_business_process(self, process_name: str, agents: List[Dict], 
                                workflows: Optional[List[Dict]] = None, 
                                description: str = '') -> Dict[str, Any]:
        """创建复杂业务流程"""
        try:
            created_agents = []
            created_workflows = []
            
            # 创建所有Agent
            for agent_data in agents:
                result = self.create_agent(**agent_data)
                if result['success']:
                    created_agents.append(result['agent_name'])
                else:
                    # 继续尝试创建其他Agent
                    print(f"创建Agent失败: {result.get('error')}")
            
            # 创建所有工作流
            if workflows:
                for workflow_data in workflows:
                    result = self.create_workflow(**workflow_data)
                    if result['success']:
                        created_workflows.append(result['workflow_name'])
            else:
                # 如果没有指定工作流，创建一个默认的
                result = self.create_workflow(
                    name=process_name,
                    agents=created_agents,
                    description=description
                )
                if result['success']:
                    created_workflows.append(result['workflow_name'])
            
            return {
                'success': True,
                'message': f'业务流程 "{process_name}" 创建成功',
                'process_name': process_name,
                'created_agents': created_agents,
                'created_workflows': created_workflows,
                'agent_count': len(created_agents),
                'workflow_count': len(created_workflows)
            }
        except Exception as e:
            return {'success': False, 'error': f'创建业务流程失败: {str(e)}'}
    
    def call_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """调用工具"""
        if tool_name not in self.tools:
            return {'success': False, 'error': f'工具 "{tool_name}" 不存在'}
        
        tool = self.tools[tool_name]
        try:
            return tool['function'](**parameters)
        except Exception as e:
            return {'success': False, 'error': f'调用工具失败: {str(e)}'}
    
    def get_tools_description(self) -> str:
        """获取所有工具的描述（用于系统提示词）"""
        descriptions = []
        for tool_name, tool_info in self.tools.items():
            desc = f"- {tool_name}: {tool_info['description']}"
            descriptions.append(desc)
        return '\n'.join(descriptions)
    
    def get_tools_schema(self) -> List[Dict]:
        """获取工具的JSON Schema（用于Function Calling）"""
        schemas = []
        for tool_name, tool_info in self.tools.items():
            schema = {
                'type': 'function',
                'function': {
                    'name': tool_name,
                    'description': tool_info['description'],
                    'parameters': tool_info['parameters']
                }
            }
            schemas.append(schema)
        return schemas


# 全局实例
_tool_registry = None

def get_tool_registry(db=None, registry=None):
    """获取工具注册表单例"""
    global _tool_registry
    if _tool_registry is None and db and registry:
        _tool_registry = AIToolRegistry(db, registry)
    return _tool_registry

