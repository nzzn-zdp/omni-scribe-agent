document.addEventListener('DOMContentLoaded', function() {
    loadDashboardData();
});

async function loadDashboardData() {
    try {
        const response = await fetch('/api/admin/dashboard');
        const data = await response.json();
        
        document.getElementById('hotspot-sources-count').textContent = data.hotspot_sources;
        document.getElementById('content-tasks-count').textContent = data.content_tasks.total;
        document.getElementById('published-count').textContent = data.publish_records.published;
    } catch (error) {
        console.error('加载仪表盘数据失败:', error);
    }
}