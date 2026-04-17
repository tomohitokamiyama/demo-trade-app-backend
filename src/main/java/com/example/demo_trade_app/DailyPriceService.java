package com.example.demo_trade_app;

import org.springframework.stereotype.Service;

import java.util.List;

@Service
public class DailyPriceService {

    private final DailyPriceRepository dailyPriceRepository;

    public DailyPriceService(DailyPriceRepository dailyPriceRepository) {
        this.dailyPriceRepository = dailyPriceRepository;
    }

    public List<DailyPrice> getDailyPrices() {
        return dailyPriceRepository.findAll();
    }

    public List<DailyPrice> getDailyPricesBySymbol(String symbol) {
        return dailyPriceRepository.findBySymbolOrderByPriceDateDesc(symbol);
    }

    public DailyPrice getLatestPrice(String symbol) {
        return dailyPriceRepository.findTopBySymbolOrderByPriceDateDesc(symbol)
                .orElseThrow(() -> new IllegalArgumentException("DailyPrice not found: symbol=" + symbol));
    }
}