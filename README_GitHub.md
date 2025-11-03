# AgentForge - AI Agent 智能编排平台 🤖

一个功能强大的AI Agent智能编排平台，支持通过对话创建智能体、工作流，并集成了丰富的工具系统。

## ✨ 核心功能

### 🤖 AI对话创建
- **对话式创建**：通过与AI对话自动生成智能体和工作流
- **Function Calling**：集成DeepSeek AI，支持实时调用工具
- **流式输出**：真正的实时流式响应，类似ChatGPT体验

### 🔧 智能体系统
- **动态创建**：对话中自动生成并保存Agent
- **多类型支持**：processor、converter、analyzer等
- **代码执行**：动态加载和执行Agent代码
- **持久化存储**：Agent自动保存到数据库

### 🔀 工作流编排
- **可视化管理**：直观的工作流创建和管理界面
- **参数输入**：执行时可输入自定义参数
- **统计分析**：执行次数、成功率、平均时间等
- **美观结果展示**：居中模态框展示执行结果

### 🛠️ 工具系统
- **天气查询**：获取实时天气信息
- **网页搜索**：Bing搜索API集成
- **网页抓取**：提取网页内容
- **计算器**：数学表达式计算
- **时间工具**：获取当前时间
- **文件读取**：读取本地文件内容

### 📊 管理功能
- **批量操作**：批量删除智能体和工作流
- **工具管理**：可视化的工具列表和测试界面
- **日志记录**：详细的执行日志和调试信息

## 🚀 快速开始

### 环境要求
- Python 3.8+
- Flask
- SQLAlchemy
- DeepSeek API Key

### 安装步骤

1. 克隆仓库
```bash
git clone https://github.com/yourusername/AI-agent.git
cd AI-agent
```

2. 安装依赖
```bash
pip install -r requirements.txt
```

3. 配置API Key
在系统设置中配置DeepSeek API Key

4. 启动服务器
```bash
python app.py
```

5. 访问应用
打开浏览器访问 `http://localhost:5000`

## 📖 使用说明

### 创建智能体

**方式1：对话创建**
1. 进入AI对话界面
2. 描述你需要的智能体功能
3. AI自动生成代码和工作流
4. 点击"🚀 立即创建"按钮

**方式2：手动创建**
1. 进入工作台
2. 点击"创建Agent"按钮
3. 填写名称、类型、代码等信息
4. 保存

### 执行工作流

1. 在工作台找到工作流
2. 点击"▶ 执行"按钮
3. 在弹出的对话框中输入参数（JSON格式）
4. 查看执行结果

### 使用工具

1. 进入"🛠️ 工具管理"页面
2. 查看所有可用工具
3. 测试工具功能
4. AI对话中会自动调用合适的工具

## 🏗️ 项目结构

```
AI-agent/
├── app.py                 # 主应用入口
├── requirements.txt       # Python依赖
├── backend/              # 后端业务逻辑
│   ├── database.py       # 数据库操作
│   ├── engine.py         # Agent执行引擎
│   ├── models.py         # 数据模型
│   ├── llm_service.py    # LLM服务
│   └── tools.py          # 工具系统
├── api/                  # API接口层
│   └── routes.py         # API路由
└── frontend/             # 前端界面
    ├── templates/        # HTML模板
    └── static/           # 静态资源
        ├── css/
        └── js/
```

## 🔥 核心特性

### 动态Agent加载
- 启动时自动从数据库加载所有Agent
- 支持热加载和动态更新
- 代码执行沙箱

### 工作流引擎
- 支持顺序执行
- 支持参数传递
- 支持错误处理
- 实时统计更新

### 工具系统
- 插件化架构
- 易于扩展
- DeepSeek Function Calling集成
- 自动参数验证

## 📝 开发日志

### 已完成功能
- ✅ 集成DeepSeek AI对话（Function Calling）
- ✅ 创建工具管理可视化界面
- ✅ 真正的流式输出
- ✅ Agent动态创建和加载
- ✅ 工作流统计数据更新
- ✅ 美观的执行结果UI
- ✅ 参数输入界面
- ✅ 批量删除功能

### 计划中功能
- 🔄 添加更多工具（邮件、数据库等）
- 🔄 MCP协议集成
- 🔄 多用户支持
- 🔄 工作流可视化编辑器

## 🤝 贡献

欢迎提交Issue和Pull Request！

## 📄 许可证

MIT License

## 👨‍💻 作者

Your Name

## 🙏 致谢

- DeepSeek AI
- Flask
- SQLAlchemy
- 所有贡献者

