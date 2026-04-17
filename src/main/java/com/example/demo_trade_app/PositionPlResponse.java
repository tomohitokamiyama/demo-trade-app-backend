package com.example.demo_trade_app;

import java.math.BigDecimal;

public class PositionPlResponse {

    private String symbol;
    private PositionType positionType;
    private int quantity;
    private double avgPrice;
    private BigDecimal currentPrice;
    private BigDecimal profitLoss;

    public PositionPlResponse() {
    }

    public PositionPlResponse(
            String symbol,
            PositionType positionType,
            int quantity,
            double avgPrice,
            BigDecimal currentPrice,
            BigDecimal profitLoss
    ) {
        this.symbol = symbol;
        this.positionType = positionType;
        this.quantity = quantity;
        this.avgPrice = avgPrice;
        this.currentPrice = currentPrice;
        this.profitLoss = profitLoss;
    }

    public String getSymbol() {
        return symbol;
    }

    public PositionType getPositionType() {
        return positionType;
    }

    public int getQuantity() {
        return quantity;
    }

    public double getAvgPrice() {
        return avgPrice;
    }

    public BigDecimal getCurrentPrice() {
        return currentPrice;
    }

    public BigDecimal getProfitLoss() {
        return profitLoss;
    }

    public void setSymbol(String symbol) {
        this.symbol = symbol;
    }

    public void setPositionType(PositionType positionType) {
        this.positionType = positionType;
    }

    public void setQuantity(int quantity) {
        this.quantity = quantity;
    }

    public void setAvgPrice(double avgPrice) {
        this.avgPrice = avgPrice;
    }

    public void setCurrentPrice(BigDecimal currentPrice) {
        this.currentPrice = currentPrice;
    }

    public void setProfitLoss(BigDecimal profitLoss) {
        this.profitLoss = profitLoss;
    }
}