package com.example.demo_trade_app;

import java.math.BigDecimal;

public class PositionPlSummaryResponse {

    private BigDecimal totalProfitLoss;
    private int positionCount;

    public PositionPlSummaryResponse() {
    }

    public PositionPlSummaryResponse(BigDecimal totalProfitLoss, int positionCount) {
        this.totalProfitLoss = totalProfitLoss;
        this.positionCount = positionCount;
    }

    public BigDecimal getTotalProfitLoss() {
        return totalProfitLoss;
    }

    public void setTotalProfitLoss(BigDecimal totalProfitLoss) {
        this.totalProfitLoss = totalProfitLoss;
    }

    public int getPositionCount() {
        return positionCount;
    }

    public void setPositionCount(int positionCount) {
        this.positionCount = positionCount;
    }
}