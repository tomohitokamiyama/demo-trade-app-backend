package com.example.demo_trade_app;

import jakarta.persistence.*;
import java.time.LocalDateTime;

@Entity
@Table(name = "signals")
public class Signal {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    private String symbol;

    @Enumerated(EnumType.STRING)
    private TradeType type;

    private int quantity;
    private double price;
    private String reason;

    @Enumerated(EnumType.STRING)
    private SignalStatus status;

    private LocalDateTime createdAt;
    private LocalDateTime executedAt;

    public Signal() {
    }

    public Signal(String symbol, TradeType type, int quantity, double price, String reason, SignalStatus status) {
        this.symbol = symbol;
        this.type = type;
        this.quantity = quantity;
        this.price = price;
        this.reason = reason;
        this.status = status;
    }

    @PrePersist
    public void prePersist() {
        if (this.createdAt == null) {
            this.createdAt = LocalDateTime.now();
        }
        if (this.status == null) {
            this.status = SignalStatus.NEW;
        }
    }

    public Long getId() {
        return id;
    }

    public String getSymbol() {
        return symbol;
    }

    public TradeType getType() {
        return type;
    }

    public int getQuantity() {
        return quantity;
    }

    public double getPrice() {
        return price;
    }

    public String getReason() {
        return reason;
    }

    public SignalStatus getStatus() {
        return status;
    }

    public LocalDateTime getCreatedAt() {
        return createdAt;
    }

    public LocalDateTime getExecutedAt() {
        return executedAt;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public void setSymbol(String symbol) {
        this.symbol = symbol;
    }

    public void setType(TradeType type) {
        this.type = type;
    }

    public void setQuantity(int quantity) {
        this.quantity = quantity;
    }

    public void setPrice(double price) {
        this.price = price;
    }

    public void setReason(String reason) {
        this.reason = reason;
    }

    public void setStatus(SignalStatus status) {
        this.status = status;
    }

    public void setCreatedAt(LocalDateTime createdAt) {
        this.createdAt = createdAt;
    }

    public void setExecutedAt(LocalDateTime executedAt) {
        this.executedAt = executedAt;
    }
}