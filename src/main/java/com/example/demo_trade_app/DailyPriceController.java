package com.example.demo_trade_app;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;

@RestController
public class DailyPriceController {

    private final DailyPriceService dailyPriceService;

    public DailyPriceController(DailyPriceService dailyPriceService) {
        this.dailyPriceService = dailyPriceService;
    }

    @GetMapping("/daily-prices")
    public List<DailyPrice> getDailyPrices(@RequestParam(required = false) String symbol) {
        if (symbol != null && !symbol.isBlank()) {
            return dailyPriceService.getDailyPricesBySymbol(symbol);
        }
        return dailyPriceService.getDailyPrices();
    }
}