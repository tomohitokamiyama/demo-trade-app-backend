package com.example.demo_trade_app;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/signals")
public class SignalController {

    private final SignalService signalService;
    private final SignalExecutionService signalExecutionService;

    public SignalController(
            SignalService signalService,
            SignalExecutionService signalExecutionService
    ) {
        this.signalService = signalService;
        this.signalExecutionService = signalExecutionService;
    }

    @GetMapping
    public List<Signal> getSignals(@RequestParam(required = false) SignalStatus status) {
        if (status != null) {
            return signalService.getSignalsByStatus(status);
        }
        return signalService.getSignals();
    }

    @PostMapping
    public Signal createSignal(@RequestBody SignalCreateRequest request) {
        return signalService.createSignal(request);
    }

    @PostMapping("/{id}/execute")
    public ResponseEntity<?> executeSignal(@PathVariable Long id) {
        try {
            Trade trade = signalExecutionService.executeById(id);
            return ResponseEntity.ok(trade);
        } catch (IllegalArgumentException e) {
            return ResponseEntity.badRequest().body(e.getMessage());
        }
    }

    @PostMapping("/execute")
    public List<Trade> executeSignals() {
        return signalExecutionService.executeNewSignals();
    }
}