import pandas as pd
import yfinance as yf
import time
import json
from pathlib import Path


# =========================
# 設定
# =========================
CSV_PATH = Path("/Users/kamiyamatomohito/Desktop/kabuka/jpx_nikkei_index_400_weight_jp.csv")
OUTPUT_PATH = Path("/Users/kamiyamatomohito/Desktop/kabuka/signals_output.json")

# まずは検証用に少なめでもOK
SLEEP_SECONDS = 2

# 下降 / ボックス判定用の対象
# 日経平均や先物のティッカーは環境によって試行が必要です。
# まずは ^N225 などで試す想定です。
MARKET_SYMBOLS = {
    "nikkei_index": "^N225",
}


# =========================
# 共通: データ取得
# =========================
def get_stock_data(symbol: str, period: str = "5y") -> pd.DataFrame:
    stock = yf.Ticker(symbol)
    hist = stock.history(period=period, auto_adjust=False)
    return hist


# =========================
# BULL: 5年高値更新おすすめ株
# =========================
def detect_bull_recommendation(stock_data: pd.DataFrame) -> dict:
    """
    条件:
    - 終値が 3000〜8000
    - 直近終値が、過去5年のそれ以前の終値最高値を更新
    """
    if stock_data.empty or "Close" not in stock_data.columns or len(stock_data) < 2:
        return {"isBull": False, "reason": "データ不足"}

    current_price = float(stock_data["Close"].iloc[-1])
    past_max_close = float(stock_data["Close"].iloc[:-1].max())

    in_price_range = 3000 <= current_price <= 8000
    is_new_high = current_price > past_max_close

    is_bull = in_price_range and is_new_high

    return {
        "isBull": is_bull,
        "reason": "5年高値更新" if is_bull else "条件未達",
        "currentPrice": round(current_price, 2),
        "pastMaxClose": round(past_max_close, 2),
    }


# =========================
# BOX: ボックス相場 + ブレイク警戒
# =========================
def detect_breakout_risk(stock_data: pd.DataFrame) -> dict:
    """
    最近の変動率が平常時より上がっていないかを見る
    """
    if stock_data.empty or "Close" not in stock_data.columns:
        return {
            "isBreakoutRisk": False,
            "reason": "価格データなし",
            "recentVol": None,
            "baseVol": None,
            "volRatio": None,
        }

    close_prices = stock_data["Close"]
    daily_move = close_prices.pct_change().abs().dropna()

    if len(daily_move) < 60:
        return {
            "isBreakoutRisk": False,
            "reason": "60日分の変動率データ不足",
            "recentVol": None,
            "baseVol": None,
            "volRatio": None,
        }

    recent_vol = float(daily_move.iloc[-5:].mean())
    base_vol = float(daily_move.iloc[-60:].mean())
    vol_ratio = recent_vol / base_vol if base_vol != 0 else 0.0

    is_breakout_risk = vol_ratio >= 1.5

    return {
        "isBreakoutRisk": is_breakout_risk,
        "reason": "最近の変動率が上昇" if is_breakout_risk else "最近の変動率は落ち着いている",
        "recentVol": round(recent_vol, 4),
        "baseVol": round(base_vol, 4),
        "volRatio": round(vol_ratio, 4),
    }


def detect_box_signal(stock_data: pd.DataFrame) -> dict:
    """
    条件:
    - 直近20日レンジ幅が 5% 以内
    - 直近60日レンジ幅が 12% 以内
    - 現在価格が20日レンジ中央から 2% 以内
    - 直近変動率の急拡大がない
    """
    if stock_data.empty or "Close" not in stock_data.columns:
        return {
            "isBox": False,
            "reason": "価格データなし",
            "range20": None,
            "range60": None,
            "midDiff20": None,
            "breakoutRisk": None,
        }

    if len(stock_data) < 60:
        return {
            "isBox": False,
            "reason": "60日分のデータ不足",
            "range20": None,
            "range60": None,
            "midDiff20": None,
            "breakoutRisk": None,
        }

    close_prices = stock_data["Close"]
    recent_20 = close_prices.iloc[-20:]
    recent_60 = close_prices.iloc[-60:]

    high20 = float(recent_20.max())
    low20 = float(recent_20.min())
    high60 = float(recent_60.max())
    low60 = float(recent_60.min())
    current_price = float(close_prices.iloc[-1])

    range20 = (high20 - low20) / low20
    range60 = (high60 - low60) / low60

    mid20 = (high20 + low20) / 2
    mid_diff20 = abs(current_price - mid20) / mid20

    breakout = detect_breakout_risk(stock_data)

    is_box_core = (
        range20 <= 0.05 and
        range60 <= 0.12 and
        mid_diff20 <= 0.02
    )

    is_box = is_box_core and (not breakout["isBreakoutRisk"])

    if is_box:
        reason = "狭いレンジかつ中央付近で、ブレイク警戒も低い"
    elif is_box_core:
        reason = "レンジ条件は満たすが、ブレイク警戒あり"
    else:
        reason = "ボックス条件未達"

    return {
        "isBox": is_box,
        "reason": reason,
        "range20": round(range20, 4),
        "range60": round(range60, 4),
        "midDiff20": round(mid_diff20, 4),
        "breakoutRisk": breakout,
    }


# =========================
# BEAR: 下降シグナル2パターン
# =========================
def detect_bear_pattern_reversal_high_fail(stock_data: pd.DataFrame) -> dict:
    """
    パターン1:
    過去1ヶ月の間に
    - その日の高値が、それ以前の過去5年高値を更新
    - その日の終値が始値を下回る
    が同日に発生
    """
    required_cols = {"Open", "High", "Close"}
    if stock_data.empty or not required_cols.issubset(stock_data.columns):
        return {
            "matched": False,
            "reason": "必要データ不足"
        }

    if len(stock_data) < 252:
        return {
            "matched": False,
            "reason": "過去データ不足"
        }

    last_20 = stock_data.iloc[-20:]

    for idx in range(len(last_20)):
        target_date = last_20.index[idx]
        current_row = last_20.iloc[idx]

        # その日以前の全履歴
        past_data = stock_data.loc[stock_data.index < target_date]
        if past_data.empty:
            continue

        today_open = float(current_row["Open"])
        today_high = float(current_row["High"])
        today_close = float(current_row["Close"])
        past_max_high = float(past_data["High"].max())

        is_new_high = today_high > past_max_high
        is_close_below_open = today_close < today_open

        if is_new_high and is_close_below_open:
            return {
                "matched": True,
                "reason": "過去1ヶ月以内に5年高値更新後の始値割れ引けが発生",
                "date": str(target_date.date()),
                "todayOpen": round(today_open, 2),
                "todayHigh": round(today_high, 2),
                "todayClose": round(today_close, 2),
                "pastMaxHigh": round(past_max_high, 2),
            }

    return {
        "matched": False,
        "reason": "高値更新失敗型の条件未達"
    }


def detect_bear_pattern_second_drop(stock_data: pd.DataFrame) -> dict:
    """
    パターン2:
    - 直近60営業日高値から現在値まで 15%以上下落
    - 直近20営業日の安値から少し戻している
    - しかし直近5日でまた弱い
    """
    if stock_data.empty or "Close" not in stock_data.columns or len(stock_data) < 60:
        return {
            "matched": False,
            "reason": "60日分のデータ不足"
        }

    close_prices = stock_data["Close"]
    recent_60 = close_prices.iloc[-60:]
    recent_20 = close_prices.iloc[-20:]

    high_60 = float(recent_60.max())
    current_price = float(close_prices.iloc[-1])
    low_20 = float(recent_20.min())
    price_5_days_ago = float(close_prices.iloc[-5]) if len(close_prices) >= 5 else current_price

    drop_rate = (high_60 - current_price) / high_60
    rebound_rate = (current_price - low_20) / low_20 if low_20 != 0 else 0.0
    is_weak_recent = current_price < price_5_days_ago

    matched = (
        drop_rate >= 0.15 and
        rebound_rate >= 0.03 and
        is_weak_recent
    )

    if matched:
        reason = "過去2ヶ月で大幅下落後、戻りが弱く再下落気配"
    else:
        reason = "再落下型の条件未達"

    return {
        "matched": matched,
        "reason": reason,
        "dropRate60": round(drop_rate, 4),
        "reboundRate20": round(rebound_rate, 4),
        "currentPrice": round(current_price, 2),
        "price5DaysAgo": round(price_5_days_ago, 2),
    }


def detect_bear_signal(stock_data: pd.DataFrame) -> dict:
    reversal = detect_bear_pattern_reversal_high_fail(stock_data)
    second_drop = detect_bear_pattern_second_drop(stock_data)

    is_bear = reversal["matched"] or second_drop["matched"]

    if reversal["matched"]:
        bear_pattern = "REVERSAL_HIGH_FAIL"
        reason = reversal["reason"]
    elif second_drop["matched"]:
        bear_pattern = "SECOND_DROP"
        reason = second_drop["reason"]
    else:
        bear_pattern = None
        reason = "下降シグナル条件未達"

    return {
        "isBear": is_bear,
        "bearPattern": bear_pattern,
        "reason": reason,
        "reversalHighFail": reversal,
        "secondDrop": second_drop,
    }


# =========================
# メイン処理
# =========================
def build_bull_recommendations() -> list:
    jpx = pd.read_csv(CSV_PATH, encoding="shift_jis")
    jpx["コード"] = jpx["コード"].astype(str).str.replace(".0", "", regex=False)
    jpx["コード"] = jpx["コード"].apply(lambda x: x.zfill(4))
    symbols = jpx["コード"].astype(str) + ".T"

    selected_stocks = []
    failed_symbols = []

    for symbol in symbols:
        print(f"checking bull: {symbol}")
        try:
            stock_data = get_stock_data(symbol)
            bull_result = detect_bull_recommendation(stock_data)

            if bull_result["isBull"]:
                code = symbol.split(".")[0]
                company_name = jpx.loc[jpx["コード"] == code, "銘柄名"].values[0]

                selected_stocks.append({
                    "symbol": code,
                    "companyName": company_name,
                    "currentPrice": bull_result["currentPrice"],
                    "reason": bull_result["reason"],
                    "signalType": "BULL",
                    "selectedDate": pd.Timestamp.today().strftime("%Y-%m-%d"),
                })

                print(f"{symbol}: BULL detected")

        except Exception as e:
            print(f"Error retrieving stock data for {symbol}: {e}")
            failed_symbols.append(symbol)

        time.sleep(SLEEP_SECONDS)

    return selected_stocks, failed_symbols


def build_market_signals() -> dict:
    results = {}

    for name, symbol in MARKET_SYMBOLS.items():
        print(f"checking market signal: {name} ({symbol})")
        try:
            stock_data = get_stock_data(symbol)

            box_result = detect_box_signal(stock_data)
            bear_result = detect_bear_signal(stock_data)

            results[name] = {
                "symbol": symbol,
                "boxSignal": box_result,
                "bearSignal": bear_result,
            }

        except Exception as e:
            results[name] = {
                "symbol": symbol,
                "error": str(e),
            }

    return results


def main():
    bull_recommendations, failed_symbols = build_bull_recommendations()
    market_signals = build_market_signals()

    output = {
        "generatedAt": pd.Timestamp.today().strftime("%Y-%m-%d %H:%M:%S"),
        "bullRecommendations": bull_recommendations,
        "marketSignals": market_signals,
        "failedSymbols": failed_symbols,
    }

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print("\nJSON出力完了:", OUTPUT_PATH)
    print("BULL銘柄数:", len(bull_recommendations))
    print("取得失敗銘柄数:", len(failed_symbols))

    print("\n=== MARKET SIGNALS ===")
    print(json.dumps(market_signals, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()