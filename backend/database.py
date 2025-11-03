# ============================================================================
# 后端层 - 数据访问层 (Backend - Database)
# ============================================================================

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.exc import SQLAlchemyError
from contextlib import contextmanager
from backend.models import Base, AIAgent, AgentVersion, Workflow, WorkflowExecution, AgentTool, Import, Log, SecretKey, User, fernet
from datetime import datetime
import json

class Database:
    """数据库操作类 - DAO层"""
    
    def __init__(self, db_path='sqlite:///agentflow.db'):
        self.engine = create_engine(db_path, echo=False)
        Base.metadata.create_all(self.engine)
        self.Session = scoped_session(sessionmaker(bind=self.engine))
        print(f"✓ 数据库初始化成功: {db_path}")
    
    @contextmanager
    def session_scope(self):
        """提供事务作用域的上下文管理器"""
        session = self.Session()
        try:
            yield session
            session.commit()
        except SQLAlchemyError as e:
            session.rollback()
            raise e
        finally:
            self.Session.remove()
    
    # ========================================================================
    # Agent 相关操作
    # ========================================================================
    
    def add_or_update_agent(self, session, name, code, metadata, dependencies, triggers, 
                           input_parameters, output_parameters, imports=None):
        """添加或更新 Agent"""
        agent = session.query(AIAgent).filter_by(name=name).first()
        
        if not agent:
            # 创建新 Agent
            agent = AIAgent(
                name=name,
                agent_type=metadata.get('agent_type', 'other'),
                llm_model=metadata.get('llm_model'),
                prompt_template=metadata.get('prompt_template'),
                category=metadata.get('category', '其他'),
                icon=metadata.get('icon', 'default'),
                description=metadata.get('description', ''),
                author=metadata.get('author', 'system')
            )
            session.add(agent)
            session.flush()
        
        # 处理导入包
        import_objects = []
        if imports:
            for import_name in imports:
                imp = session.query(Import).filter_by(name=import_name).first()
                if not imp:
                    imp = Import(name=import_name, source='external')
                    session.add(imp)
                    session.flush()
                import_objects.append(imp)
        
        # 创建新版本
        version = AgentVersion(
            agent=agent,
            version=len(agent.versions) + 1,
            code=code,
            agent_metadata=metadata or {},
            is_active=True,
            input_parameters=input_parameters or [],
            output_parameters=output_parameters or [],
            imports=import_objects,
            triggers=triggers or []
        )
        session.add(version)
        
        # 处理依赖
        if dependencies:
            for dep in dependencies:
                dep_agent = session.query(AIAgent).filter_by(name=dep).first()
                if dep_agent:
                    version.dependencies.append(dep_agent)
        
        # 停用旧版本
        for v in agent.versions:
            if v != version:
                v.is_active = False
        
        return agent.id
    
    def get_agent(self, session, name):
        """获取 Agent"""
        agent = session.query(AIAgent).filter_by(name=name).first()
        if not agent:
            return None
        
        active_version = session.query(AgentVersion)\
            .filter_by(agent_id=agent.id, is_active=True)\
            .first()
        
        if not active_version:
            return None
        
        return {
            'id': agent.id,
            'name': agent.name,
            'agent_type': agent.agent_type,
            'llm_model': agent.llm_model,
            'version': active_version.version,
            'code': active_version.code,
            'metadata': active_version.agent_metadata,
            'input_parameters': active_version.input_parameters,
            'output_parameters': active_version.output_parameters,
            'dependencies': [dep.name for dep in active_version.dependencies],
            'imports': [imp.name for imp in active_version.imports],
            'prompt_template': agent.prompt_template,
            'category': agent.category,
            'icon': agent.icon,
            'description': agent.description
        }
    
    def get_all_agents(self, session):
        """获取所有 Agent"""
        agents = session.query(AIAgent).all()
        result = []
        
        for agent in agents:
            active_version = session.query(AgentVersion)\
                .filter_by(agent_id=agent.id, is_active=True)\
                .first()
            
            if active_version:
                result.append({
                    'id': agent.id,
                    'name': agent.name,
                    'agent_type': agent.agent_type,
                    'category': agent.category,
                    'icon': agent.icon,
                    'description': agent.description,
                    'version': active_version.version,
                    'total_executions': agent.total_executions,
                    'success_rate': agent.success_rate,
                    'avg_execution_time': agent.avg_execution_time
                })
        
        return result
    
    def delete_agent(self, session, agent_name):
        """删除Agent及其所有版本"""
        agent = session.query(AIAgent).filter_by(name=agent_name).first()
        if agent:
            # 删除所有版本
            session.query(AgentVersion).filter_by(agent_id=agent.id).delete()
            # 删除Agent
            session.delete(agent)
            session.flush()
            return True
        return False
    
    # ========================================================================
    # 工作流相关操作
    # ========================================================================
    
    def create_workflow(self, session, name, description, workflow_definition, 
                       category='其他', trigger_type='manual'):
        """创建工作流"""
        workflow = Workflow(
            name=name,
            description=description,
            workflow_definition=workflow_definition if isinstance(workflow_definition, str) else json.dumps(workflow_definition),
            category=category,
            trigger_type=trigger_type,
            status='draft',
            created_by='system'
        )
        session.add(workflow)
        session.flush()
        return workflow.id
    
    def get_workflow(self, session, workflow_id):
        """获取工作流"""
        workflow = session.query(Workflow).filter_by(id=workflow_id).first()
        if not workflow:
            return None
        
        return {
            'id': workflow.id,
            'name': workflow.name,
            'description': workflow.description,
            'workflow_definition': workflow.workflow_definition,
            'category': workflow.category,
            'status': workflow.status,
            'trigger_type': workflow.trigger_type,
            'total_executions': workflow.total_executions,
            'success_count': workflow.success_count,
            'fail_count': workflow.fail_count,
            'avg_execution_time': workflow.avg_execution_time,
            'created_date': workflow.created_date,
            'last_executed': workflow.last_executed
        }
    
    def get_all_workflows(self, session):
        """获取所有工作流"""
        workflows = session.query(Workflow).all()
        return [{
            'id': w.id,
            'name': w.name,
            'description': w.description,
            'category': w.category,
            'status': w.status,
            'total_executions': w.total_executions,
            'success_rate': (w.success_count / w.total_executions * 100) if w.total_executions > 0 else 0,
            'created_date': w.created_date.isoformat() if w.created_date else None
        } for w in workflows]
    
    def create_workflow_execution(self, session, workflow_id, input_data, status, started_at):
        """创建工作流执行记录"""
        execution = WorkflowExecution(
            workflow_id=workflow_id,
            input_data=input_data,
            status=status,
            started_at=started_at,
            triggered_by='manual'
        )
        session.add(execution)
        session.flush()
        return execution.id
    
    def update_workflow_execution(self, session, execution_id, **kwargs):
        """更新工作流执行记录"""
        execution = session.query(WorkflowExecution).filter_by(id=execution_id).first()
        if execution:
            # 保存旧状态
            old_status = execution.status
            
            # 更新执行记录
            for key, value in kwargs.items():
                if hasattr(execution, key):
                    setattr(execution, key, value)
            
            # 更新工作流统计数据（只在状态第一次变为completed或failed时更新，避免重复计数）
            new_status = kwargs.get('status')
            workflow = session.query(Workflow).filter_by(id=execution.workflow_id).first()
            
            # 关键：只在状态从running变为completed或failed时才更新统计
            if (workflow and 
                new_status in ['completed', 'failed'] and 
                old_status not in ['completed', 'failed']):
                
                workflow.total_executions += 1
                workflow.last_executed = kwargs.get('completed_at', datetime.utcnow())
                
                if new_status == 'completed':
                    workflow.success_count += 1
                elif new_status == 'failed':
                    workflow.fail_count += 1
                
                # 更新平均执行时间
                exec_time = kwargs.get('execution_time')
                if exec_time:
                    if workflow.avg_execution_time == 0:
                        workflow.avg_execution_time = exec_time
                    else:
                        workflow.avg_execution_time = (
                            (workflow.avg_execution_time * (workflow.total_executions - 1) + exec_time) 
                            / workflow.total_executions
                        )
    
    def get_workflow_execution(self, session, execution_id):
        """获取工作流执行记录"""
        execution = session.query(WorkflowExecution).filter_by(id=execution_id).first()
        if not execution:
            return None
        
        return {
            'id': execution.id,
            'workflow_id': execution.workflow_id,
            'status': execution.status,
            'input_data': execution.input_data,
            'output_data': execution.output_data,
            'started_at': execution.started_at.isoformat() if execution.started_at else None,
            'completed_at': execution.completed_at.isoformat() if execution.completed_at else None,
            'execution_time': execution.execution_time,
            'error_message': execution.error_message,
            'execution_graph': execution.execution_graph,
            'tokens_used': execution.tokens_used,
            'cost': execution.cost
        }
    
    # ========================================================================
    # 日志相关操作
    # ========================================================================
    
    def add_log(self, session, agent_name, message, timestamp, params, output, 
                time_spent, parent_log_id=None, triggered_by_log_id=None, log_type='info'):
        """添加日志"""
        if isinstance(timestamp, str):
            timestamp = datetime.fromisoformat(timestamp)
        
        new_log = Log(
            agent_name=agent_name,
            message=message,
            timestamp=timestamp,
            params=params,
            output=output,
            time_spent=time_spent,
            parent_log_id=parent_log_id,
            triggered_by_log_id=triggered_by_log_id,
            log_type=log_type
        )
        session.add(new_log)
        session.flush()
        return new_log.id
    
    def get_logs(self, session, agent_name=None, limit=100):
        """获取日志"""
        query = session.query(Log)
        
        if agent_name:
            query = query.filter(Log.agent_name == agent_name)
        
        logs = query.order_by(Log.timestamp.desc()).limit(limit).all()
        
        return [{
            'id': log.id,
            'agent_name': log.agent_name,
            'message': log.message,
            'timestamp': log.timestamp.isoformat() if log.timestamp else None,
            'params': log.params,
            'output': log.output,
            'time_spent': log.time_spent,
            'log_type': log.log_type
        } for log in logs]
    
    # ========================================================================
    # 密钥相关操作
    # ========================================================================
    
    def add_secret_key(self, session, key_name, key_value):
        """添加密钥"""
        key = session.query(SecretKey).filter_by(name=key_name).first()
        
        if key:
            key.value = key_value
        else:
            key = SecretKey(name=key_name)
            key.value = key_value
            session.add(key)
    
    def get_secret_key(self, session, key_name):
        """获取密钥"""
        key = session.query(SecretKey).filter_by(name=key_name).first()
        return key.value if key else None
    
    def get_all_secret_keys(self, session):
        """获取所有密钥名称"""
        keys = session.query(SecretKey).all()
        return [{'name': key.name} for key in keys]
    
    # ========================================================================
    # 用户相关操作
    # ========================================================================
    
    def create_user(self, session, username, email, password, role='user'):
        """创建用户"""
        user = User(username=username, email=email, role=role)
        user.password = password  # 自动加密
        session.add(user)
        session.flush()
        return user.id
    
    def get_user_by_username(self, session, username):
        """通过用户名获取用户"""
        return session.query(User).filter_by(username=username).first()
    
    def get_user_by_id(self, session, user_id):
        """通过ID获取用户"""
        return session.query(User).filter_by(id=user_id).first()
    
    def update_last_login(self, session, user_id):
        """更新最后登录时间"""
        user = session.query(User).filter_by(id=user_id).first()
        if user:
            user.last_login = datetime.utcnow()
    
    def get_all_users(self, session):
        """获取所有用户"""
        users = session.query(User).all()
        return [{
            'id': u.id,
            'username': u.username,
            'email': u.email,
            'role': u.role,
            'is_active': u.is_active,
            'created_date': u.created_date.isoformat() if u.created_date else None,
            'last_login': u.last_login.isoformat() if u.last_login else None
        } for u in users]
    
    # ========================================================================
    # AI对话相关操作
    # ========================================================================
    
    def create_chat_session(self, session, user_id=None, title='新对话'):
        """创建对话会话"""
        from .models import ChatSession
        chat_session = ChatSession(user_id=user_id, title=title)
        session.add(chat_session)
        session.flush()
        return chat_session.id
    
    def get_chat_sessions(self, session, user_id=None, limit=50):
        """获取对话会话列表"""
        from .models import ChatSession
        query = session.query(ChatSession)
        if user_id:
            query = query.filter_by(user_id=user_id)
        sessions = query.order_by(ChatSession.updated_at.desc()).limit(limit).all()
        return [{
            'id': s.id,
            'title': s.title,
            'created_at': s.created_at.isoformat() if s.created_at else None,
            'updated_at': s.updated_at.isoformat() if s.updated_at else None
        } for s in sessions]
    
    def add_chat_message(self, session, session_id, role, content, tokens=0):
        """添加对话消息"""
        from .models import ChatMessage, ChatSession
        message = ChatMessage(
            session_id=session_id,
            role=role,
            content=content,
            tokens=tokens
        )
        session.add(message)
        
        # 更新会话更新时间
        chat_session = session.query(ChatSession).get(session_id)
        if chat_session:
            from datetime import datetime
            chat_session.updated_at = datetime.utcnow()
        
        session.flush()
        return message.id
    
    def get_chat_messages(self, session, session_id, limit=100):
        """获取对话消息历史"""
        from .models import ChatMessage
        messages = session.query(ChatMessage)\
            .filter_by(session_id=session_id)\
            .order_by(ChatMessage.created_at)\
            .limit(limit)\
            .all()
        return [{
            'id': m.id,
            'role': m.role,
            'content': m.content,
            'tokens': m.tokens,
            'created_at': m.created_at.isoformat() if m.created_at else None
        } for m in messages]
    
    def delete_chat_session(self, session, session_id):
        """删除对话会话"""
        from .models import ChatSession, ChatMessage
        # 先删除消息
        session.query(ChatMessage).filter_by(session_id=session_id).delete()
        # 再删除会话
        session.query(ChatSession).filter_by(id=session_id).delete()
    
    # ========================================================================
    # 密钥管理操作
    # ========================================================================
    
    def set_secret_key(self, session, key_name, key_value):
        """
        设置密钥
        
        Args:
            session: 数据库会话
            key_name: 密钥名称
            key_value: 密钥值（明文，会自动加密）
        """
        from .models import SecretKey
        
        # 查找是否已存在（注意模型中使用的是name字段）
        secret = session.query(SecretKey).filter_by(name=key_name).first()
        
        if secret:
            # 更新现有密钥（注意模型中使用的是value属性）
            secret.value = key_value
        else:
            # 创建新密钥
            secret = SecretKey(name=key_name)
            secret.value = key_value
            session.add(secret)
        
        session.flush()
    
    def get_secret_key(self, session, key_name):
        """
        获取密钥
        
        Args:
            session: 数据库会话
            key_name: 密钥名称
            
        Returns:
            str: 密钥值（明文），如果不存在返回None
        """
        from .models import SecretKey
        
        secret = session.query(SecretKey).filter_by(name=key_name).first()
        if secret:
            return secret.value
        return None

