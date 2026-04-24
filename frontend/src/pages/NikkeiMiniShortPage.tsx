import { useEffect, useState } from "react";

type BearSignal = {
  isBear: boolean;
  bearPattern: string | null;
  reason: string;
  reversalHighFail?: {
    matched: boolean;
    date?: string;
    todayOpen?: number;
    todayHigh?: number;
    todayClose?: number;
    pastMaxHigh?: number;
  };
  secondDrop?: {
    matched: boolean;
    dropRate60?: number;
    reboundRate20?: number;
    currentPrice?: number;
    price5DaysAgo?: number;
  };
};

function NikkeiMiniShortPage() {
  const [bearSignal, setBearSignal] = useState<BearSignal | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  const fetchMarketSignal = async () => {
    try {
      setLoading(true);
      setError("");

      const response = await fetch("http://localhost:8080/market-signals/latest");
      if (!response.ok) {
        throw new Error("マーケットシグナル取得に失敗しました");
      }

      const data = await response.json();
      setBearSignal(data.marketSignals?.nikkei_index?.bearSignal ?? null);
    } catch (err) {
      console.error(err);
      setError("マーケットシグナル取得でエラーが発生しました");
    } finally {
      setLoading(false);
    }
  };

  const shortNikkeiMini = async () => {
    if (!bearSignal) return;

    try {
      setSubmitting(true);

      const currentPrice =
        bearSignal.reversalHighFail?.todayClose ??
        bearSignal.secondDrop?.currentPrice ??
        0;

      const hasBearSignal = bearSignal.isBear;

      const response = await fetch("http://localhost:8080/trades", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          symbol: "N225MINI",
          tradeType: "SHORT",
          quantity: 1,
          price: currentPrice,
          tradeDate: new Date().toISOString().slice(0, 10),
          signalType: hasBearSignal ? "BEAR" : "NONE",
          entryReason: hasBearSignal
            ? bearSignal.reason
            : "下降シグナルなしで手動判断",
        }),
      });

      if (!response.ok) {
        const message = await response.text();
        throw new Error(message || "日経mini売り登録に失敗しました");
      }

      alert(
        hasBearSignal
          ? "BEARシグナル付きで日経mini売りを登録しました"
          : "シグナルなしの手動判断として日経mini売りを登録しました"
      );
    } catch (err) {
      console.error(err);
      alert("日経mini売り登録でエラーが発生しました");
    } finally {
      setSubmitting(false);
    }
  };

  useEffect(() => {
    fetchMarketSignal();
  }, []);

  return (
    <div>
      <h2>日経平均mini売りページ</h2>
      <p style={{ color: "#555" }}>
        下降シグナルが出ている時と出ていない時の売り成績を比較するページです。
      </p>

      {loading && <p>読み込み中...</p>}
      {error && <p style={{ color: "red" }}>{error}</p>}

      {!loading && bearSignal && (
        <div
          style={{
            border: "1px solid #d9d9d9",
            borderRadius: "12px",
            padding: "20px",
            background: "#fff",
            maxWidth: "720px",
          }}
        >
          <h3>現在の下降シグナル</h3>

          <p>
            <strong>判定:</strong>{" "}
            {bearSignal.isBear ? "下降シグナルあり" : "下降シグナルなし"}
          </p>

          <p>
            <strong>パターン:</strong> {bearSignal.bearPattern ?? "-"}
          </p>

          <p>
            <strong>理由:</strong> {bearSignal.reason}
          </p>

          {bearSignal.reversalHighFail?.matched && (
            <div>
              <h4>高値更新失敗型</h4>
              <p>発生日: {bearSignal.reversalHighFail.date}</p>
              <p>始値: {bearSignal.reversalHighFail.todayOpen}</p>
              <p>高値: {bearSignal.reversalHighFail.todayHigh}</p>
              <p>終値: {bearSignal.reversalHighFail.todayClose}</p>
              <p>過去最高値: {bearSignal.reversalHighFail.pastMaxHigh}</p>
            </div>
          )}

          {bearSignal.secondDrop?.matched && (
            <div>
              <h4>再落下型</h4>
              <p>60日下落率: {bearSignal.secondDrop.dropRate60}</p>
              <p>20日反発率: {bearSignal.secondDrop.reboundRate20}</p>
              <p>現在価格: {bearSignal.secondDrop.currentPrice}</p>
              <p>5日前価格: {bearSignal.secondDrop.price5DaysAgo}</p>
            </div>
          )}

          {!bearSignal.isBear && (
            <p style={{ color: "#b26a00" }}>
              現在は下降シグナルなしです。登録すると signalType は NONE になります。
            </p>
          )}

          <button
            onClick={shortNikkeiMini}
            disabled={submitting}
            style={{ marginTop: "16px" }}
          >
            {submitting
              ? "登録中..."
              : bearSignal.isBear
              ? "BEARシグナルで日経miniを売る"
              : "手動判断で日経miniを売る"}
          </button>
        </div>
      )}
    </div>
  );
}

export default NikkeiMiniShortPage;