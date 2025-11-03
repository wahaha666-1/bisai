// ============================================================================
// 批量删除功能 - 适配实际HTML结构
// ============================================================================

let selectedAgents = new Set();
let selectedWorkflows = new Set();
let batchModeEnabled = false;

// 初始化批量操作
function initBatchOperations() {
    console.log('[批量删除] 正在初始化...');
    
    // 添加批量操作按钮
    addBatchButtons();
    
    // 监听列表变化，自动添加复选框
    observeListChanges();
    
    console.log('[批量删除] ✅ 初始化完成');
}

// 添加批量操作按钮
function addBatchButtons() {
    // Agent批量操作按钮
    const agentSection = document.querySelector('#agent-list')?.parentElement;
    if (agentSection && !document.getElementById('agent-batch-bar')) {
        const header = agentSection.querySelector('.section-header');
        if (header) {
            const batchBar = document.createElement('div');
            batchBar.id = 'agent-batch-bar';
            batchBar.style.cssText = 'margin: 10px 0; padding: 10px; background: #f8f9fa; border-radius: 8px; display: flex; gap: 10px; align-items: center;';
            batchBar.innerHTML = `
                <button onclick="toggleAgentBatchMode()" class="btn" style="background: #6c757d; color: white; padding: 8px 15px; border: none; border-radius: 5px; cursor: pointer;">
                    <span id="agent-batch-toggle-text">📋 批量管理</span>
                </button>
                <div id="agent-batch-actions" style="display: none; flex: 1; display: flex; gap: 10px; align-items: center;">
                    <button onclick="selectAllAgents()" style="padding: 6px 12px; background: #667eea; color: white; border: none; border-radius: 4px; cursor: pointer;">全选</button>
                    <button onclick="deselectAllAgents()" style="padding: 6px 12px; background: #94a3b8; color: white; border: none; border-radius: 4px; cursor: pointer;">取消</button>
                    <button onclick="batchDeleteAgents()" style="padding: 6px 12px; background: #ef4444; color: white; border: none; border-radius: 4px; cursor: pointer; font-weight: bold;">
                        🗑️ 批量删除 (<span id="agent-selected-count">0</span>)
                    </button>
                    <span style="color: #6c757d; font-size: 14px; margin-left: auto;">提示: 点击卡片选择，再次点击取消</span>
                </div>
            `;
            agentSection.insertBefore(batchBar, agentSection.querySelector('#agent-list'));
        }
    }
    
    // Workflow批量操作按钮
    const workflowSection = document.querySelector('#workflow-list')?.parentElement;
    if (workflowSection && !document.getElementById('workflow-batch-bar')) {
        const header = workflowSection.querySelector('.section-header');
        if (header) {
            const batchBar = document.createElement('div');
            batchBar.id = 'workflow-batch-bar';
            batchBar.style.cssText = 'margin: 10px 0; padding: 10px; background: #f8f9fa; border-radius: 8px; display: flex; gap: 10px; align-items: center;';
            batchBar.innerHTML = `
                <button onclick="toggleWorkflowBatchMode()" class="btn" style="background: #6c757d; color: white; padding: 8px 15px; border: none; border-radius: 5px; cursor: pointer;">
                    <span id="workflow-batch-toggle-text">📋 批量管理</span>
                </button>
                <div id="workflow-batch-actions" style="display: none; flex: 1; display: flex; gap: 10px; align-items: center;">
                    <button onclick="selectAllWorkflows()" style="padding: 6px 12px; background: #667eea; color: white; border: none; border-radius: 4px; cursor: pointer;">全选</button>
                    <button onclick="deselectAllWorkflows()" style="padding: 6px 12px; background: #94a3b8; color: white; border: none; border-radius: 4px; cursor: pointer;">取消</button>
                    <button onclick="batchDeleteWorkflows()" style="padding: 6px 12px; background: #ef4444; color: white; border: none; border-radius: 4px; cursor: pointer; font-weight: bold;">
                        🗑️ 批量删除 (<span id="workflow-selected-count">0</span>)
                    </button>
                    <span style="color: #6c757d; font-size: 14px; margin-left: auto;">提示: 点击卡片选择，再次点击取消</span>
                </div>
            `;
            workflowSection.insertBefore(batchBar, workflowSection.querySelector('#workflow-list'));
        }
    }
}

// 监听列表变化（移除自动调用，避免无限循环）
function observeListChanges() {
    // 暂时禁用自动监听，改为手动触发
    console.log('[批量删除] 列表监听已禁用，使用手动模式');
}

// 切换Agent批量模式（暴露到全局）
window.toggleAgentBatchMode = function toggleAgentBatchMode() {
    console.log('[批量删除] toggleAgentBatchMode 被调用');
    const actions = document.getElementById('agent-batch-actions');
    const toggleText = document.getElementById('agent-batch-toggle-text');
    
    if (!actions || !toggleText) {
        console.error('[批量删除] 找不到批量操作按钮元素');
        return;
    }
    
    if (actions.style.display === 'none' || !actions.style.display) {
        actions.style.display = 'flex';
        toggleText.textContent = '❌ 退出批量';
        console.log('[批量删除] 启用Agent批量模式');
        enableAgentBatchMode();
    } else {
        actions.style.display = 'none';
        toggleText.textContent = '📋 批量管理';
        console.log('[批量删除] 禁用Agent批量模式');
        disableAgentBatchMode();
    }
}

// 切换Workflow批量模式（暴露到全局）
window.toggleWorkflowBatchMode = function toggleWorkflowBatchMode() {
    const actions = document.getElementById('workflow-batch-actions');
    const toggleText = document.getElementById('workflow-batch-toggle-text');
    
    if (actions.style.display === 'none' || !actions.style.display) {
        actions.style.display = 'flex';
        toggleText.textContent = '❌ 退出批量';
        enableWorkflowBatchMode();
    } else {
        actions.style.display = 'none';
        toggleText.textContent = '📋 批量管理';
        disableWorkflowBatchMode();
    }
}

// 启用Agent批量模式
function enableAgentBatchMode() {
    const agentList = document.getElementById('agent-list');
    if (!agentList) {
        console.error('[批量删除] 找不到agent-list元素');
        return;
    }
    
    const cards = agentList.querySelectorAll('.card');
    console.log(`[批量删除] 找到 ${cards.length} 个Agent卡片`);
    
    let processedCount = 0;
    cards.forEach((card, index) => {
        // 如果已经处理过，跳过
        if (card.dataset.batchProcessed === 'true') {
            return;
        }
        
        const title = card.querySelector('.card-title')?.textContent || '';
        const agentName = title.replace(/^[^\s]+\s+/, '').trim(); // 移除emoji
        
        if (!agentName) {
            console.warn(`[批量删除] 卡片 ${index} 没有有效的agentName`);
            return;
        }
        
        processedCount++;
        
        // 添加data属性
        card.dataset.agentName = agentName;
        card.dataset.batchItem = 'agent';
        card.dataset.batchProcessed = 'true'; // 标记为已处理
        
        // 添加点击选择功能
        card.style.cursor = 'pointer';
        card.style.transition = 'all 0.3s';
        
        // 移除旧的点击事件
        const newCard = card.cloneNode(true);
        card.parentNode.replaceChild(newCard, card);
        
        // 添加新的点击事件
        newCard.addEventListener('click', function(e) {
            // 如果点击的是删除按钮，不触发选择
            if (e.target.closest('.btn-delete') || e.target.closest('button')) {
                return;
            }
            
            const isSelected = selectedAgents.has(agentName);
            
            if (isSelected) {
                selectedAgents.delete(agentName);
                this.style.border = '1px solid #dee2e6';
                this.style.backgroundColor = '';
            } else {
                selectedAgents.add(agentName);
                this.style.border = '2px solid #667eea';
                this.style.backgroundColor = '#f0f4ff';
            }
            
            updateAgentCount();
        });
        
        // 恢复选中状态
        if (selectedAgents.has(agentName)) {
            newCard.style.border = '2px solid #667eea';
            newCard.style.backgroundColor = '#f0f4ff';
        }
    });
    
    console.log(`[批量删除] Agent批量模式已启用，处理了 ${processedCount} 个卡片`);
}

// 启用Workflow批量模式
function enableWorkflowBatchMode() {
    const workflowList = document.getElementById('workflow-list');
    if (!workflowList) return;
    
    const cards = workflowList.querySelectorAll('.card');
    cards.forEach(card => {
        // 如果已经处理过，跳过
        if (card.dataset.batchProcessed === 'true') {
            return;
        }
        
        const title = card.querySelector('.card-title')?.textContent || '';
        const workflowId = extractWorkflowId(card);
        
        if (!workflowId) return;
        
        // 添加data属性
        card.dataset.workflowId = workflowId;
        card.dataset.batchItem = 'workflow';
        card.dataset.batchProcessed = 'true'; // 标记为已处理
        
        // 添加点击选择功能
        card.style.cursor = 'pointer';
        card.style.transition = 'all 0.3s';
        
        // 移除旧的点击事件
        const newCard = card.cloneNode(true);
        card.parentNode.replaceChild(newCard, card);
        
        // 添加新的点击事件
        newCard.addEventListener('click', function(e) {
            // 如果点击的是按钮，不触发选择
            if (e.target.closest('button')) return;
            
            const isSelected = selectedWorkflows.has(workflowId);
            
            if (isSelected) {
                selectedWorkflows.delete(workflowId);
                this.style.border = '1px solid #dee2e6';
                this.style.backgroundColor = '';
            } else {
                selectedWorkflows.add(workflowId);
                this.style.border = '2px solid #667eea';
                this.style.backgroundColor = '#f0f4ff';
            }
            
            updateWorkflowCount();
        });
        
        // 恢复选中状态
        if (selectedWorkflows.has(workflowId)) {
            newCard.style.border = '2px solid #667eea';
            newCard.style.backgroundColor = '#f0f4ff';
        }
    });
}

// 禁用批量模式
function disableAgentBatchMode() {
    selectedAgents.clear();
    updateAgentCount();
    const cards = document.querySelectorAll('#agent-list .card');
    cards.forEach(card => {
        card.style.cursor = '';
        card.style.border = '';
        card.style.backgroundColor = '';
        // 清除批量处理标记，允许下次重新处理
        delete card.dataset.batchProcessed;
    });
}

function disableWorkflowBatchMode() {
    selectedWorkflows.clear();
    updateWorkflowCount();
    const cards = document.querySelectorAll('#workflow-list .card');
    cards.forEach(card => {
        card.style.cursor = '';
        card.style.border = '';
        card.style.backgroundColor = '';
        // 清除批量处理标记
        delete card.dataset.batchProcessed;
    });
}

// 提取Workflow ID（从按钮的onclick属性中）
function extractWorkflowId(card) {
    const executeBtn = card.querySelector('button[onclick*="executeWorkflow"]');
    if (executeBtn) {
        const onclick = executeBtn.getAttribute('onclick');
        const match = onclick.match(/executeWorkflow\((\d+)/);
        return match ? match[1] : null;
    }
    return null;
}

// 更新选中数量
function updateAgentCount() {
    const countEl = document.getElementById('agent-selected-count');
    if (countEl) countEl.textContent = selectedAgents.size;
}

function updateWorkflowCount() {
    const countEl = document.getElementById('workflow-selected-count');
    if (countEl) countEl.textContent = selectedWorkflows.size;
}

// 全选/取消（暴露到全局）
window.selectAllAgents = function selectAllAgents() {
    console.log('[批量删除] selectAllAgents 被调用');
    
    const cards = document.querySelectorAll('#agent-list .card[data-agent-name]');
    console.log(`[批量删除] 找到 ${cards.length} 个带data-agent-name的卡片`);
    
    if (cards.length === 0) {
        alert('❌ 请先点击「批量管理」按钮进入批量模式');
        return;
    }
    
    cards.forEach(card => {
        const agentName = card.dataset.agentName;
        selectedAgents.add(agentName);
        card.style.border = '2px solid #667eea';
        card.style.backgroundColor = '#f0f4ff';
    });
    updateAgentCount();
    console.log(`[批量删除] 全选完成，已选中 ${selectedAgents.size} 个`);
}

window.deselectAllAgents = function deselectAllAgents() {
    const cards = document.querySelectorAll('#agent-list .card[data-agent-name]');
    cards.forEach(card => {
        card.style.border = '1px solid #dee2e6';
        card.style.backgroundColor = '';
    });
    selectedAgents.clear();
    updateAgentCount();
}

window.selectAllWorkflows = function selectAllWorkflows() {
    const cards = document.querySelectorAll('#workflow-list .card[data-workflow-id]');
    cards.forEach(card => {
        const workflowId = card.dataset.workflowId;
        selectedWorkflows.add(workflowId);
        card.style.border = '2px solid #667eea';
        card.style.backgroundColor = '#f0f4ff';
    });
    updateWorkflowCount();
}

window.deselectAllWorkflows = function deselectAllWorkflows() {
    const cards = document.querySelectorAll('#workflow-list .card[data-workflow-id]');
    cards.forEach(card => {
        card.style.border = '1px solid #dee2e6';
        card.style.backgroundColor = '';
    });
    selectedWorkflows.clear();
    updateWorkflowCount();
}

// 批量删除（暴露到全局）
window.batchDeleteAgents = async function batchDeleteAgents() {
    if (selectedAgents.size === 0) {
        alert('❌ 请先选择要删除的Agent');
        return;
    }
    
    if (!confirm(`⚠️ 确认删除 ${selectedAgents.size} 个Agent吗？\n\n此操作无法撤销！`)) {
        return;
    }
    
    try {
        const response = await fetch('/api/agents/batch-delete', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({agents: Array.from(selectedAgents)})
        });
        
        const result = await response.json();
        
        if (result.success) {
            alert(`✅ ${result.message}`);
            selectedAgents.clear();
            disableAgentBatchMode();
            toggleAgentBatchMode(); // 退出批量模式
            
            // 重新加载列表
            if (typeof loadAgents === 'function') {
                loadAgents();
            }
            if (typeof loadStats === 'function') {
                loadStats();
            }
        } else {
            alert('❌ 删除失败: ' + (result.error || '未知错误'));
        }
    } catch (error) {
        alert('❌ 网络错误: ' + error.message);
    }
}

window.batchDeleteWorkflows = async function batchDeleteWorkflows() {
    if (selectedWorkflows.size === 0) {
        alert('❌ 请先选择要删除的工作流');
        return;
    }
    
    if (!confirm(`⚠️ 确认删除 ${selectedWorkflows.size} 个工作流吗？\n\n此操作无法撤销！`)) {
        return;
    }
    
    try {
        const response = await fetch('/api/workflows/batch-delete', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({workflows: Array.from(selectedWorkflows)})
        });
        
        const result = await response.json();
        
        if (result.success) {
            alert(`✅ ${result.message}`);
            selectedWorkflows.clear();
            disableWorkflowBatchMode();
            toggleWorkflowBatchMode(); // 退出批量模式
            
            // 重新加载列表
            if (typeof loadWorkflows === 'function') {
                loadWorkflows();
            }
            if (typeof loadStats === 'function') {
                loadStats();
            }
        } else {
            alert('❌ 删除失败: ' + (result.error || '未知错误'));
        }
    } catch (error) {
        alert('❌ 网络错误: ' + error.message);
    }
}

// 页面加载时初始化
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        setTimeout(initBatchOperations, 1000);
    });
} else {
    setTimeout(initBatchOperations, 1000);
}

console.log('[批量删除] 脚本已加载');
