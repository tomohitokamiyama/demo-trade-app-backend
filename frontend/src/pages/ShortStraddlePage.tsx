import { useEffect, useState } from "react";

type BoxSignal = {
  isBox: boolean;
  isPreBreakout: boolean;
  reason: string;
  range20?: number;
  range60?: number;
  upperDiff20?: number;
  risingLows?: boolean;
  upperTouches20?: number;
};

function ShortStraddlePage() {
  const [boxSignal, setBoxSignal] = useState<BoxSignal | null>(null);
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
      setBoxSignal(data.marketSignals?.nikkei_index?.boxSignal ?? null);
    } catch (err) {
      console.error(err);
      setError("マーケットシグナル取得でエラーが発生しました");
    } finally {
      setLoading(false);
    }
  };

  const shortStraddle = async () => {
    if (!boxSignal) return;

    try {
      setSubmitting(true);

      const hasBoxSignal = boxSignal.isBox && !boxSignal.isPreBreakout;

      const response = await fetch("http://localhost:8080/trades", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          symbol: "N225_OPTION_STRADDLE",
          tradeType: "SHORT",
          quantity: 1,
          price: 0,
          tradeDate: new Date().toISOString().slice(0, 10),
          signalType: hasBoxSignal ? "BOX" : "NONE",
          entryReason: hasBoxSignal
            ? boxSignal.reason
            : boxSignal.isPreBreakout
            ? "上抜け前候補のためBOXシグナル扱いせず手動判断"
            : "ボックスシグナルなしで手動判断",
        }),
      });

      if (!response.ok) {
        const message = await response.text();
        throw new Error(message || "売りストラドル登録に失敗しました");
      }

      alert(
        hasBoxSignal
          ? "BOXシグナル付きで売りストラドルを登録しました"
          : "シグナルなしの手動判断として売りストラドルを登録しました"
      );
    } catch (err) {
      console.error(err);
      alert("売りストラドル登録でエラーが発生しました");
    } finally {
      setSubmitting(false);
    }
  };

  useEffect(() => {
    fetchMarketSignal();
  }, []);

  return (
    <div>
      <h2>売りストラドルページ</h2>
      <p style={{ color: "#555" }}>
        ボックスシグナルが出ている時と出ていない時の成績を比較するページです。
      </p>

      {loading && <p>読み込み中...</p>}
      {error && <p style={{ color: "red" }}>{error}</p>}

      {!loading && boxSignal && (
        <div
          style={{
            border: "1px solid #d9d9d9",
            borderRadius: "12px",
            padding: "20px",
            background: "#fff",
            maxWidth: "720px",
          }}
        >
          <h3>現在のボックスシグナル</h3>

          <p>
            <strong>判定:</strong>{" "}
            {boxSignal.isBox ? "ボックス相場" : "ボックス相場ではない"}
          </p>

          <p>
            <strong>上抜け前候補:</strong>{" "}
            {boxSignal.isPreBreakout ? "あり" : "なし"}
          </p>

          <p>
            <strong>理由:</strong> {boxSignal.reason}
          </p>

          <p>
            <strong>20日レンジ:</strong> {boxSignal.range20 ?? "-"}
          </p>

          <p>
            <strong>60日レンジ:</strong> {boxSignal.range60 ?? "-"}
          </p>

          <p>
            <strong>20日上限との差:</strong> {boxSignal.upperDiff20 ?? "-"}
          </p>

          <p>
            <strong>安値切り上がり:</strong>{" "}
            {boxSignal.risingLows ? "あり" : "なし"}
          </p>

          <p>
            <strong>上限接触回数:</strong> {boxSignal.upperTouches20 ?? "-"}
          </p>

          {(!boxSignal.isBox || boxSignal.isPreBreakout) && (
            <p style={{ color: "#b26a00" }}>
              現在は有効なBOXシグナルなしです。登録すると signalType は NONE になります。
            </p>
          )}

          <button
            onClick={shortStraddle}
            disabled={submitting}
            style={{ marginTop: "16px" }}
          >
            {submitting
              ? "登録中..."
              : boxSignal.isBox && !boxSignal.isPreBreakout
              ? "BOXシグナルで売りストラドルを登録"
              : "手動判断で売りストラドルを登録"}
          </button>
        </div>
      )}
    </div>
  );
}

export default ShortStraddlePage;