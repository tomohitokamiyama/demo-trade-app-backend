package com.example.demo_trade_app;

import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;

@Service
public class SignalExecutionService {

    private final SignalRepository signalRepository;
    private final SignalService signalService;
    private final TradeService tradeService;

    public SignalExecutionService(
            SignalRepository signalRepository,
            SignalService signalService,
            TradeService tradeService
    ) {
        this.signalRepository = signalRepository;
        this.signalService = signalService;
        this.tradeService = tradeService;
    }

    @Transactional
    public Trade executeById(Long id) {
        Signal signal = signalRepository.findById(id)
                .orElseThrow(() -> new IllegalArgumentException("Signal not found: id=" + id));

        if (signal.getStatus() == SignalStatus.EXECUTED) {
            throw new IllegalArgumentException("このSignalはすでに実行済みです");
        }

        TradeRequest request = signalService.toTradeRequest(signal);
        Trade trade = tradeService.createTrade(request);

        signal.setStatus(SignalStatus.EXECUTED);
        signal.setExecutedAt(LocalDateTime.now());
        signalRepository.save(signal);

        return trade;
    }

    @Transactional
    public List<Trade> executeNewSignals() {
        List<Signal> signals = signalRepository.findByStatus(SignalStatus.NEW);
        List<Trade> result = new ArrayList<>();

        for (Signal signal : signals) {
            TradeRequest request = signalService.toTradeRequest(signal);
            Trade trade = tradeService.createTrade(request);

            signal.setStatus(SignalStatus.EXECUTED);
            signal.setExecutedAt(LocalDateTime.now());
            signalRepository.save(signal);

            result.add(trade);
        }

        return result;
    }
}