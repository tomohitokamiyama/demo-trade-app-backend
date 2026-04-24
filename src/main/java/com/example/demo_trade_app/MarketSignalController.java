package com.example.demo_trade_app;

import com.example.demo_trade_app.MarketSignalResponse;
import com.example.demo_trade_app.MarketSignalService;
import org.springframework.web.bind.annotation.CrossOrigin;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@CrossOrigin(origins = "http://localhost:5173")
public class MarketSignalController {

    private final MarketSignalService marketSignalService;

    public MarketSignalController(MarketSignalService marketSignalService) {
        this.marketSignalService = marketSignalService;
    }

    @GetMapping("/market-signals/latest")
    public MarketSignalResponse getLatestMarketSignals() {
        return marketSignalService.getLatestMarketSignals();
    }
}