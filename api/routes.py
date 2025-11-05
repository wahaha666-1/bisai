# ============================================================================
# API 层 - REST API 接口 (API Layer - REST Endpoints)
# ============================================================================

from flask import Blueprint, jsonify, request, session
from backend.database import Database
from backend.engine import WorkflowEngine
import secrets
from datetime import datetime

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

@api.route('/community/data', methods=['GET'])
def get_community_data():
    """
    获取社区广场数据（本地+外部）
    
    Query参数:
        include_external: bool - 是否包含外部数据，默认True
        use_mock: bool - 是否使用模拟外部数据，默认True
    """
    try:
        include_external = request.args.get('include_external', 'true').lower() == 'true'
        use_mock = request.args.get('use_mock', 'true').lower() == 'true'
        
        # 获取本地数据
        with db.session_scope() as db_session:
            local_agents = db.get_all_agents(db_session)
            local_workflows = db.get_all_workflows(db_session)
        
        result = {
            'local': {
                'agents': local_agents,
                'workflows': local_workflows
            },
            'external': {
                'agents': [],
                'workflows': []
            }
        }
        
        # 如果需要外部数据
        if include_external:
            try:
                from backend.external_community import external_fetcher
                external_data = external_fetcher.get_combined_data(use_mock=use_mock)
                result['external'] = external_data
            except Exception as e:
                print(f"[API] 获取外部数据失败: {e}")
                # 即使外部数据失败，也返回本地数据
        
        return jsonify(result), 200
        
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

@api.route('/workflows/<int:workflow_id>', methods=['GET', 'PUT', 'DELETE'])
def manage_workflow(workflow_id):
    """管理单个工作流：获取(GET)、更新(PUT)、删除(DELETE)"""
    from backend.models import Workflow, WorkflowExecution
    
    if request.method == 'GET':
        # 获取工作流详情
        try:
            with db.session_scope() as db_session:
                workflow = db_session.query(Workflow).filter_by(id=workflow_id).first()
                if not workflow:
                    return jsonify({'error': '工作流不存在'}), 404
                
                return jsonify({
                    'id': workflow.id,
                    'name': workflow.name,
                    'description': workflow.description,
                    'workflow_definition': workflow.workflow_definition,
                    'category': workflow.category,
                    'status': workflow.status,
                    'created_date': workflow.created_date.isoformat() if workflow.created_date else None
                }), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    elif request.method == 'PUT':
        # 更新工作流定义
        try:
            data = request.get_json()
            
            with db.session_scope() as db_session:
                workflow = db_session.query(Workflow).filter_by(id=workflow_id).first()
                if not workflow:
                    return jsonify({'error': '工作流不存在'}), 404
                
                # 更新字段
                if 'name' in data:
                    workflow.name = data['name']
                if 'description' in data:
                    workflow.description = data['description']
                if 'workflow_definition' in data:
                    import json
                    # 确保是JSON字符串
                    if isinstance(data['workflow_definition'], dict):
                        workflow.workflow_definition = json.dumps(data['workflow_definition'], ensure_ascii=False)
                    else:
                        workflow.workflow_definition = data['workflow_definition']
                if 'category' in data:
                    workflow.category = data['category']
                if 'status' in data:
                    workflow.status = data['status']
                
                print(f"[更新工作流] ✅ 工作流 #{workflow_id} 更新成功")
                return jsonify({
                    'message': '工作流更新成功',
                    'workflow_id': workflow_id
                }), 200
                
        except Exception as e:
            print(f"[更新工作流] ❌ 更新失败: {e}")
            import traceback
            traceback.print_exc()
            return jsonify({'error': str(e)}), 500
    
    elif request.method == 'DELETE':
        # 删除工作流
        try:
            with db.session_scope() as db_session:
                workflow = db_session.query(Workflow).filter_by(id=workflow_id).first()
                if workflow:
                    # 先删除所有关联的执行记录（解决外键约束问题）
                    executions = db_session.query(WorkflowExecution).filter_by(workflow_id=workflow_id).all()
                    for execution in executions:
                        db_session.delete(execution)
                    
                    print(f"[删除工作流] 已删除 {len(executions)} 条执行记录")
                    
                    # 然后删除工作流本身
                    db_session.delete(workflow)
                    
                    print(f"[删除工作流] 成功删除工作流 #{workflow_id}: {workflow.name}")
                    return jsonify({'message': f'工作流 #{workflow_id} 删除成功'}), 200
                else:
                    return jsonify({'error': '工作流不存在'}), 404
        except Exception as e:
            print(f"[删除工作流] ❌ 删除失败: {e}")
            import traceback
            traceback.print_exc()
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


@api.route('/ai/create-from-chat', methods=['POST'])
def create_from_chat():
    """🆕 从聊天界面一键创建Agent和工作流"""
    try:
        data = request.get_json()
        print(f"\n{'='*60}")
        print(f"[API] 从聊天创建Agent和工作流")
        print(f"{'='*60}")
        print(f"数据: {data}")
        
        created_agents = []
        created_workflow = None
        
        with db.session_scope() as session:
            # 1. 创建所有Agents
            if 'agents' in data and isinstance(data['agents'], list):
                for agent_data in data['agents']:
                    try:
                        print(f"\n[创建Agent] {agent_data['name']}")
                        
                        agent_id = db.add_or_update_agent(
                            session=session,
                            name=agent_data['name'],
                            code=agent_data['code'],
                            metadata={
                                'agent_type': agent_data.get('type', 'processor'),
                                'description': agent_data.get('description', ''),
                                'category': agent_data.get('category', '其他'),
                                'icon': agent_data.get('icon', '🤖')
                            },
                            dependencies=[],
                            triggers=[],
                            input_parameters={},
                            output_parameters={}
                        )
                        
                        # 注册到内存Registry
                        registry.register_agent(
                            name=agent_data['name'],
                            agent_type=agent_data.get('type', 'processor'),
                            description=agent_data.get('description', ''),
                            code=agent_data['code'],
                            category=agent_data.get('category', '其他'),
                            icon=agent_data.get('icon', '🤖')
                        )
                        
                        created_agents.append({
                            'id': agent_id,
                            'name': agent_data['name']
                        })
                        print(f"  ✅ 创建成功，ID: {agent_id}")
                        
                    except Exception as e:
                        print(f"  ❌ 创建失败: {e}")
                        raise Exception(f"创建Agent '{agent_data['name']}' 失败: {str(e)}")
            
            # 2. 创建工作流
            if 'workflow' in data:
                workflow_data = data['workflow']
                try:
                    print(f"\n[创建工作流] {workflow_data['name']}")
                    
                    # 兼容两种字段名：workflow_definition 或 definition
                    workflow_def = workflow_data.get('workflow_definition') or workflow_data.get('definition')
                    
                    # 如果没有提供workflow_definition，自动从agents生成简单的顺序执行流程
                    if not workflow_def and 'agents' in data:
                        print("  [自动生成] 从agents列表自动生成顺序执行工作流")
                        agent_names = []  # 只存储名称字符串
                        sequence = []
                        
                        for i, agent in enumerate(data['agents']):
                            agent_name = agent['name']
                            agent_names.append(agent_name)  # 只添加字符串名称
                            
                            # 生成sequence
                            if i == 0:
                                # 第一个agent从input获取数据
                                input_mapping = {'input_data': '$.input'}
                            else:
                                # 后续agent从前一个agent的输出获取数据
                                prev_agent_name = data['agents'][i-1]['name']
                                input_mapping = {'input_data': f'$.{prev_agent_name}'}
                            
                            sequence.append({
                                'agent': agent_name,
                                'input_mapping': input_mapping,
                                'output_key': agent_name
                            })
                        
                        # 🔥 修复：统一使用 input_data 参数
                        # 修改所有sequence的input_mapping，统一使用input_data参数名
                        for step in sequence:
                            if 'input_mapping' in step:
                                # 将所有映射的参数名改为 input_data
                                old_mapping = step['input_mapping']
                                step['input_mapping'] = {'input_data': list(old_mapping.values())[0] if old_mapping else '$.input'}
                        
                        workflow_def = {
                            'agents': agent_names,  # 使用字符串列表而不是字典列表
                            'sequence': sequence
                        }
                        print(f"  [自动生成] 生成了包含 {len(agent_names)} 个Agent的顺序执行流程")
                    
                    if not workflow_def:
                        raise ValueError("缺少workflow_definition字段，且无法自动生成")
                    
                    workflow_id = db.create_workflow(
                        session=session,
                        name=workflow_data['name'],
                        description=workflow_data.get('description', ''),
                        workflow_definition=workflow_def,
                        category=workflow_data.get('category', '其他'),
                        trigger_type='manual'
                    )
                    
                    created_workflow = {
                        'id': workflow_id,
                        'name': workflow_data['name']
                    }
                    print(f"  ✅ 创建成功，ID: {workflow_id}")
                    
                except Exception as e:
                    print(f"  ❌ 创建失败: {e}")
                    raise Exception(f"创建工作流失败: {str(e)}")
        
        print(f"\n{'='*60}")
        print(f"✅ 全部创建完成！")
        print(f"  Agents: {len(created_agents)}")
        print(f"  工作流: {'是' if created_workflow else '否'}")
        print(f"{'='*60}\n")
        
        return jsonify({
            'success': True,
            'message': f'成功创建 {len(created_agents)} 个Agent' + 
                      (f'和工作流 {created_workflow["name"]}' if created_workflow else ''),
            'agents': created_agents,
            'workflow': created_workflow
        })
        
    except Exception as e:
        print(f"\n[API] ❌ 创建失败: {e}")
        import traceback
        traceback.print_exc()
        
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


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

**⚠️ 重要：统一参数命名规范**
- 第一个Agent（接收用户输入）：参数名必须是 `input_data`
- 后续Agent（接收前一个Agent输出）：参数名必须是 `input_data`
- 返回格式：必须包含 `{'success': True/False, 'result': {...}}`

```CREATE_AGENTS_AND_WORKFLOW
{
  "agents": [
    {
      "name": "agent名称",
      "type": "processor",
      "description": "Agent描述",
      "code": "def agent_function(input_data: dict) -> dict:\\n    \"\"\"函数说明\"\"\"\\n    try:\\n        # 从input_data中提取所需数据\\n        value = input_data.get('key', 'default')\\n        result = 处理逻辑\\n        return {'success': True, 'result': result}\\n    except Exception as e:\\n        return {'success': False, 'error': str(e)}"
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

**重要：生成简洁高效的代码！避免过长的模拟数据，每个Agent代码控制在30-50行内。**

1. **函数签名（必须遵守）**
- 所有Agent统一使用 input_data 作为参数名
- 函数签名示例：def agent_name(input_data: dict) -> dict
- ✅ 正确：def data_crawler(input_data: dict) -> dict
- ❌ 错误：def data_crawler(keyword: str) -> dict
- 提取数据：keyword = input_data.get('keyword') or input_data

2. **文档字符串**（简洁版）
```python
\"\"\"Agent功能简述
Args:
    param1: 参数说明
Returns:
    dict: 包含success和result的字典
\"\"\"
```

3. **错误处理**
```python
try:
    # 核心业务逻辑（简洁实现）
    # 模拟数据：使用random生成或简单字典，不要超过5-10行
    result = process_data()
    return {'success': True, 'result': result}
except Exception as e:
    return {'success': False, 'error': str(e)}
```

4. **模拟数据规范**
```python
# ✅ 好的做法：简洁的模拟数据
cities_data = {'北京': {'temp': 25, 'weather': '晴'}, '上海': {'temp': 28, 'weather': '多云'}}

# ❌ 避免：超长的模拟数据库
# 不要写几十行的数据字典
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
        from backend.models import Workflow, WorkflowExecution
        data = request.get_json()
        workflow_ids = data.get('workflows', [])
        
        if not workflow_ids:
            return jsonify({'error': '没有选择要删除的工作流'}), 400
        
        print(f"[批量删除工作流] 收到删除请求，工作流IDs: {workflow_ids}")
        
        deleted_count = 0
        failed = []
        
        for workflow_id in workflow_ids:
            try:
                with db.session_scope() as db_session:
                    workflow = db_session.query(Workflow).filter_by(id=workflow_id).first()
                    if workflow:
                        # 🔥 先删除执行记录
                        executions = db_session.query(WorkflowExecution).filter_by(workflow_id=workflow_id).all()
                        for execution in executions:
                            db_session.delete(execution)
                        
                        # 再删除工作流
                        db_session.delete(workflow)
                        deleted_count += 1
                        print(f"[批量删除工作流] ✅ 成功删除 #{workflow_id}")
                    else:
                        failed.append({'id': workflow_id, 'error': '工作流不存在'})
            except Exception as e:
                print(f"[批量删除工作流] ❌ 删除 #{workflow_id} 失败: {e}")
                failed.append({'id': workflow_id, 'error': str(e)})
        
        return jsonify({
            'success': True,
            'message': f'成功删除 {deleted_count} 个工作流',
            'deleted': deleted_count,
            'failed': failed
        }), 200
    except Exception as e:
        print(f"[批量删除工作流] ❌ 批量操作失败: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500

# ============================================================================
# 工作流API发布接口
# ============================================================================

@api.route('/workflows/<int:workflow_id>/publish', methods=['POST'])
def publish_workflow_api(workflow_id):
    """为工作流生成API Key"""
    try:
        from backend.models import WorkflowAPIKey, Workflow
        
        data = request.get_json() or {}
        key_name = data.get('name', 'Default API Key')
        
        # 生成唯一密钥
        api_key = f"sk-{secrets.token_urlsafe(32)}"
        
        # 🔧 修复：在session内获取所有需要的数据
        with db.session_scope() as db_session:
            # 验证工作流存在
            workflow = db_session.query(Workflow).filter_by(id=workflow_id).first()
            if not workflow:
                return jsonify({'error': '工作流不存在'}), 404
            
            # 在session内获取workflow name
            workflow_name = workflow.name
            
            # 创建API Key记录
            key_record = WorkflowAPIKey(
                workflow_id=workflow_id,
                api_key=api_key,
                name=key_name,
                is_active=True,
                created_date=datetime.utcnow()
            )
            db_session.add(key_record)
        
        print(f"[API发布] 为工作流 #{workflow_id} 生成API Key: {api_key[:10]}...")
        
        return jsonify({
            'success': True,
            'api_key': api_key,
            'endpoint': '/api/public/execute',
            'workflow_id': workflow_id,
            'workflow_name': workflow_name,
            'examples': {
                'curl': f'''curl -X POST {request.host_url}api/public/execute \\
  -H "X-API-Key: {api_key}" \\
  -H "Content-Type: application/json" \\
  -d '{{"input_data": {{}}}}\'''',
                'python': f'''import requests

response = requests.post(
    '{request.host_url}api/public/execute',
    headers={{
        'X-API-Key': '{api_key}',
        'Content-Type': 'application/json'
    }},
    json={{'input_data': {{}}}}
)

result = response.json()
print(result['output'])''',
                'javascript': f'''fetch('{request.host_url}api/public/execute', {{
    method: 'POST',
    headers: {{
        'X-API-Key': '{api_key}',
        'Content-Type': 'application/json'
    }},
    body: JSON.stringify({{input_data: {{}}}})
}})
.then(res => res.json())
.then(data => console.log(data.output));'''
            }
        }), 201
    
    except Exception as e:
        print(f"[API发布] ❌ 发布失败: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@api.route('/workflows/<int:workflow_id>/api-keys', methods=['GET'])
def get_workflow_api_keys(workflow_id):
    """获取工作流的所有API Keys"""
    try:
        from backend.models import WorkflowAPIKey
        
        with db.session_scope() as db_session:
            keys = db_session.query(WorkflowAPIKey).filter_by(workflow_id=workflow_id).all()
            
            return jsonify({
                'success': True,
                'keys': [{
                    'id': k.id,
                    'name': k.name,
                    'api_key': k.api_key,
                    'is_active': k.is_active,
                    'calls_count': k.calls_count,
                    'last_used': k.last_used.isoformat() if k.last_used else None,
                    'created_date': k.created_date.isoformat() if k.created_date else None
                } for k in keys]
            }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@api.route('/workflows/api-keys/<int:key_id>', methods=['DELETE'])
def delete_api_key(key_id):
    """删除API Key"""
    try:
        from backend.models import WorkflowAPIKey
        
        with db.session_scope() as db_session:
            key = db_session.query(WorkflowAPIKey).filter_by(id=key_id).first()
            if not key:
                return jsonify({'error': 'API Key不存在'}), 404
            
            db_session.delete(key)
        
        return jsonify({'success': True, 'message': 'API Key已删除'}), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@api.route('/public/execute', methods=['POST'])
def public_execute_workflow():
    """🔌 公开API接口 - 通过API Key执行工作流"""
    try:
        from backend.models import WorkflowAPIKey
        
        # 1. 验证API Key
        api_key = request.headers.get('X-API-Key')
        if not api_key:
            return jsonify({
                'success': False,
                'error': 'Missing API Key',
                'message': '请在请求头中提供 X-API-Key'
            }), 401
        
        with db.session_scope() as db_session:
            key_record = db_session.query(WorkflowAPIKey).filter_by(
                api_key=api_key,
                is_active=True
            ).first()
            
            if not key_record:
                return jsonify({
                    'success': False,
                    'error': 'Invalid API Key',
                    'message': 'API Key无效或已被禁用'
                }), 401
            
            workflow_id = key_record.workflow_id
            
            # 更新调用次数和最后使用时间
            key_record.calls_count += 1
            key_record.last_used = datetime.utcnow()
            db_session.commit()
        
        # 2. 获取输入数据
        input_data = request.get_json() or {}
        
        print(f"\n{'='*60}")
        print(f"[公开API] 收到请求")
        print(f"{'='*60}")
        print(f"API Key: {api_key[:10]}...")
        print(f"Workflow ID: {workflow_id}")
        print(f"Input Data: {input_data}")
        
        # 3. 执行工作流
        start_time = datetime.utcnow()
        result = engine.execute_workflow(workflow_id, input_data)
        execution_time = (datetime.utcnow() - start_time).total_seconds()
        
        # 4. 返回结果
        return jsonify({
            'success': result.get('success', False),
            'execution_id': result.get('execution_id'),
            'output': result.get('output'),
            'execution_time': execution_time,
            'error': result.get('error'),
            'message': '执行成功' if result.get('success') else '执行失败'
        }), 200 if result.get('success') else 500
    
    except Exception as e:
        print(f"[公开API] ❌ 执行失败: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e),
            'message': '服务器错误'
        }), 500

# ============================================================================
# Agent升级 API
# ============================================================================

@api.route('/agents/upgrade', methods=['POST'])
def upgrade_agents_to_ai():
    """🚀 真正通用的AI升级系统 - 适用于所有Agent"""
    try:
        data = request.get_json() or {}
        agent_names = data.get('agents', [])
        
        if not agent_names:
            return jsonify({'success': False, 'error': '未指定要升级的Agent'}), 400
        
        print(f"\n[🚀 通用AI升级] 收到升级请求，Agent列表: {agent_names}")
        
        # 获取LLM服务
        from backend.llm_service import get_llm_service
        llm = get_llm_service()
        
        if not llm.is_configured():
            return jsonify({'success': False, 'error': 'LLM服务未配置，无法进行AI升级'}), 400
        
        def generate_universal_ai_code(agent_name: str, agent_description: str, input_params: dict) -> str:
            """🎯 通用AI代码生成器 - 适用于所有Agent"""
            
            # 通用模板 - 适配所有Agent
            template = f'''def {agent_name}(input_data: dict) -> dict:
    """{agent_description or '智能处理任务'}"""
    try:
        from backend.llm_service import get_llm_service
        import json
        import re
        
        # 🔍 智能提取用户输入
        user_input = None
        if isinstance(input_data, dict):
            # 优先级：input_data > 关键词 > topic > 第一个非系统字段
            user_input = (
                input_data.get('input_data') or 
                input_data.get('关键词') or 
                input_data.get('topic') or
                input_data.get('keyword') or
                input_data.get('query')
            )
            
            # 如果是嵌套的result结构
            if 'result' in input_data and isinstance(input_data['result'], dict):
                result_data = input_data['result']
                user_input = user_input or result_data
            
            # 如果还没找到，取第一个有值的字段
            if not user_input:
                for key, value in input_data.items():
                    if key not in ['success', 'error', 'status'] and value:
                        user_input = value
                        break
        
        if not user_input:
            return {{'success': False, 'error': '未提供有效的输入数据'}}
        
        # 🤖 调用LLM处理
        llm = get_llm_service()
        
        if llm.is_configured():
            # 构建提示词
            if isinstance(user_input, dict):
                input_str = json.dumps(user_input, ensure_ascii=False, indent=2)
            else:
                input_str = str(user_input)
            
            prompt = f"""任务：{agent_description or '处理用户请求'}

用户输入：
{{input_str}}

要求：
1. 根据用户输入和任务描述，生成相关的处理结果
2. 输出必须与用户输入紧密相关，不要生成无关内容
3. 以JSON格式返回结果"""
            
            response = llm.chat([
                {{'role': 'system', 'content': f'你是一个专业的AI助手。任务：{agent_description}'}},
                {{'role': 'user', 'content': prompt}}
            ], temperature=0.7, max_tokens=3000)
            
            if response['success']:
                content = response['content'].strip()
                
                # 尝试提取JSON
                json_match = re.search(r'\\{{[\\s\\S]*?\\}}', content)
                if json_match:
                    try:
                        result_data = json.loads(json_match.group())
                        return {{'success': True, 'result': result_data}}
                    except:
                        pass
                
                # 如果不是JSON，直接返回文本
                return {{
                    'success': True,
                    'result': {{
                        'output': content,
                        'input': user_input
                    }}
                }}
        
        return {{'success': False, 'error': 'LLM服务未配置或调用失败'}}
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {{'success': False, 'error': f'执行失败: {{str(e)}}'}}'}}'''
            
            return template
        
        # 执行升级
        upgraded = []
        failed = []
        
        from backend.models import AIAgent, AgentVersion
        
        with db.session_scope() as session:
            for agent_name in agent_names:
                try:
                    # 1. 获取Agent信息
                    agent = session.query(AIAgent).filter_by(name=agent_name).first()
                    
                    if not agent:
                        failed.append({'name': agent_name, 'error': 'Agent不存在'})
                        continue
                    
                    # 2. 获取活跃版本
                    active_version = session.query(AgentVersion).filter_by(
                        agent_id=agent.id, 
                        is_active=True
                    ).first()
                    
                    if not active_version:
                        failed.append({'name': agent_name, 'error': '未找到活跃版本'})
                        continue
                    
                    # 3. 生成通用AI代码
                    print(f"[🚀 通用AI升级] 正在为 {agent_name} 生成AI代码...")
                    
                    ai_code = generate_universal_ai_code(
                        agent_name=agent_name,
                        agent_description=agent.description or '智能处理任务',
                        input_params=active_version.input_parameters or {}
                    )
                    
                    # 4. 更新代码
                    active_version.code = ai_code
                    
                    # 5. 标记为AI驱动
                    metadata = active_version.agent_metadata or {}
                    metadata['ai_powered'] = True
                    metadata['upgraded_at'] = datetime.now().isoformat()
                    active_version.agent_metadata = metadata
                    
                    upgraded.append(agent_name)
                    print(f"[🚀 通用AI升级] ✅ {agent_name} 升级成功并标记为AI驱动")
                        
                except Exception as e:
                    print(f"[🚀 通用AI升级] ❌ {agent_name} 升级失败: {e}")
                    import traceback
                    traceback.print_exc()
                    failed.append({'name': agent_name, 'error': str(e)})
        
        print(f"\n[Agent升级] 完成！成功: {len(upgraded)}, 失败: {len(failed)}")
        
        return jsonify({
            'success': True,
            'upgraded': upgraded,
            'failed': failed,
            'message': f'成功升级 {len(upgraded)} 个Agent为AI驱动版本'
        }), 200
        
    except Exception as e:
        print(f"[Agent升级] ❌ 处理失败: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500

# ============================================================================
# Agent状态检查 API
# ============================================================================

@api.route('/agents/<agent_name>/ai-status', methods=['GET'])
def check_agent_ai_status(agent_name):
    """检查Agent是否为AI驱动版本"""
    try:
        from backend.models import AIAgent, AgentVersion
        
        with db.session_scope() as session:
            agent = session.query(AIAgent).filter_by(name=agent_name).first()
            
            if not agent:
                return jsonify({'success': False, 'error': 'Agent不存在'}), 404
            
            active_version = session.query(AgentVersion).filter_by(
                agent_id=agent.id,
                is_active=True
            ).first()
            
            if not active_version:
                return jsonify({'success': False, 'error': '未找到活跃版本'}), 404
            
            metadata = active_version.agent_metadata or {}
            is_ai_powered = metadata.get('ai_powered', False)
            
            return jsonify({
                'success': True,
                'ai_powered': is_ai_powered,
                'agent_name': agent_name,
                'upgraded_at': metadata.get('upgraded_at')
            }), 200
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# 旧代码删除标记 - 以下是之前的预设代码部分（已删除）
# ============================================================================
