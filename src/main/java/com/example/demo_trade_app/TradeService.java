package com.example.demo_trade_app;

import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

@Service
public class TradeService {

    private final TradeRepository tradeRepository;
    private final PositionService positionService;

    public TradeService(TradeRepository tradeRepository, PositionService positionService) {
        this.tradeRepository = tradeRepository;
        this.positionService = positionService;
    }

    public List<Trade> getTrades() {
        return tradeRepository.findAll();
    }

    @Transactional
    public Trade createTrade(TradeRequest request) {
        validateRequest(request);

        Trade trade = new Trade(
                request.getSymbol(),
                request.getTradeType(),
                request.getQuantity(),
                request.getPrice(),
                request.getTradeDate()
        );

        Trade savedTrade = tradeRepository.save(trade);
        positionService.updatePositionByTrade(savedTrade);

        return savedTrade;
    }

    private void validateRequest(TradeRequest request) {
        if (request.getSymbol() == null || request.getSymbol().isBlank()) {
            throw new IllegalArgumentException("symbol is required");
        }
        if (request.getTradeType() == null) {
            throw new IllegalArgumentException("tradeType is required");
        }
        if (request.getQuantity() <= 0) {
            throw new IllegalArgumentException("quantity must be greater than 0");
        }
        if (request.getPrice() <= 0) {
            throw new IllegalArgumentException("price must be greater than 0");
        }
        if (request.getTradeDate() == null) {
            throw new IllegalArgumentException("tradeDate is required");
        }
    }
}