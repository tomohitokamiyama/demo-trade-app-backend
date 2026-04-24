package com.example.demo_trade_app;

import org.springframework.stereotype.Service;
import tools.jackson.databind.json.JsonMapper;

import java.io.File;

@Service
public class MarketSignalService {

    private static final String SIGNAL_JSON_PATH =
            "/Users/kamiyamatomohito/Desktop/kabuka/signals_output.json";

    private final JsonMapper jsonMapper;

    public MarketSignalService(JsonMapper jsonMapper) {
        this.jsonMapper = jsonMapper;
    }

    public MarketSignalResponse getLatestMarketSignals() {
        try {
            File file = new File(SIGNAL_JSON_PATH);
            return jsonMapper.readValue(file, MarketSignalResponse.class);
        } catch (Exception e) {
            throw new RuntimeException("signals_output.json の読み込みに失敗しました", e);
        }
    }
}