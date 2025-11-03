# ============================================================================
# API 层 - REST API 接口 (API Layer - REST Endpoints)
# ============================================================================

from flask import Blueprint, jsonify, request, session
from backend.database import Database
from backend.engine import WorkflowEngine

# 创建 Blueprint
api = Blueprint('api', __name__, url_prefix='/api')

# 将在 app.py 中注入
db = None
engine = None
registry = None

def init_api(database: Database, workflow_engine: WorkflowEngine, agent_registry=None):
    """初始化 API 层"""
    global db, engine, registry
    db = database
    engine = workflow_engine
    registry = agent_registry

# ============================================================================
# Agent API
# ============================================================================

@api.route('/agents', methods=['GET'])
def get_agents():
    """获取所有 Agent"""
    try:
        with db.session_scope() as db_session:
            agents = db.get_all_agents(db_session)
            return jsonify(agents), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api.route('/agents', methods=['POST'])
def create_agent():
    """创建新 Agent"""
    try:
        data = request.get_json()
        name = data.get('name')
        agent_type = data.get('agent_type', 'other')
        description = data.get('description', '')
        code = data.get('code')
        
        if not name or not code:
            return jsonify({'error': '缺少必填字段：name 和 code'}), 400
        
        with db.session_scope() as db_session:
            # 创建 Agent
            metadata = {
                'agent_type': agent_type,
                'description': description,
                'category': '用户创建',
                'author': '用户'
            }
            
            db.add_or_update_agent(
                session=db_session,
                name=name,
                code=code,
                metadata=metadata,
                dependencies=[],
                triggers=None,
                input_parameters={},
                output_parameters={},
                imports=None
            )
        
        return jsonify({'message': 'Agent 创建成功', 'name': name}), 201
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api.route('/agents/<name>', methods=['GET'])
def get_agent(name):
    """获取单个 Agent"""
    try:
        with db.session_scope() as db_session:
            agent = db.get_agent(db_session, name)
            if agent:
                return jsonify(agent), 200
            else:
                return jsonify({'error': 'Agent not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============================================================================
# 工作流 API
# ============================================================================

@api.route('/workflows', methods=['GET'])
def get_workflows():
    """获取所有工作流"""
    try:
        with db.session_scope() as db_session:
            workflows = db.get_all_workflows(db_session)
            return jsonify(workflows), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api.route('/workflows/<int:workflow_id>', methods=['GET'])
def get_workflow(workflow_id):
    """获取单个工作流"""
    try:
        with db.session_scope() as db_session:
            workflow = db.get_workflow(db_session, workflow_id)
            if workflow:
                return jsonify(workflow), 200
            else:
                return jsonify({'error': 'Workflow not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api.route('/workflows', methods=['POST'])
def create_workflow():
    """创建工作流"""
    try:
        data = request.get_json()
        
        required_fields = ['name', 'workflow_definition']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing field: {field}'}), 400
        
        with db.session_scope() as db_session:
            workflow_id = db.create_workflow(
                session=db_session,
                name=data['name'],
                description=data.get('description', ''),
                workflow_definition=data['workflow_definition'],
                category=data.get('category', '其他'),
                trigger_type=data.get('trigger_type', 'manual')
            )
        
        return jsonify({'workflow_id': workflow_id, 'message': 'Workflow created'}), 201
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api.route('/workflows/<int:workflow_id>/execute', methods=['POST'])
def execute_workflow(workflow_id):
    """执行工作流"""
    try:
        input_data = request.get_json() or {}
        result = engine.execute_workflow(workflow_id, input_data)
        
        # 打印返回结果，方便调试
        print(f"\n[API] 返回结果: success={result['success']}, output={result.get('output')}\n")
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 500
    
    except Exception as e:
        print(f"\n[API] 执行异常: {e}\n")
        return jsonify({'success': False, 'error': str(e)}), 500

# ============================================================================
# 工作流执行记录 API
# ============================================================================

@api.route('/executions/<int:execution_id>', methods=['GET'])
def get_execution(execution_id):
    """获取执行记录"""
    try:
        with db.session_scope() as db_session:
            execution = db.get_workflow_execution(db_session, execution_id)
            if execution:
                return jsonify(execution), 200
            else:
                return jsonify({'error': 'Execution not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============================================================================
# 日志 API
# ============================================================================

@api.route('/logs', methods=['GET'])
def get_logs():
    """获取日志"""
    try:
        agent_name = request.args.get('agent_name')
        limit = request.args.get('limit', 100, type=int)
        
        with db.session_scope() as db_session:
            logs = db.get_logs(db_session, agent_name=agent_name, limit=limit)
            return jsonify(logs), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============================================================================
# 统计 API
# ============================================================================

@api.route('/stats', methods=['GET'])
def get_stats():
    """获取统计数据"""
    try:
        with db.session_scope() as db_session:
            agents = db.get_all_agents(db_session)
            workflows = db.get_all_workflows(db_session)
            
            total_executions = sum(w.get('total_executions', 0) for w in workflows)
            
            return jsonify({
                'agent_count': len(agents),
                'workflow_count': len(workflows),
                'total_executions': total_executions,
                'avg_success_rate': sum(a.get('success_rate', 0) for a in agents) / len(agents) if agents else 0
            }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============================================================================
# 密钥 API
# ============================================================================

@api.route('/keys', methods=['GET'])
def get_keys():
    """获取所有密钥名称"""
    try:
        with db.session_scope() as db_session:
            keys = db.get_all_secret_keys(db_session)
            return jsonify(keys), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api.route('/keys', methods=['POST'])
def add_key():
    """添加密钥"""
    try:
        data = request.get_json()
        
        if 'name' not in data or 'value' not in data:
            return jsonify({'error': 'Missing name or value'}), 400
        
        with db.session_scope() as db_session:
            db.add_secret_key(db_session, data['name'], data['value'])
        
        return jsonify({'message': 'Key added successfully'}), 201
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============================================================================
# 认证 API
# ============================================================================

@api.route('/auth/register', methods=['POST'])
def register():
    """用户注册"""
    try:
        data = request.get_json()
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        
        if not username or not email or not password:
            return jsonify({'error': '请填写所有字段'}), 400
        
        with db.session_scope() as db_session:
            # 检查用户是否存在
            existing_user = db.get_user_by_username(db_session, username)
            if existing_user:
                return jsonify({'error': '用户名已存在'}), 400
            
            # 创建用户
            user_id = db.create_user(db_session, username, email, password)
        
        return jsonify({'message': '注册成功', 'user_id': user_id}), 201
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api.route('/auth/login', methods=['POST'])
def login():
    """用户登录"""
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({'error': '请输入用户名和密码'}), 400
        
        with db.session_scope() as db_session:
            user = db.get_user_by_username(db_session, username)
            
            if not user or not user.verify_password(password):
                return jsonify({'error': '用户名或密码错误'}), 401
            
            if not user.is_active:
                return jsonify({'error': '账号已被禁用'}), 403
            
            # 更新最后登录时间
            db.update_last_login(db_session, user.id)
            
            # 在 session 关闭前提取需要的数据
            user_data = {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'role': user.role
            }
            
            # 设置 session (Flask 的用户会话)
            session['user_id'] = user.id
            session['username'] = user.username
            session['role'] = user.role
        
        # 在 session 外返回数据
        return jsonify({
            'message': '登录成功',
            'user': user_data
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api.route('/auth/logout', methods=['POST'])
def logout():
    """用户登出"""
    session.clear()
    return jsonify({'message': '已登出'}), 200

@api.route('/auth/me', methods=['GET'])
def get_current_user():
    """获取当前登录用户"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': '未登录'}), 401
    
    try:
        with db.session_scope() as db_session:
            user = db.get_user_by_id(db_session, user_id)
            if not user:
                return jsonify({'error': '用户不存在'}), 404
            
            # 在 session 关闭前提取需要的数据
            user_data = {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'role': user.role,
                'last_login': user.last_login.isoformat() if user.last_login else None
            }
        
        return jsonify(user_data), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api.route('/auth/users', methods=['GET'])
def list_users():
    """获取所有用户（管理员功能）"""
    # 检查权限
    if session.get('role') != 'admin':
        return jsonify({'error': '权限不足'}), 403
    
    try:
        with db.session_scope() as db_session:
            users = db.get_all_users(db_session)
            return jsonify(users), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ===========================================================================
#  Rd� API
#============================================================================

# ============================================================================
# 删除 API
# ============================================================================

@api.route('/agents/<string:agent_name>', methods=['DELETE'])
def delete_agent(agent_name):
    """删除 Agent"""
    try:
        from backend.models import AIAgent
        with db.session_scope() as db_session:
            agent = db_session.query(AIAgent).filter_by(name=agent_name).first()
            if agent:
                db_session.delete(agent)
                return jsonify({'message': f'Agent {agent_name} 删除成功'}), 200
            else:
                return jsonify({'error': 'Agent 不存在'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api.route('/workflows/<int:workflow_id>', methods=['DELETE'])
def delete_workflow(workflow_id):
    """删除工作流"""
    try:
        from backend.models import Workflow
        with db.session_scope() as db_session:
            workflow = db_session.query(Workflow).filter_by(id=workflow_id).first()
            if workflow:
                db_session.delete(workflow)
                return jsonify({'message': f'工作流 #{workflow_id} 删除成功'}), 200
            else:
                return jsonify({'error': '工作流不存在'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============================================================================
# AI 对话 API
# ============================================================================

@api.route('/chat/sessions', methods=['GET', 'POST'])
def manage_chat_sessions():
    """管理对话会话"""
    if request.method == 'GET':
        # 获取会话列表
        try:
            with db.session_scope() as db_session:
                sessions = db.get_chat_sessions(db_session, limit=50)
                return jsonify(sessions), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    elif request.method == 'POST':
        # 创建新会话
        try:
            data = request.get_json() or {}
            title = data.get('title', '新对话')
            
            with db.session_scope() as db_session:
                session_id = db.create_chat_session(db_session, title=title)
                return jsonify({'session_id': session_id, 'message': '会话创建成功'}), 201
        except Exception as e:
            return jsonify({'error': str(e)}), 500


@api.route('/chat/sessions/<int:session_id>/messages', methods=['GET', 'POST'])
def manage_chat_messages(session_id):
    """管理对话消息"""
    print(f"\n{'='*60}")
    print(f"[API请求] {request.method} /api/chat/sessions/{session_id}/messages")
    print(f"[API请求] 时间: {__import__('datetime').datetime.now()}")
    print(f"{'='*60}\n")
    
    if request.method == 'GET':
        # 获取消息历史
        try:
            with db.session_scope() as db_session:
                messages = db.get_chat_messages(db_session, session_id)
                return jsonify(messages), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    elif request.method == 'POST':
        # 发送消息并获取AI回复
        try:
            from backend.llm_service import get_llm_service
            
            data = request.get_json()
            user_message = data.get('message', '')
            
            if not user_message:
                return jsonify({'error': '消息内容不能为空'}), 400
            
            llm = get_llm_service()
            
            if not llm.is_configured():
                return jsonify({
                    'error': '未配置 DeepSeek API Key',
                    'message': '请在设置中配置 API Key'
                }), 400
            
            # 保存用户消息
            with db.session_scope() as db_session:
                db.add_chat_message(db_session, session_id, 'user', user_message)
                
                # 获取历史消息
                history = db.get_chat_messages(db_session, session_id, limit=20)
            
            # 构建系统提示词
            system_prompt = """你是 AgentFlow 平台的AI助手。AgentFlow 是一个企业级 AI Agent 工作流编排平台。

【平台核心功能】
1. 🤖 AI Agent 管理
   - 创建自定义Agent（Python函数）
   - 注册Agent到系统
   - 管理Agent生命周期
   - Agent类型：processor（处理器）、analyzer（分析器）、converter（转换器）

2. 🔄 工作流编排
   - 将多个Agent串联成工作流
   - 支持顺序执行和条件分支
   - 可视化工作流设计
   - 工作流版本管理

3. ⚡ 工作流执行
   - 一键执行工作流
   - 实时查看执行日志
   - 支持参数传递
   - 错误处理和重试

4. 💬 AI辅助功能（你的角色）
   - 生成Agent代码
   - 提供工作流设计建议
   - 解答技术问题
   - 平台使用指导

5. 📊 数据看板
   - 执行历史统计
   - 性能分析
   - Agent使用情况

6. 👥 用户管理
   - 用户注册登录
   - 权限控制（admin/user）
   - 会话管理

【你的职责】
- 帮助用户生成Python Agent代码
- 提供工作流设计方案
- 解答平台使用问题
- 提供技术咨询

【重要说明】
- 本平台不支持文件上传（PDF、图片等）
- 专注于Agent和工作流的创建与管理
- 所有Agent都是Python函数
- 工作流通过JSON配置定义

【特殊功能：智能创建系统】

你具有强大的Agent和工作流创建能力，可以处理简单和复杂的业务场景。

## 创建方式

### 1. 简单场景（1-3个Agent）
直接生成代码并在回复末尾添加创建标记：

```CREATE_AGENTS_AND_WORKFLOW
{
  "agents": [
    {
      "name": "agent名称",
      "type": "processor",
      "description": "Agent描述",
      "code": "def agent_function(param1: str = 'default') -> dict:\\n    \"\"\"函数说明\"\"\"\\n    try:\\n        result = 处理逻辑\\n        return {'success': True, 'result': result}\\n    except Exception as e:\\n        return {'success': False, 'error': str(e)}"
    }
  ],
  "workflow": {
    "name": "工作流名称",
    "description": "工作流描述"
  }
}
```

### 2. 复杂业务系统（4+个Agent）
当用户要求创建复杂系统（如电商、客服、旅游规划等）时：

**步骤1：分析业务流程**
- 识别关键业务阶段
- 确定每个阶段需要的Agent
- 设计Agent之间的协作关系

**步骤2：设计Agent架构**
```
【阶段1】数据接入
- Agent1: 功能描述
- Agent2: 功能描述

【阶段2】数据处理
- Agent3: 功能描述
- Agent4: 功能描述

【阶段3】结果输出
- Agent5: 功能描述
```

**步骤3：生成完整系统**
为每个Agent生成：
- 完整的Python函数（带类型注解）
- 详细的docstring
- 完善的错误处理
- 标准化的返回格式

**步骤4：添加创建标记**
```CREATE_AGENTS_AND_WORKFLOW
{
  "agents": [
    // 所有Agent的完整定义
  ],
  "workflow": {
    "name": "业务系统名称",
    "description": "完整的业务流程描述"
  }
}
```

## 复杂场景处理指南

### 电商系统
包含：订单验证、库存检查、价格计算、支付验证、库存扣减、物流分配、通知生成等

### 客服系统
包含：意图识别、情绪分析、知识库检索、答案生成、优先级评估、人工转接等

### 旅游规划
包含：需求解析、偏好分析、景点推荐、路线优化、住宿推荐、行程生成等

### 数据分析
包含：数据接入、格式转换、数据清洗、异常检测、统计分析、可视化、报告生成等

## 代码质量要求

1. **函数签名**
```python
def agent_name(param1: str = 'default', param2: int = 0) -> dict:
```

2. **文档字符串**
```python
\"\"\"Agent功能的详细说明
    
Args:
    param1: 参数说明
    param2: 参数说明
    
Returns:
    dict: 返回值说明
\"\"\"
```

3. **错误处理**
```python
try:
    # 主要逻辑
    return {'success': True, 'result': result}
except Exception as e:
    return {'success': False, 'error': str(e)}
```

4. **标准返回格式**
- 成功：`{'success': True, 'result': 结果数据, ...}`
- 失败：`{'success': False, 'error': 错误信息}`

## 注意事项

1. 对于简单任务（1-3个Agent），直接生成代码
2. 对于复杂系统（4+个Agent），先展示架构设计，再生成代码
3. 所有代码必须是完整可执行的Python函数
4. 每个Agent都要有独立的功能和清晰的职责
5. 工作流名称要体现业务含义
6. Agent名称要使用snake_case命名风格

请基于以上信息回答用户问题，创建强大的企业级系统。"""
            
            # 构建消息列表（添加系统提示词）
            messages = [{'role': 'system', 'content': system_prompt}]
            messages.extend([{'role': msg['role'], 'content': msg['content']} for msg in history])
            
            # 调用 LLM（流式输出）
            from flask import Response
            import json as json_module
            
            def generate_stream():
                """生成流式响应 - 支持工具调用的实时流式输出"""
                import sys
                import time
                full_content = ""
                
                print(f"\n[对话流式输出] 开始生成回复...")
                print(f"[对话流式输出] 会话ID: {session_id}")
                print(f"[对话流式输出] 消息数量: {len(messages)}")
                
                try:
                    # 获取工具列表
                    from backend.tools import global_tool_registry
                    tools = global_tool_registry.get_function_schemas()
                    print(f"[对话流式输出] 可用工具数量: {len(tools)}")
                    
                    # 第一次调用：可能返回工具调用请求
                    response = llm.chat(
                        messages, 
                        temperature=0.7, 
                        stream=False,  # 工具调用不使用流式
                        tools=tools if len(tools) > 0 else None,
                        tool_choice="auto"
                    )
                    
                    if not response['success']:
                        error_msg = response.get('error', '未知错误')
                        error_type = response.get('error_type', 'unknown')
                        print(f"[对话流式输出] ❌ LLM调用失败: {error_msg} (类型: {error_type})")
                        yield f"data: {json_module.dumps({'success': False, 'error': error_msg, 'error_type': error_type, 'done': True}, ensure_ascii=False)}\n\n"
                        return
                    
                    print(f"[对话流式输出] ✅ LLM调用成功")
                    
                    # 检查是否需要调用工具
                    if response.get('tool_calls'):
                        tool_calls = response['tool_calls']
                        print(f"\n[工具调用] AI请求调用 {len(tool_calls)} 个工具")
                        
                        # 执行所有工具调用
                        tool_messages = []
                        for tool_call in tool_calls:
                            tool_name = tool_call['function']['name']
                            tool_args = json_module.loads(tool_call['function']['arguments'])
                            
                            print(f"[工具调用] 执行工具: {tool_name}, 参数: {tool_args}")
                            
                            # 发送工具调用通知
                            yield f"data: {json_module.dumps({'success': True, 'tool_call': {'name': tool_name, 'arguments': tool_args}, 'done': False}, ensure_ascii=False)}\n\n"
                            sys.stdout.flush()
                            
                            # 执行工具
                            tool_result = global_tool_registry.execute_tool(tool_name, tool_args)
                            print(f"[工具调用] 工具结果: {tool_result}")
                            
                            # 添加工具结果消息
                            tool_messages.append({
                                "role": "tool",
                                "tool_call_id": tool_call['id'],
                                "content": json_module.dumps(tool_result, ensure_ascii=False)
                            })
                        
                        # 将工具结果添加到对话历史
                        messages.append(response['message'])  # AI的工具调用请求
                        messages.extend(tool_messages)  # 工具执行结果
                        
                        # 第二次调用：获取基于工具结果的最终回复
                        print("[工具调用] 获取基于工具结果的最终回复...")
                        final_response = llm.chat(messages, temperature=0.7, stream=True)
                        
                        if not final_response['success']:
                            yield f"data: {json_module.dumps({'success': False, 'error': final_response.get('error', '未知错误'), 'done': True}, ensure_ascii=False)}\n\n"
                            return
                        
                        # 流式输出最终回复
                        for chunk in final_response.get('stream', []):
                            if chunk:
                                full_content += chunk
                                data = json_module.dumps({'success': True, 'content': chunk, 'done': False}, ensure_ascii=False)
                                yield f"data: {data}\n\n"
                                sys.stdout.flush()
                    else:
                        # 没有工具调用，重新发起真正的流式调用
                        print("[对话流式输出] 无工具调用，重新发起流式请求...")
                        
                        # 移除工具参数，重新流式调用
                        stream_response = llm.chat(messages, temperature=0.7, stream=True)
                        
                        if not stream_response['success']:
                            yield f"data: {json_module.dumps({'success': False, 'error': stream_response.get('error', '未知错误'), 'done': True}, ensure_ascii=False)}\n\n"
                            return
                        
                        # 真正的流式输出
                        print("[对话流式输出] ✅ 开始真正流式输出...")
                        for chunk in stream_response.get('stream', []):
                            if chunk:
                                full_content += chunk
                                data = json_module.dumps({'success': True, 'content': chunk, 'done': False}, ensure_ascii=False)
                                yield f"data: {data}\n\n"
                                sys.stdout.flush()
                    
                    # 保存完整消息到数据库
                    with db.session_scope() as save_session:
                        db.add_chat_message(save_session, session_id, 'assistant', full_content)
                    
                    # 发送结束标记
                    yield f"data: {json_module.dumps({'success': True, 'done': True, 'full_content': full_content}, ensure_ascii=False)}\n\n"
                    
                except Exception as e:
                    import traceback
                    traceback.print_exc()
                    yield f"data: {json_module.dumps({'success': False, 'error': str(e), 'done': True}, ensure_ascii=False)}\n\n"
            
            return Response(
                generate_stream(), 
                mimetype='text/event-stream',
                headers={
                    'Cache-Control': 'no-cache, no-transform',
                    'X-Accel-Buffering': 'no',
                    'Content-Type': 'text/event-stream; charset=utf-8',
                    'Connection': 'keep-alive'
                }
            )
                
        except Exception as e:
            return jsonify({'error': str(e)}), 500


@api.route('/chat/sessions/<int:session_id>', methods=['DELETE'])
def delete_chat_session(session_id):
    """删除对话会话"""
    try:
        with db.session_scope() as db_session:
            db.delete_chat_session(db_session, session_id)
            return jsonify({'message': '会话删除成功'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@api.route('/chat/config', methods=['GET', 'POST'])
def manage_chat_config():
    """管理聊天配置（API Key等）"""
    if request.method == 'GET':
        # 检查配置状态
        from backend.llm_service import get_llm_service
        llm = get_llm_service()
        
        response_data = {
            'configured': llm.is_configured(),
            'model': llm.model if llm.is_configured() else None
        }
        
        # 如果已配置，返回API Key的前缀
        if llm.is_configured() and llm.api_key:
            response_data['key_prefix'] = llm.api_key[:10] + '...'
        
        return jsonify(response_data), 200
    
    elif request.method == 'POST':
        # 设置 API Key
        try:
            from backend.llm_service import get_llm_service
            
            data = request.get_json()
            api_key = data.get('api_key', '').strip()
            
            if not api_key:
                return jsonify({'error': 'API Key 不能为空'}), 400
            
            # 验证API Key格式
            if not api_key.startswith('sk-'):
                return jsonify({'error': 'API Key 格式错误，应该以 sk- 开头'}), 400
            
            llm = get_llm_service()
            # 持久化保存到数据库
            llm.set_api_key(api_key, persist=True)
            
            print(f"[API Key] ✅ 已保存到数据库")
            
            return jsonify({
                'message': 'API Key 配置成功',
                'key_prefix': api_key[:10] + '...'  # 只返回前10个字符
            }), 200
        except Exception as e:
            print(f"[API Key] ❌ 保存失败: {e}")
            return jsonify({'error': f'保存失败: {str(e)}'}), 500


@api.route('/ai/generate-agent', methods=['POST'])
def generate_agent_code():
    """使用AI生成Agent代码"""
    try:
        from backend.llm_service import get_llm_service
        
        data = request.get_json()
        description = data.get('description', '')
        agent_type = data.get('agent_type', 'processor')
        
        if not description:
            return jsonify({'error': '请提供Agent功能描述'}), 400
        
        llm = get_llm_service()
        
        if not llm.is_configured():
            return jsonify({
                'error': '未配置 DeepSeek API Key',
                'message': '请先配置 API Key'
            }), 400
        
        result = llm.generate_agent_code(description, agent_type)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@api.route('/ai/create-from-chat', methods=['POST'])
def create_from_chat():
    """从AI对话创建Agent和工作流"""
    try:
        data = request.get_json()
        agents = data.get('agents', [])
        workflow = data.get('workflow', {})
        
        if not agents:
            return jsonify({'error': '没有Agent定义'}), 400
        
        created_agents = []
        created_workflow = None
        
        # 创建Agents
        for agent_data in agents:
            agent_name = agent_data.get('name')
            agent_code = agent_data.get('code')
            agent_type = agent_data.get('type', 'processor')
            description = agent_data.get('description', '')
            
            print(f"\n[创建Agent] 开始处理: {agent_name}")
            print(f"[创建Agent] 类型: {agent_type}")
            print(f"[创建Agent] 代码长度: {len(agent_code) if agent_code else 0}")
            
            if not agent_name or not agent_code:
                print(f"[创建Agent] ❌ 跳过：缺少name或code")
                continue
            
            try:
                # 执行代码以注册函数
                exec_globals = {}
                print(f"[创建Agent] 开始执行代码...")
                exec(agent_code, exec_globals)
                print(f"[创建Agent] 代码执行成功，globals: {list(exec_globals.keys())}")
                
                # 查找定义的函数
                agent_func = None
                for name, obj in exec_globals.items():
                    if callable(obj) and not name.startswith('_'):
                        agent_func = obj
                        print(f"[创建Agent] 找到函数: {name}")
                        break
                
                if agent_func:
                    # 直接添加到registry（绕过装饰器，因为动态函数无法获取源代码）
                    print(f"[创建Agent] 开始注册Agent到registry...")
                    
                    # 直接存储到registry（注意：字段名必须是agent_type，与执行引擎匹配）
                    registry.agents[agent_name] = {
                        'name': agent_name,
                        'agent_type': agent_type,  # 修复：改为agent_type
                        'description': description,
                        'function': agent_func,
                        'code': agent_code,
                        'category': '动态创建',
                        'icon': 'ai'
                    }
                    
                    # 保存到数据库
                    try:
                        with db.session_scope() as db_session:
                            # 构建metadata
                            metadata = {
                                'agent_type': agent_type,
                                'category': 'AI动态创建',
                                'icon': '🤖',
                                'description': description
                            }
                            
                            # 创建或更新Agent（使用正确的方法名和参数）
                            db.add_or_update_agent(
                                session=db_session,
                                name=agent_name,
                                code=agent_code,
                                metadata=metadata,
                                dependencies=[],
                                triggers=[],
                                input_parameters=[],
                                output_parameters=[],
                                imports=None
                            )
                        print(f"[创建Agent] ✅ 已保存到数据库")
                    except Exception as db_error:
                        import traceback
                        print(f"[创建Agent] ⚠️ 数据库保存失败: {db_error}")
                        traceback.print_exc()
                        # 不阻断流程，Agent已在内存中
                    
                    created_agents.append(agent_name)
                    print(f"[创建Agent] ✅ 成功注册: {agent_name}")
                else:
                    print(f"[创建Agent] ❌ 未找到可调用函数")
                    
            except Exception as e:
                import traceback
                print(f"[创建Agent] ❌ 创建Agent '{agent_name}' 失败: {e}")
                print(f"[创建Agent] 详细错误:")
                traceback.print_exc()
                continue
        
        # 创建工作流（如果提供）
        if workflow and created_agents:
            workflow_name = workflow.get('name', 'AI生成工作流')
            workflow_desc = workflow.get('description', '由AI助手创建')
            
            # 构建工作流定义（修复：sequence应该是字典列表，不是整数列表）
            workflow_def = {
                'agents': created_agents,
                'sequence': []  # 空sequence表示按agents顺序执行
            }
            
            try:
                with db.session_scope() as db_session:
                    workflow_id = db.create_workflow(
                        db_session,
                        name=workflow_name,
                        description=workflow_desc,
                        workflow_definition=workflow_def  # 修正参数名
                    )
                    created_workflow = {
                        'id': workflow_id,
                        'name': workflow_name
                    }
            except Exception as e:
                print(f"创建工作流失败: {e}")
        
        return jsonify({
            'success': True,
            'agents': created_agents,
            'workflow': created_workflow,
            'message': f'成功创建 {len(created_agents)} 个Agent' + (f'和工作流 {workflow_name}' if created_workflow else '')
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ============================================================================
# 工具系统 API
# ============================================================================

@api.route('/tools', methods=['GET'])
def list_tools():
    """列出所有可用工具"""
    try:
        from backend.tools import global_tool_registry
        
        tools = []
        for tool_name, tool in global_tool_registry.tools.items():
            tools.append({
                'name': tool.name,
                'description': tool.description,
                'parameters': tool.parameters
            })
        
        return jsonify({
            'success': True,
            'count': len(tools),
            'tools': tools
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@api.route('/tools/<string:tool_name>/execute', methods=['POST'])
def execute_tool(tool_name):
    """执行指定工具"""
    try:
        from backend.tools import global_tool_registry
        import traceback
        
        data = request.get_json() or {}
        arguments = data.get('arguments', {})
        
        print(f"\n[工具执行] 工具: {tool_name}")
        print(f"[工具执行] 参数: {arguments}")
        
        result = global_tool_registry.execute_tool(tool_name, arguments)
        
        print(f"[工具执行] 结果: {result.get('success', False)}")
        
        if result.get('success'):
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        import traceback
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500


# ============================================================================
# 批量操作 API
# ============================================================================

@api.route('/agents/batch-delete', methods=['POST'])
def batch_delete_agents():
    """批量删除Agents"""
    try:
        data = request.get_json()
        agent_names = data.get('agents', [])
        
        print(f"\n[批量删除Agent] 收到请求，要删除的Agent: {agent_names}")
        
        if not agent_names:
            return jsonify({'error': '没有选择要删除的Agent'}), 400
        
        deleted_count = 0
        failed = []
        
        for agent_name in agent_names:
            try:
                print(f"[批量删除Agent] 正在删除: {agent_name}")
                
                # 从registry中删除（如果存在）
                if agent_name in registry.agents:
                    del registry.agents[agent_name]
                    print(f"[批量删除Agent] 从registry删除: {agent_name}")
                
                # 从数据库中删除
                with db.session_scope() as db_session:
                    db.delete_agent(db_session, agent_name)
                    print(f"[批量删除Agent] 从数据库删除: {agent_name}")
                
                deleted_count += 1
                print(f"[批量删除Agent] ✅ 成功删除: {agent_name}")
                
            except Exception as e:
                print(f"[批量删除Agent] ❌ 删除失败: {agent_name}, 错误: {e}")
                import traceback
                traceback.print_exc()
                failed.append({'name': agent_name, 'error': str(e)})
        
        print(f"[批量删除Agent] 完成！成功: {deleted_count}, 失败: {len(failed)}")
        
        return jsonify({
            'success': True,
            'message': f'成功删除 {deleted_count} 个Agent',
            'deleted': deleted_count,
            'failed': failed
        }), 200
    except Exception as e:
        print(f"[批量删除Agent] 请求处理异常: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


@api.route('/workflows/batch-delete', methods=['POST'])
def batch_delete_workflows():
    """批量删除Workflows"""
    try:
        data = request.get_json()
        workflow_ids = data.get('workflows', [])
        
        if not workflow_ids:
            return jsonify({'error': '没有选择要删除的工作流'}), 400
        
        deleted_count = 0
        failed = []
        
        for workflow_id in workflow_ids:
            try:
                with db.session_scope() as db_session:
                    db.delete_workflow(db_session, workflow_id)
                    deleted_count += 1
            except Exception as e:
                failed.append({'id': workflow_id, 'error': str(e)})
        
        return jsonify({
            'success': True,
            'message': f'成功删除 {deleted_count} 个工作流',
            'deleted': deleted_count,
            'failed': failed
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

