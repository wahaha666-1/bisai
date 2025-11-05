/**
 * 工作流编辑器高级功能
 * 1. 撤销/重做
 * 2. 画布缩放/拖拽
 * 3. 自动布局（Dagre）
 * 4. 模板库
 */

// ============================================================================
// 1. 撤销/重做功能
// ============================================================================

function saveHistory() {
    const state = {
        nodes: JSON.parse(JSON.stringify(nodes)),
        connections: JSON.parse(JSON.stringify(connections)),
        nodeIdCounter: nodeIdCounter
    };
    
    // 删除当前索引之后的历史
    history = history.slice(0, historyIndex + 1);
    
    // 添加新状态
    history.push(state);
    
    // 限制历史记录数量
    if (history.length > MAX_HISTORY) {
        history.shift();
    } else {
        historyIndex++;
    }
    
    updateHistoryButtons();
}

function undo() {
    if (historyIndex <= 0) return;
    
    historyIndex--;
    restoreState(history[historyIndex]);
    updateHistoryButtons();
}

function redo() {
    if (historyIndex >= history.length - 1) return;
    
    historyIndex++;
    restoreState(history[historyIndex]);
    updateHistoryButtons();
}

function restoreState(state) {
    // 清空当前画布
    document.querySelectorAll('.workflow-node').forEach(node => node.remove());
    
    // 恢复状态
    nodes = JSON.parse(JSON.stringify(state.nodes));
    connections = JSON.parse(JSON.stringify(state.connections));
    nodeIdCounter = state.nodeIdCounter;
    
    // 重新创建节点
    nodes.forEach(nodeData => {
        const type = nodeData.type;
        const x = nodeData.x;
        const y = nodeData.y;
        const agentName = nodeData.config.agent_name;
        
        const nodeId = createNodeWithId(nodeData.id, type, x, y, agentName);
        const node = nodes.find(n => n.id === nodeId);
        if (node) {
            node.config = nodeData.config;
        }
    });
    
    updateConnections();
}

function updateHistoryButtons() {
    document.getElementById('undo-btn').disabled = historyIndex <= 0;
    document.getElementById('redo-btn').disabled = historyIndex >= history.length - 1;
}

// 修改createNode以支持指定ID
function createNodeWithId(id, type, x, y, agentName = null) {
    const nodeId = id;
    
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
        ${type !== 'output' ? '<div class="connection-point output" data-type="output"></div>' : ''}
        ${type !== 'input' ? '<div class="connection-point input" data-type="input"></div>' : ''}
    `;
    
    makeNodeDraggable(nodeElement);
    nodeElement.addEventListener('dblclick', () => editNodeConfig(nodeId));
    
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
    
    return nodeId;
}

// ============================================================================
// 2. 画布缩放和拖拽
// ============================================================================

function setupCanvasZoomPan() {
    const canvasContainer = document.getElementById('canvas-container');
    const canvas = document.getElementById('canvas');
    
    // 🔧 修复：鼠标滚轮缩放（监听容器而不是canvas）
    canvasContainer.addEventListener('wheel', (e) => {
        e.preventDefault();
        
        const delta = e.deltaY > 0 ? 0.9 : 1.1;
        const newScale = Math.min(Math.max(scale * delta, 0.1), 3);
        
        // 计算缩放中心点
        const rect = canvasContainer.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;
        
        translateX = x - (x - translateX) * (newScale / scale);
        translateY = y - (y - translateY) * (newScale / scale);
        
        scale = newScale;
        applyTransform();
    });
    
    // 🔧 修复：空格键 + 鼠标拖拽画布
    let spacePressed = false;
    
    document.addEventListener('keydown', (e) => {
        if (e.code === 'Space' && !spacePressed && e.target.tagName !== 'INPUT' && e.target.tagName !== 'TEXTAREA') {
            spacePressed = true;
            canvasContainer.style.cursor = 'grab';
            e.preventDefault();
        }
    });
    
    document.addEventListener('keyup', (e) => {
        if (e.code === 'Space') {
            spacePressed = false;
            canvasContainer.style.cursor = 'default';
            if (isPanning) {
                isPanning = false;
            }
        }
    });
    
    // 🔧 修复：空格+鼠标左键 或 鼠标中键拖拽
    canvasContainer.addEventListener('mousedown', (e) => {
        if ((spacePressed && e.button === 0) || e.button === 1) { // 空格+左键 或 中键
            isPanning = true;
            panStartX = e.clientX - translateX;
            panStartY = e.clientY - translateY;
            canvasContainer.style.cursor = 'grabbing';
            e.preventDefault();
        }
    });
    
    document.addEventListener('mousemove', (e) => {
        if (isPanning) {
            translateX = e.clientX - panStartX;
            translateY = e.clientY - panStartY;
            applyTransform();
            e.preventDefault();
        }
    });
    
    document.addEventListener('mouseup', (e) => {
        if (isPanning) {
            isPanning = false;
            canvasContainer.style.cursor = spacePressed ? 'grab' : 'default';
        }
    });
}

function applyTransform() {
    const canvas = document.getElementById('canvas');
    canvas.style.transform = `translate(${translateX}px, ${translateY}px) scale(${scale})`;
    canvas.style.transformOrigin = '0 0';
    
    // 🔧 修复：延迟更新连线，确保transform已应用
    requestAnimationFrame(() => {
        if (typeof updateConnections === 'function') {
            updateConnections();
        }
    });
}

function zoomIn() {
    scale = Math.min(scale * 1.2, 3);
    applyTransform();
}

function zoomOut() {
    scale = Math.max(scale * 0.8, 0.1);
    applyTransform();
}

function resetZoom() {
    scale = 1;
    translateX = 0;
    translateY = 0;
    applyTransform();
}

// ============================================================================
// 3. 自动布局（使用Dagre.js）
// ============================================================================

function autoLayout() {
    if (nodes.length === 0) {
        alert('❌ 画布为空，无法布局！');
        return;
    }
    
    if (typeof dagre === 'undefined') {
        alert('❌ Dagre库未加载，无法使用自动布局！');
        return;
    }
    
    // 创建Dagre图
    const g = new dagre.graphlib.Graph();
    g.setGraph({
        rankdir: 'LR',  // 从左到右
        nodesep: 100,   // 节点间距
        ranksep: 200    // 层级间距
    });
    g.setDefaultEdgeLabel(() => ({}));
    
    // 添加节点
    nodes.forEach(node => {
        g.setNode(node.id, { width: 200, height: 120 });
    });
    
    // 添加边
    connections.forEach(conn => {
        g.setEdge(conn.from, conn.to);
    });
    
    // 执行布局
    dagre.layout(g);
    
    // 应用布局结果
    g.nodes().forEach(nodeId => {
        const layoutNode = g.node(nodeId);
        const node = nodes.find(n => n.id === nodeId);
        if (node) {
            node.x = layoutNode.x;
            node.y = layoutNode.y;
            
            const element = document.getElementById(nodeId);
            if (element) {
                element.style.left = layoutNode.x + 'px';
                element.style.top = layoutNode.y + 'px';
            }
        }
    });
    
    updateConnections();
    saveHistory();
    
    alert('✅ 自动布局完成！');
}

// ============================================================================
// 4. 工作流模板库
// ============================================================================

const workflowTemplates = [
    {
        name: '🌍 旅游规划工作流',
        description: '从天气查询到行程规划的完整旅游助手',
        category: '生活服务',
        agents: ['weather_agent', 'attraction_agent', 'hotel_agent', 'itinerary_agent'],
        icon: '✈️'
    },
    {
        name: '📝 内容创作工作流',
        description: '大纲→撰写→优化→SEO的内容生产流程',
        category: '内容创作',
        agents: ['outline_agent', 'writing_agent', 'polish_agent', 'seo_agent'],
        icon: '✍️'
    },
    {
        name: '📊 数据分析工作流',
        description: '数据采集→清洗→分析→报告生成',
        category: '数据处理',
        agents: ['data_collector', 'data_cleaner', 'data_analyzer', 'report_generator'],
        icon: '📈'
    },
    {
        name: '🛒 电商决策工作流',
        description: '竞品分析→价格策略→营销方案→投放计划',
        category: '商业智能',
        agents: ['competitor_analyzer', 'pricing_strategist', 'marketing_planner', 'campaign_launcher'],
        icon: '🛍️'
    },
    {
        name: '🎯 简单顺序流',
        description: '基础的输入→Agent处理→输出流程',
        category: '基础模板',
        agents: ['processor_agent'],  // 至少一个agent
        icon: '→'
    }
];

function showTemplates() {
    const modal = document.getElementById('templates-modal');
    const grid = document.getElementById('templates-grid');
    
    grid.innerHTML = workflowTemplates.map((template, index) => `
        <div style="
            border: 2px solid #e5e7eb;
            border-radius: 12px;
            padding: 20px;
            cursor: pointer;
            transition: all 0.3s;
            background: white;
        " onmouseover="this.style.borderColor='#667eea'; this.style.boxShadow='0 4px 12px rgba(102,126,234,0.2)'" 
           onmouseout="this.style.borderColor='#e5e7eb'; this.style.boxShadow='none'"
           onclick="applyTemplate(${index})">
            <div style="font-size: 48px; text-align: center; margin-bottom: 16px;">${template.icon}</div>
            <h3 style="margin: 0 0 8px 0; font-size: 16px; color: #111827;">${template.name}</h3>
            <p style="margin: 0 0 12px 0; font-size: 13px; color: #6b7280;">${template.description}</p>
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <span style="
                    background: #f3f4f6;
                    color: #6b7280;
                    padding: 4px 12px;
                    border-radius: 12px;
                    font-size: 12px;
                ">${template.category}</span>
                <span style="color: #667eea; font-size: 13px; font-weight: 600;">使用模板 →</span>
            </div>
        </div>
    `).join('');
    
    modal.style.display = 'block';
}

function applyTemplate(templateIndex) {
    const template = workflowTemplates[templateIndex];
    
    if (nodes.length > 0) {
        if (!confirm('应用模板将清空当前画布，确定继续？')) {
            return;
        }
        clearCanvas();
    }
    
    document.getElementById('templates-modal').style.display = 'none';
    
    // 根据模板创建节点
    if (template.agents.length > 0) {
        // 使用自动布局创建
        let x = 100;
        const y = 200;
        const spacing = 300;
        
        // 输入节点
        const inputId = createNode('input', x, y);
        x += spacing;
        
        // Agent节点
        const agentIds = [];
        template.agents.forEach(agentName => {
            const nodeId = createNode('agent', x, y, agentName);
            agentIds.push(nodeId);
            x += spacing;
        });
        
        // 输出节点
        const outputId = createNode('output', x, y);
        
        // 创建连接
        connections.push({ from: inputId, to: agentIds[0] });
        for (let i = 0; i < agentIds.length - 1; i++) {
            connections.push({ from: agentIds[i], to: agentIds[i + 1] });
        }
        connections.push({ from: agentIds[agentIds.length - 1], to: outputId });
        
        updateConnections();
        
        // 应用自动布局
        setTimeout(() => autoLayout(), 100);
    } else {
        // 创建基础模板
        createNode('input', 200, 300);
        createNode('output', 800, 300);
    }
    
    saveHistory();
    document.getElementById('empty-state').style.display = 'none';
}

// 初始化高级功能
document.addEventListener('DOMContentLoaded', () => {
    setupCanvasZoomPan();
    
    // 保存初始状态
    setTimeout(() => saveHistory(), 500);
});

