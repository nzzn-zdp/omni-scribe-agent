document.addEventListener('DOMContentLoaded', function() {
    loadConfigs('llm');
    loadPlatformInfo();
    
    // 初始化配置按钮
    document.getElementById('init-configs-btn').addEventListener('click', initConfigs);
    
    // 标签切换
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            
            const category = this.dataset.category;
            if (category === 'platform') {
                loadPlatformConfigs();
            } else {
                loadConfigs(category);
            }
        });
    });
});

let platformInfoCache = {};

async function loadPlatformInfo() {
    try {
        const response = await fetch('/api/admin/platforms/info');
        if (response.ok) {
            platformInfoCache = await response.json();
        }
    } catch (error) {
        console.error('加载平台信息失败:', error);
    }
}

async function loadConfigs(category) {
    try {
        const response = await fetch(`/api/admin/configs?category=${category}`);
        const configs = await response.json();
        renderConfigs(configs);
    } catch (error) {
        console.error('加载配置失败:', error);
        showNotification('加载配置失败', 'error');
    }
}

async function loadPlatformConfigs() {
    try {
        const response = await fetch('/api/admin/configs?category=platform');
        const configs = await response.json();
        renderPlatformConfigs(configs);
    } catch (error) {
        console.error('加载平台配置失败:', error);
        showNotification('加载平台配置失败', 'error');
    }
}

function renderConfigs(configs) {
    const container = document.getElementById('configs-list');
    container.innerHTML = '';
    
    if (configs.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <h3>暂无配置项</h3>
                <p>点击"初始化默认配置"按钮添加配置</p>
            </div>
        `;
        return;
    }
    
    configs.forEach(config => {
        const configItem = document.createElement('div');
        configItem.className = 'config-item';
        configItem.innerHTML = `
            <div class="config-header">
                <label for="config-${config.key}">${config.description || config.key}</label>
                <span class="config-key">${config.key}</span>
            </div>
            ${config.help ? `<div class="config-help">${config.help}</div>` : ''}
            <div class="config-input">
                <input type="${config.is_sensitive ? 'password' : 'text'}" 
                       id="config-${config.key}" 
                       value="${config.value || ''}" 
                       data-key="${config.key}"
                       placeholder="请输入${config.description || config.key}">
                <button class="btn btn-save" onclick="saveConfig('${config.key}')">保存</button>
            </div>
        `;
        container.appendChild(configItem);
    });
}

function renderPlatformConfigs(configs) {
    const container = document.getElementById('configs-list');
    container.innerHTML = '';
    
    // 按平台分组
    const groupedConfigs = {};
    configs.forEach(config => {
        const platform = config.platform || 'other';
        if (!groupedConfigs[platform]) {
            groupedConfigs[platform] = [];
        }
        groupedConfigs[platform].push(config);
    });
    
    // 渲染每个平台的配置
    Object.keys(groupedConfigs).forEach(platformType => {
        const platformConfigs = groupedConfigs[platformType];
        const platformInfo = platformInfoCache[platformType] || { name: platformType, icon: '🔧', description: '' };
        
        const platformSection = document.createElement('div');
        platformSection.className = 'platform-section';
        platformSection.innerHTML = `
            <div class="platform-header">
                <div class="platform-title">
                    <span class="platform-icon">${platformInfo.icon}</span>
                    <h3>${platformInfo.name}</h3>
                </div>
                <p class="platform-description">${platformInfo.description}</p>
                ${platformInfo.docs_url ? `<a href="${platformInfo.docs_url}" target="_blank" class="platform-docs-link">查看文档 →</a>` : ''}
            </div>
            ${platformInfo.setup_steps ? `
                <div class="platform-setup-steps">
                    <h4>配置步骤：</h4>
                    <ol>
                        ${platformInfo.setup_steps.map(step => `<li>${step}</li>`).join('')}
                    </ol>
                </div>
            ` : ''}
            <div class="platform-configs">
                ${platformConfigs.map(config => `
                    <div class="config-item">
                        <div class="config-header">
                            <label for="config-${config.key}">${config.description || config.key}</label>
                            <span class="config-key">${config.key}</span>
                        </div>
                        ${config.help ? `<div class="config-help">${config.help}</div>` : ''}
                        <div class="config-input">
                            <input type="${config.is_sensitive ? 'password' : 'text'}" 
                                   id="config-${config.key}" 
                                   value="${config.value || ''}" 
                                   data-key="${config.key}"
                                   placeholder="请输入${config.description || config.key}">
                            <button class="btn btn-save" onclick="saveConfig('${config.key}')">保存</button>
                        </div>
                    </div>
                `).join('')}
            </div>
        `;
        container.appendChild(platformSection);
    });
}

async function saveConfig(key) {
    const input = document.getElementById(`config-${key}`);
    const value = input.value;
    
    try {
        const response = await fetch(`/api/admin/configs/${key}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ value })
        });
        
        if (response.ok) {
            showNotification('配置已保存', 'success');
        } else {
            showNotification('保存失败', 'error');
        }
    } catch (error) {
        console.error('保存配置失败:', error);
        showNotification('保存失败', 'error');
    }
}

async function initConfigs() {
    try {
        const response = await fetch('/api/admin/configs/init', {
            method: 'POST'
        });
        
        if (response.ok) {
            const result = await response.json();
            showNotification(result.message, 'success');
            const activeTab = document.querySelector('.tab-btn.active');
            const category = activeTab.dataset.category;
            if (category === 'platform') {
                loadPlatformConfigs();
            } else {
                loadConfigs(category);
            }
        } else {
            showNotification('初始化失败', 'error');
        }
    } catch (error) {
        console.error('初始化配置失败:', error);
        showNotification('初始化失败', 'error');
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