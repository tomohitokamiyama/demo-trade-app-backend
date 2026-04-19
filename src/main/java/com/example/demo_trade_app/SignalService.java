package com.example.demo_trade_app;

import org.springframework.stereotype.Service;

import java.time.LocalDate;
import java.util.List;

@Service
public class SignalService {

    private final SignalRepository signalRepository;

    public SignalService(SignalRepository signalRepository) {
        this.signalRepository = signalRepository;
    }

    public List<Signal> getSignals() {
        return signalRepository.findAll();
    }

    public List<Signal> getSignalsByStatus(SignalStatus status) {
        return signalRepository.findByStatus(status);
    }

    public Signal createSignal(SignalCreateRequest request) {
        validateCreateRequest(request);

        Signal signal = new Signal();
        signal.setSymbol(request.getSymbol());
        signal.setType(request.getType());
        signal.setQuantity(request.getQuantity());
        signal.setPrice(request.getPrice());
        signal.setReason(request.getReason());
        signal.setStatus(SignalStatus.NEW);

        return signalRepository.save(signal);
    }

    public TradeRequest toTradeRequest(Signal signal) {
        TradeRequest request = new TradeRequest();
        request.setSymbol(signal.getSymbol());
        request.setTradeType(signal.getType());
        request.setQuantity(signal.getQuantity());
        request.setPrice(signal.getPrice());
        request.setTradeDate(java.time.LocalDate.now());

        request.setSignalType(SignalType.BULL);
        request.setEntryReason(signal.getReason());

        return request;
    }

    private void validateCreateRequest(SignalCreateRequest request) {
        if (request.getSymbol() == null || request.getSymbol().isBlank()) {
            throw new IllegalArgumentException("symbol is required");
        }
        if (request.getType() == null) {
            throw new IllegalArgumentException("type is required");
        }
        if (request.getQuantity() <= 0) {
            throw new IllegalArgumentException("quantity must be greater than 0");
        }
        if (request.getPrice() <= 0) {
            throw new IllegalArgumentException("price must be greater than 0");
        }
        if (request.getReason() == null || request.getReason().isBlank()) {
            throw new IllegalArgumentException("reason is required");
        }
    }
}