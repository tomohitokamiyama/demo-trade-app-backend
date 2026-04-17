package com.example.demo_trade_app;

import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;
import java.util.Optional;

public interface DailyPriceRepository extends JpaRepository<DailyPrice, Long> {

    List<DailyPrice> findBySymbolOrderByPriceDateDesc(String symbol);

    Optional<DailyPrice> findTopBySymbolOrderByPriceDateDesc(String symbol);
}