/**
 * 交易日志系统主JavaScript文件
 */

// 等待DOM加载完成
document.addEventListener('DOMContentLoaded', function() {
    // 初始化提示框
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // 自动隐藏提示消息
    const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });

    // 确认删除操作
    const deleteButtons = document.querySelectorAll('.delete-confirm');
    deleteButtons.forEach(function(button) {
        button.addEventListener('click', function(e) {
            if (!confirm('确定要删除这条记录吗？此操作不可撤销。')) {
                e.preventDefault();
            }
        });
    });

    // 表格排序功能
    const sortableHeaders = document.querySelectorAll('th[data-sort]');
    sortableHeaders.forEach(function(header) {
        header.addEventListener('click', function() {
            const sort = this.dataset.sort;
            const order = this.dataset.order === 'asc' ? 'desc' : 'asc';
            
            // 更新URL参数
            const url = new URL(window.location);
            url.searchParams.set('sort', sort);
            url.searchParams.set('order', order);
            window.location = url.toString();
        });
    });

    // 自动计算当前价格
    const symbolInput = document.getElementById('symbol');
    const currentPriceBtn = document.getElementById('fetch-current-price');
    
    if (currentPriceBtn && symbolInput) {
        currentPriceBtn.addEventListener('click', function() {
            const symbol = symbolInput.value.trim();
            if (!symbol) {
                alert('请先输入交易品种');
                return;
            }
            
            // 显示加载状态
            currentPriceBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> 获取中...';
            currentPriceBtn.disabled = true;
            
            // 这里应该是一个AJAX请求获取当前价格
            // 为了演示，我们使用setTimeout模拟
            setTimeout(function() {
                // 模拟获取到的价格
                const mockPrice = (Math.random() * 10000).toFixed(2);
                document.getElementById('price').value = mockPrice;
                
                // 恢复按钮状态
                currentPriceBtn.innerHTML = '<i class="fas fa-sync-alt me-1"></i>获取当前价格';
                currentPriceBtn.disabled = false;
                
                // 触发价格变更事件，以便更新盈亏比计算
                const event = new Event('change');
                document.getElementById('price').dispatchEvent(event);
            }, 1000);
        });
    }

    // 支撑阻力位可视化
    const priceDisplays = document.querySelectorAll('.price-visualization');
    priceDisplays.forEach(function(display) {
        renderPriceVisualization(display);
    });
});

/**
 * 渲染价格可视化图表
 * @param {HTMLElement} container - 容器元素
 */
function renderPriceVisualization(container) {
    if (!container) return;
    
    const currentPrice = parseFloat(container.dataset.currentPrice);
    const resistances = container.dataset.resistances.split(',').map(x => parseFloat(x.trim())).filter(x => !isNaN(x));
    const supports = container.dataset.supports.split(',').map(x => parseFloat(x.trim())).filter(x => !isNaN(x));
    
    // 创建Canvas元素
    const canvas = document.createElement('canvas');
    container.appendChild(canvas);
    
    const ctx = canvas.getContext('2d');
    const chart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: ['价格水平'],
            datasets: [
                {
                    label: '当前价格',
                    data: [currentPrice],
                    backgroundColor: 'rgba(52, 152, 219, 0.5)',
                    borderColor: 'rgba(52, 152, 219, 1)',
                    borderWidth: 2,
                    pointRadius: 6,
                    pointHoverRadius: 8
                },
                {
                    label: '阻力位',
                    data: resistances.map(() => 0), // Y轴位置由pointStyle和pointRadius决定
                    backgroundColor: 'rgba(231, 76, 60, 0.5)',
                    borderColor: 'rgba(231, 76, 60, 1)',
                    borderWidth: 2,
                    pointStyle: 'line',
                    pointRadius: 10,
                    pointHoverRadius: 12,
                    pointRotation: 90
                },
                {
                    label: '支撑位',
                    data: supports.map(() => 0), // Y轴位置由pointStyle和pointRadius决定
                    backgroundColor: 'rgba(46, 204, 113, 0.5)',
                    borderColor: 'rgba(46, 204, 113, 1)',
                    borderWidth: 2,
                    pointStyle: 'line',
                    pointRadius: 10,
                    pointHoverRadius: 12,
                    pointRotation: 90
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: false,
                    min: Math.min(...supports, currentPrice) * 0.98,
                    max: Math.max(...resistances, currentPrice) * 1.02
                }
            },
            plugins: {
                legend: {
                    position: 'bottom'
                }
            }
        }
    });
}

/**
 * 格式化日期时间
 * @param {Date} date - 日期对象
 * @returns {string} - 格式化后的日期字符串
 */
function formatDateTime(date) {
    if (!(date instanceof Date)) {
        date = new Date(date);
    }
    
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    const hours = String(date.getHours()).padStart(2, '0');
    const minutes = String(date.getMinutes()).padStart(2, '0');
    
    return `${year}-${month}-${day} ${hours}:${minutes}`;
}

/**
 * 格式化价格
 * @param {number} price - 价格
 * @param {number} decimals - 小数位数
 * @returns {string} - 格式化后的价格字符串
 */
function formatPrice(price, decimals = 2) {
    return parseFloat(price).toFixed(decimals);
}

/**
 * 计算盈亏比
 * @param {number} entryPrice - 入场价格
 * @param {number} stopLoss - 止损价格
 * @param {number} takeProfit - 止盈价格
 * @param {string} direction - 交易方向 (buy/sell)
 * @returns {number} - 盈亏比
 */
function calculateRiskRewardRatio(entryPrice, stopLoss, takeProfit, direction) {
    if (!entryPrice || !stopLoss || !takeProfit) return null;
    
    let risk, reward;
    
    if (direction === 'buy') {
        risk = entryPrice - stopLoss;
        reward = takeProfit - entryPrice;
    } else {
        risk = stopLoss - entryPrice;
        reward = entryPrice - takeProfit;
    }
    
    if (risk <= 0) return null;
    return (reward / risk).toFixed(2);
}
