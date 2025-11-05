// ============================================================================
// 前端层 - JavaScript (Frontend - Main Script)
// Version: 2.0 - 2025-11-02 (修复执行结果显示)
// ============================================================================

// 加载统计数据
async function loadStats() {
    try {
        // 加载 Agent 数量
        const agentsResp = await fetch('/api/agents');
        if (agentsResp.ok) {
            const agents = await agentsResp.json();
            document.getElementById('agent-count').textContent = agents.length;
        }
        
        // 加载工作流数量
        const workflowsResp = await fetch('/api/workflows');
        if (workflowsResp.ok) {
            const workflows = await workflowsResp.json();
            document.getElementById('workflow-count').textContent = workflows.length;
            
            // 计算总执行次数和成功率
            let totalExec = workflows.reduce((sum, w) => sum + (w.total_executions || 0), 0);
            document.getElementById('execution-count').textContent = totalExec;
            
            if (workflows.length > 0 && totalExec > 0) {
                let avgSuccess = workflows.reduce((sum, w) => sum + (w.success_rate || 0), 0) / workflows.length;
                document.getElementById('success-rate').textContent = avgSuccess.toFixed(1) + '%';
            } else {
                document.getElementById('success-rate').textContent = '0%';
            }
        }
    } catch (error) {
        console.error('加载统计数据失败:', error);
    }
}

// 加载 Agent 列表
async function loadAgents() {
    try {
        const response = await fetch('/api/agents');
        if (!response.ok) throw new Error('加载失败');
        
        const agents = await response.json();
        const agentList = document.getElementById('agent-list');
        
        if (agents.length === 0) {
            agentList.innerHTML = `
                <div style="text-align: center; padding: 40px; color: #999;">
                    <div style="font-size: 3em; margin-bottom: 20px;">📭</div>
                    <div>暂无 Agent</div>
                    <div style="margin-top: 10px; font-size: 14px;">点击右上角「➕ 创建 Agent」按钮开始</div>
                </div>
            `;
        } else {
            agentList.innerHTML = agents.map(agent => `
                <div class="card">
                    <div class="card-title">${agent.icon || '📦'} ${agent.name}</div>
                    <div class="card-meta">${agent.description || '暂无描述'}</div>
                    <div style="margin: 10px 0;">
                        <span class="badge">${agent.agent_type}</span>
                        <span class="badge">${agent.category || '其他'}</span>
                    </div>
                    <div class="card-meta">
                        执行次数: ${agent.total_executions || 0} | 
                        成功率: ${(agent.success_rate || 0).toFixed(1)}%
                    </div>
                    <div style="margin-top: 15px;">
                        <button class="action-btn btn-delete" onclick="deleteAgent('${agent.name}')">🗑️ 删除</button>
                    </div>
                </div>
            `).join('');
        }
    } catch (error) {
        console.error('加载 Agent 失败:', error);
        document.getElementById('agent-list').innerHTML = `
            <div style="text-align: center; padding: 40px; color: #dc3545;">
                <div style="font-size: 3em; margin-bottom: 20px;">❌</div>
                <div>加载失败：${error.message}</div>
            </div>
        `;
    }
}

// 加载工作流列表
async function loadWorkflows() {
    try {
        const response = await fetch('/api/workflows');
        if (!response.ok) throw new Error('加载失败');
        
        const workflows = await response.json();
        const workflowList = document.getElementById('workflow-list');
        
        if (workflows.length === 0) {
            workflowList.innerHTML = `
                <div style="text-align: center; padding: 40px; color: #999;">
                    <div style="font-size: 3em; margin-bottom: 20px;">📭</div>
                    <div>暂无工作流</div>
                    <div style="margin-top: 10px; font-size: 14px;">点击右上角「➕ 创建工作流」按钮开始</div>
                </div>
            `;
        } else {
            workflowList.innerHTML = workflows.map(workflow => `
                <div class="card">
                    <div class="card-title">🔄 ${workflow.name}</div>
                    <div class="card-meta">${workflow.description || '暂无描述'}</div>
                    <div style="margin: 10px 0;">
                        <span class="badge">${workflow.category || '其他'}</span>
                        <span class="badge">${workflow.status || 'active'}</span>
                    </div>
                    <div class="card-meta">
                        执行: ${workflow.total_executions || 0} 次 | 
                        成功率: ${(workflow.success_rate || 0).toFixed(1)}%
                    </div>
                    <div style="margin-top: 15px;">
                        <button class="action-btn btn-execute" onclick="executeWorkflow(${workflow.id}, '${workflow.name}')">▶️ 执行</button>
                        <button class="action-btn" onclick="window.open('/workflow-editor?id=${workflow.id}', '_blank')" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white;">🎨 可视化编辑</button>
                        <button class="action-btn btn-delete" onclick="deleteWorkflow(${workflow.id}, '${workflow.name}')">🗑️ 删除</button>
                    </div>
                </div>
            `).join('');
        }
    } catch (error) {
        console.error('加载工作流失败:', error);
        document.getElementById('workflow-list').innerHTML = `
            <div style="text-align: center; padding: 40px; color: #dc3545;">
                <div style="font-size: 3em; margin-bottom: 20px;">❌</div>
                <div>加载失败：${error.message}</div>
            </div>
        `;
    }
}

// 加载日志列表
async function loadLogs() {
    try {
        const response = await fetch('/api/logs?limit=10');
        if (!response.ok) throw new Error('加载失败');
        
        const logs = await response.json();
        const logList = document.getElementById('log-list');
        
        if (logs.length === 0) {
            logList.innerHTML = `
                <div style="text-align: center; padding: 40px; color: #999;">
                    <div style="font-size: 3em; margin-bottom: 20px;">📭</div>
                    <div>暂无日志</div>
                </div>
            `;
        } else {
            logList.innerHTML = logs.map(log => `
                <div class="log-entry">
                    <div class="log-time">${log.timestamp || '未知时间'}</div>
                    <div><strong>${log.agent_name || log.workflow_name || 'System'}</strong>: ${log.message || '无消息'}</div>
                    ${log.time_spent ? `<div class="card-meta">耗时: ${log.time_spent.toFixed(3)}秒</div>` : ''}
                </div>
            `).join('');
        }
    } catch (error) {
        console.error('加载日志失败:', error);
        document.getElementById('log-list').innerHTML = `
            <div style="text-align: center; padding: 40px; color: #dc3545;">
                <div style="font-size: 3em; margin-bottom: 20px;">❌</div>
                <div>加载失败：${error.message}</div>
            </div>
        `;
    }
}

// ============================================================================
// 工作流执行功能
// ============================================================================

async function executeWorkflow(workflowId, workflowName) {
    try {
        // 确认执行
        const confirmed = confirm(`确定要执行工作流「${workflowName}」吗？`);
        if (!confirmed) return;
        
        console.log(`[执行工作流] ID: ${workflowId}, 名称: ${workflowName}`);
        
        // 发送执行请求
        const response = await fetch(`/api/workflows/${workflowId}/execute`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({})
        });
        
        const result = await response.json();
        console.log('[执行结果]', result);
        
        if (result.success) {
            // 格式化输出结果
            let outputText = '';
            if (result.output) {
                outputText = JSON.stringify(result.output, null, 2);
            }
            
            alert(`✅ 工作流执行成功！\n\n执行时间: ${result.execution_time.toFixed(3)}秒\n\n结果:\n${outputText}`);
            
            // 刷新数据
            loadData();
        } else {
            alert(`❌ 工作流执行失败！\n\n错误信息:\n${result.error}`);
        }
    } catch (error) {
        alert(`❌ 执行工作流时发生错误！\n\n${error.message}`);
        console.error('执行工作流失败:', error);
    }
}

// ============================================================================
// 删除功能
// ============================================================================

async function deleteAgent(agentName) {
    try {
        const confirmed = confirm(`确定要删除 Agent「${agentName}」吗？\n\n此操作不可撤销！`);
        if (!confirmed) return;
        
        const response = await fetch(`/api/agents/${encodeURIComponent(agentName)}`, {
            method: 'DELETE'
        });
        
        const result = await response.json();
        
        if (response.ok) {
            alert(`✅ Agent 删除成功！`);
            loadData();
        } else {
            alert(`❌ 删除失败！\n\n${result.error || '未知错误'}`);
        }
    } catch (error) {
        alert(`❌ 删除 Agent 时发生错误！\n\n${error.message}`);
        console.error('删除 Agent 失败:', error);
    }
}

async function deleteWorkflow(workflowId, workflowName) {
    try {
        const confirmed = confirm(`确定要删除工作流「${workflowName}」吗？\n\n此操作不可撤销！`);
        if (!confirmed) return;
        
        const response = await fetch(`/api/workflows/${workflowId}`, {
            method: 'DELETE'
        });
        
        const result = await response.json();
        
        if (response.ok) {
            alert(`✅ 工作流删除成功！`);
            loadData();
        } else {
            alert(`❌ 删除失败！\n\n${result.error || '未知错误'}`);
        }
    } catch (error) {
        alert(`❌ 删除工作流时发生错误！\n\n${error.message}`);
        console.error('删除工作流失败:', error);
    }
}

// ============================================================================
// 页面加载和刷新
// ============================================================================

async function loadData() {
    await loadStats();
    await loadAgents();
    await loadWorkflows();
    await loadLogs();
}

// 页面加载时执行
document.addEventListener('DOMContentLoaded', function() {
    console.log('[前端] 页面加载完成，开始加载数据...');
    loadData();
    
    // 每30秒自动刷新
    setInterval(loadData, 30000);
});

console.log('[前端] main.js 加载成功 - Version 2.0');
