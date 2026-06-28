document.addEventListener('DOMContentLoaded', function() {
    loadHotspotSources();
    loadHotspots();
    
    // 添加热点源按钮
    document.getElementById('add-source-btn').addEventListener('click', function() {
        document.getElementById('add-source-modal').style.display = 'block';
    });
    
    // 刷新热点按钮
    document.getElementById('refresh-hotspots-btn').addEventListener('click', function() {
        loadHotspotSources();
        loadHotspots();
    });
    
    // 模态框关闭
    document.querySelectorAll('.modal-close').forEach(function(closeBtn) {
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
    
    // 添加热点源表单提交
    document.getElementById('add-source-form').addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const formData = new FormData(this);
        const data = {
            name: formData.get('name'),
            source_type: formData.get('source_type'),
            config: JSON.parse(formData.get('config'))
        };
        
        try {
            const response = await fetch('/api/hotspots/sources/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            });
            
            if (response.ok) {
                showNotification('热点源添加成功', 'success');
                document.getElementById('add-source-modal').style.display = 'none';
                this.reset();
                loadHotspotSources();
            } else {
                showNotification('添加失败', 'error');
            }
        } catch (error) {
            console.error('添加热点源失败:', error);
            showNotification('添加失败', 'error');
        }
    });
    
    // 编辑热点源表单提交
    document.getElementById('edit-source-form').addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const formData = new FormData(this);
        const sourceId = formData.get('id');
        const data = {
            name: formData.get('name'),
            source_type: formData.get('source_type'),
            config: JSON.parse(formData.get('config')),
            is_active: formData.get('is_active') === 'true'
        };
        
        try {
            const response = await fetch(`/api/hotspots/sources/${sourceId}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            });
            
            if (response.ok) {
                showNotification('热点源更新成功', 'success');
                document.getElementById('edit-source-modal').style.display = 'none';
                loadHotspotSources();
            } else {
                showNotification('更新失败', 'error');
            }
        } catch (error) {
            console.error('更新热点源失败:', error);
            showNotification('更新失败', 'error');
        }
    });
});

async function loadHotspotSources() {
    try {
        const response = await fetch('/api/hotspots/sources/');
        const sources = await response.json();
        renderHotspotSources(sources);
    } catch (error) {
        console.error('加载热点源失败:', error);
    }
}

async function loadHotspots() {
    try {
        const response = await fetch('/api/hotspots/');
        const hotspots = await response.json();
        renderHotspots(hotspots);
    } catch (error) {
        console.error('加载热点列表失败:', error);
    }
}

function renderHotspotSources(sources) {
    const container = document.getElementById('hotspot-sources-list');
    container.innerHTML = '';
    
    if (sources.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <h3>暂无热点源</h3>
                <p>点击"添加热点源"按钮添加第一个热点源</p>
            </div>
        `;
        return;
    }
    
    sources.forEach(source => {
        const sourceItem = document.createElement('div');
        sourceItem.className = 'source-item';
        sourceItem.innerHTML = `
            <div class="source-info">
                <h3>${source.name}</h3>
                <p>类型: ${source.source_type}</p>
                <p>状态: <span class="status-badge ${source.is_active ? 'status-completed' : 'status-failed'}">${source.is_active ? '活跃' : '停用'}</span></p>
            </div>
            <div class="source-actions">
                <button class="btn btn-secondary" onclick="editSource(${source.id})">编辑</button>
                <button class="btn btn-danger" onclick="deleteSource(${source.id})">删除</button>
            </div>
        `;
        container.appendChild(sourceItem);
    });
}

function renderHotspots(hotspots) {
    const container = document.getElementById('hotspots-list');
    container.innerHTML = '';
    
    if (hotspots.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <h3>暂无热点</h3>
                <p>系统将自动抓取热点内容</p>
            </div>
        `;
        return;
    }
    
    hotspots.forEach(hotspot => {
        const hotspotItem = document.createElement('div');
        hotspotItem.className = 'hotspot-item';
        hotspotItem.innerHTML = `
            <div class="hotspot-info">
                <h3>${hotspot.title}</h3>
                <p>${hotspot.content ? hotspot.content.substring(0, 100) + '...' : '暂无内容'}</p>
                <div class="score">
                    <span class="score-label">热度:</span>
                    <span class="score-value">${hotspot.score || 0}</span>
                </div>
            </div>
            <div class="hotspot-actions">
                <button class="btn btn-primary" onclick="evaluateHotspot(${hotspot.id})">评估</button>
                <button class="btn btn-secondary" onclick="generateContent(${hotspot.id})">生成内容</button>
                ${hotspot.url ? `<a href="${hotspot.url}" target="_blank" class="btn btn-secondary">查看原文</a>` : ''}
            </div>
        `;
        container.appendChild(hotspotItem);
    });
}

async function evaluateHotspot(hotspotId) {
    try {
        const response = await fetch(`/api/hotspots/evaluate/${hotspotId}`, {
            method: 'POST'
        });
        
        if (response.ok) {
            showNotification('评估请求已提交', 'success');
        } else {
            showNotification('评估失败', 'error');
        }
    } catch (error) {
        console.error('评估热点失败:', error);
        showNotification('评估失败', 'error');
    }
}

async function generateContent(hotspotId) {
    try {
        const response = await fetch(`/api/content/generate/${hotspotId}`, {
            method: 'POST'
        });
        
        if (response.ok) {
            showNotification('内容生成请求已提交', 'success');
        } else {
            showNotification('生成失败', 'error');
        }
    } catch (error) {
        console.error('生成内容失败:', error);
        showNotification('生成失败', 'error');
    }
}

async function editSource(sourceId) {
    try {
        const response = await fetch(`/api/hotspots/sources/${sourceId}`);
        if (response.ok) {
            const source = await response.json();
            
            // 填充编辑表单
            document.getElementById('edit-source-id').value = source.id;
            document.getElementById('edit-source-name').value = source.name;
            document.getElementById('edit-source-type').value = source.source_type;
            document.getElementById('edit-source-config').value = source.config || '{}';
            document.getElementById('edit-source-active').value = source.is_active.toString();
            
            // 显示编辑模态框
            document.getElementById('edit-source-modal').style.display = 'block';
        } else {
            showNotification('获取热点源信息失败', 'error');
        }
    } catch (error) {
        console.error('获取热点源信息失败:', error);
        showNotification('获取热点源信息失败', 'error');
    }
}

async function deleteSource(sourceId) {
    if (!confirm('确定要删除这个热点源吗？')) {
        return;
    }
    
    try {
        const response = await fetch(`/api/hotspots/sources/${sourceId}`, {
            method: 'DELETE'
        });
        
        if (response.ok) {
            showNotification('删除成功', 'success');
            loadHotspotSources();
        } else {
            showNotification('删除失败', 'error');
        }
    } catch (error) {
        console.error('删除热点源失败:', error);
        showNotification('删除失败', 'error');
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