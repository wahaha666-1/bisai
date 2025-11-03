# ============================================================================
# 后端层 - 数据模型 (Backend - Models)
# ============================================================================

from sqlalchemy import Column, Integer, String, DateTime, JSON, ForeignKey, Boolean, Table, Float, LargeBinary, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from cryptography.fernet import Fernet
from cryptography.fernet import InvalidToken
from sqlalchemy.ext.hybrid import hybrid_property
import os
import json
from datetime import datetime

Base = declarative_base()

# 加密密钥管理
KEY_FILE = 'encryption_key.json'

def get_or_create_key():
    if os.path.exists(KEY_FILE):
        with open(KEY_FILE, 'r') as f:
            return json.load(f)['key']
    else:
        key = Fernet.generate_key().decode()
        with open(KEY_FILE, 'w') as f:
            json.dump({'key': key}, f)
        return key

ENCRYPTION_KEY = get_or_create_key()
fernet = Fernet(ENCRYPTION_KEY.encode())

# 关联表
agent_dependency = Table('agent_dependency', Base.metadata,
    Column('agent_version_id', Integer, ForeignKey('agent_versions.id')),
    Column('dependency_id', Integer, ForeignKey('ai_agents.id'))
)

agent_version_imports = Table('agent_version_imports', Base.metadata,
    Column('agent_version_id', Integer, ForeignKey('agent_versions.id')),
    Column('import_id', Integer, ForeignKey('imports.id'))
)

agent_version_tools = Table('agent_version_tools', Base.metadata,
    Column('agent_version_id', Integer, ForeignKey('agent_versions.id')),
    Column('tool_id', Integer, ForeignKey('agent_tools.id'))
)

# AI Agent 表
class AIAgent(Base):
    __tablename__ = 'ai_agents'
    
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    agent_type = Column(String, nullable=False)
    llm_model = Column(String, default='gpt-4')
    prompt_template = Column(Text)
    category = Column(String, default='其他')
    icon = Column(String)
    description = Column(Text)
    is_public = Column(Boolean, default=False)
    author = Column(String)
    tags = Column(JSON)
    input_schema = Column(JSON)
    output_schema = Column(JSON)
    avg_execution_time = Column(Float, default=0.0)
    success_rate = Column(Float, default=0.0)
    total_executions = Column(Integer, default=0)
    rating = Column(Float, default=0.0)
    created_date = Column(DateTime, default=datetime.utcnow)
    updated_date = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    versions = relationship("AgentVersion", back_populates="agent", cascade="all, delete-orphan")

# Agent 版本表
class AgentVersion(Base):
    __tablename__ = 'agent_versions'
    
    id = Column(Integer, primary_key=True)
    agent_id = Column(Integer, ForeignKey('ai_agents.id'))
    version = Column(Integer)
    code = Column(Text)
    agent_metadata = Column(JSON)
    is_active = Column(Boolean, default=False)
    created_date = Column(DateTime, default=datetime.utcnow)
    input_parameters = Column(JSON)
    output_parameters = Column(JSON)
    triggers = Column(JSON, nullable=True)
    performance_score = Column(Float, default=0.0)
    avg_execution_time = Column(Float, default=0.0)
    cost_per_run = Column(Float, default=0.0)
    timeout = Column(Integer, default=300)
    retry_times = Column(Integer, default=0)
    max_concurrent = Column(Integer, default=1)
    
    agent = relationship("AIAgent", back_populates="versions")
    dependencies = relationship('AIAgent', secondary=agent_dependency,
                              primaryjoin=(agent_dependency.c.agent_version_id == id),
                              secondaryjoin=(agent_dependency.c.dependency_id == AIAgent.id))
    imports = relationship('Import', secondary=agent_version_imports, back_populates='agent_versions')
    tools = relationship('AgentTool', secondary=agent_version_tools, back_populates='agent_versions')

# 工作流表
class Workflow(Base):
    __tablename__ = 'workflows'
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    category = Column(String, default='其他')
    icon = Column(String)
    workflow_definition = Column(JSON, nullable=False)
    trigger_type = Column(String, default='manual')
    trigger_config = Column(JSON)
    status = Column(String, default='draft')
    is_template = Column(Boolean, default=False)
    is_public = Column(Boolean, default=False)
    total_executions = Column(Integer, default=0)
    success_count = Column(Integer, default=0)
    fail_count = Column(Integer, default=0)
    avg_execution_time = Column(Float, default=0.0)
    created_by = Column(String)
    shared_with = Column(JSON)
    created_date = Column(DateTime, default=datetime.utcnow)
    updated_date = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_executed = Column(DateTime)
    
    executions = relationship('WorkflowExecution', back_populates='workflow', cascade="all, delete-orphan")

# 工作流执行记录表
class WorkflowExecution(Base):
    __tablename__ = 'workflow_executions'
    
    id = Column(Integer, primary_key=True)
    workflow_id = Column(Integer, ForeignKey('workflows.id'))
    status = Column(String, default='pending')
    input_data = Column(JSON)
    output_data = Column(JSON)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    execution_time = Column(Float)
    error_message = Column(Text)
    execution_graph = Column(JSON)
    tokens_used = Column(Integer, default=0)
    cost = Column(Float, default=0.0)
    triggered_by = Column(String)
    triggered_by_user = Column(String)
    
    workflow = relationship('Workflow', back_populates='executions')

# Agent 工具表
class AgentTool(Base):
    __tablename__ = 'agent_tools'
    
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(Text)
    tool_type = Column(String, default='function')
    code = Column(Text)
    config = Column(JSON)
    input_schema = Column(JSON)
    output_schema = Column(JSON)
    category = Column(String)
    requires_auth = Column(Boolean, default=False)
    auth_type = Column(String)
    is_builtin = Column(Boolean, default=False)
    created_date = Column(DateTime, default=datetime.utcnow)
    
    agent_versions = relationship('AgentVersion', secondary=agent_version_tools, back_populates='tools')

# 导入包表
class Import(Base):
    __tablename__ = 'imports'
    
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    lib = Column(String, nullable=True)
    source = Column(String)
    
    agent_versions = relationship('AgentVersion', secondary=agent_version_imports, back_populates='imports')

# 日志表
class Log(Base):
    __tablename__ = 'logs'
    
    id = Column(Integer, primary_key=True)
    workflow_execution_id = Column(Integer, ForeignKey('workflow_executions.id'), nullable=True)
    agent_name = Column(String, nullable=False)
    message = Column(String, nullable=False)
    timestamp = Column(DateTime, nullable=False)
    params = Column(JSON, nullable=True)
    output = Column(JSON, nullable=True)
    time_spent = Column(Float, nullable=True)
    log_type = Column(String, nullable=False)
    level = Column(String, default='INFO')
    tags = Column(JSON)
    context = Column(JSON)
    parent_log_id = Column(Integer, ForeignKey('logs.id'), nullable=True)
    triggered_by_log_id = Column(Integer, ForeignKey('logs.id'), nullable=True)
    
    parent_log = relationship('Log', remote_side=[id], backref='child_logs', foreign_keys=[parent_log_id])
    triggered_by_log = relationship('Log', remote_side=[id], backref='triggered_logs', foreign_keys=[triggered_by_log_id])

# 用户表
class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    _password_hash = Column(LargeBinary, nullable=False)
    role = Column(String, default='user')  # user, admin
    is_active = Column(Boolean, default=True)
    created_date = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime)
    
    @hybrid_property
    def password(self):
        raise AttributeError('password is not readable')
    
    @password.setter
    def password(self, plaintext_password):
        """加密存储密码"""
        self._password_hash = fernet.encrypt(plaintext_password.encode())
    
    def verify_password(self, plaintext_password):
        """验证密码"""
        try:
            stored_password = fernet.decrypt(self._password_hash).decode()
            return stored_password == plaintext_password
        except:
            return False


# ============================================================================
# AI对话相关模型
# ============================================================================

class ChatSession(Base):
    """AI对话会话"""
    __tablename__ = 'chat_sessions'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    title = Column(String, default='新对话')
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    
class ChatMessage(Base):
    """AI对话消息"""
    __tablename__ = 'chat_messages'
    
    id = Column(Integer, primary_key=True)
    session_id = Column(Integer, ForeignKey('chat_sessions.id'), nullable=False)
    role = Column(String, nullable=False)  # user, assistant, system
    content = Column(Text, nullable=False)
    tokens = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

# 密钥表
class SecretKey(Base):
    __tablename__ = 'secret_keys'
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)
    _encrypted_value = Column(LargeBinary, nullable=False)
    
    @hybrid_property
    def value(self):
        if self._encrypted_value:
            try:
                return fernet.decrypt(self._encrypted_value).decode()
            except InvalidToken:
                print(f"Error decrypting value for key: {self.name}")
                return None
        return None
    
    @value.setter
    def value(self, plaintext_value):
        if plaintext_value:
            self._encrypted_value = fernet.encrypt(plaintext_value.encode())
        else:
            self._encrypted_value = None

