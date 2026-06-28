document.addEventListener('DOMContentLoaded', function() {
    loadContentTasks();
    loadContentDrafts();
    
    // 生成内容按钮
    document.getElementById('generate-content-btn').addEventListener('click', function() {
        document.getElementById('generate-content-modal').style.display = 'block';
    });
    
    // 刷新按钮
    document.getElementById('refresh-content-btn').addEventListener('click', function() {
        loadContentTasks();
        loadContentDrafts();
    });
    
    // 标签切换
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            
            document.querySelectorAll('.content-list').forEach(list => list.classList.remove('active'));
            document.getElementById(`${this.dataset.tab}-list`).classList.add('active');
        });
    });
    
    // 模态框关闭
    document.querySelectorAll('.modal-close').forEach(closeBtn => {
        closeBtn.addEventListener('click', function() {
            this.closest('.modal').style.display = 'none';
        });
    });
    
    // 点击模态框外部关闭
    window.addEventListener('click', function(event) {
        if (event.target.classList.contains('modal')) {
            event.target.style.display = 'none';
        }
    });
    
    // 生成内容表单提交
    document.getElementById('generate-content-form').addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const formData = new FormData(this);
        const hotspotId = formData.get('hotspot_id');
        
        try {
            const response = await fetch(`/api/content/generate/${hotspotId}`, {
                method: 'POST'
            });
            
            if (response.ok) {
                showNotification('内容生成请求已提交', 'success');
                document.getElementById('generate-content-modal').style.display = 'none';
                this.reset();
                loadContentTasks();
            } else {
                showNotification('生成失败', 'error');
            }
        } catch (error) {
            console.error('生成内容失败:', error);
            showNotification('生成失败', 'error');
        }
    });
    
    // 编辑草稿表单提交
    document.getElementById('edit-draft-form').addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const formData = new FormData(this);
        const draftId = formData.get('id');
        const data = {
            title: formData.get('title'),
            content: formData.get('content'),
            summary: formData.get('summary')
        };
        
        try {
            const response = await fetch(`/api/content/drafts/${draftId}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            });
            
            if (response.ok) {
                showNotification('草稿更新成功', 'success');
                document.getElementById('edit-draft-modal').style.display = 'none';
                loadContentDrafts();
            } else {
                showNotification('更新失败', 'error');
            }
        } catch (error) {
            console.error('更新草稿失败:', error);
            showNotification('更新失败', 'error');
        }
    });
    
    // 发布草稿表单提交
    document.getElementById('publish-draft-form').addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const formData = new FormData(this);
        const draftId = formData.get('draft_id');
        const selectedPlatforms = [];
        
        document.querySelectorAll('#publish-platforms-checkboxes input[type="checkbox"]:checked').forEach(checkbox => {
            selectedPlatforms.push(checkbox.value);
        });
        
        if (selectedPlatforms.length === 0) {
            showNotification('请选择至少一个平台', 'warning');
            return;
        }
        
        try {
            const response = await fetch(`/api/publish/publish/${draftId}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(selectedPlatforms)
            });
            
            if (response.ok) {
                showNotification('发布请求已提交', 'success');
                document.getElementById('publish-draft-modal').style.display = 'none';
            } else {
                showNotification('发布失败', 'error');
            }
        } catch (error) {
            console.error('发布草稿失败:', error);
            showNotification('发布失败', 'error');
        }
    });
});

async function loadContentTasks() {
    try {
        const response = await fetch('/api/content/tasks/');
        const tasks = await response.json();
        renderContentTasks(tasks);
    } catch (error) {
        console.error('加载内容任务失败:', error);
    }
}

async function loadContentDrafts() {
    try {
        const response = await fetch('/api/content/drafts/');
        const drafts = await response.json();
        renderContentDrafts(drafts);
    } catch (error) {
        console.error('加载内容草稿失败:', error);
    }
}

function renderContentTasks(tasks) {
    const container = document.getElementById('tasks-list');
    container.innerHTML = '';
    
    if (tasks.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <h3>暂无内容任务</h3>
                <p>点击"生成新内容"按钮创建第一个任务</p>
            </div>
        `;
        return;
    }
    
    tasks.forEach(task => {
        const taskItem = document.createElement('div');
        taskItem.className = 'task-item';
        taskItem.innerHTML = `
            <div class="task-info">
                <h3>任务 #${task.id}</h3>
                <p>热点ID: ${task.hotspot_id}</p>
                <p>内容类型: ${task.content_type}</p>
                <p>创建时间: ${new Date(task.created_at).toLocaleString()}</p>
            </div>
            <div class="task-actions">
                <span class="status-badge status-${task.status}">${getStatusText(task.status)}</span>
                <button class="btn btn-primary" onclick="viewTaskDetails(${task.id})">查看详情</button>
            </div>
        `;
        container.appendChild(taskItem);
    });
}

function renderContentDrafts(drafts) {
    const container = document.getElementById('drafts-list');
    container.innerHTML = '';
    
    if (drafts.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <h3>暂无内容草稿</h3>
                <p>系统将自动生成内容草稿</p>
            </div>
        `;
        return;
    }
    
    drafts.forEach(draft => {
        const draftItem = document.createElement('div');
        draftItem.className = 'draft-item';
        draftItem.innerHTML = `
            <div class="draft-info">
                <h3>${draft.title || '无标题'}</h3>
                <p>${draft.content || '暂无内容'}</p>
                <div class="scores">
                    <div class="score">
                        <span class="score-label">SEO:</span>
                        <span class="score-value">${draft.seo_score || 0}</span>
                    </div>
                    <div class="score">
                        <span class="score-label">可读性:</span>
                        <span class="score-value">${draft.readability_score || 0}</span>
                    </div>
                </div>
            </div>
            <div class="draft-actions">
                <button class="btn btn-primary" onclick="editDraft(${draft.id})">编辑</button>
                <button class="btn btn-success" onclick="publishDraft(${draft.id})">发布</button>
                <button class="btn btn-secondary" onclick="viewDraftDetails(${draft.id})">详情</button>
            </div>
        `;
        container.appendChild(draftItem);
    });
}

function getStatusText(status) {
    const statusMap = {
        'pending': '待处理',
        'processing': '处理中',
        'completed': '已完成',
        'failed': '失败'
    };
    return statusMap[status] || status;
}

async function viewTaskDetails(taskId) {
    try {
        const response = await fetch(`/api/content/tasks/${taskId}`);
        if (response.ok) {
            const task = await response.json();
            
            const content = `
                <div class="task-details">
                    <p><strong>任务ID:</strong> ${task.id}</p>
                    <p><strong>热点ID:</strong> ${task.hotspot_id}</p>
                    <p><strong>内容类型:</strong> ${task.content_type}</p>
                    <p><strong>状态:</strong> <span class="status-badge status-${task.status}">${getStatusText(task.status)}</span></p>
                    <p><strong>创建时间:</strong> ${new Date(task.created_at).toLocaleString()}</p>
                    ${task.updated_at ? `<p><strong>更新时间:</strong> ${new Date(task.updated_at).toLocaleString()}</p>` : ''}
                </div>
            `;
            
            document.getElementById('task-details-content').innerHTML = content;
            document.getElementById('task-details-modal').style.display = 'block';
        } else {
            showNotification('获取任务详情失败', 'error');
        }
    } catch (error) {
        console.error('获取任务详情失败:', error);
        showNotification('获取任务详情失败', 'error');
    }
}

async function editDraft(draftId) {
    try {
        const response = await fetch(`/api/content/drafts/${draftId}`);
        if (response.ok) {
            const draft = await response.json();
            
            // 填充编辑表单
            document.getElementById('edit-draft-id').value = draft.id;
            document.getElementById('edit-draft-title').value = draft.title || '';
            document.getElementById('edit-draft-content').value = draft.content || '';
            document.getElementById('edit-draft-summary').value = draft.summary || '';
            
            // 显示编辑模态框
            document.getElementById('edit-draft-modal').style.display = 'block';
        } else {
            showNotification('获取草稿信息失败', 'error');
        }
    } catch (error) {
        console.error('获取草稿信息失败:', error);
        showNotification('获取草稿信息失败', 'error');
    }
}

async function publishDraft(draftId) {
    try {
        // 加载平台列表
        const response = await fetch('/api/publish/platforms/');
        if (response.ok) {
            const platforms = await response.json();
            
            // 渲染平台复选框
            const container = document.getElementById('publish-platforms-checkboxes');
            container.innerHTML = '';
            
            platforms.forEach(platform => {
                if (platform.is_active) {
                    const checkboxItem = document.createElement('div');
                    checkboxItem.className = 'checkbox-item';
                    checkboxItem.innerHTML = `
                        <input type="checkbox" id="publish-platform-${platform.id}" value="${platform.id}">
                        <label for="publish-platform-${platform.id}">${platform.name}</label>
                    `;
                    container.appendChild(checkboxItem);
                }
            });
            
            // 设置草稿ID
            document.getElementById('publish-draft-id').value = draftId;
            
            // 显示发布模态框
            document.getElementById('publish-draft-modal').style.display = 'block';
        } else {
            showNotification('获取平台列表失败', 'error');
        }
    } catch (error) {
        console.error('获取平台列表失败:', error);
        showNotification('获取平台列表失败', 'error');
    }
}

async function viewDraftDetails(draftId) {
    try {
        const response = await fetch(`/api/content/drafts/${draftId}`);
        if (response.ok) {
            const draft = await response.json();
            
            const content = `
                <div class="draft-details">
                    <p><strong>草稿ID:</strong> ${draft.id}</p>
                    <p><strong>任务ID:</strong> ${draft.task_id}</p>
                    <p><strong>标题:</strong> ${draft.title || '无标题'}</p>
                    <p><strong>摘要:</strong> ${draft.summary || '无摘要'}</p>
                    <p><strong>SEO分数:</strong> ${draft.seo_score || 0}</p>
                    <p><strong>可读性分数:</strong> ${draft.readability_score || 0}</p>
                    <p><strong>创建时间:</strong> ${new Date(draft.created_at).toLocaleString()}</p>
                    <div class="draft-content-preview">
                        <h4>内容预览:</h4>
                        <div class="content-preview">${draft.content || '暂无内容'}</div>
                    </div>
                </div>
            `;
            
            document.getElementById('draft-details-content').innerHTML = content;
            document.getElementById('draft-details-modal').style.display = 'block';
        } else {
            showNotification('获取草稿详情失败', 'error');
        }
    } catch (error) {
        console.error('获取草稿详情失败:', error);
        showNotification('获取草稿详情失败', 'error');
    }
}

function showNotification(message, type = 'success') {
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.textContent = message;
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.remove();
    }, 3000);
}