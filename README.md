# AgentFlow - AI智能体工作流平台

<div align="center">

**🚀 基于Flask的可视化AI Agent编排平台**

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-2.0+-green.svg)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

[功能特性](#-功能特性) • [快速开始](#-快速开始) • [详细文档](#-详细文档) • [示例](#-使用示例) • [API文档](#-api文档)

</div>

---

## 📖 目录

- [项目简介](#-项目简介)
- [功能特性](#-功能特性)
- [技术栈](#-技术栈)
- [项目结构](#-项目结构)
- [快速开始](#-快速开始)
- [详细配置](#-详细配置)
- [核心功能使用](#-核心功能使用)
- [Agent开发指南](#-agent开发指南)
- [工作流开发](#-工作流开发)
- [API文档](#-api文档)
- [常见问题](#-常见问题)
- [更新日志](#-更新日志)

---

## 🎯 项目简介

**AgentFlow** 是一个强大的AI智能体工作流平台，让您能够轻松创建、编排和执行复杂的AI Agent工作流。

### 核心优势

- 🎨 **可视化编排**：拖拽式工作流设计，无需编写复杂代码
- 🤖 **AI驱动**：集成DeepSeek等主流LLM，真正的智能Agent
- ⚡ **即时反馈**：实时进度显示、流式输出、零延迟体验
- 🔌 **API发布**：一键将工作流发布为RESTful API
- 👥 **多用户系统**：完整的用户管理和权限控制
- 🛡️ **安全可靠**：超时控制、错误处理、详细日志

### 适用场景

- 📝 **内容创作**：自动生成文章、报告、营销文案
- 🔍 **数据分析**：智能数据处理和分析工作流
- 🤝 **业务自动化**：复杂业务流程的自动化编排
- 🧪 **AI实验**：快速构建和测试AI Agent原型

---

## ✨ 功能特性

### 1️⃣ Agent管理

- ✅ **AI助手创建**：通过对话自动生成Agent代码
- ✅ **手动创建**：编写Python代码创建自定义Agent
- ✅ **一键升级**：将模板Agent升级为AI驱动版本
- ✅ **版本管理**：Agent多版本支持和回滚
- ✅ **批量操作**：批量导入、导出、删除

### 2️⃣ 工作流编排

- ✅ **可视化编辑器**：拖拽式画布工作流设计器
- ✅ **自动布局**：智能节点排列
- ✅ **实时预览**：即时查看工作流结构
- ✅ **参数映射**：灵活的输入输出配置
- ✅ **条件分支**：支持复杂的执行逻辑

### 3️⃣ 执行监控

- ✅ **实时进度**：进度条显示执行状态
- ✅ **流式输出**：逐字打印执行日志
- ✅ **超时控制**：120秒Agent超时保护
- ✅ **详细日志**：完整的执行追踪
- ✅ **错误处理**：优雅的错误提示和恢复

### 4️⃣ API服务

- ✅ **一键发布**：将工作流发布为API
- ✅ **密钥管理**：安全的API Key认证
- ✅ **调用统计**：API使用情况分析
- ✅ **文档生成**：自动生成API文档

### 5️⃣ 用户体验

- ✅ **零延迟响应**：所有操作立即反馈
- ✅ **精美界面**：现代化UI设计
- ✅ **流畅动画**：淡入、滑动、毛玻璃效果
- ✅ **终端风格**：专业的日志显示
- ✅ **移动适配**：响应式布局

---

## 🛠 技术栈

### 后端技术

| 技术 | 版本 | 用途 |
|------|------|------|
| Python | 3.8+ | 核心语言 |
| Flask | 2.0+ | Web框架 |
| SQLAlchemy | 1.4+ | ORM |
| SQLite | 3.0+ | 数据库 |
| Requests | 2.28+ | HTTP客户端 |
| Cryptography | 41.0+ | 加密服务 |

### 前端技术

| 技术 | 说明 |
|------|------|
| 原生JavaScript | 无框架依赖 |
| HTML5/CSS3 | 现代化界面 |
| Fetch API | 异步请求 |
| CSS Grid/Flexbox | 布局系统 |

### AI集成

| 服务 | 用途 |
|------|------|
| DeepSeek API | 主要LLM服务 |
| OpenAI兼容接口 | 支持多种LLM |

---

## 📂 项目结构

```
AI-agent/
├── app.py                 # Flask主应用入口
├── agents.py              # 预置Agent定义
├── requirements.txt       # Python依赖列表
├── README.md              # 项目文档（本文件）
├── encryption_key.json    # 加密密钥配置
├── babyagi.db            # SQLite数据库
│
├── api/                   # API路由模块
│   ├── __init__.py
│   └── routes.py          # RESTful API定义
│
├── backend/               # 后端核心模块
│   ├── __init__.py
│   ├── database.py        # 数据库操作层
│   ├── engine.py          # Agent执行引擎
│   ├── llm_service.py     # LLM服务封装
│   ├── models.py          # 数据模型定义
│   ├── tools.py           # 工具函数
│   └── ai_tools.py        # AI相关工具
│
└── frontend/              # 前端资源
    ├── __init__.py
    ├── static/            # 静态资源
    │   ├── css/
    │   │   └── style.css          # 全局样式
    │   └── js/
    │       ├── main.js            # 主脚本
    │       ├── workflow-editor.js # 工作流编辑器
    │       └── batch-operations.js # 批量操作
    │
    └── templates/         # HTML模板
        ├── workspace_new.html     # 工作台主界面
        ├── workflow_editor.html   # 工作流编辑器
        ├── upgrade_agents.html    # Agent升级中心
        ├── ai_assistant.html      # AI助手
        └── ...                    # 其他页面
```

---

## 🚀 快速开始

### 前置要求

- Python 3.8 或更高版本
- pip 包管理器
- （可选）DeepSeek API Key

### 安装步骤

#### 1. 克隆项目

```bash
git clone <repository-url>
cd AI-agent
```

#### 2. 安装依赖

```bash
pip install -r requirements.txt
```

#### 3. 启动服务器

```bash
python app.py
```

#### 4. 访问平台

打开浏览器访问：

```
http://localhost:5000
```

默认账号：
- 用户名：`admin`
- 密码：`admin123`

### 🎉 完成！

现在您可以开始使用AgentFlow了！

---

## ⚙️ 详细配置

### 1. LLM服务配置

#### 方法1：代码配置（推荐）

编辑 `backend/llm_service.py`：

```python
class DeepSeekLLM:
    def __init__(self, api_key: Optional[str] = None, base_url: str = "https://api.deepseek.com/v1"):
        self._api_key = api_key or "your-api-key-here"
        self.base_url = base_url
```

#### 方法2：环境变量

```bash
# Windows
set DEEPSEEK_API_KEY=your-api-key

# Linux/Mac
export DEEPSEEK_API_KEY=your-api-key
```

#### 方法3：数据库配置

通过Web界面设置（开发中）

### 2. 数据库配置

默认使用SQLite，如需更换：

编辑 `backend/database.py`：

```python
DATABASE_URL = "sqlite:///babyagi.db"

# 或使用其他数据库
# DATABASE_URL = "postgresql://user:pass@localhost/dbname"
# DATABASE_URL = "mysql://user:pass@localhost/dbname"
```

### 3. 安全配置

#### 修改默认密码

首次登录后，请立即修改默认管理员密码。

#### 生成新的加密密钥

```python
from cryptography.fernet import Fernet
key = Fernet.generate_key()
print(key.decode())
```

将生成的密钥更新到 `encryption_key.json`。

### 4. 超时配置

编辑 `backend/engine.py`：

```python
# Agent执行超时（默认120秒）
def execute(self, agent_name: str, ..., timeout: int = 120):
    ...
```

编辑 `backend/llm_service.py`：

```python
# LLM请求超时（默认连接10秒，读取60秒）
timeout=(10, 60)
```

---

## 🎯 核心功能使用

### 1. 创建Agent

#### 方式1：AI助手创建（推荐）

1. 点击顶部导航 **"AI助手"**
2. 输入需求：

```
帮我创建一个生成产品文案的Agent，
要求：
- 调用DeepSeek API
- 输入：产品名称、特点
- 输出：创意文案
```

3. AI自动生成并注册Agent ✅

#### 方式2：升级预置Agent

1. 进入工作台
2. 点击 **"🚀 升级中心"**
3. 点击 **"✨ 立即升级"**
4. 等待流式输出完成
5. 重启服务器：
   ```bash
   # Ctrl+C 停止
   python app.py
   ```

#### 方式3：手动编写代码

创建 `my_agent.py`：

```python
def 我的Agent(input_data: dict) -> dict:
    """
    Agent功能描述
    
    Args:
        input_data: 输入参数字典
        
    Returns:
        {'success': bool, 'result': Any, 'error': str}
    """
    try:
        # 1. 获取输入
        param = input_data.get('param_name', 'default')
        
        # 2. 调用LLM（可选）
        from backend.llm_service import get_llm_service
        llm = get_llm_service()
        
        if llm.is_configured():
            response = llm.chat([
                {'role': 'user', 'content': f'你的prompt: {param}'}
            ])
            result = response['content']
        else:
            result = f'默认处理: {param}'
        
        # 3. 返回结果
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

### 2. 创建工作流

#### 可视化创建

1. 点击 **"🎨 可视化创建"**
2. 从左侧拖拽Agent到画布
3. 连接Agent形成工作流
4. 配置每个节点的参数映射
5. 点击 **"保存工作流"**

#### JSON创建

```json
{
  "name": "我的工作流",
  "description": "工作流描述",
  "agents": [
    {
      "name": "agent1",
      "input_mapping": {
        "param": "{input.user_input}"
      },
      "output_key": "agent1_result"
    },
    {
      "name": "agent2",
      "input_mapping": {
        "data": "{agent1_result}"
      },
      "output_key": "final_result"
    }
  ]
}
```

### 3. 执行工作流

1. 在工作台找到工作流
2. 点击 **"▶ 执行"**
3. 输入参数（JSON格式）：

```json
{
  "topic": "人工智能",
  "keywords": "机器学习",
  "target_audience": "技术爱好者"
}
```

4. 点击 **"确定"**
5. 立即看到：
   - ⚡ 精美的进度窗口
   - 📊 实时进度条（0% → 100%）
   - 💬 逐字打印的执行日志
   - 📄 最终生成的结果

### 4. 发布API

1. 进入工作流详情
2. 点击 **"发布为API"**
3. 生成API密钥
4. 获取调用地址和文档

#### API调用示例

```python
import requests

url = "http://localhost:5000/api/public/workflow/execute"
headers = {
    "X-API-Key": "your-api-key",
    "Content-Type": "application/json"
}
data = {
    "workflow_id": 1,
    "input": {
        "topic": "人工智能",
        "keywords": "机器学习"
    }
}

response = requests.post(url, headers=headers, json=data)
result = response.json()
print(result)
```

---

## 📚 Agent开发指南

### Agent结构

一个标准的Agent函数应该包含：

```python
def Agent名称(input_data: dict) -> dict:
    """
    【必需】Agent功能描述
    
    Args:
        input_data: 输入数据字典
        
    Returns:
        dict: 包含success, result, error的字典
    """
    try:
        # 1. 参数获取
        param1 = input_data.get('param1', 'default_value')
        param2 = input_data.get('param2', 'default_value')
        
        # 2. 业务逻辑
        # 可以调用LLM、API、数据库等
        result = process_data(param1, param2)
        
        # 3. 返回结果
        return {
            'success': True,
            'result': result
        }
        
    except Exception as e:
        # 4. 错误处理
        return {
            'success': False,
            'error': str(e)
        }
```

### LLM调用

```python
def AI_Agent(input_data: dict) -> dict:
    try:
        # 导入LLM服务
        from backend.llm_service import get_llm_service
        llm = get_llm_service()
        
        # 检查配置
        if not llm.is_configured():
            return {
                'success': False,
                'error': '未配置LLM API Key'
            }
        
        # 构建prompt
        prompt = f"请根据以下信息生成内容：{input_data}"
        
        # 调用LLM
        response = llm.chat([
            {'role': 'system', 'content': '你是一个专业的助手'},
            {'role': 'user', 'content': prompt}
        ], temperature=0.7, max_tokens=2000)
        
        # 处理响应
        if response['success']:
            return {
                'success': True,
                'result': response['content']
            }
        else:
            return {
                'success': False,
                'error': response['error']
            }
            
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }
```

### 智能降级

```python
def 智能Agent(input_data: dict) -> dict:
    """支持智能降级的Agent"""
    try:
        from backend.llm_service import get_llm_service
        llm = get_llm_service()
        
        # 尝试使用LLM
        if llm.is_configured():
            try:
                response = llm.chat([...])
                if response['success']:
                    return {
                        'success': True,
                        'result': response['content'],
                        'mode': 'ai'
                    }
            except Exception as e:
                print(f"LLM调用失败: {e}")
        
        # 降级到模板处理
        result = template_process(input_data)
        return {
            'success': True,
            'result': result,
            'mode': 'template'
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }
```

---

## 🔄 工作流开发

### 参数映射

工作流中的参数映射支持以下格式：

```json
{
  "input_mapping": {
    "param1": "{input.user_input}",      // 用户输入
    "param2": "{agent1_result}",         // 前置Agent输出
    "param3": "{agent2_result.field}",   // 前置Agent输出的特定字段
    "param4": "固定值"                    // 固定值
  }
}
```

### 条件执行（开发中）

```json
{
  "name": "条件Agent",
  "condition": {
    "field": "{previous_result.status}",
    "operator": "equals",
    "value": "success"
  },
  "input_mapping": {...}
}
```

### 循环执行（开发中）

```json
{
  "name": "循环Agent",
  "loop": {
    "source": "{previous_result.items}",
    "max_iterations": 10
  },
  "input_mapping": {...}
}
```

---

## 📡 API文档

### 认证

所有API请求需要包含API Key：

```http
X-API-Key: your-api-key-here
```

### 端点列表

#### Agent管理

```http
GET    /api/agents              # 获取所有Agent
POST   /api/agents              # 创建Agent
PUT    /api/agents/{id}         # 更新Agent
DELETE /api/agents/{id}         # 删除Agent
POST   /api/agents/upgrade      # 升级Agent
```

#### 工作流管理

```http
GET    /api/workflows           # 获取所有工作流
POST   /api/workflows           # 创建工作流
PUT    /api/workflows/{id}      # 更新工作流
DELETE /api/workflows/{id}      # 删除工作流
POST   /api/workflows/{id}/execute  # 执行工作流
```

#### 公开API

```http
POST   /api/public/workflow/execute  # 执行工作流（需要API Key）
```

### 请求示例

#### 执行工作流

```bash
curl -X POST http://localhost:5000/api/workflows/1/execute \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "人工智能",
    "keywords": "机器学习"
  }'
```

#### 响应格式

```json
{
  "success": true,
  "workflow_id": 1,
  "execution_id": 123,
  "output": {
    "agent1_result": {...},
    "agent2_result": {...},
    "final_result": "..."
  },
  "execution_time": 5.23
}
```

---

## ❓ 常见问题

### Q1: Agent不使用我的输入参数？

**A:** 确保Agent代码正确读取 `input_data`：

```python
# ✅ 正确
topic = input_data.get('topic', '默认值')

# ❌ 错误
topic = '固定值'
```

### Q2: 升级后Agent没有效果？

**A:** 需要重启Flask服务器：

```bash
# Windows/Linux/Mac
Ctrl+C 停止
python app.py 重启
```

### Q3: LLM调用失败？

**A:** 检查以下几点：

1. API Key是否正确配置
2. 网络连接是否正常
3. API余额是否充足
4. 查看日志定位具体错误

```python
from backend.llm_service import get_llm_service
llm = get_llm_service()
print(f"配置状态: {llm.is_configured()}")
print(f"API Key: {llm.api_key[:10]}...")
```

### Q4: 工作流执行超时？

**A:** 查看日志判断卡在哪里：

```
[AgentExecutor] 开始执行 Agent: xxx
[LLM] 准备调用DeepSeek API...
[LLM] 收到响应，耗时: XXs
[AgentExecutor] Agent执行完成
```

超时层级：
- 连接超时：10秒
- 读取超时：60秒
- Agent超时：120秒

### Q5: 如何调试Agent？

**A:** 在Agent代码中添加日志：

```python
def 我的Agent(input_data: dict) -> dict:
    print(f"[DEBUG] 输入参数: {input_data}")
    
    # 处理逻辑
    result = process(input_data)
    
    print(f"[DEBUG] 处理结果: {result}")
    return {'success': True, 'result': result}
```

### Q6: 数据库迁移

**A:** 使用SQLite浏览器或命令行：

```bash
# 备份数据库
cp babyagi.db babyagi.db.backup

# 导出数据
sqlite3 babyagi.db .dump > backup.sql

# 导入数据
sqlite3 new_babyagi.db < backup.sql
```

---

## 📝 更新日志

### v2.1.0 (2025-11-05)

#### 新增
- ✅ Agent执行超时机制（120秒）
- ✅ 详细的执行日志
- ✅ LLM调用状态追踪

#### 优化
- ✅ 工作流执行立即弹窗
- ✅ 实时进度条显示
- ✅ 流式输出效果
- ✅ 超时错误提示

### v2.0.0 (2025-11-04)

#### 新增
- ✅ Web界面Agent升级中心
- ✅ 流式输出和实时进度条
- ✅ 工作流执行结果优化展示

#### 修复
- ✅ 工作流画布清空确认问题
- ✅ Agent不使用输入参数问题
- ✅ 执行结果显示问题

#### 优化
- ✅ 用户体验大幅提升
- ✅ 界面动画效果
- ✅ 立即反馈机制

### v1.0.0 (2025-11-01)

- ✅ 初始版本发布
- ✅ 基础Agent和工作流系统
- ✅ 可视化工作流编辑器
- ✅ API发布功能
- ✅ 用户管理系统

---

## 🤝 贡献指南

欢迎贡献代码、报告问题、提出建议！

### 开发流程

1. Fork 本仓库
2. 创建特性分支：`git checkout -b feature/amazing-feature`
3. 提交更改：`git commit -m 'Add amazing feature'`
4. 推送分支：`git push origin feature/amazing-feature`
5. 提交 Pull Request

### 代码规范

- Python：遵循 PEP 8
- JavaScript：使用 ES6+ 语法
- 注释：中文注释，清晰明了
- 命名：使用有意义的变量和函数名

---

## 📄 许可证

本项目采用 [MIT License](LICENSE) 许可证。

---

## 🙏 致谢

感谢以下开源项目：

- [Flask](https://flask.palletsprojects.com/) - Web框架
- [SQLAlchemy](https://www.sqlalchemy.org/) - ORM
- [DeepSeek](https://www.deepseek.com/) - LLM服务

---

## 🌟 Star History

如果这个项目对您有帮助，请给我们一个 ⭐ Star！

---

<div align="center">

**Built with ❤️ by AgentFlow Team**

[⬆ 回到顶部](#agentflow---ai智能体工作流平台)

</div>
