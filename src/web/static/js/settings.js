document.addEventListener('DOMContentLoaded', function() {
    loadConfigs('llm');
    
    // 初始化配置按钮
    document.getElementById('init-configs-btn').addEventListener('click', initConfigs);
    
    // 标签切换
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            loadConfigs(this.dataset.category);
        });
    });
});

async function loadConfigs(category) {
    try {
        const response = await fetch(`/api/admin/configs?category=${category}`);
        const configs = await response.json();
        renderConfigs(configs);
    } catch (error) {
        console.error('加载配置失败:', error);
    }
}

function renderConfigs(configs) {
    const container = document.getElementById('configs-list');
    container.innerHTML = '';
    
    configs.forEach(config => {
        const configItem = document.createElement('div');
        configItem.className = 'config-item';
        configItem.innerHTML = `
            <div class="config-header">
                <label for="config-${config.key}">${config.description || config.key}</label>
                <span class="config-key">${config.key}</span>
            </div>
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
            alert('配置已保存');
        } else {
            alert('保存失败');
        }
    } catch (error) {
        console.error('保存配置失败:', error);
        alert('保存失败');
    }
}

async function initConfigs() {
    try {
        const response = await fetch('/api/admin/configs/init', {
            method: 'POST'
        });
        
        if (response.ok) {
            const result = await response.json();
            alert(result.message);
            loadConfigs(document.querySelector('.tab-btn.active').dataset.category);
        } else {
            alert('初始化失败');
        }
    } catch (error) {
        console.error('初始化配置失败:', error);
        alert('初始化失败');
    }
}