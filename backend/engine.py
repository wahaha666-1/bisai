# ============================================================================
# 后端层 - 业务逻辑引擎 (Backend - Business Logic)
# ============================================================================

from typing import List, Dict, Any, Callable, Optional
from datetime import datetime
import inspect
import json
import time
import traceback

# ============================================================================
# Agent 注册系统
# ============================================================================

class AgentRegistry:
    """Agent 注册中心"""
    
    def __init__(self, db):
        self.db = db
        self.agents = {}  # 内存缓存
        self._load_agents_from_db()  # 启动时从数据库加载Agents
    
    def _load_agents_from_db(self):
        """从数据库加载所有Agent到内存"""
        try:
            print("[AgentRegistry] 开始从数据库加载Agents...")
            
            with self.db.session_scope() as session:
                db_agents = self.db.get_all_agents(session)
            
            loaded_count = 0
            for db_agent in db_agents:
                agent_name = db_agent['name']
                
                try:
                    # 获取Agent的详细信息（包含代码）
                    with self.db.session_scope() as session:
                        agent_detail = self.db.get_agent(session, agent_name)
                    
                    if not agent_detail or 'code' not in agent_detail:
                        print(f"  ⚠️  跳过Agent '{agent_name}': 缺少代码")
                        continue
                    
                    # 执行代码以获取函数对象
                    code = agent_detail['code']
                    exec_globals = {}
                    exec(code, exec_globals)
                    
                    # 查找定义的函数
                    agent_func = None
                    for name, obj in exec_globals.items():
                        if callable(obj) and not name.startswith('_'):
                            agent_func = obj
                            break
                    
                    if not agent_func:
                        print(f"  ⚠️  跳过Agent '{agent_name}': 代码中未找到函数")
                        continue
                    
                    # 存储到内存
                    self.agents[agent_name] = {
                        'name': agent_name,
                        'agent_type': db_agent.get('agent_type', 'processor'),
                        'description': db_agent.get('description', ''),
                        'function': agent_func,
                        'code': code,
                        'category': db_agent.get('category', '其他'),
                        'icon': db_agent.get('icon', 'default')
                    }
                    
                    loaded_count += 1
                    print(f"  ✓ 加载Agent: {agent_name}")
                    
                except Exception as e:
                    print(f"  ✗ 加载Agent '{agent_name}' 失败: {e}")
                    import traceback
                    traceback.print_exc()
            
            print(f"[AgentRegistry] ✅ 成功加载 {loaded_count} 个Agents")
            
        except Exception as e:
            print(f"[AgentRegistry] ⚠️  从数据库加载Agents失败: {e}")
            import traceback
            traceback.print_exc()
    
    def register(
        self,
        name: str,
        agent_type: str,
        llm_model: str = None,
        tools: List[str] = None,
        description: str = "",
        input_schema: Dict = None,
        output_schema: Dict = None,
        prompt_template: str = None,
        category: str = "其他",
        icon: str = "default"
    ):
        """Agent 注册装饰器"""
        def decorator(func: Callable):
            try:
                code = inspect.getsource(func)
                sig = inspect.signature(func)
                
                # 解析输入参数
                if input_schema is None:
                    input_params = []
                    for param_name, param in sig.parameters.items():
                        param_type = 'Any'
                        if param.annotation != inspect.Parameter.empty:
                            param_type = param.annotation.__name__ if hasattr(param.annotation, '__name__') else str(param.annotation)
                        
                        input_params.append({
                            'name': param_name,
                            'type': param_type,
                            'default': str(param.default) if param.default != inspect.Parameter.empty else None
                        })
                else:
                    input_params = input_schema
                
                # 解析返回类型
                if output_schema is None:
                    output_params = []
                    if sig.return_annotation != inspect.Signature.empty:
                        output_params.append({
                            'name': 'return',
                            'type': str(sig.return_annotation.__name__ if hasattr(sig.return_annotation, '__name__') else sig.return_annotation)
                        })
                else:
                    output_params = output_schema
                
                # 构建 Agent 数据
                agent_data = {
                    'name': name,
                    'agent_type': agent_type,
                    'llm_model': llm_model,
                    'tools': tools or [],
                    'description': description,
                    'code': code,
                    'input_parameters': input_params,
                    'output_parameters': output_params,
                    'prompt_template': prompt_template,
                    'category': category,
                    'icon': icon,
                    'function': func
                }
                
                # 存储到内存和数据库
                self.agents[name] = agent_data
                
                with self.db.session_scope() as session:
                    self.db.add_or_update_agent(
                        session=session,
                        name=name,
                        code=code,
                        metadata={
                            'agent_type': agent_type,
                            'llm_model': llm_model,
                            'description': description,
                            'category': category,
                            'icon': icon,
                            'prompt_template': prompt_template
                        },
                        dependencies=[],
                        triggers=[],
                        input_parameters=input_params,
                        output_parameters=output_params,
                        imports=tools or []
                    )
                
                print(f"✓ Agent '{name}' 注册成功 ({agent_type})")
                
            except Exception as e:
                print(f"✗ 注册 Agent '{name}' 失败: {e}")
                traceback.print_exc()
            
            return func
        
        return decorator
    
    def get_agent(self, name: str) -> Optional[Dict]:
        return self.agents.get(name)
    
    def list_agents(self, category: str = None) -> List[Dict]:
        agents = list(self.agents.values())
        if category:
            agents = [a for a in agents if a.get('category') == category]
        return agents

# ============================================================================
# LLM 服务
# ============================================================================

class LLMService:
    """LLM 服务封装"""
    
    def __init__(self, api_key: str = None, base_url: str = None):
        self.client = None
        try:
            from openai import OpenAI
            if base_url:
                self.client = OpenAI(api_key=api_key, base_url=base_url)
            else:
                self.client = OpenAI(api_key=api_key)
            print("✓ LLM 服务初始化成功")
        except ImportError:
            print("警告：未安装 openai 库，AI Agent 功能将不可用")
        except Exception as e:
            print(f"警告：LLM 服务初始化失败: {e}")
    
    def chat(
        self,
        prompt: str,
        model: str = "gpt-4",
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> Dict[str, Any]:
        """调用 LLM"""
        if not self.client:
            raise Exception("LLM 客户端未初始化")
        
        response = self.client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        content = response.choices[0].message.content
        tokens = response.usage.total_tokens
        
        return {
            'content': content,
            'tokens_used': tokens,
            'model': model,
            'cost': self._calculate_cost(model, tokens)
        }
    
    def _calculate_cost(self, model: str, tokens: int) -> float:
        prices = {
            'gpt-4': 0.03 / 1000,
            'gpt-3.5-turbo': 0.002 / 1000,
            'deepseek-chat': 0.001 / 1000
        }
        return prices.get(model, 0) * tokens

# ============================================================================
# Agent 执行器
# ============================================================================

class AgentExecutor:
    """Agent 执行引擎"""
    
    def __init__(self, db, registry: AgentRegistry, llm_service=None):
        self.db = db
        self.registry = registry
        self.llm_service = llm_service
        self.execution_stack = []
    
    def execute(
        self,
        agent_name: str,
        params: Dict[str, Any],
        context: Dict[str, Any] = None,
        execution_id: int = None
    ) -> Dict[str, Any]:
        """执行 Agent"""
        start_time = time.time()
        parent_log_id = self.execution_stack[-1] if self.execution_stack else None
        
        try:
            print(f"[AgentExecutor] 开始执行 Agent: {agent_name}")
            
            agent = self.registry.get_agent(agent_name)
            if not agent:
                raise Exception(f"Agent '{agent_name}' 不存在")
            
            # 解析参数
            resolved_params = self._resolve_params(params, context or {})
            
            # 如果是 AI Agent，调用 LLM
            if agent['agent_type'] == 'ai_analyzer' and agent.get('llm_model'):
                result = self._execute_ai_agent(agent, resolved_params)
            else:
                # 普通 Agent，直接调用函数
                func = agent['function']
                result = func(**resolved_params)
            
            # 记录日志
            execution_time = time.time() - start_time
            log_id = self._add_log(
                agent_name=agent_name,
                message=f"执行成功",
                log_type='info',
                params=resolved_params,
                output=result,
                time_spent=execution_time,
                parent_log_id=parent_log_id
            )
            
            self.execution_stack.append(log_id)
            
            print(f"[AgentExecutor] Agent '{agent_name}' 执行完成，耗时: {execution_time:.2f}s")
            
            return {
                'success': True,
                'output': result,
                'execution_time': execution_time,
                'error': None
            }
            
        except Exception as e:
            execution_time = time.time() - start_time
            error_msg = f"{type(e).__name__}: {str(e)}"
            
            self._add_log(
                agent_name=agent_name,
                message=f"执行失败: {error_msg}",
                log_type='error',
                params=params,
                time_spent=execution_time,
                parent_log_id=parent_log_id
            )
            
            print(f"[AgentExecutor] Agent '{agent_name}' 执行失败: {error_msg}")
            
            return {
                'success': False,
                'output': None,
                'execution_time': execution_time,
                'error': error_msg
            }
    
    def _execute_ai_agent(self, agent: Dict, params: Dict) -> Any:
        """执行 AI Agent"""
        if not self.llm_service:
            raise Exception("LLM 服务未配置")
        
        prompt_template = agent.get('prompt_template', '')
        prompt = prompt_template.format(**params)
        
        llm_result = self.llm_service.chat(
            prompt=prompt,
            model=agent['llm_model']
        )
        
        return llm_result
    
    def _resolve_params(self, params: Dict, context: Dict) -> Dict:
        """解析参数，支持引用上下文变量"""
        resolved = {}
        for key, value in params.items():
            if isinstance(value, str) and value.startswith('$'):
                var_path = value[1:].split('.')
                resolved[key] = self._get_nested_value(context, var_path)
            else:
                resolved[key] = value
        return resolved
    
    def _get_nested_value(self, data: Dict, path: List[str]) -> Any:
        """获取嵌套字典的值"""
        current = data
        for key in path:
            if isinstance(current, dict):
                current = current.get(key)
            else:
                return None
        return current
    
    def _add_log(
        self,
        agent_name: str,
        message: str,
        log_type: str,
        params: Dict = None,
        output: Any = None,
        time_spent: float = None,
        parent_log_id: int = None
    ) -> int:
        """添加日志"""
        with self.db.session_scope() as session:
            log_id = self.db.add_log(
                session=session,
                agent_name=agent_name,
                message=message,
                timestamp=datetime.utcnow(),
                params=params,
                output=output,
                time_spent=time_spent,
                parent_log_id=parent_log_id,
                log_type=log_type
            )
            return log_id

# ============================================================================
# 工作流引擎
# ============================================================================

class WorkflowEngine:
    """工作流编排引擎"""
    
    def __init__(self, db, agent_executor: AgentExecutor):
        self.db = db
        self.executor = agent_executor
    
    def execute_workflow(
        self,
        workflow_id: int,
        input_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """执行工作流"""
        start_time = time.time()
        
        try:
            print(f"\n{'='*60}")
            print(f"[WorkflowEngine] 开始执行工作流 #{workflow_id}")
            print(f"{'='*60}\n")
            
            with self.db.session_scope() as session:
                workflow = self.db.get_workflow(session, workflow_id)
            
            if not workflow:
                raise Exception(f"工作流 #{workflow_id} 不存在")
            
            workflow_def = json.loads(workflow['workflow_definition']) if isinstance(workflow['workflow_definition'], str) else workflow['workflow_definition']
            
            # 创建执行记录
            with self.db.session_scope() as session:
                execution_id = self.db.create_workflow_execution(
                    session=session,
                    workflow_id=workflow_id,
                    input_data=input_data,
                    status='running',
                    started_at=datetime.utcnow()
                )
            
            print(f"[WorkflowEngine] 执行ID: #{execution_id}")
            
            # 解析执行顺序
            execution_order = self._parse_workflow(workflow_def)
            
            print(f"[WorkflowEngine] 执行计划: {len(execution_order)} 个步骤")
            for i, node in enumerate(execution_order, 1):
                print(f"  步骤 {i}: {node['agent']}")
            print()
            
            # 执行 Agent 链
            context = input_data.copy()
            execution_graph = []
            
            for i, node in enumerate(execution_order, 1):
                agent_name = node['agent']
                node_params = node.get('params', {})
                
                # 如果 node params 为空，使用 context 中的参数
                if not node_params and i == 1:
                    # 第一个 Agent，使用 input_data
                    params = input_data.copy()
                elif not node_params:
                    # 后续 Agent，使用上一个 Agent 的输出
                    prev_result_key = f"{execution_order[i-2]['agent']}_result"
                    params = {'data': context.get(prev_result_key, {})}
                else:
                    # 使用显式指定的参数
                    params = node_params
                
                print(f"[{i}/{len(execution_order)}] 执行 Agent: {agent_name}")
                print(f"  参数: {list(params.keys())}")
                
                node_start = time.time()
                result = self.executor.execute(
                    agent_name=agent_name,
                    params=params,
                    context=context,
                    execution_id=execution_id
                )
                node_time = time.time() - node_start
                
                execution_graph.append({
                    'agent': agent_name,
                    'status': 'completed' if result['success'] else 'failed',
                    'execution_time': node_time,
                    'output': result['output'],
                    'error': result.get('error')
                })
                
                if not result['success']:
                    raise Exception(f"Agent '{agent_name}' 执行失败: {result['error']}")
                
                context[f"{agent_name}_result"] = result['output']
                
                print(f"  ✓ 完成，耗时: {node_time:.2f}s\n")
            
            # 标记完成
            execution_time = time.time() - start_time
            
            with self.db.session_scope() as session:
                self.db.update_workflow_execution(
                    session=session,
                    execution_id=execution_id,
                    status='completed',
                    output_data=context,
                    completed_at=datetime.utcnow(),
                    execution_time=execution_time,
                    execution_graph=execution_graph
                )
            
            print(f"{'='*60}")
            print(f"[WorkflowEngine] 工作流执行完成！")
            print(f"总耗时: {execution_time:.2f}s")
            print(f"{'='*60}\n")
            
            return {
                'success': True,
                'execution_id': execution_id,
                'output': context,
                'execution_time': execution_time,
                'error': None
            }
            
        except Exception as e:
            execution_time = time.time() - start_time
            error_msg = f"{type(e).__name__}: {str(e)}"
            
            try:
                with self.db.session_scope() as session:
                    self.db.update_workflow_execution(
                        session=session,
                        execution_id=execution_id,
                        status='failed',
                        error_message=error_msg,
                        completed_at=datetime.utcnow(),
                        execution_time=execution_time
                    )
            except:
                pass
            
            print(f"\n{'='*60}")
            print(f"[WorkflowEngine] 工作流执行失败！")
            print(f"错误: {error_msg}")
            print(f"{'='*60}\n")
            
            return {
                'success': False,
                'execution_id': execution_id if 'execution_id' in locals() else None,
                'output': None,
                'execution_time': execution_time,
                'error': error_msg
            }
    
    def _parse_workflow(self, workflow_def: Dict) -> List[Dict]:
        """解析工作流，支持两种格式"""
        
        # 格式1: 简化格式 {"agents": [...], "sequence": [...]}
        if 'agents' in workflow_def and 'sequence' in workflow_def:
            return self._parse_simple_workflow(workflow_def)
        
        # 格式2: 完整格式 {"nodes": [...], "edges": [...]}
        elif 'nodes' in workflow_def:
            return self._parse_graph_workflow(workflow_def)
        
        else:
            raise Exception("工作流定义格式错误，需要 'agents'+'sequence' 或 'nodes'+'edges'")
    
    def _parse_simple_workflow(self, workflow_def: Dict) -> List[Dict]:
        """解析简化格式的工作流"""
        agents = workflow_def['agents']
        sequence = workflow_def.get('sequence', [])
        
        # 如果没有 sequence，按 agents 顺序执行
        if not sequence:
            return [{'agent': agent, 'params': {}} for agent in agents]
        
        # 解析 sequence（增加容错：处理旧格式的整数列表）
        result = []
        for step in sequence:
            # 兼容旧格式：如果是整数，表示agents数组的索引
            if isinstance(step, int):
                if 0 <= step < len(agents):
                    agent_name = agents[step]
                    result.append({'agent': agent_name, 'params': {}})
                continue
            
            # 新格式：字典
            if isinstance(step, dict):
                agent_name = step.get('agent')
                params = step.get('params', {})
                
                if agent_name not in agents:
                    raise Exception(f"Agent '{agent_name}' 不在 agents 列表中")
                
                result.append({
                    'agent': agent_name,
                    'params': params
                })
        
        return result
    
    def _parse_graph_workflow(self, workflow_def: Dict) -> List[Dict]:
        """解析图形式工作流，拓扑排序"""
        nodes = workflow_def['nodes']
        edges = workflow_def.get('edges', [])
        
        node_map = {node['id']: node for node in nodes}
        graph = {node['id']: [] for node in nodes}
        in_degree = {node['id']: 0 for node in nodes}
        
        for edge in edges:
            graph[edge['from']].append(edge['to'])
            in_degree[edge['to']] += 1
        
        queue = [nid for nid, degree in in_degree.items() if degree == 0]
        result = []
        
        while queue:
            current = queue.pop(0)
            result.append(node_map[current])
            
            for neighbor in graph[current]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)
        
        if len(result) != len(nodes):
            raise Exception("工作流定义存在循环依赖")
        
        return result

