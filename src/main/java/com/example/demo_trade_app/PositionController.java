package com.example.demo_trade_app;

import org.springframework.web.bind.annotation.CrossOrigin;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;

@CrossOrigin(origins = "http://localhost:5173")
@RestController
public class PositionController {

    private final PositionService positionService;

    public PositionController(PositionService positionService) {
        this.positionService = positionService;
    }

    @GetMapping("/positions")
    public List<Position> getPositions() {
        return positionService.getPositions(1L);
    }

    @GetMapping("/positions/pl")
    public List<PositionPlResponse> getPositionPl() {
        return positionService.getPositionPl(1L);
    }

    @GetMapping("/positions/pl/summary")
    public PositionPlSummaryResponse getPositionPlSummary() {
        return positionService.getPositionPlSummary(1L);
    }
}