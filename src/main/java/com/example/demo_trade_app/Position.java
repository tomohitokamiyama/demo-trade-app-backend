package com.example.demo_trade_app;

import jakarta.persistence.*;
import java.time.LocalDateTime;

@Entity
@Table(name = "positions")
public class Position {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    private Long userId;
    private String symbol;

    @Enumerated(EnumType.STRING)
    private PositionType positionType;

    private int quantity;
    private double avgPrice;

    @Enumerated(EnumType.STRING)
    private PositionStatus status;

    private LocalDateTime openedAt;
    private LocalDateTime closedAt;
    private LocalDateTime createdAt;
    private LocalDateTime updatedAt;

    public Position() {
    }

    public Position(Long userId, String symbol, PositionType positionType, int quantity, double avgPrice,
                    PositionStatus status, LocalDateTime openedAt, LocalDateTime closedAt,
                    LocalDateTime createdAt, LocalDateTime updatedAt) {
        this.userId = userId;
        this.symbol = symbol;
        this.positionType = positionType;
        this.quantity = quantity;
        this.avgPrice = avgPrice;
        this.status = status;
        this.openedAt = openedAt;
        this.closedAt = closedAt;
        this.createdAt = createdAt;
        this.updatedAt = updatedAt;
    }

    @PrePersist
    public void prePersist() {
        LocalDateTime now = LocalDateTime.now();
        this.createdAt = now;
        this.updatedAt = now;
        if (this.openedAt == null) {
            this.openedAt = now;
        }
    }

    @PreUpdate
    public void preUpdate() {
        this.updatedAt = LocalDateTime.now();
    }

    public Long getId() {
        return id;
    }

    public Long getUserId() {
        return userId;
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

    public PositionStatus getStatus() {
        return status;
    }

    public LocalDateTime getOpenedAt() {
        return openedAt;
    }

    public LocalDateTime getClosedAt() {
        return closedAt;
    }

    public LocalDateTime getCreatedAt() {
        return createdAt;
    }

    public LocalDateTime getUpdatedAt() {
        return updatedAt;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public void setUserId(Long userId) {
        this.userId = userId;
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

    public void setStatus(PositionStatus status) {
        this.status = status;
    }

    public void setOpenedAt(LocalDateTime openedAt) {
        this.openedAt = openedAt;
    }

    public void setClosedAt(LocalDateTime closedAt) {
        this.closedAt = closedAt;
    }

    public void setCreatedAt(LocalDateTime createdAt) {
        this.createdAt = createdAt;
    }

    public void setUpdatedAt(LocalDateTime updatedAt) {
        this.updatedAt = updatedAt;
    }
}