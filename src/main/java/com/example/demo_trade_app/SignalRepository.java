package com.example.demo_trade_app;

import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;

public interface SignalRepository extends JpaRepository<Signal, Long> {
    List<Signal> findByStatus(SignalStatus status);
}