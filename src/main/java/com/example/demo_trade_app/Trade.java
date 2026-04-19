package com.example.demo_trade_app;

import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.EnumType;
import jakarta.persistence.Enumerated;

import java.time.LocalDate;

@Entity
public class Trade {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    private String symbol;

    @Enumerated(EnumType.STRING)
    private TradeType tradeType;

    private int quantity;
    private double price;
    private LocalDate tradeDate;

    @Enumerated(EnumType.STRING)
    private SignalType signalType;

    private String entryReason;

    public Trade() {
    }

    public Trade(
            String symbol,
            TradeType tradeType,
            int quantity,
            double price,
            LocalDate tradeDate,
            SignalType signalType,
            String entryReason
    ) {
        this.symbol = symbol;
        this.tradeType = tradeType;
        this.quantity = quantity;
        this.price = price;
        this.tradeDate = tradeDate;
        this.signalType = signalType;
        this.entryReason = entryReason;
    }

    public Long getId() {
        return id;
    }

    public String getSymbol() {
        return symbol;
    }

    public TradeType getTradeType() {
        return tradeType;
    }

    public int getQuantity() {
        return quantity;
    }

    public double getPrice() {
        return price;
    }

    public LocalDate getTradeDate() {
        return tradeDate;
    }

    public SignalType getSignalType() {
        return signalType;
    }

    public String getEntryReason() {
        return entryReason;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public void setSymbol(String symbol) {
        this.symbol = symbol;
    }

    public void setTradeType(TradeType tradeType) {
        this.tradeType = tradeType;
    }

    public void setQuantity(int quantity) {
        this.quantity = quantity;
    }

    public void setPrice(double price) {
        this.price = price;
    }

    public void setTradeDate(LocalDate tradeDate) {
        this.tradeDate = tradeDate;
    }

    public void setSignalType(SignalType signalType) {
        this.signalType = signalType;
    }

    public void setEntryReason(String entryReason) {
        this.entryReason = entryReason;
    }
}