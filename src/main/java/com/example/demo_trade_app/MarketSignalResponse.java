package com.example.demo_trade_app;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import java.util.List;
import java.util.Map;

@JsonIgnoreProperties(ignoreUnknown = true)
public class MarketSignalResponse {

    private String generatedAt;
    private List<Map<String, Object>> recommendedStocks;
    private List<Map<String, Object>> bullRecommendations;
    private List<Map<String, Object>> longTermUptrendRecommendations;
    private Map<String, Object> marketSignals;
    private Map<String, Object> failedSymbols;
    private Map<String, Object> selectionConfig;

    public String getGeneratedAt() {
        return generatedAt;
    }

    public void setGeneratedAt(String generatedAt) {
        this.generatedAt = generatedAt;
    }

    public List<Map<String, Object>> getRecommendedStocks() {
        return recommendedStocks;
    }

    public void setRecommendedStocks(List<Map<String, Object>> recommendedStocks) {
        this.recommendedStocks = recommendedStocks;
    }

    public List<Map<String, Object>> getBullRecommendations() {
        return bullRecommendations;
    }

    public void setBullRecommendations(List<Map<String, Object>> bullRecommendations) {
        this.bullRecommendations = bullRecommendations;
    }

    public List<Map<String, Object>> getLongTermUptrendRecommendations() {
        return longTermUptrendRecommendations;
    }

    public void setLongTermUptrendRecommendations(List<Map<String, Object>> longTermUptrendRecommendations) {
        this.longTermUptrendRecommendations = longTermUptrendRecommendations;
    }

    public Map<String, Object> getMarketSignals() {
        return marketSignals;
    }

    public void setMarketSignals(Map<String, Object> marketSignals) {
        this.marketSignals = marketSignals;
    }

    public Map<String, Object> getFailedSymbols() {
        return failedSymbols;
    }

    public void setFailedSymbols(Map<String, Object> failedSymbols) {
        this.failedSymbols = failedSymbols;
    }

    public Map<String, Object> getSelectionConfig() {
        return selectionConfig;
    }

    public void setSelectionConfig(Map<String, Object> selectionConfig) {
        this.selectionConfig = selectionConfig;
    }
}