package com.example.demo_trade_app;

import java.time.LocalDate;

public class TradeRequest {

    private String symbol;
    private TradeType tradeType;
    private int quantity;
    private double price;
    private LocalDate tradeDate;
    private SignalType signalType;
    private String entryReason;

    public TradeRequest() {
    }

    public String getSymbol() {
        return symbol;
    }

    public void setSymbol(String symbol) {
        this.symbol = symbol;
    }

    public TradeType getTradeType() {
        return tradeType;
    }

    public void setTradeType(TradeType tradeType) {
        this.tradeType = tradeType;
    }

    public int getQuantity() {
        return quantity;
    }

    public void setQuantity(int quantity) {
        this.quantity = quantity;
    }

    public double getPrice() {
        return price;
    }

    public void setPrice(double price) {
        this.price = price;
    }

    public LocalDate getTradeDate() {
        return tradeDate;
    }

    public void setTradeDate(LocalDate tradeDate) {
        this.tradeDate = tradeDate;
    }

    public SignalType getSignalType() {
        return signalType;
    }

    public void setSignalType(SignalType signalType) {
        this.signalType = signalType;
    }

    public String getEntryReason() {
        return entryReason;
    }

    public void setEntryReason(String entryReason) {
        this.entryReason = entryReason;
    }
}