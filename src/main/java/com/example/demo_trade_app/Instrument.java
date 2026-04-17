package com.example.demo_trade_app;

public class Instrument {

    private String symbol;
    private String name;
    private String type;

    public Instrument(String symbol, String name, String type) {
        this.symbol = symbol;
        this.name = name;
        this.type = type;
    }

    public String getSymbol() {
        return symbol;
    }

    public String getName() {
        return name;
    }

    public String getType() {
        return type;
    }
}