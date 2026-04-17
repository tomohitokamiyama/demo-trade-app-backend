package com.example.demo_trade_app;

import org.springframework.stereotype.Service;

import java.util.ArrayList;
import java.util.List;

@Service
public class InstrumentService {

    public List<Instrument> getInstruments() {
        List<Instrument> list = new ArrayList<>();

        list.add(new Instrument("7203", "トヨタ自動車", "STOCK"));
        list.add(new Instrument("6758", "ソニーグループ", "STOCK"));
        list.add(new Instrument("^N225", "日経平均株価", "INDEX"));
        list.add(new Instrument("N225MINI", "日経225先物mini", "FUTURES"));

        return list;
    }
}