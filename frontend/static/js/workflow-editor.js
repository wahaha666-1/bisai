/**
 * 工作流可视化编辑器 - 
 */

// 全局状态
let nodes = [];
let connections = [];
let selectedNode = null;
let draggedNode = null;
let connectingFrom = null;
let nodeIdCounter = 1;
let workflowId = null;

// 🆕 缩放和平移状态
let scale = 1;
let translateX = 0;
let translateY = 0;
let isPanning = false;
let panStartX = 0;
let panStartY = 0;

// 🆕 撤销/重做历史
let history = [];
let historyIndex = -1;
const MAX_HISTORY = 50;

// 初始化
document.addEventListener('DOMContentLoaded', async () => {
    await loadAgents();
    setupEventListeners();
    
    // 从URL获取工作流ID（如果是编辑模式）
    const urlParams = new URLSearchParams(window.location.search);
    workflowId = urlParams.get('id');
    
    if (workflowId) {
        await loadExistingWorkflow(workflowId);
    }
});

// 加载所有Agents到侧边栏
async function loadAgents() {
    try {
        const response = await fetch('/api/agents');
        const agents = await response.json();
        
        const palette = document.getElementById('agent-palette');
        palette.innerHTML = agents.map(agent => `
            <div class="palette-node" draggable="true" data-node-type="agent" data-agent-name="${agent.name}">
                <span class="node-icon">🤖</span>
                <span class="node-label">${agent.name}</span>
            </div>
        `).join('');
        
        // 添加拖拽事件
        document.querySelectorAll('.palette-node').forEach(node => {
            node.addEventListener('dragstart', handlePaletteDragStart);
        });
    } catch (error) {
        console.error('加载Agents失败:', error);
    }
}

// 设置事件监听器
function setupEventListeners() {
    const canvas = document.getElementById('canvas');
    
    // 画布拖放
    canvas.addEventListener('dragover', handleCanvasDragOver);
    canvas.addEventListener('drop', handleCanvasDrop);
    
    // 右键菜单
    canvas.addEventListener('contextmenu', handleContextMenu);
    document.addEventListener('click', () => {
        document.getElementById('context-menu').style.display = 'none';
    });
}

// 从侧边栏拖拽节点
function handlePaletteDragStart(e) {
    const nodeType = e.target.closest('.palette-node').dataset.nodeType;
    const agentName = e.target.closest('.palette-node').dataset.agentName;
    e.dataTransfer.setData('nodeType', nodeType);
    if (agentName) {
        e.dataTransfer.setData('agentName', agentName);
    }
}

// 画布拖放处理
function handleCanvasDragOver(e) {
    e.preventDefault();
    e.dataTransfer.dropEffect = 'copy';
}

function handleCanvasDrop(e) {
    e.preventDefault();
    
    const nodeType = e.dataTransfer.getData('nodeType');
    const agentName = e.dataTransfer.getData('agentName');
    
    const canvas = document.getElementById('canvas');
    const rect = canvas.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    
    createNode(nodeType, x, y, agentName);
    
    // 隐藏空状态
    document.getElementById('empty-state').style.display = 'none';
}

// 创建节点
function createNode(type, x, y, agentName = null) {
    const nodeId = `node-${nodeIdCounter++}`;
    
    let nodeData = {
        id: nodeId,
        type: type,
        x: x,
        y: y,
        config: {}
    };
    
    let headerClass = '';
    let icon = '';
    let title = '';
    let body = '';
    
    switch(type) {
        case 'input':
            headerClass = 'input';
            icon = '📥';
            title = '输入节点';
            body = `
                <div class="node-field">
                    <div class="field-label">输入参数</div>
                    <div>用户提供的初始数据</div>
                </div>
            `;
            nodeData.config = { type: 'input' };
            break;
            
        case 'output':
            headerClass = 'output';
            icon = '📤';
            title = '输出节点';
            body = `
                <div class="node-field">
                    <div class="field-label">输出结果</div>
                    <div>工作流的最终结果</div>
                </div>
            `;
            nodeData.config = { type: 'output' };
            break;
            
        case 'agent':
            icon = '🤖';
            title = agentName || 'Agent';
            body = `
                <div class="node-field">
                    <div class="field-label">Agent名称</div>
                    <div>${agentName}</div>
                </div>
                <div class="node-field">
                    <div class="field-label">输入映射</div>
                    <div style="font-size: 12px; color: #9ca3af;">双击编辑配置</div>
                </div>
            `;
            nodeData.config = {
                agent_name: agentName,
                input_mapping: {},
                output_key: agentName + '_output'
            };
            break;
    }
    
    const nodeElement = document.createElement('div');
    nodeElement.className = 'workflow-node';
    nodeElement.id = nodeId;
    nodeElement.style.left = x + 'px';
    nodeElement.style.top = y + 'px';
    nodeElement.innerHTML = `
        <div class="node-header ${headerClass}">
            <span>${icon}</span>
            <span class="node-title">${title}</span>
        </div>
        <div class="node-body">
            ${body}
        </div>
        <!-- 连接点 -->
        ${type !== 'output' ? '<div class="connection-point output" data-type="output"></div>' : ''}
        ${type !== 'input' ? '<div class="connection-point input" data-type="input"></div>' : ''}
    `;
    
    // 添加拖拽功能
    makeNodeDraggable(nodeElement);
    
    // 添加双击编辑
    nodeElement.addEventListener('dblclick', () => editNodeConfig(nodeId));
    
    // 添加连接点事件
    const outputPoint = nodeElement.querySelector('.connection-point.output');
    const inputPoint = nodeElement.querySelector('.connection-point.input');
    
    if (outputPoint) {
        outputPoint.addEventListener('click', (e) => {
            e.stopPropagation();
            startConnection(nodeId, 'output');
        });
    }
    
    if (inputPoint) {
        inputPoint.addEventListener('click', (e) => {
            e.stopPropagation();
            if (connectingFrom) {
                finishConnection(nodeId, 'input');
            }
        });
    }
    
    document.getElementById('canvas').appendChild(nodeElement);
    nodes.push(nodeData);
    
    // 保存历史记录（如果函数存在）
    if (typeof saveHistory === 'function') {
        setTimeout(() => saveHistory(), 100);
    }
    
    return nodeId;
}

// 使节点可拖拽
function makeNodeDraggable(element) {
    let isDragging = false;
    let currentX;
    let currentY;
    let initialX;
    let initialY;
    
    const header = element.querySelector('.node-header');
    
    header.addEventListener('mousedown', dragStart);
    
    function dragStart(e) {
        if (e.target.closest('.connection-point')) return;
        
        initialX = e.clientX - element.offsetLeft;
        initialY = e.clientY - element.offsetTop;
        
        isDragging = true;
        element.classList.add('dragging');
        
        document.addEventListener('mousemove', drag);
        document.addEventListener('mouseup', dragEnd);
    }
    
    function drag(e) {
        if (!isDragging) return;
        
        e.preventDefault();
        currentX = e.clientX - initialX;
        currentY = e.clientY - initialY;
        
        element.style.left = currentX + 'px';
        element.style.top = currentY + 'px';
        
        // 更新连线
        updateConnections();
    }
    
    function dragEnd() {
        if (!isDragging) return;
        
        isDragging = false;
        element.classList.remove('dragging');
        
        // 更新节点数据
        const node = nodes.find(n => n.id === element.id);
        if (node) {
            node.x = parseInt(element.style.left);
            node.y = parseInt(element.style.top);
        }
        
        document.removeEventListener('mousemove', drag);
        document.removeEventListener('mouseup', dragEnd);
    }
}

// 开始创建连接
function startConnection(nodeId, pointType) {
    if (connectingFrom) {
        // 取消之前的连接
        connectingFrom = null;
        updateConnections();
        return;
    }
    
    connectingFrom = { nodeId, pointType };
    console.log('开始连接从:', nodeId);
}

// 完成连接
function finishConnection(toNodeId, toPointType) {
    if (!connectingFrom) return;
    
    const fromNodeId = connectingFrom.nodeId;
    
    // 防止自己连接自己
    if (fromNodeId === toNodeId) {
        connectingFrom = null;
        return;
    }
    
    // 检查是否已存在连接
    const exists = connections.some(c => 
        c.from === fromNodeId && c.to === toNodeId
    );
    
    if (!exists) {
        connections.push({
            from: fromNodeId,
            to: toNodeId
        });
        console.log('创建连接:', fromNodeId, '->', toNodeId);
    }
    
    connectingFrom = null;
    updateConnections();
}

// 更新所有连线
function updateConnections() {
    const svg = document.getElementById('connections-svg');
    const svgRect = svg.getBoundingClientRect();
    
    // 清空现有连线
    svg.querySelectorAll('path').forEach(path => path.remove());
    
    // 绘制所有连线
    connections.forEach(conn => {
        const fromNode = document.getElementById(conn.from);
        const toNode = document.getElementById(conn.to);
        
        if (!fromNode || !toNode) return;
        
        const fromPoint = fromNode.querySelector('.connection-point.output');
        const toPoint = toNode.querySelector('.connection-point.input');
        
        if (!fromPoint || !toPoint) return;
        
        // 🔧 修复：使用SVG的边界框而不是canvas
        const fromRect = fromPoint.getBoundingClientRect();
        const toRect = toPoint.getBoundingClientRect();
        
        const x1 = fromRect.left + fromRect.width/2 - svgRect.left;
        const y1 = fromRect.top + fromRect.height/2 - svgRect.top;
        const x2 = toRect.left + toRect.width/2 - svgRect.left;
        const y2 = toRect.top + toRect.height/2 - svgRect.top;
        
        // 创建贝塞尔曲线路径
        const midX = (x1 + x2) / 2;
        const path = `M ${x1} ${y1} C ${midX} ${y1}, ${midX} ${y2}, ${x2} ${y2}`;
        
        const pathElement = document.createElementNS('http://www.w3.org/2000/svg', 'path');
        pathElement.setAttribute('d', path);
        pathElement.setAttribute('class', 'connection-line');
        pathElement.setAttribute('marker-end', 'url(#arrowhead)');
        pathElement.dataset.from = conn.from;
        pathElement.dataset.to = conn.to;
        
        // 点击连线删除
        pathElement.addEventListener('click', (e) => {
            e.stopPropagation();
            if (confirm('删除这条连接？')) {
                connections = connections.filter(c => 
                    !(c.from === conn.from && c.to === conn.to)
                );
                updateConnections();
            }
        });
        
        svg.appendChild(pathElement);
    });
}

// 编辑节点配置
// 🆕 打开右侧编辑面板
let editingNodeId = null;

function openNodeEditor() {
    if (contextMenuNode) {
        editingNodeId = contextMenuNode;
        const node = nodes.find(n => n.id === contextMenuNode);
        if (!node) return;
        
        // 构建编辑表单
        const content = document.getElementById('node-editor-content');
        content.innerHTML = `
            <div style="margin-bottom: 24px;">
                <label style="display: block; font-weight: 600; margin-bottom: 8px; color: #374151;">
                    节点类型
                </label>
                <div style="
                    background: #f3f4f6;
                    padding: 12px;
                    border-radius: 8px;
                    color: #6b7280;
                    font-size: 14px;
                ">${node.type === 'input' ? '📥 输入节点' : node.type === 'output' ? '📤 输出节点' : '🤖 Agent节点'}</div>
            </div>
            
            ${node.type === 'agent' ? `
                <div style="margin-bottom: 24px;">
                    <label style="display: block; font-weight: 600; margin-bottom: 8px; color: #374151;">
                        Agent名称
                    </label>
                    <input type="text" id="agent-name-input" value="${node.config.agent_name || ''}" style="
                        width: 100%;
                        padding: 10px 12px;
                        border: 2px solid #e5e7eb;
                        border-radius: 8px;
                        font-size: 14px;
                        outline: none;
                        transition: border-color 0.2s;
                    " onfocus="this.style.borderColor='#667eea'" onblur="this.style.borderColor='#e5e7eb'">
                </div>
                
                <div style="margin-bottom: 24px;">
                    <label style="display: block; font-weight: 600; margin-bottom: 8px; color: #374151;">
                        输入映射 (Input Mapping)
                        <span style="font-weight: 400; color: #9ca3af; font-size: 12px;">- 从上下文提取参数</span>
                    </label>
                    <div style="
                        background: #fef3c7;
                        border-left: 4px solid #f59e0b;
                        padding: 12px;
                        border-radius: 4px;
                        margin-bottom: 12px;
                        font-size: 13px;
                        color: #92400e;
                    ">
                        💡 格式: {"参数名": "$.input.变量名"}<br>
                        例如: {"destination": "$.input.destination"}
                    </div>
                    <textarea id="input-mapping-input" rows="6" style="
                        width: 100%;
                        padding: 12px;
                        border: 2px solid #e5e7eb;
                        border-radius: 8px;
                        font-size: 13px;
                        font-family: 'Courier New', monospace;
                        outline: none;
                        resize: vertical;
                    " onfocus="this.style.borderColor='#667eea'" onblur="this.style.borderColor='#e5e7eb'">${JSON.stringify(node.config.input_mapping || {}, null, 2)}</textarea>
                </div>
                
                <div style="margin-bottom: 24px;">
                    <label style="display: block; font-weight: 600; margin-bottom: 8px; color: #374151;">
                        输出键名 (Output Key)
                        <span style="font-weight: 400; color: #9ca3af; font-size: 12px;">- 存储到上下文的键名</span>
                    </label>
                    <input type="text" id="output-key-input" value="${node.config.output_key || ''}" placeholder="例如: weather_info" style="
                        width: 100%;
                        padding: 10px 12px;
                        border: 2px solid #e5e7eb;
                        border-radius: 8px;
                        font-size: 14px;
                        outline: none;
                    " onfocus="this.style.borderColor='#667eea'" onblur="this.style.borderColor='#e5e7eb'">
                </div>
            ` : ''}
            
            <div style="margin-bottom: 24px;">
                <label style="display: block; font-weight: 600; margin-bottom: 8px; color: #374151;">
                    完整配置 (JSON)
                    <span style="font-weight: 400; color: #9ca3af; font-size: 12px;">- 高级用户</span>
                </label>
                <textarea id="full-config-input" rows="10" style="
                    width: 100%;
                    padding: 12px;
                    border: 2px solid #e5e7eb;
                    border-radius: 8px;
                    font-size: 12px;
                    font-family: 'Courier New', monospace;
                    background: #f9fafb;
                    outline: none;
                    resize: vertical;
                " onfocus="this.style.borderColor='#667eea'" onblur="this.style.borderColor='#e5e7eb'">${JSON.stringify(node.config, null, 2)}</textarea>
            </div>
        `;
        
        // 显示面板（滑入动画）
        const panel = document.getElementById('node-editor-panel');
        panel.style.right = '0';
    }
    document.getElementById('context-menu').style.display = 'none';
}

function closeNodeEditor() {
    const panel = document.getElementById('node-editor-panel');
    panel.style.right = '-500px';
    editingNodeId = null;
}

function saveNodeConfig() {
    if (!editingNodeId) return;
    
    const node = nodes.find(n => n.id === editingNodeId);
    if (!node) return;
    
    try {
        if (node.type === 'agent') {
            // 从表单字段获取值
            const agentName = document.getElementById('agent-name-input').value;
            const inputMappingStr = document.getElementById('input-mapping-input').value;
            const outputKey = document.getElementById('output-key-input').value;
            
            const inputMapping = JSON.parse(inputMappingStr);
            
            node.config = {
                agent_name: agentName,
                input_mapping: inputMapping,
                output_key: outputKey
            };
        } else {
            // 使用完整JSON配置
            const fullConfigStr = document.getElementById('full-config-input').value;
            node.config = JSON.parse(fullConfigStr);
        }
        
        // 显示成功提示
        showToast('✅ 配置已保存！', 'success');
        closeNodeEditor();
        
        // 保存历史
        if (typeof saveHistory === 'function') {
            saveHistory();
        }
    } catch (e) {
        showToast('❌ JSON格式错误: ' + e.message, 'error');
    }
}

function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.style.cssText = `
        position: fixed;
        top: 80px;
        right: 20px;
        background: ${type === 'success' ? '#10b981' : type === 'error' ? '#ef4444' : '#3b82f6'};
        color: white;
        padding: 16px 24px;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
        z-index: 10000;
        font-size: 14px;
        font-weight: 500;
    `;
    toast.textContent = message;
    document.body.appendChild(toast);
    
    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateX(100px)';
        toast.style.transition = 'all 0.3s ease';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

function editNodeConfig(nodeId) {
    contextMenuNode = nodeId;
    openNodeEditor();
}

// 右键菜单
let contextMenuNode = null;

function handleContextMenu(e) {
    const node = e.target.closest('.workflow-node');
    if (!node) return;
    
    e.preventDefault();
    contextMenuNode = node.id;
    
    const menu = document.getElementById('context-menu');
    menu.style.left = e.pageX + 'px';
    menu.style.top = e.pageY + 'px';
    menu.style.display = 'block';
}

function editNode() {
    if (contextMenuNode) {
        editNodeConfig(contextMenuNode);
    }
    document.getElementById('context-menu').style.display = 'none';
}

function deleteNode() {
    if (contextMenuNode) {
        // 删除节点
        document.getElementById(contextMenuNode).remove();
        nodes = nodes.filter(n => n.id !== contextMenuNode);
        
        // 删除相关连接
        connections = connections.filter(c => 
            c.from !== contextMenuNode && c.to !== contextMenuNode
        );
        
        updateConnections();
        
        // 保存历史记录
        if (typeof saveHistory === 'function') {
            saveHistory();
        }
    }
    document.getElementById('context-menu').style.display = 'none';
}

// 清空画布（内部函数，不带确认）
function clearCanvasInternal() {
    document.querySelectorAll('.workflow-node').forEach(node => node.remove());
    nodes = [];
    connections = [];
    updateConnections();
    document.getElementById('empty-state').style.display = 'block';
}

// 清空画布（用户操作，带确认）
function clearCanvas() {
    if (!confirm('确定清空整个画布？')) return;
    clearCanvasInternal();
}

// 保存工作流
async function saveWorkflow() {
    if (nodes.length === 0) {
        alert('❌ 画布为空，无法保存！');
        return;
    }
    
    const workflowName = prompt('请输入工作流名称:', workflowId ? document.getElementById('workflow-title').textContent : '新建工作流');
    if (!workflowName) return;
    
    // 构建工作流定义
    const agentNodes = nodes.filter(n => n.type === 'agent');
    const agents = agentNodes.map(n => n.config.agent_name);
    
    // 根据连接关系构建sequence
    const sequence = [];
    
    // 从输入节点开始遍历
    const inputNode = nodes.find(n => n.type === 'input');
    if (!inputNode) {
        alert('❌ 缺少输入节点！');
        return;
    }
    
    // 简单的顺序构建（可以改进为拓扑排序）
    const visited = new Set();
    let currentNodeId = inputNode.id;
    
    while (currentNodeId) {
        visited.add(currentNodeId);
        
        const node = nodes.find(n => n.id === currentNodeId);
        if (node && node.type === 'agent') {
            sequence.push(node.config);
        }
        
        // 找到下一个节点
        const nextConn = connections.find(c => c.from === currentNodeId && !visited.has(c.to));
        currentNodeId = nextConn ? nextConn.to : null;
    }
    
    const workflowDefinition = {
        agents: agents,
        sequence: sequence,
        visual: {
            nodes: nodes,
            connections: connections
        }
    };
    
    try {
        let response;
        if (workflowId) {
            // 更新现有工作流
            response = await fetch(`/api/workflows/${workflowId}`, {
                method: 'PUT',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    name: workflowName,
                    workflow_definition: workflowDefinition
                })
            });
        } else {
            // 创建新工作流
            response = await fetch('/api/workflows', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    name: workflowName,
                    description: '通过可视化编辑器创建',
                    workflow_definition: workflowDefinition,
                    category: '自定义'
                })
            });
        }
        
        const result = await response.json();
        
        if (response.ok) {
            alert('✅ 工作流保存成功！');
            if (!workflowId && result.workflow_id) {
                workflowId = result.workflow_id;
                window.history.pushState({}, '', `?id=${workflowId}`);
            }
        } else {
            alert('❌ 保存失败：' + result.error);
        }
    } catch (error) {
        alert('❌ 保存失败：' + error.message);
    }
}

// 加载已有工作流
async function loadWorkflow() {
    const id = prompt('请输入工作流ID:');
    if (!id) return;
    
    await loadExistingWorkflow(id);
}

async function loadExistingWorkflow(id) {
    try {
        const response = await fetch(`/api/workflows/${id}`);
        const workflow = await response.json();
        
        if (!response.ok) {
            alert('❌ 加载失败：' + workflow.error);
            return;
        }
        
        // 更新标题
        document.getElementById('workflow-title').textContent = workflow.name;
        workflowId = id;
        
        // 解析定义
        let definition = workflow.workflow_definition;
        if (typeof definition === 'string') {
            definition = JSON.parse(definition);
        }
        
        // 清空画布（静默清空，不需要确认）
        clearCanvasInternal();
        
        // 恢复节点和连接
        if (definition.visual) {
            // 新格式：包含可视化信息
            definition.visual.nodes.forEach(nodeData => {
                const type = nodeData.type;
                const x = nodeData.x;
                const y = nodeData.y;
                const agentName = nodeData.config.agent_name;
                
                const nodeId = createNode(type, x, y, agentName);
                const node = nodes.find(n => n.id === nodeId);
                if (node) {
                    node.config = nodeData.config;
                }
            });
            
            connections = definition.visual.connections;
            updateConnections();
        } else {
            // 旧格式：自动布局
            alert('⚠️ 这是旧格式的工作流，将自动布局节点');
            autoLayoutWorkflow(definition);
        }
        
        document.getElementById('empty-state').style.display = 'none';
        
    } catch (error) {
        alert('❌ 加载失败：' + error.message);
    }
}

// 自动布局（旧格式工作流）
function autoLayoutWorkflow(definition) {
    // 简单的水平布局
    let x = 100;
    const y = 200;
    const spacing = 300;
    
    // 创建输入节点
    createNode('input', x, y);
    x += spacing;
    
    // 创建Agent节点
    if (definition.sequence) {
        definition.sequence.forEach((step, index) => {
            const agentName = step.agent_name || step.agent;
            const nodeId = createNode('agent', x, y, agentName);
            const node = nodes.find(n => n.id === nodeId);
            if (node) {
                node.config = step;
            }
            
            // 创建连接
            if (index === 0) {
                connections.push({ from: nodes[0].id, to: nodeId });
            } else {
                connections.push({ from: nodes[index].id, to: nodeId });
            }
            
            x += spacing;
        });
    }
    
    // 创建输出节点
    const outputId = createNode('output', x, y);
    if (nodes.length > 1) {
        connections.push({ from: nodes[nodes.length - 2].id, to: outputId });
    }
    
    updateConnections();
}

