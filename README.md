# AgentForge - AI Agent 智能编排平台 🤖

<div align="center">

![Version](https://img.shields.io/badge/version-1.0-blue)
![Python](https://img.shields.io/badge/python-3.8+-green)
![License](https://img.shields.io/badge/license-MIT-orange)

**让 AI Agent 编排像搭积木一样简单**

[快速开始](#-快速开始) • [功能特性](#-功能特性) • [架构说明](#-架构说明) • [使用文档](#-使用文档)

</div>

---

## 📖 项目简介

AgentForge 是一个**AI Agent 智能编排平台**，让你通过简单的装饰器注册 Agent，然后像搭积木一样将它们组合成复杂的工作流。

### 🎯 核心特点

| 特性 | 说明 |
|------|------|
| 🚀 **极简注册** | 一行装饰器，Agent 即可工作 |
| 🔄 **工作流编排** | 支持 DAG（有向无环图）工作流 |
| 🤖 **多种 Agent** | Python 函数 + AI Agent (LLM) + 外部工具 |
| 📊 **完整监控** | 执行日志、性能统计、成本追踪 |
| 🏗️ **三层架构** | Backend + API + Frontend 完全分离 |
| 🎨 **现代化 UI** | 响应式设计、实时刷新 |

### 💡 适用场景

- 📊 **数据分析流程**：爬虫 → 清洗 → 分析 → 生成报告
- 🤖 **智能客服**：意图识别 → 知识检索 → 智能回复
- 🔍 **信息采集**：多源爬取 → 内容提取 → AI 摘要
- 📝 **内容生成**：主题生成 → AI 创作 → 质量评估

---

## 🚀 快速开始

### 1️⃣ 安装依赖

```bash
cd "AI agent"
pip install flask sqlalchemy cryptography openai requests beautifulsoup4
```

### 2️⃣ 运行示例

```bash
# 注册示例 Agent
python demo_simple.py
```

你会看到：
```
============================================================
AgentFlow 系统启动中...
============================================================

[1/4] 初始化数据库...
✓ 数据库初始化成功

[2/4] 初始化 Agent 注册中心...
✓ Agent 'text_processor' 注册成功 (processor)
✓ Agent 'calculator' 注册成功 (calculator)
✓ Agent 'formatter' 注册成功 (formatter)

...
✓ 所有测试完成！
```

### 3️⃣ 启动 Web 界面

```bash
python app.py
```

然后访问：**http://localhost:5000**

你会看到一个漂亮的 Web 界面，展示：
- 📊 统计卡片（Agent 数量、执行次数、成功率）
- 📦 Agent 库（所有注册的 Agent）
- 🔄 工作流列表
- 📝 执行日志

### 4️⃣ 运行完整工作流

```bash
python demo_web_crawler.py
```

这会创建一个完整的工作流：**网页爬虫 → AI 分析 → 报告生成 → 结果输出**

---

## 🏗️ 架构说明

### 三层架构

```
┌────────────────────────────────────┐
│  Frontend (前端层)                  │
│  - HTML/CSS/JavaScript             │
│  - 用户交互界面                    │
└────────────┬───────────────────────┘
             ↓↑ REST API
┌────────────┴───────────────────────┐
│  API (中间层)                       │
│  - REST API 接口                    │
│  - 请求/响应处理                    │
└────────────┬───────────────────────┘
             ↓↑ Function Call
┌────────────┴───────────────────────┐
│  Backend (后端层)                   │
│  - 数据模型 (Models)                │
│  - 数据访问 (Database)              │
│  - 业务逻辑 (Engine)                │
└────────────┬───────────────────────┘
             ↓↑ SQL
┌────────────┴───────────────────────┐
│  数据库 (SQLite)                    │
└────────────────────────────────────┘
```

### 目录结构

```
AI agent/
│
├── backend/              # 后端层
│   ├── models.py        # 数据模型 (ORM)
│   ├── database.py      # 数据访问层
│   └── engine.py        # 业务逻辑引擎
│
├── api/                 # API 层
│   └── routes.py        # REST API 路由
│
├── frontend/            # 前端层
│   ├── templates/       # HTML 模板
│   └── static/          # CSS/JS 资源
│
├── app.py              # 应用入口
├── demo_simple.py      # 简单示例
└── demo_web_crawler.py # 完整示例
```

### 核心组件

| 组件 | 说明 | 文件 |
|------|------|------|
| **AgentRegistry** | Agent 注册中心，管理所有 Agent | `backend/engine.py` |
| **AgentExecutor** | Agent 执行引擎，负责执行 Agent | `backend/engine.py` |
| **WorkflowEngine** | 工作流引擎，编排 Agent 执行顺序 | `backend/engine.py` |
| **LLMService** | LLM 服务封装，支持 OpenAI/DeepSeek | `backend/engine.py` |
| **Database** | 数据访问层，封装所有数据库操作 | `backend/database.py` |

---

## 📦 功能特性

### 1. Agent 系统

#### 三种 Agent 类型

| 类型 | 说明 | 示例 |
|------|------|------|
| **Python Function** | 普通 Python 函数 | 文本处理、数据计算 |
| **AI Agent** | 调用 LLM 模型 | 内容分析、智能问答 |
| **External Tool** | 外部 API/工具 | 网页爬取、文件操作 |

#### Agent 注册示例

```python
from app import registry

@registry.register(
    name="text_analyzer",
    agent_type="processor",
    category="文本处理",
    icon="📝",
    description="分析文本的情感和关键词"
)
def text_analyzer(text: str) -> dict:
    """分析文本"""
    return {
        'length': len(text),
        'words': len(text.split()),
        'sentiment': 'positive'  # 示例
    }
```

### 2. 工作流编排

#### 工作流定义

```python
workflow = {
    "nodes": [
        {"id": "1", "agent": "fetch_data", "params": {"url": "$input_url"}},
        {"id": "2", "agent": "process_data", "params": {"data": "$fetch_data_result"}},
        {"id": "3", "agent": "save_result", "params": {"data": "$process_data_result"}}
    ],
    "edges": [
        {"from": "1", "to": "2"},
        {"from": "2", "to": "3"}
    ]
}
```

#### 参数引用

支持使用 `$variable` 语法引用上一个 Agent 的输出：
- `$agent_name_result` - 引用某个 Agent 的输出
- `$agent_name_result.field` - 引用输出的某个字段

### 3. REST API

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/agents` | 获取所有 Agent |
| GET | `/api/agents/<name>` | 获取单个 Agent |
| GET | `/api/workflows` | 获取所有工作流 |
| POST | `/api/workflows` | 创建工作流 |
| POST | `/api/workflows/<id>/execute` | 执行工作流 |
| GET | `/api/logs` | 获取执行日志 |
| GET | `/api/stats` | 获取统计数据 |

### 4. Web 界面

#### 主要功能
- ✅ **实时统计**：Agent 数量、执行次数、成功率
- ✅ **Agent 管理**：查看所有注册的 Agent
- ✅ **工作流管理**：创建、查看、执行工作流
- ✅ **日志查看**：完整的执行日志和性能数据
- ✅ **自动刷新**：每 30 秒自动更新数据

---

## 💻 使用文档

### 创建你的第一个 Agent

```python
# 1. 导入注册器
from app import registry, executor

# 2. 注册 Agent
@registry.register(
    name="my_first_agent",
    agent_type="processor",
    category="数据处理",
    icon="🎯",
    description="我的第一个 Agent"
)
def my_first_agent(input_text: str) -> dict:
    """处理输入文本"""
    return {
        "output": input_text.upper(),
        "length": len(input_text)
    }

# 3. 执行 Agent
result = executor.execute(
    agent_name="my_first_agent",
    params={"input_text": "hello world"}
)

print(result['output'])
# {'output': 'HELLO WORLD', 'length': 11}
```

### 创建工作流

```python
from app import db, engine

# 1. 定义工作流
workflow_def = {
    "nodes": [
        {"id": "1", "agent": "agent1", "params": {"input": "$input"}},
        {"id": "2", "agent": "agent2", "params": {"data": "$agent1_result"}}
    ],
    "edges": [
        {"from": "1", "to": "2"}
    ]
}

# 2. 创建工作流
with db.session_scope() as session:
    workflow_id = db.create_workflow(
        session=session,
        name="我的工作流",
        description="示例工作流",
        workflow_definition=workflow_def,
        category="数据处理"
    )

# 3. 执行工作流
result = engine.execute_workflow(
    workflow_id=workflow_id,
    input_data={"input": "test data"}
)

print(f"执行状态: {result['success']}")
print(f"执行时间: {result['execution_time']:.2f}秒")
```

### 集成 AI Agent (LLM)

```python
# 1. 配置 API Key
with db.session_scope() as session:
    db.add_secret_key(session, 'openai_api_key', 'sk-your-api-key')

# 2. 注册 AI Agent
@registry.register(
    name="ai_analyzer",
    agent_type="ai_analyzer",
    llm_model="gpt-4",
    prompt_template="分析以下内容：{content}",
    description="AI 内容分析器"
)
def ai_analyzer(content: str) -> dict:
    """AI 分析（自动调用 LLM）"""
    pass  # 框架会自动调用 LLM

# 3. 执行 AI Agent
result = executor.execute(
    agent_name="ai_analyzer",
    params={"content": "这是一篇关于 AI 的文章..."}
)
```

---

## 🎓 使用案例

### 案例 1: 网页内容分析

```python
# 工作流：网页爬虫 → 内容提取 → AI 分析 → 生成报告

workflow = {
    "nodes": [
        {"id": "1", "agent": "web_crawler", "params": {"url": "$input_url"}},
        {"id": "2", "agent": "content_extractor", "params": {"html": "$web_crawler_result.html"}},
        {"id": "3", "agent": "ai_analyzer", "params": {"content": "$content_extractor_result.text"}},
        {"id": "4", "agent": "report_generator", "params": {"analysis": "$ai_analyzer_result"}}
    ],
    "edges": [
        {"from": "1", "to": "2"},
        {"from": "2", "to": "3"},
        {"from": "3", "to": "4"}
    ]
}
```

### 案例 2: 数据处理管道

```python
# 工作流：读取数据 → 清洗 → 特征提取 → 模型预测 → 保存结果

workflow = {
    "nodes": [
        {"id": "1", "agent": "data_reader", "params": {"file": "$input_file"}},
        {"id": "2", "agent": "data_cleaner", "params": {"data": "$data_reader_result"}},
        {"id": "3", "agent": "feature_extractor", "params": {"data": "$data_cleaner_result"}},
        {"id": "4", "agent": "ml_predictor", "params": {"features": "$feature_extractor_result"}},
        {"id": "5", "agent": "result_saver", "params": {"results": "$ml_predictor_result"}}
    ],
    "edges": [
        {"from": "1", "to": "2"},
        {"from": "2", "to": "3"},
        {"from": "3", "to": "4"},
        {"from": "4", "to": "5"}
    ]
}
```

---

## 📊 技术栈

### Backend
- **Python 3.8+**
- **SQLAlchemy** - ORM 框架
- **SQLite** - 数据库（可升级到 MySQL/PostgreSQL）
- **Cryptography** - 数据加密

### API
- **Flask** - Web 框架
- **Flask Blueprint** - 模块化路由
- **RESTful API** - 标准 HTTP 接口

### Frontend
- **HTML5 / CSS3**
- **Vanilla JavaScript**
- **响应式设计**

### AI & Tools
- **OpenAI API** / **DeepSeek API**
- **Requests** - HTTP 客户端
- **BeautifulSoup4** - HTML 解析

---

## 🎯 核心优势

### 1. 开发效率高

```python
# 传统方式：需要写大量代码
def process_workflow():
    result1 = fetch_data()
    result2 = process_data(result1)
    result3 = save_result(result2)
    # ... 大量胶水代码

# AgentForge 方式：只需定义工作流
workflow = {
    "nodes": [
        {"id": "1", "agent": "fetch_data"},
        {"id": "2", "agent": "process_data"},
        {"id": "3", "agent": "save_result"}
    ],
    "edges": [...]
}
```

### 2. 易于维护

- ✅ **模块化**：每个 Agent 独立开发、测试、部署
- ✅ **可复用**：Agent 可在多个工作流中复用
- ✅ **易调试**：完整的日志追踪

### 3. 可扩展性强

- ✅ **添加新 Agent**：只需一个装饰器
- ✅ **扩展数据库**：支持 MySQL、PostgreSQL
- ✅ **扩展 LLM**：支持任何兼容 OpenAI 格式的 API

### 4. 企业级架构

- ✅ **三层架构**：Backend + API + Frontend 分离
- ✅ **事务管理**：完整的数据一致性保证
- ✅ **错误处理**：完善的异常捕获和日志记录

---

## 🛠️ 开发指南

### 添加新的 Agent

```python
# 在你的脚本中
from app import registry

@registry.register(
    name="your_agent_name",
    agent_type="processor",
    category="分类",
    icon="🎯",
    description="Agent 描述"
)
def your_agent_name(param1: str, param2: int) -> dict:
    """
    Agent 功能说明
    
    Args:
        param1: 参数1说明
        param2: 参数2说明
    
    Returns:
        结果字典
    """
    # 你的逻辑
    return {"result": "success"}
```

### 添加新的 API 接口

```python
# 在 api/routes.py 中
@api.route('/your-endpoint', methods=['POST'])
def your_endpoint():
    """你的 API 端点"""
    data = request.get_json()
    
    # 处理逻辑
    result = process_data(data)
    
    return jsonify(result), 200
```

### 修改前端界面

```javascript
// 在 frontend/static/js/main.js 中
async function loadYourData() {
    const resp = await fetch('/api/your-endpoint');
    const data = await resp.json();
    
    // 更新界面
    document.getElementById('your-element').innerHTML = renderData(data);
}
```

---

## 🎬 比赛演示建议

### 演示流程（5分钟）

#### 1. 介绍项目（30秒）
> "AgentForge 是一个 AI Agent 智能编排平台，让复杂的自动化流程像搭积木一样简单。"

#### 2. 展示架构（1分钟）
> "我们采用标准三层架构：Backend 负责数据和业务，API 提供 REST 接口，Frontend 提供用户界面。"

#### 3. 演示功能（2分钟）
```bash
# 终端1：注册 Agent
python demo_simple.py

# 终端2：启动服务
python app.py

# 浏览器：展示界面
http://localhost:5000
```

#### 4. 讲解代码（1分钟）
```python
# 展示装饰器注册的简洁性
@registry.register(name="my_agent", agent_type="processor")
def my_agent(text: str):
    return {"result": text.upper()}
```

#### 5. 回答问题（30秒）
- **为什么用三层架构？** → 职责分离、易维护、工业标准
- **如何扩展系统？** → 每层独立扩展
- **有什么创新点？** → 装饰器注册、工作流编排、参数引用

---

## 📝 常见问题

### Q1: 支持哪些 LLM？
**A**: 支持所有兼容 OpenAI API 格式的 LLM，包括 OpenAI、DeepSeek、Anthropic Claude 等。

### Q2: 如何部署到生产环境？
**A**: 
```bash
# 1. 使用 Gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app

# 2. 使用 Docker
docker build -t agentforge .
docker run -p 5000:5000 agentforge

# 3. 配置 Nginx 反向代理
```

### Q3: 数据库可以换成 MySQL 吗？
**A**: 可以！只需修改 `app.py` 中的数据库连接字符串：
```python
db = Database('mysql://user:pass@localhost/dbname')
```

### Q4: 如何添加用户认证？
**A**: 可以使用 Flask-Login 或 JWT：
```python
# 在 api/routes.py 中添加认证装饰器
from flask_login import login_required

@api.route('/api/workflows', methods=['POST'])
@login_required
def create_workflow():
    # ...
```

---

## 📄 许可证

MIT License - 可自由用于学习、比赛和商业项目

---

## 🙏 致谢

- Flask - Web 框架
- SQLAlchemy - ORM 框架
- OpenAI - LLM API

---

## 📧 联系我们

- **项目名称**: AgentForge
- **版本**: v1.0
- **团队**: 见下方建议

---

<div align="center">

## 🚀 立即开始使用 AgentForge！

```bash
cd "AI agent"
python demo_simple.py    # 运行示例
python app.py            # 启动服务
```

**让 AI Agent 编排像搭积木一样简单！**

[查看开发文档](开发文档.md) • [报告问题](https://github.com/your-repo/issues)

</div>
