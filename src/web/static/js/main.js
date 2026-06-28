document.addEventListener('DOMContentLoaded', function() {
    loadDashboardData();
    
    // 添加刷新功能
    document.addEventListener('keydown', function(e) {
        if (e.key === 'r' && e.ctrlKey) {
            e.preventDefault();
            loadDashboardData();
        }
    });
});

async function loadDashboardData() {
    try {
        const response = await fetch('/api/admin/dashboard');
        const data = await response.json();
        
        // 更新统计卡片
        animateNumber('hotspot-sources-count', data.hotspot_sources);
        animateNumber('content-tasks-count', data.content_tasks.total);
        animateNumber('published-count', data.publish_records.published);
        
        // 添加系统状态信息
        updateSystemStatus();
        
    } catch (error) {
        console.error('加载仪表盘数据失败:', error);
        showNotification('加载仪表盘数据失败', 'error');
    }
}

function animateNumber(elementId, targetNumber) {
    const element = document.getElementById(elementId);
    if (!element) return;
    
    const currentNumber = parseInt(element.textContent) || 0;
    const duration = 1000;
    const startTime = performance.now();
    
    function updateNumber(currentTime) {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);
        
        // 使用缓动函数
        const easeOutQuart = 1 - Math.pow(1 - progress, 4);
        const current = Math.round(currentNumber + (targetNumber - currentNumber) * easeOutQuart);
        
        element.textContent = current;
        
        if (progress < 1) {
            requestAnimationFrame(updateNumber);
        }
    }
    
    requestAnimationFrame(updateNumber);
}

async function updateSystemStatus() {
    try {
        const response = await fetch('/api/admin/system/status');
        const status = await response.json();
        
        // 更新系统状态指示器
        const statusElements = document.querySelectorAll('.system-status');
        statusElements.forEach(element => {
            const service = element.dataset.service;
            if (status[service]) {
                element.className = `system-status status-${status[service]}`;
                element.title = `${service}: ${status[service]}`;
            }
        });
        
    } catch (error) {
        console.error('获取系统状态失败:', error);
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

// 添加快捷键提示
console.log('快捷键说明:');
console.log('Ctrl + R: 刷新仪表盘数据');