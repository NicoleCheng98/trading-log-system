/**
 * 风险管理计算器
 * 用于计算交易的风险管理相关指标
 */

document.addEventListener('DOMContentLoaded', function() {
    // 获取相关输入元素
    const accountSizeInput = document.getElementById('account_size');
    const riskPercentageInput = document.getElementById('risk_percentage');
    const initialRiskInput = document.getElementById('initial_risk');
    const positionSizeInput = document.getElementById('position_size');
    const entryPriceInput = document.getElementById('entry_price');
    const stopLossInput = document.getElementById('stop_loss');
    const profitLossInput = document.getElementById('profit_loss');
    const rMultipleInput = document.getElementById('r_multiple');

    // 计算初始风险金额
    function calculateInitialRisk() {
        if (accountSizeInput && riskPercentageInput && initialRiskInput) {
            const accountSize = parseFloat(accountSizeInput.value) || 0;
            const riskPercentage = parseFloat(riskPercentageInput.value) || 0;
            
            if (accountSize > 0 && riskPercentage > 0) {
                const initialRisk = (accountSize * riskPercentage / 100).toFixed(2);
                initialRiskInput.value = initialRisk;
                
                // 触发仓位大小计算
                calculatePositionSize();
            }
        }
    }

    // 计算仓位大小
    function calculatePositionSize() {
        if (initialRiskInput && entryPriceInput && stopLossInput && positionSizeInput) {
            const initialRisk = parseFloat(initialRiskInput.value) || 0;
            const entryPrice = parseFloat(entryPriceInput.value) || 0;
            const stopLoss = parseFloat(stopLossInput.value) || 0;
            
            if (initialRisk > 0 && entryPrice > 0 && stopLoss > 0 && entryPrice !== stopLoss) {
                // 计算每单位的风险
                const riskPerUnit = Math.abs(entryPrice - stopLoss);
                // 计算可以购买的单位数量
                const units = (initialRisk / riskPerUnit).toFixed(4);
                positionSizeInput.value = units;
            }
        }
    }

    // 计算R倍数
    function calculateRMultiple() {
        if (profitLossInput && initialRiskInput && rMultipleInput) {
            const profitLoss = parseFloat(profitLossInput.value) || 0;
            const initialRisk = parseFloat(initialRiskInput.value) || 0;
            
            if (initialRisk > 0) {
                const rMultiple = (profitLoss / initialRisk).toFixed(2);
                rMultipleInput.value = rMultiple;
            }
        }
    }

    // 添加事件监听器
    if (accountSizeInput && riskPercentageInput) {
        accountSizeInput.addEventListener('input', calculateInitialRisk);
        riskPercentageInput.addEventListener('input', calculateInitialRisk);
    }

    if (entryPriceInput && stopLossInput && initialRiskInput) {
        entryPriceInput.addEventListener('input', calculatePositionSize);
        stopLossInput.addEventListener('input', calculatePositionSize);
        initialRiskInput.addEventListener('input', calculatePositionSize);
    }

    if (profitLossInput && initialRiskInput) {
        profitLossInput.addEventListener('input', calculateRMultiple);
        initialRiskInput.addEventListener('input', calculateRMultiple);
    }

    // 初始计算（如果页面加载时已有值）
    if (accountSizeInput && riskPercentageInput) {
        calculateInitialRisk();
    }
    if (profitLossInput && initialRiskInput) {
        calculateRMultiple();
    }
});
