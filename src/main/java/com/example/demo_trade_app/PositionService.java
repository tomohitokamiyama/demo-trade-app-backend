package com.example.demo_trade_app;

import org.springframework.stereotype.Service;

import java.math.BigDecimal;
import java.util.ArrayList;
import java.util.List;

@Service
public class PositionService {

    private static final Long DEMO_USER_ID = 1L;

    private final PositionRepository positionRepository;
    private final DailyPriceRepository dailyPriceRepository;

    public PositionService(PositionRepository positionRepository, DailyPriceRepository dailyPriceRepository) {
        this.positionRepository = positionRepository;
        this.dailyPriceRepository = dailyPriceRepository;
    }

    public List<Position> getPositions(Long userId) {
        return positionRepository.findByUserIdAndStatus(userId, PositionStatus.OPEN);
    }

    public List<PositionPlResponse> getPositionPl(Long userId) {
        List<Position> positions = positionRepository.findByUserIdAndStatus(userId, PositionStatus.OPEN);
        List<PositionPlResponse> result = new ArrayList<>();

        for (Position position : positions) {
        	DailyPrice latestPrice = dailyPriceRepository
        	        .findTopBySymbolOrderByPriceDateDesc(position.getSymbol())
        	        .orElse(null);

        	BigDecimal currentPrice;

        	if (latestPrice != null) {
        	    currentPrice = latestPrice.getClosePrice();
        	} else {
        	    currentPrice = BigDecimal.valueOf(position.getAvgPrice());
        	}
            BigDecimal avgPrice = BigDecimal.valueOf(position.getAvgPrice());
            BigDecimal quantity = BigDecimal.valueOf(position.getQuantity());

            BigDecimal profitLoss;

            if (position.getPositionType() == PositionType.LONG) {
                profitLoss = currentPrice.subtract(avgPrice).multiply(quantity);
            } else if (position.getPositionType() == PositionType.SHORT) {
                profitLoss = avgPrice.subtract(currentPrice).multiply(quantity);
            } else {
                throw new IllegalArgumentException("Unsupported positionType: " + position.getPositionType());
            }

            PositionPlResponse response = new PositionPlResponse(
                    position.getSymbol(),
                    position.getPositionType(),
                    position.getQuantity(),
                    position.getAvgPrice(),
                    currentPrice,
                    profitLoss
            );

            result.add(response);
        }

        return result;
    }
    
    public PositionPlSummaryResponse getPositionPlSummary(Long userId) {
        List<PositionPlResponse> positionPlList = getPositionPl(userId);

        BigDecimal totalProfitLoss = BigDecimal.ZERO;

        for (PositionPlResponse item : positionPlList) {
            totalProfitLoss = totalProfitLoss.add(item.getProfitLoss());
        }

        return new PositionPlSummaryResponse(totalProfitLoss, positionPlList.size());
    }

    public void updatePositionByTrade(Trade trade) {
        Long userId = DEMO_USER_ID;

        switch (trade.getTradeType()) {
            case BUY:
                handleBuy(userId, trade);
                break;
            case SELL:
                handleSell(userId, trade);
                break;
            case SHORT:
                handleShort(userId, trade);
                break;
            case COVER:
                handleCover(userId, trade);
                break;
            default:
                throw new IllegalArgumentException("未対応のtradeTypeです: " + trade.getTradeType());
        }
    }

    private void handleBuy(Long userId, Trade trade) {
        Position position = positionRepository
                .findByUserIdAndSymbolAndPositionTypeAndStatus(
                        userId,
                        trade.getSymbol(),
                        PositionType.LONG,
                        PositionStatus.OPEN
                )
                .orElse(null);

        if (position == null) {
            Position newPosition = new Position();
            newPosition.setUserId(userId);
            newPosition.setSymbol(trade.getSymbol());
            newPosition.setPositionType(PositionType.LONG);
            newPosition.setQuantity(trade.getQuantity());
            newPosition.setAvgPrice(trade.getPrice());
            newPosition.setStatus(PositionStatus.OPEN);

            positionRepository.save(newPosition);
            return;
        }

        int oldQty = position.getQuantity();
        int newQty = oldQty + trade.getQuantity();

        double newAvgPrice =
                ((position.getAvgPrice() * oldQty) + (trade.getPrice() * trade.getQuantity())) / newQty;

        position.setQuantity(newQty);
        position.setAvgPrice(newAvgPrice);

        positionRepository.save(position);
    }

    private void handleSell(Long userId, Trade trade) {
        Position position = positionRepository
                .findByUserIdAndSymbolAndPositionTypeAndStatus(
                        userId,
                        trade.getSymbol(),
                        PositionType.LONG,
                        PositionStatus.OPEN
                )
                .orElseThrow(() -> new IllegalArgumentException("売却対象のLONGポジションがありません"));

        if (position.getQuantity() < trade.getQuantity()) {
            throw new IllegalArgumentException("保有数量が足りません");
        }

        int newQty = position.getQuantity() - trade.getQuantity();
        position.setQuantity(newQty);

        if (newQty == 0) {
            position.setStatus(PositionStatus.CLOSED);
            position.setClosedAt(java.time.LocalDateTime.now());
        }

        positionRepository.save(position);
    }

    private void handleShort(Long userId, Trade trade) {
        Position position = positionRepository
                .findByUserIdAndSymbolAndPositionTypeAndStatus(
                        userId,
                        trade.getSymbol(),
                        PositionType.SHORT,
                        PositionStatus.OPEN
                )
                .orElse(null);

        if (position == null) {
            Position newPosition = new Position();
            newPosition.setUserId(userId);
            newPosition.setSymbol(trade.getSymbol());
            newPosition.setPositionType(PositionType.SHORT);
            newPosition.setQuantity(trade.getQuantity());
            newPosition.setAvgPrice(trade.getPrice());
            newPosition.setStatus(PositionStatus.OPEN);

            positionRepository.save(newPosition);
            return;
        }

        int oldQty = position.getQuantity();
        int newQty = oldQty + trade.getQuantity();

        double newAvgPrice =
                ((position.getAvgPrice() * oldQty) + (trade.getPrice() * trade.getQuantity())) / newQty;

        position.setQuantity(newQty);
        position.setAvgPrice(newAvgPrice);

        positionRepository.save(position);
    }

    private void handleCover(Long userId, Trade trade) {
        Position position = positionRepository
                .findByUserIdAndSymbolAndPositionTypeAndStatus(
                        userId,
                        trade.getSymbol(),
                        PositionType.SHORT,
                        PositionStatus.OPEN
                )
                .orElseThrow(() -> new IllegalArgumentException("買い戻し対象のSHORTポジションがありません"));

        if (position.getQuantity() < trade.getQuantity()) {
            throw new IllegalArgumentException("保有数量が足りません");
        }

        int newQty = position.getQuantity() - trade.getQuantity();
        position.setQuantity(newQty);

        if (newQty == 0) {
            position.setStatus(PositionStatus.CLOSED);
            position.setClosedAt(java.time.LocalDateTime.now());
        }

        positionRepository.save(position);
    }
}