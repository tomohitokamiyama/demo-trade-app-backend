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

SLEEP_SECONDS = 2

MARKET_SYMBOLS = {
    "nikkei_index": "^N225",
}

# LONG_TERM_UPTREND の抽出率
LONG_TERM_TOP_PERCENT = 0.03   # 上位3%
LONG_TERM_MIN_COUNT = 3
LONG_TERM_MAX_COUNT = 8

# 最終おすすめ株数
MAX_RECOMMENDED_COUNT = 10


# =========================
# 共通: データ取得
# =========================
def get_stock_data(symbol: str, period: str = "5y") -> pd.DataFrame:
    stock = yf.Ticker(symbol)
    hist = stock.history(period=period, auto_adjust=False)
    return hist


# =========================
# 共通: CSV読み込み
# =========================
def load_jpx_symbols() -> pd.DataFrame:
    jpx = pd.read_csv(CSV_PATH, encoding="shift_jis")
    jpx["コード"] = pd.to_numeric(jpx["コード"], errors="coerce")
    jpx = jpx.dropna(subset=["コード"]).copy()
    jpx["コード"] = jpx["コード"].astype(int).astype(str).str.zfill(4)
    return jpx


# =========================
# 共通: 補助関数
# =========================
def safe_round(value, digits=4):
    if value is None:
        return None
    return round(float(value), digits)


def count_upper_touches(close_prices: pd.Series, high_price: float, tolerance: float = 0.02) -> int:
    """
    直近の終値がレンジ上限から何回近づいたかを数える
    tolerance=0.02 -> 上限から2%以内をタッチとみなす
    """
    if close_prices.empty or high_price <= 0:
        return 0

    threshold = high_price * (1 - tolerance)
    return int((close_prices >= threshold).sum())


def detect_recent_volatility_expansion(stock_data: pd.DataFrame) -> dict:
    """
    最近5営業日の絶対騰落率平均が、
    その前55営業日平均よりどれだけ増えているかを見る
    """
    if stock_data.empty or "Close" not in stock_data.columns:
        return {
            "isVolatilityExpansion": False,
            "reason": "価格データなし",
            "recentVol": None,
            "baseVol": None,
            "volRatio": None,
        }

    close_prices = stock_data["Close"].dropna()
    daily_move = close_prices.pct_change(fill_method=None).abs().dropna()

    if len(daily_move) < 60:
        return {
            "isVolatilityExpansion": False,
            "reason": "60日分の変動率データ不足",
            "recentVol": None,
            "baseVol": None,
            "volRatio": None,
        }

    recent_vol = float(daily_move.iloc[-5:].mean())
    base_vol = float(daily_move.iloc[-60:-5].mean())
    vol_ratio = recent_vol / base_vol if base_vol != 0 else 0.0

    is_expanding = vol_ratio >= 1.5

    return {
        "isVolatilityExpansion": is_expanding,
        "reason": "最近の変動率が拡大" if is_expanding else "最近の変動率は落ち着いている",
        "recentVol": safe_round(recent_vol, 4),
        "baseVol": safe_round(base_vol, 4),
        "volRatio": safe_round(vol_ratio, 4),
    }


def detect_volume_expansion(stock_data: pd.DataFrame) -> dict:
    """
    出来高が20日平均より増えているかを見る
    """
    if stock_data.empty or "Volume" not in stock_data.columns or len(stock_data) < 21:
        return {
            "isVolumeExpansion": False,
            "reason": "出来高データ不足",
            "todayVolume": None,
            "avgVolume20": None,
            "volumeRatio": None,
        }

    volume = stock_data["Volume"].fillna(0)
    today_volume = float(volume.iloc[-1])
    avg_volume_20 = float(volume.iloc[-21:-1].mean())
    volume_ratio = today_volume / avg_volume_20 if avg_volume_20 != 0 else 0.0

    is_expanding = volume_ratio >= 1.1

    return {
        "isVolumeExpansion": is_expanding,
        "reason": "出来高増加" if is_expanding else "出来高は平常圏",
        "todayVolume": int(today_volume),
        "avgVolume20": int(avg_volume_20),
        "volumeRatio": safe_round(volume_ratio, 4),
    }


# =========================
# BULL: ブレイク株候補
# =========================
def detect_bull_recommendation(stock_data: pd.DataFrame) -> dict:
    """
    条件:
    - 終値が 2000〜10000
    - 5年分近いデータがある
    - 直近終値が、それ以前の終値最高値の95%以上
    - 直近出来高が20日平均の1.0倍以上

    補足:
    - 98%以上 + 出来高1.1倍以上なら CORE
    - 95%以上 + 出来高1.0倍以上なら WATCH
    """
    required_cols = {"Close", "Volume"}
    if stock_data.empty or not required_cols.issubset(stock_data.columns):
        return {"isBull": False, "reason": "必要データ不足"}

    close_prices = stock_data["Close"].dropna()
    if len(close_prices) < 1000:
        return {"isBull": False, "reason": "5年分のデータ不足"}

    current_price = float(close_prices.iloc[-1])
    past_max_close = float(close_prices.iloc[:-1].max())

    in_price_range = 2000 <= current_price <= 10000
    high_distance_rate = current_price / past_max_close if past_max_close else 0.0

    is_core_breakout = high_distance_rate >= 0.98
    is_watch_breakout = high_distance_rate >= 0.95

    volume_result = detect_volume_expansion(stock_data)
    volume_ratio = volume_result["volumeRatio"] or 0.0

    is_bull = in_price_range and (
        (is_core_breakout and volume_ratio >= 1.1) or
        (is_watch_breakout and volume_ratio >= 1.0)
    )

    bull_rank = None
    if in_price_range and is_core_breakout and volume_ratio >= 1.1:
        bull_rank = "CORE"
        reason = "5年高値圏(98%以上) + 出来高増加"
    elif in_price_range and is_watch_breakout and volume_ratio >= 1.0:
        bull_rank = "WATCH"
        reason = "5年高値圏(95%以上) + 監視候補"
    else:
        reason = "条件未達"

    return {
        "isBull": is_bull,
        "bullRank": bull_rank,
        "reason": reason,
        "currentPrice": safe_round(current_price, 2),
        "pastMaxClose": safe_round(past_max_close, 2),
        "highDistanceRate": safe_round(high_distance_rate, 4),
        "volumeExpansion": volume_result,
    }


# =========================
# LONG_TERM_UPTREND: 5年右肩上がり候補
# =========================
def detect_long_term_uptrend_stock(stock_data: pd.DataFrame) -> dict:
    """
    5年単位で右肩上がりの候補を評価する
    """
    required_cols = {"Close"}
    if stock_data.empty or not required_cols.issubset(stock_data.columns):
        return {"isUptrend": False, "reason": "必要データ不足"}

    close_prices = stock_data["Close"].dropna()
    if len(close_prices) < 1000:
        return {"isUptrend": False, "reason": "5年分のデータ不足"}

    current_price = float(close_prices.iloc[-1])
    price_5y_ago = float(close_prices.iloc[0])

    ma50 = float(close_prices.iloc[-50:].mean())
    ma200 = float(close_prices.iloc[-200:].mean())

    high_5y = float(close_prices.max())
    low_20 = float(close_prices.iloc[-20:].min())
    high_20 = float(close_prices.iloc[-20:].max())

    growth_5y = current_price / price_5y_ago if price_5y_ago != 0 else 0.0
    high_distance_rate_5y = current_price / high_5y if high_5y != 0 else 0.0
    range20 = (high_20 - low_20) / low_20 if low_20 != 0 else 0.0

    vol_result = detect_recent_volatility_expansion(stock_data)

    checks = {
        "priceRange": 1000 <= current_price <= 15000,
        "upOver5Years": growth_5y >= 1.5,
        "aboveMa200": current_price > ma200,
        "ma50AboveMa200": ma50 > ma200,
        "nearHigh5Y": high_distance_rate_5y >= 0.90,
        "stableRange20": range20 <= 0.12,
        "notTooVolatile": not vol_result["isVolatilityExpansion"],
    }

    score = 0
    if checks["priceRange"]:
        score += 1
    if checks["upOver5Years"]:
        score += 3
    if checks["aboveMa200"]:
        score += 2
    if checks["ma50AboveMa200"]:
        score += 2
    if checks["nearHigh5Y"]:
        score += 2
    if checks["stableRange20"]:
        score += 1
    if checks["notTooVolatile"]:
        score += 1

    is_uptrend = (
        checks["upOver5Years"] and
        checks["aboveMa200"] and
        checks["ma50AboveMa200"] and
        checks["nearHigh5Y"]
    )

    if is_uptrend:
        reason = "5年右肩上がり候補"
    else:
        reason = "条件未達"

    return {
        "isUptrend": is_uptrend,
        "reason": reason,
        "score": score,
        "checks": checks,
        "currentPrice": safe_round(current_price, 2),
        "price5yAgo": safe_round(price_5y_ago, 2),
        "growth5Y": safe_round(growth_5y, 4),
        "ma50": safe_round(ma50, 2),
        "ma200": safe_round(ma200, 2),
        "high5Y": safe_round(high_5y, 2),
        "highDistanceRate5Y": safe_round(high_distance_rate_5y, 4),
        "range20": safe_round(range20, 4),
        "volatilityExpansion": vol_result,
    }


# =========================
# BOX: ボックス相場 + 上抜け前候補
# =========================
def detect_box_signal(stock_data: pd.DataFrame) -> dict:
    """
    条件:
    - 直近20日レンジ幅が 5% 以内
    - 直近60日レンジ幅が 12% 以内
    - 現在価格が20日レンジ上限から 2% 以内
    - 最近の変動率急拡大がない
    - 直近10日安値 > その前10日安値
    - 上限タッチが複数回ある
    """
    if stock_data.empty or "Close" not in stock_data.columns:
        return {
            "isBox": False,
            "isPreBreakout": False,
            "reason": "価格データなし",
            "range20": None,
            "range60": None,
            "upperDiff20": None,
            "risingLows": None,
            "upperTouches20": None,
            "volatilityExpansion": None,
            "volumeExpansion": None,
        }

    close_prices = stock_data["Close"].dropna()
    if len(close_prices) < 60:
        return {
            "isBox": False,
            "isPreBreakout": False,
            "reason": "60日分のデータ不足",
            "range20": None,
            "range60": None,
            "upperDiff20": None,
            "risingLows": None,
            "upperTouches20": None,
            "volatilityExpansion": None,
            "volumeExpansion": None,
        }

    recent_20 = close_prices.iloc[-20:]
    recent_60 = close_prices.iloc[-60:]
    prev_10 = close_prices.iloc[-20:-10]
    last_10 = close_prices.iloc[-10:]

    high20 = float(recent_20.max())
    low20 = float(recent_20.min())
    high60 = float(recent_60.max())
    low60 = float(recent_60.min())
    current_price = float(close_prices.iloc[-1])

    range20 = (high20 - low20) / low20 if low20 != 0 else 0.0
    range60 = (high60 - low60) / low60 if low60 != 0 else 0.0
    upper_diff20 = (high20 - current_price) / high20 if high20 != 0 else 0.0

    prev_low_10 = float(prev_10.min()) if len(prev_10) == 10 else None
    last_low_10 = float(last_10.min()) if len(last_10) == 10 else None
    rising_lows = (last_low_10 > prev_low_10) if prev_low_10 is not None and last_low_10 is not None else False

    upper_touches20 = count_upper_touches(recent_20, high20, tolerance=0.02)

    volatility_result = detect_recent_volatility_expansion(stock_data)
    volume_result = detect_volume_expansion(stock_data)

    is_box = (
        range20 <= 0.05 and
        range60 <= 0.12
    )

    is_pre_breakout = (
        is_box and
        upper_diff20 <= 0.02 and
        not volatility_result["isVolatilityExpansion"] and
        rising_lows and
        upper_touches20 >= 3
    )

    if is_pre_breakout and volume_result["isVolumeExpansion"]:
        reason = "ボックス上限付近・安値切り上がり・上限複数回接触・出来高増で上抜け候補"
    elif is_pre_breakout:
        reason = "ボックス上限付近・安値切り上がり・上限複数回接触で上抜け候補"
    elif is_box:
        reason = "ボックス相場"
    else:
        reason = "ボックス条件未達"

    return {
        "isBox": is_box,
        "isPreBreakout": is_pre_breakout,
        "reason": reason,
        "range20": safe_round(range20, 4),
        "range60": safe_round(range60, 4),
        "upperDiff20": safe_round(upper_diff20, 4),
        "risingLows": rising_lows,
        "prevLow10": safe_round(prev_low_10, 2) if prev_low_10 is not None else None,
        "lastLow10": safe_round(last_low_10, 2) if last_low_10 is not None else None,
        "upperTouches20": upper_touches20,
        "volatilityExpansion": volatility_result,
        "volumeExpansion": volume_result,
    }


# =========================
# BEAR: 下降シグナル2パターン
# =========================
def detect_bear_pattern_reversal_high_fail(stock_data: pd.DataFrame) -> dict:
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

    target_data = stock_data.dropna(subset=["Open", "High", "Close"])
    last_20 = target_data.iloc[-20:]

    for idx in range(len(last_20)):
        target_date = last_20.index[idx]
        current_row = last_20.iloc[idx]

        past_data = target_data.loc[target_data.index < target_date]
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
                "todayOpen": safe_round(today_open, 2),
                "todayHigh": safe_round(today_high, 2),
                "todayClose": safe_round(today_close, 2),
                "pastMaxHigh": safe_round(past_max_high, 2),
            }

    return {
        "matched": False,
        "reason": "高値更新失敗型の条件未達"
    }


def detect_bear_pattern_second_drop(stock_data: pd.DataFrame) -> dict:
    if stock_data.empty or "Close" not in stock_data.columns:
        return {
            "matched": False,
            "reason": "60日分のデータ不足"
        }

    close_prices = stock_data["Close"].dropna()
    if len(close_prices) < 60:
        return {
            "matched": False,
            "reason": "60日分のデータ不足"
        }

    recent_60 = close_prices.iloc[-60:]
    recent_20 = close_prices.iloc[-20:]

    high_60 = float(recent_60.max())
    current_price = float(close_prices.iloc[-1])
    low_20 = float(recent_20.min())
    price_5_days_ago = float(close_prices.iloc[-5]) if len(close_prices) >= 5 else current_price

    drop_rate = (high_60 - current_price) / high_60 if high_60 != 0 else 0.0
    rebound_rate = (current_price - low_20) / low_20 if low_20 != 0 else 0.0
    is_weak_recent = current_price < price_5_days_ago

    matched = (
        drop_rate >= 0.15 and
        rebound_rate >= 0.03 and
        is_weak_recent
    )

    reason = "過去2ヶ月で大幅下落後、戻りが弱く再下落気配" if matched else "再落下型の条件未達"

    return {
        "matched": matched,
        "reason": reason,
        "dropRate60": safe_round(drop_rate, 4),
        "reboundRate20": safe_round(rebound_rate, 4),
        "currentPrice": safe_round(current_price, 2),
        "price5DaysAgo": safe_round(price_5_days_ago, 2),
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
# メイン処理: BULL一覧
# =========================
def build_bull_recommendations() -> tuple[list, list]:
    jpx = load_jpx_symbols()
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
                    "bullRank": bull_result["bullRank"],
                    "selectedDate": pd.Timestamp.today().strftime("%Y-%m-%d"),
                    "highDistanceRate": bull_result["highDistanceRate"],
                    "volumeExpansion": bull_result["volumeExpansion"],
                })

                print(f"{symbol}: BULL detected")

        except Exception as e:
            print(f"Error retrieving stock data for {symbol}: {e}")
            failed_symbols.append(symbol)

        time.sleep(SLEEP_SECONDS)

    return selected_stocks, failed_symbols


# =========================
# メイン処理: 5年右肩上がり一覧（割合抽出）
# =========================
def build_long_term_uptrend_recommendations(
    top_percent: float = LONG_TERM_TOP_PERCENT,
    min_count: int = LONG_TERM_MIN_COUNT,
    max_count: int = LONG_TERM_MAX_COUNT
) -> tuple[list, list]:
    jpx = load_jpx_symbols()
    symbols = jpx["コード"].astype(str) + ".T"

    selected_stocks = []
    failed_symbols = []

    for symbol in symbols:
        print(f"checking long-term uptrend: {symbol}")
        try:
            stock_data = get_stock_data(symbol)
            result = detect_long_term_uptrend_stock(stock_data)

            if result["isUptrend"]:
                code = symbol.split(".")[0]
                company_name = jpx.loc[jpx["コード"] == code, "銘柄名"].values[0]

                selected_stocks.append({
                    "symbol": code,
                    "companyName": company_name,
                    "currentPrice": result["currentPrice"],
                    "reason": result["reason"],
                    "signalType": "LONG_TERM_UPTREND",
                    "selectedDate": pd.Timestamp.today().strftime("%Y-%m-%d"),
                    "score": result["score"],
                    "growth5Y": result["growth5Y"],
                    "ma50": result["ma50"],
                    "ma200": result["ma200"],
                    "highDistanceRate5Y": result["highDistanceRate5Y"],
                    "range20": result["range20"],
                    "checks": result["checks"],
                })

                print(f"{symbol}: LONG_TERM_UPTREND detected")

        except Exception as e:
            print(f"Error retrieving stock data for {symbol}: {e}")
            failed_symbols.append(symbol)

        time.sleep(SLEEP_SECONDS)

    selected_stocks = sorted(
        selected_stocks,
        key=lambda x: (x["score"], x["growth5Y"], x["highDistanceRate5Y"]),
        reverse=True
    )

    candidate_count = len(selected_stocks)
    picked_count = int(candidate_count * top_percent)

    if picked_count < min_count:
        picked_count = min_count
    if picked_count > max_count:
        picked_count = max_count
    if picked_count > candidate_count:
        picked_count = candidate_count

    return selected_stocks[:picked_count], failed_symbols


# =========================
# メイン処理: おすすめ株一覧
# =========================
def build_recommended_stocks(
    bull_recommendations: list,
    long_term_uptrend_recommendations: list,
    max_count: int = MAX_RECOMMENDED_COUNT
) -> list:
    """
    LONG_TERM_UPTREND と BULL を結合し、
    symbol単位で重複を排除したおすすめ株一覧を作る

    方針:
    1. BULL を優先
    2. LONG_TERM_UPTREND を追加
    3. 最後にスコア順で並べて上位 max_count 件だけ返す
    """
    recommended_map = {}

    # BULLはやや優先度高めのスコアにする
    for stock in bull_recommendations:
        symbol = stock["symbol"]
        high_distance = stock.get("highDistanceRate") or 0.0
        volume_ratio = (stock.get("volumeExpansion") or {}).get("volumeRatio") or 0.0
        bull_rank = stock.get("bullRank")

        rank_score = 2 if bull_rank == "CORE" else 1

        final_score = (
            100
            + rank_score * 10
            + high_distance * 10
            + volume_ratio
        )

        recommended_map[symbol] = {
            **stock,
            "recommendationSource": "BULL",
            "finalScore": safe_round(final_score, 4),
        }

    # LONG_TERM_UPTRENDはBULLに入っていないものだけ追加
    for stock in long_term_uptrend_recommendations:
        symbol = stock["symbol"]
        if symbol not in recommended_map:
            score = stock.get("score") or 0
            growth_5y = stock.get("growth5Y") or 0.0
            high_distance_5y = stock.get("highDistanceRate5Y") or 0.0

            final_score = (
                score * 10
                + growth_5y * 5
                + high_distance_5y * 5
            )

            recommended_map[symbol] = {
                **stock,
                "recommendationSource": "LONG_TERM_UPTREND",
                "finalScore": safe_round(final_score, 4),
            }

    final_list = sorted(
        recommended_map.values(),
        key=lambda x: x["finalScore"],
        reverse=True
    )

    return final_list[:max_count]


# =========================
# メイン処理: 市場シグナル
# =========================
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


# =========================
# main
# =========================
def main():
    bull_recommendations, bull_failed_symbols = build_bull_recommendations()
    long_term_uptrend_recommendations, uptrend_failed_symbols = build_long_term_uptrend_recommendations()
    recommended_stocks = build_recommended_stocks(
        bull_recommendations=bull_recommendations,
        long_term_uptrend_recommendations=long_term_uptrend_recommendations
    )
    market_signals = build_market_signals()

    output = {
        "generatedAt": pd.Timestamp.today().strftime("%Y-%m-%d %H:%M:%S"),
        "recommendedStocks": recommended_stocks,
        "bullRecommendations": bull_recommendations,
        "longTermUptrendRecommendations": long_term_uptrend_recommendations,
        "marketSignals": market_signals,
        "failedSymbols": {
            "bull": bull_failed_symbols,
            "longTermUptrend": uptrend_failed_symbols,
        },
        "selectionConfig": {
            "longTermTopPercent": LONG_TERM_TOP_PERCENT,
            "longTermMinCount": LONG_TERM_MIN_COUNT,
            "longTermMaxCount": LONG_TERM_MAX_COUNT,
            "maxRecommendedCount": MAX_RECOMMENDED_COUNT,
        },
    }

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print("\nJSON出力完了:", OUTPUT_PATH)
    print("おすすめ株数:", len(recommended_stocks))
    print("BULL銘柄数:", len(bull_recommendations))
    print("LONG_TERM_UPTREND銘柄数:", len(long_term_uptrend_recommendations))
    print("BULL取得失敗銘柄数:", len(bull_failed_symbols))
    print("LONG_TERM_UPTREND取得失敗銘柄数:", len(uptrend_failed_symbols))

    print("\n=== MARKET SIGNALS ===")
    print(json.dumps(market_signals, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()