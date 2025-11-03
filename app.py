# ============================================================================
# AgentFlow - 应用入口 (Application Entry Point)
# ============================================================================
# 三层架构:
#   - Backend:  后端层 (数据模型 + 业务逻辑)
#   - API:      中间层 (REST API 接口)
#   - Frontend: 前端层 (用户界面)
# ============================================================================

from flask import Flask, render_template, redirect, session, url_for, request
import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# ============================================================================
# 导入三层
# ============================================================================

# Backend 层
from backend.database import Database
from backend.engine import AgentRegistry, AgentExecutor, WorkflowEngine, LLMService

# API 层
from api.routes import api, init_api

# ============================================================================
# 创建 Flask 应用
# ============================================================================

app = Flask(__name__, 
            template_folder='frontend/templates',
            static_folder='frontend/static')

# 设置 Session 密钥（生产环境应使用环境变量）
app.secret_key = 'agentforge-secret-key-change-in-production'

# ============================================================================
# 初始化系统
# ============================================================================

print("\n" + "="*60)
print("AgentFlow 系统启动中...")
print("="*60)

# 1. 初始化数据库 (Backend)
print("\n[1/4] 初始化数据库...")
db = Database('sqlite:///agentflow.db')

# 2. 初始化 Agent 注册中心 (Backend)
print("[2/4] 初始化 Agent 注册中心...")
registry = AgentRegistry(db)

# 3. 初始化 LLM 服务 (Backend)
print("[3/4] 初始化 LLM 服务...")
llm_service = None
try:
    with db.session_scope() as db_session:
        api_key = db.get_secret_key(db_session, 'openai_api_key')
        if api_key:
            llm_service = LLMService(api_key=api_key)
        else:
            print("  ⚠️  未配置 OpenAI API Key，AI Agent 功能将不可用")
except Exception as e:
    print(f"  ⚠️  LLM 服务初始化失败: {e}")

# 初始化 DeepSeek LLM
from backend.llm_service import get_llm_service
deepseek_llm = get_llm_service()
deepseek_llm.set_database(db)
print("  ✓ DeepSeek LLM 服务已初始化")

# 初始化工具系统
from backend.tools import global_tool_registry, register_default_tools
register_default_tools()
print("  ✓ 工具系统已初始化")

# 4. 初始化执行引擎 (Backend)
executor = AgentExecutor(db, registry, llm_service)
engine = WorkflowEngine(db, executor)

# 5. 初始化 API 层 (API)
print("[4/4] 初始化 API 层...")
init_api(db, engine, registry)  # 传递 registry 参数
app.register_blueprint(api)

# 6. 加载预置 Agent（已禁用，避免自动创建多余智能体）
# print("[5/5] 加载预置 Agent...")
# from agents import register_all_agents
# register_all_agents(registry)
print("[5/5] 跳过预置 Agent 加载（仅加载用户创建的Agent）")

print("\n" + "="*60)
print("✓ AgentFlow 系统启动完成！")
print("="*60)

# ============================================================================
# 前端路由
# ============================================================================

@app.before_request
def log_request():
    """记录所有请求"""
    import sys
    print(f"\n🔔 [Flask请求] {request.method} {request.path}", flush=True)
    sys.stdout.flush()

@app.route('/')
def index():
    """公开主页 - 展示平台信息"""
    return render_template('home.html')

@app.route('/workspace')
def workspace():
    """工作台 - 需要登录"""
    if 'user_id' not in session:
        return redirect('/login')
    
    return render_template('index.html', 
                         username=session.get('username'),
                         role=session.get('role'))

@app.route('/admin')
def admin():
    """管理后台 - 仅管理员可访问"""
    if 'user_id' not in session:
        return redirect('/login')
    if session.get('role') != 'admin':
        return '⛔ 仅管理员可访问', 403
    
    return render_template('admin.html', 
                         username=session.get('username'))

@app.route('/login')
def login_page():
    """登录页面"""
    # 如果已登录，跳转到工作台
    if 'user_id' in session:
        return redirect('/workspace')
    
    return render_template('login.html')

@app.route('/register')
def register_page():
    """注册页面"""
    # 如果已登录，跳转到工作台
    if 'user_id' in session:
        return redirect('/workspace')
    
    return render_template('register.html')

@app.route('/demo')
def demo_page():
    """演示页面 - 展示示例"""
    return render_template('index.html', 
                         username='Demo User',
                         role='user')

@app.route('/ai-assistant')
def ai_assistant():
    """AI 助手页面"""
    if 'user_id' not in session:
        return redirect('/login')
    
    return render_template('ai_assistant.html',
                         username=session.get('username'),
                         role=session.get('role'))

@app.route('/chat')
def chat_page():
    """AI 对话页面（DeepSeek集成）"""
    if 'user_id' not in session:
        return redirect('/login')
    
    return render_template('chat.html',
                         username=session.get('username'),
                         role=session.get('role'))

@app.route('/tools')
def tools_page():
    """工具管理页面"""
    if 'user_id' not in session:
        return redirect('/login')
    
    return render_template('tools.html',
                         username=session.get('username'),
                         role=session.get('role'))

@app.route('/network-test')
def network_test():
    """网络诊断工具"""
    return render_template('network_test.html')

@app.route('/dashboard')
def dashboard():
    """数据可视化看板"""
    if 'user_id' not in session:
        return redirect('/login')
    
    return render_template('dashboard.html',
                         username=session.get('username'),
                         role=session.get('role'))

@app.route('/logout')
def logout():
    """登出"""
    session.clear()
    return redirect('/login')

@app.route('/test')
def test_page():
    """测试页面 - 用于调试工作流执行"""
    with open('test_execute.html', 'r', encoding='utf-8') as f:
        return f.read()

@app.route('/test-inline')
def test_inline_page():
    """内联JS测试页面 - 完全不依赖外部JS"""
    return render_template('test_inline.html')

# ============================================================================
# 导出对象供外部使用
# ============================================================================

# 导出给 demo 脚本使用
__all__ = ['db', 'registry', 'executor', 'engine', 'app']

# ============================================================================
# 启动服务器
# ============================================================================

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🚀 AgentFlow Web 服务器启动")
    print("="*60)
    print("\n访问地址：http://localhost:5000")
    print("\n提示：")
    print("  1. 运行 demo_simple.py 创建示例 Agent")
    print("  2. 运行 demo_web_crawler.py 创建完整工作流")
    print("  3. 在浏览器中查看 Web 界面")
    print("\n按 Ctrl+C 停止服务器\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)

