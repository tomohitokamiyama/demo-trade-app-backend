package com.example.demo_trade_app;

import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;
import java.util.Optional;

public interface PositionRepository extends JpaRepository<Position, Long> {

    Optional<Position> findByUserIdAndSymbolAndPositionTypeAndStatus(
            Long userId,
            String symbol,
            PositionType positionType,
            PositionStatus status
    );

    List<Position> findByUserId(Long userId);

    List<Position> findByUserIdAndStatus(Long userId, PositionStatus status);
}