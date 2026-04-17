package com.example.demo_trade_app;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;

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
}