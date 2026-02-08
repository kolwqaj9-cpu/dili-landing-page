// ============================================
// 购买统计 JavaScript 代码
// 从 PostHog 和 localStorage 读取购买数据
// ============================================

// 配置
const POSTHOG_PROJECT_API_KEY = 'phc_F9AHEWXMyYP8Z6K0LQzFv3de99UPGZ2c8C12PSQMzFt';
const POSTHOG_API_HOST = 'https://us.i.posthog.com';
const UNIT_PRICE = 99.00;
const EVENT_NAME = 'purchase_intent_confirmed';

// ============================================
// 方法 1: 从 localStorage 读取（推荐，简单快速）
// ============================================
function loadStatsFromLocalStorage() {
    try {
        // 从 localStorage 读取购买计数
        const storedCount = localStorage.getItem('purchase_intent_count');
        const count = storedCount ? parseInt(storedCount, 10) : 0;
        
        // 计算总营收
        const revenue = count * UNIT_PRICE;
        
        return {
            count: count,
            revenue: revenue,
            source: 'localStorage'
        };
    } catch (error) {
        console.error('读取 localStorage 失败:', error);
        return {
            count: 0,
            revenue: 0,
            source: 'localStorage',
            error: error.message
        };
    }
}

// ============================================
// 方法 2: 从 PostHog API 读取（需要 Personal API Key）
// ============================================
async function loadStatsFromPostHogAPI(personalApiKey) {
    if (!personalApiKey) {
        console.warn('需要 PostHog Personal API Key 才能使用 API 查询');
        return null;
    }
    
    try {
        // 查询最近 30 天的 purchase_intent_confirmed 事件
        const endDate = new Date().toISOString().split('T')[0];
        const startDate = new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0];
        
        const response = await fetch(`${POSTHOG_API_HOST}/api/projects/${POSTHOG_PROJECT_API_KEY}/events/?event=${EVENT_NAME}&after=${startDate}&before=${endDate}`, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${personalApiKey}`,
                'Content-Type': 'application/json'
            }
        });
        
        if (!response.ok) {
            throw new Error(`PostHog API 错误: ${response.status} ${response.statusText}`);
        }
        
        const data = await response.json();
        const count = data.results ? data.results.length : 0;
        const revenue = count * UNIT_PRICE;
        
        return {
            count: count,
            revenue: revenue,
            source: 'posthog_api',
            rawData: data
        };
    } catch (error) {
        console.error('PostHog API 查询失败:', error);
        return {
            count: 0,
            revenue: 0,
            source: 'posthog_api',
            error: error.message
        };
    }
}

// ============================================
// 方法 3: 使用 PostHog Insights API（推荐用于生产环境）
// ============================================
async function loadStatsFromPostHogInsights(personalApiKey) {
    if (!personalApiKey) {
        console.warn('需要 PostHog Personal API Key');
        return null;
    }
    
    try {
        // 使用 Insights API 查询事件总数
        const response = await fetch(`${POSTHOG_API_HOST}/api/projects/${POSTHOG_PROJECT_API_KEY}/insights/`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${personalApiKey}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                events: [{
                    id: EVENT_NAME,
                    name: EVENT_NAME,
                    type: 'events'
                }],
                date_from: '-30d',
                date_to: 'today',
                insight: 'TRENDS',
                interval: 'day'
            })
        });
        
        if (!response.ok) {
            throw new Error(`PostHog Insights API 错误: ${response.status}`);
        }
        
        const data = await response.json();
        
        // 计算总数
        let totalCount = 0;
        if (data.result && data.result.length > 0) {
            totalCount = data.result.reduce((sum, day) => sum + (day.count || 0), 0);
        }
        
        const revenue = totalCount * UNIT_PRICE;
        
        return {
            count: totalCount,
            revenue: revenue,
            source: 'posthog_insights',
            rawData: data
        };
    } catch (error) {
        console.error('PostHog Insights API 查询失败:', error);
        return {
            count: 0,
            revenue: 0,
            source: 'posthog_insights',
            error: error.message
        };
    }
}

// ============================================
// 更新页面显示
// ============================================
function updateStatsDisplay(stats) {
    if (!stats) {
        console.error('统计数据为空');
        return;
    }
    
    // 更新购买数量
    const countElement = document.getElementById('purchase-count');
    if (countElement) {
        countElement.textContent = stats.count || 0;
    }
    
    // 更新营收
    const revenueElement = document.getElementById('purchase-revenue');
    if (revenueElement) {
        const formattedRevenue = (stats.revenue || 0).toLocaleString('en-US', {
            style: 'currency',
            currency: 'USD',
            minimumFractionDigits: 0,
            maximumFractionDigits: 0
        });
        revenueElement.textContent = formattedRevenue;
    }
    
    // 显示数据来源
    const sourceElement = document.getElementById('data-source');
    if (sourceElement) {
        sourceElement.textContent = `数据来源: ${stats.source}`;
    }
    
    console.log('统计数据已更新:', stats);
}

// ============================================
// 主函数：加载并显示统计数据
// ============================================
async function loadPurchaseStats(options = {}) {
    const {
        usePostHogAPI = false,
        postHogPersonalApiKey = null,
        useInsights = false
    } = options;
    
    let stats = null;
    
    // 优先使用 PostHog API（如果提供了 API Key）
    if (usePostHogAPI && postHogPersonalApiKey) {
        if (useInsights) {
            stats = await loadStatsFromPostHogInsights(postHogPersonalApiKey);
        } else {
            stats = await loadStatsFromPostHogAPI(postHogPersonalApiKey);
        }
    }
    
    // 如果 API 失败或未使用，回退到 localStorage
    if (!stats || stats.error) {
        stats = loadStatsFromLocalStorage();
    }
    
    // 更新页面显示
    updateStatsDisplay(stats);
    
    return stats;
}

// ============================================
// 自动刷新（可选）
// ============================================
function startAutoRefresh(intervalSeconds = 30, options = {}) {
    // 立即加载一次
    loadPurchaseStats(options);
    
    // 设置定时刷新
    setInterval(() => {
        loadPurchaseStats(options);
    }, intervalSeconds * 1000);
}

// ============================================
// 导出函数（如果使用模块化）
// ============================================
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        loadPurchaseStats,
        loadStatsFromLocalStorage,
        loadStatsFromPostHogAPI,
        loadStatsFromPostHogInsights,
        updateStatsDisplay,
        startAutoRefresh
    };
}

// ============================================
// 使用示例：
// ============================================
/*
// 示例 1: 从 localStorage 读取（最简单）
loadPurchaseStats();

// 示例 2: 从 PostHog API 读取（需要 Personal API Key）
loadPurchaseStats({
    usePostHogAPI: true,
    postHogPersonalApiKey: 'your-personal-api-key-here'
});

// 示例 3: 使用 Insights API
loadPurchaseStats({
    usePostHogAPI: true,
    postHogPersonalApiKey: 'your-personal-api-key-here',
    useInsights: true
});

// 示例 4: 自动刷新（每 30 秒）
startAutoRefresh(30);
*/
