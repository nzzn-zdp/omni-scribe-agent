document.addEventListener('DOMContentLoaded', function() {
    loadPlatforms();
    loadPublishRecords();
    
    // 添加平台按钮
    document.getElementById('add-platform-btn').addEventListener('click', function() {
        document.getElementById('add-platform-modal').style.display = 'block';
    });
    
    // 刷新按钮
    document.getElementById('refresh-publish-btn').addEventListener('click', function() {
        loadPlatforms();
        loadPublishRecords();
    });
    
    // 标签切换
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            
            document.querySelectorAll('.publish-list').forEach(list => list.classList.remove('active'));
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
    
    // 添加平台表单提交
    document.getElementById('add-platform-form').addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const formData = new FormData(this);
        const data = {
            name: formData.get('name'),
            platform_type: formData.get('platform_type'),
            config: JSON.parse(formData.get('config'))
        };
        
        try {
            const response = await fetch('/api/publish/platforms/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            });
            
            if (response.ok) {
                showNotification('平台添加成功', 'success');
                document.getElementById('add-platform-modal').style.display = 'none';
                this.reset();
                loadPlatforms();
            } else {
                showNotification('添加失败', 'error');
            }
        } catch (error) {
            console.error('添加平台失败:', error);
            showNotification('添加失败', 'error');
        }
    });
    
    // 编辑平台表单提交
    document.getElementById('edit-platform-form').addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const formData = new FormData(this);
        const platformId = formData.get('id');
        const data = {
            name: formData.get('name'),
            platform_type: formData.get('platform_type'),
            config: JSON.parse(formData.get('config')),
            is_active: formData.get('is_active') === 'true'
        };
        
        try {
            const response = await fetch(`/api/publish/platforms/${platformId}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            });
            
            if (response.ok) {
                showNotification('平台更新成功', 'success');
                document.getElementById('edit-platform-modal').style.display = 'none';
                loadPlatforms();
            } else {
                showNotification('更新失败', 'error');
            }
        } catch (error) {
            console.error('更新平台失败:', error);
            showNotification('更新失败', 'error');
        }
    });
    
    // 发布内容表单提交
    document.getElementById('publish-content-form').addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const formData = new FormData(this);
        const draftId = formData.get('draft_id');
        const selectedPlatforms = [];
        
        document.querySelectorAll('#platforms-checkboxes input[type="checkbox"]:checked').forEach(checkbox => {
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
                document.getElementById('publish-content-modal').style.display = 'none';
                this.reset();
                loadPublishRecords();
            } else {
                showNotification('发布失败', 'error');
            }
        } catch (error) {
            console.error('发布内容失败:', error);
            showNotification('发布失败', 'error');
        }
    });
});

async function loadPlatforms() {
    try {
        const response = await fetch('/api/publish/platforms/');
        const platforms = await response.json();
        renderPlatforms(platforms);
        renderPlatformCheckboxes(platforms);
    } catch (error) {
        console.error('加载平台列表失败:', error);
    }
}

async function loadPublishRecords() {
    try {
        const response = await fetch('/api/publish/records/');
        const records = await response.json();
        renderPublishRecords(records);
    } catch (error) {
        console.error('加载发布记录失败:', error);
    }
}

function renderPlatforms(platforms) {
    const container = document.getElementById('platforms-list');
    container.innerHTML = '';
    
    if (platforms.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <h3>暂无平台配置</h3>
                <p>点击"添加平台"按钮添加第一个平台</p>
            </div>
        `;
        return;
    }
    
    platforms.forEach(platform => {
        const platformItem = document.createElement('div');
        platformItem.className = 'platform-item';
        platformItem.innerHTML = `
            <div class="platform-info">
                <h3>${platform.name}</h3>
                <p>类型: ${getPlatformTypeText(platform.platform_type)}</p>
                <p>状态: <span class="status-badge ${platform.is_active ? 'status-completed' : 'status-failed'}">${platform.is_active ? '活跃' : '停用'}</span></p>
            </div>
            <div class="platform-actions">
                <button class="btn btn-secondary" onclick="editPlatform(${platform.id})">编辑</button>
                <button class="btn btn-danger" onclick="deletePlatform(${platform.id})">删除</button>
            </div>
        `;
        container.appendChild(platformItem);
    });
}

function renderPlatformCheckboxes(platforms) {
    const container = document.getElementById('platforms-checkboxes');
    container.innerHTML = '';
    
    platforms.forEach(platform => {
        if (platform.is_active) {
            const checkboxItem = document.createElement('div');
            checkboxItem.className = 'checkbox-item';
            checkboxItem.innerHTML = `
                <input type="checkbox" id="platform-${platform.id}" value="${platform.id}">
                <label for="platform-${platform.id}">${platform.name}</label>
            `;
            container.appendChild(checkboxItem);
        }
    });
}

function renderPublishRecords(records) {
    const container = document.getElementById('records-list');
    container.innerHTML = '';
    
    if (records.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <h3>暂无发布记录</h3>
                <p>发布内容后将在这里显示记录</p>
            </div>
        `;
        return;
    }
    
    records.forEach(record => {
        const recordItem = document.createElement('div');
        recordItem.className = 'record-item';
        recordItem.innerHTML = `
            <div class="record-info">
                <h3>发布记录 #${record.id}</h3>
                <p>草稿ID: ${record.draft_id}</p>
                <p>平台ID: ${record.platform_id}</p>
                <p>状态: <span class="status-badge status-${record.status}">${getPublishStatusText(record.status)}</span></p>
                ${record.platform_url ? `<p>链接: <a href="${record.platform_url}" target="_blank">${record.platform_url}</a></p>` : ''}
                ${record.published_at ? `<p>发布时间: ${new Date(record.published_at).toLocaleString()}</p>` : ''}
            </div>
            <div class="record-actions">
                <button class="btn btn-secondary" onclick="viewRecordDetails(${record.id})">详情</button>
                ${record.platform_url ? `<a href="${record.platform_url}" target="_blank" class="btn btn-primary">查看</a>` : ''}
            </div>
        `;
        container.appendChild(recordItem);
    });
}

function getPlatformTypeText(type) {
    const typeMap = {
        'wechat': '微信公众号',
        'weibo': '微博',
        'zhihu': '知乎',
        'xiaohongshu': '小红书',
        'wordpress': 'WordPress'
    };
    return typeMap[type] || type;
}

function getPublishStatusText(status) {
    const statusMap = {
        'pending': '待发布',
        'publishing': '发布中',
        'published': '已发布',
        'failed': '失败'
    };
    return statusMap[status] || status;
}

async function editPlatform(platformId) {
    try {
        const response = await fetch(`/api/publish/platforms/${platformId}`);
        if (response.ok) {
            const platform = await response.json();
            
            // 填充编辑表单
            document.getElementById('edit-platform-id').value = platform.id;
            document.getElementById('edit-platform-name').value = platform.name;
            document.getElementById('edit-platform-type').value = platform.platform_type;
            document.getElementById('edit-platform-config').value = platform.config || '{}';
            document.getElementById('edit-platform-active').value = platform.is_active.toString();
            
            // 显示编辑模态框
            document.getElementById('edit-platform-modal').style.display = 'block';
        } else {
            showNotification('获取平台信息失败', 'error');
        }
    } catch (error) {
        console.error('获取平台信息失败:', error);
        showNotification('获取平台信息失败', 'error');
    }
}

async function deletePlatform(platformId) {
    if (!confirm('确定要删除这个平台配置吗？')) {
        return;
    }
    
    try {
        const response = await fetch(`/api/publish/platforms/${platformId}`, {
            method: 'DELETE'
        });
        
        if (response.ok) {
            showNotification('删除成功', 'success');
            loadPlatforms();
        } else {
            showNotification('删除失败', 'error');
        }
    } catch (error) {
        console.error('删除平台失败:', error);
        showNotification('删除失败', 'error');
    }
}

function viewRecordDetails(recordId) {
    // TODO: 实现查看详情功能
    showNotification('查看详情功能开发中', 'warning');
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