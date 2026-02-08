# 购买统计 JavaScript 代码说明

## 📋 代码文件

已创建以下文件：
1. **`purchase_stats_js.js`** - 完整的 JavaScript 统计代码（独立文件）
2. **`purchase_stats.html`** - 已集成统计功能的页面
3. **`checkout.html`** - 已更新，会在购买时更新计数

## 🚀 使用方法

### 方法 1: 使用 localStorage（最简单，已集成）

当前 `purchase_stats.html` 已集成此方法，无需额外配置。

**工作原理：**
- 用户在 `checkout.html` 点击购买时，会：
  1. 发送 PostHog 事件
  2. 自动更新 localStorage 中的计数
- `purchase_stats.html` 页面加载时：
  1. 从 localStorage 读取计数
  2. 计算营收（计数 × $99）
  3. 自动显示在页面上
  4. 每 10 秒自动刷新

### 方法 2: 使用 PostHog API（需要 Personal API Key）

如果需要从 PostHog 服务器直接读取真实数据，需要：

1. **获取 PostHog Personal API Key：**
   - 登录 PostHog 后台
   - 进入 Settings → Personal API Keys
   - 创建新的 API Key

2. **在 `purchase_stats.html` 中使用：**

```javascript
// 替换页面中的 loadPurchaseStats() 调用
loadPurchaseStats({
    usePostHogAPI: true,
    postHogPersonalApiKey: 'your-personal-api-key-here',
    useInsights: true  // 使用 Insights API（推荐）
});
```

## 📊 核心 JavaScript 代码

### 完整代码（已集成到 purchase_stats.html）

```javascript
// ============================================
// 购买统计 JavaScript 代码
// ============================================
const UNIT_PRICE = 99.00;
const EVENT_NAME = 'purchase_intent_confirmed';

// 从 localStorage 读取统计数据
function loadStatsFromLocalStorage() {
    try {
        const storedCount = localStorage.getItem('purchase_intent_count');
        const count = storedCount ? parseInt(storedCount, 10) : 0;
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

// 更新页面显示
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

// 加载并显示统计数据
function loadPurchaseStats() {
    const stats = loadStatsFromLocalStorage();
    updateStatsDisplay(stats);
    return stats;
}

// 页面加载时自动加载统计数据
document.addEventListener('DOMContentLoaded', function() {
    loadPurchaseStats();
    
    // 每 10 秒自动刷新一次
    setInterval(loadPurchaseStats, 10000);
});
```

### checkout.html 中的更新代码

```javascript
// 在 handlePayment() 函数中添加：
// 2. 发送核心意向信号给 PostHog
posthog.capture('purchase_intent_confirmed', { 
    amount: 99,
    currency: 'USD',
    product: '2026 Season Alpha'
});

// 3. 更新 localStorage 中的购买计数（用于统计页面）
try {
    const currentCount = parseInt(localStorage.getItem('purchase_intent_count') || '0', 10);
    localStorage.setItem('purchase_intent_count', (currentCount + 1).toString());
    console.log('购买计数已更新:', currentCount + 1);
} catch (error) {
    console.error('更新 localStorage 失败:', error);
}
```

## 🎯 HTML 元素 ID

确保页面中有以下 ID 的元素：

- `purchase-count` - 显示购买数量
- `purchase-revenue` - 显示总营收
- `data-source` - 显示数据来源（可选）

## ✅ 测试步骤

1. **清除 localStorage（可选）：**
   ```javascript
   localStorage.removeItem('purchase_intent_count');
   ```

2. **访问 checkout.html 并完成购买：**
   - 每次购买后，计数会自动 +1

3. **访问 purchase_stats.html：**
   - 应该能看到最新的购买统计
   - 数据每 10 秒自动刷新

## 📝 注意事项

1. **localStorage 限制：**
   - 数据存储在浏览器本地
   - 清除浏览器数据会丢失统计
   - 不同浏览器/设备的数据不共享

2. **PostHog API：**
   - 需要 Personal API Key（不是 Project API Key）
   - 可能有 CORS 限制（需要后端代理）
   - 更适合生产环境使用

3. **自动刷新：**
   - 当前设置为每 10 秒刷新
   - 可在代码中修改 `setInterval(loadPurchaseStats, 10000)` 的间隔

## 🔧 自定义配置

```javascript
// 修改单价
const UNIT_PRICE = 99.00;  // 改为你的价格

// 修改事件名称
const EVENT_NAME = 'purchase_intent_confirmed';  // 改为你的事件名

// 修改刷新间隔（毫秒）
setInterval(loadPurchaseStats, 10000);  // 10秒 = 10000毫秒
```
