import { useEffect, useState } from "react";

type RecommendedStock = {
  symbol: string;
  companyName: string;
  currentPrice: number;
  reason: string;
  signalType?: string;
  recommendationSource?: string;
};

function RecommendedStocksPage() {
  const [stocks, setStocks] = useState<RecommendedStock[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [submittingSymbol, setSubmittingSymbol] = useState<string | null>(null);

  const fetchRecommendedStocks = async () => {
    try {
      setLoading(true);
      setError("");

      const response = await fetch("http://localhost:8080/market-signals/latest");
      if (!response.ok) {
        throw new Error("おすすめ株取得に失敗しました");
      }

      const data = await response.json();
      setStocks(data.recommendedStocks ?? []);
    } catch (err) {
      console.error(err);
      setError("おすすめ株の取得でエラーが発生しました");
    } finally {
      setLoading(false);
    }
  };

  const buyStock = async (stock: RecommendedStock) => {
    try {
      setSubmittingSymbol(stock.symbol);

      const response = await fetch("http://localhost:8080/trades", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          symbol: stock.symbol,
          tradeType: "BUY",
          quantity: 100,
          price: stock.currentPrice,
          tradeDate: new Date().toISOString().slice(0, 10),
          signalType: stock.signalType ?? "BULL",
          entryReason: stock.reason,
        }),
      });

      if (!response.ok) {
        const message = await response.text();
        throw new Error(message || "買い付けに失敗しました");
      }

      alert(`${stock.symbol} を買いました`);
    } catch (err) {
      console.error(err);
      alert("買い付けでエラーが発生しました");
    } finally {
      setSubmittingSymbol(null);
    }
  };

  useEffect(() => {
    fetchRecommendedStocks();
  }, []);

  return (
    <div>
      <h2>おすすめ株ページ</h2>
      <p style={{ color: "#555" }}>
        Pythonで抽出したおすすめ銘柄を、Spring Boot API経由で表示しています。
      </p>

      {loading && <p>読み込み中...</p>}
      {error && <p style={{ color: "red" }}>{error}</p>}
      {!loading && stocks.length === 0 && <p>おすすめ株がありません。</p>}

      {!loading && stocks.length > 0 && (
        <div
          style={{
            display: "grid",
            gap: "16px",
            gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))",
          }}
        >
          {stocks.map((stock) => (
            <div
              key={stock.symbol}
              style={{
                border: "1px solid #d9d9d9",
                borderRadius: "12px",
                padding: "20px",
                background: "#fff",
                boxShadow: "0 2px 8px rgba(0,0,0,0.05)",
              }}
            >
              <h3 style={{ marginTop: 0, marginBottom: "12px" }}>
                {stock.symbol}
              </h3>

              <div style={{ display: "grid", gap: "10px" }}>
                <div>
                  <p style={{ margin: "0 0 4px 0", color: "#666" }}>会社名</p>
                  <p style={{ margin: 0, fontWeight: "bold" }}>{stock.companyName}</p>
                </div>

                <div>
                  <p style={{ margin: "0 0 4px 0", color: "#666" }}>現在価格</p>
                  <p style={{ margin: 0, fontWeight: "bold" }}>
                    {stock.currentPrice}
                  </p>
                </div>

                <div>
                  <p style={{ margin: "0 0 4px 0", color: "#666" }}>理由</p>
                  <p style={{ margin: 0, fontWeight: "bold" }}>{stock.reason}</p>
                </div>

                <div>
                  <p style={{ margin: "0 0 4px 0", color: "#666" }}>抽出元</p>
                  <p style={{ margin: 0, fontWeight: "bold" }}>
                    {stock.recommendationSource ?? stock.signalType ?? "-"}
                  </p>
                </div>
              </div>

              <button
                onClick={() => buyStock(stock)}
                disabled={submittingSymbol === stock.symbol}
                style={{ marginTop: "16px" }}
              >
                {submittingSymbol === stock.symbol ? "買付中..." : "買う"}
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default RecommendedStocksPage;