package com.example.demo_trade_app;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;

@RestController
public class TradeController {

    private final TradeService tradeService;

    public TradeController(TradeService tradeService) {
        this.tradeService = tradeService;
    }

    @GetMapping("/trades")
    public List<Trade> getTrades() {
        return tradeService.getTrades();
    }

    @PostMapping("/trades")
    public Trade createTrade(@RequestBody TradeRequest request) {
        return tradeService.createTrade(request);
    }
}