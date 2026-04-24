import { useEffect, useState } from "react";

type TradeType = "BUY" | "SELL" | "SHORT" | "COVER";
type SignalType = "BULL" | "BEAR" | "BOX" | "NONE";

type Trade = {
  id: number;
  symbol: string;
  tradeType: TradeType;
  quantity: number;
  price: number;
  tradeDate: string;
  signalType: SignalType;
  entryReason: string;
};

function TradesPage() {
  const [trades, setTrades] = useState<Trade[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const fetchTrades = async () => {
    try {
      setLoading(true);
      setError("");

      const response = await fetch("http://localhost:8080/trades");
      if (!response.ok) {
        throw new Error("取引履歴取得に失敗しました");
      }

      const data: Trade[] = await response.json();
      setTrades(data);
    } catch (err) {
      console.error(err);
      setError("取引履歴の取得でエラーが発生しました");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTrades();
  }, []);

  return (
    <div>
      <h2>取引履歴</h2>

      {loading && <p>読み込み中...</p>}
      {error && <p style={{ color: "red" }}>{error}</p>}

      {!loading && trades.length === 0 && <p>取引履歴がありません</p>}

      {!loading && trades.length > 0 && (
        <table
          border={1}
          cellPadding={8}
          style={{ borderCollapse: "collapse", width: "100%" }}
        >
          <thead>
            <tr>
              <th>ID</th>
              <th>銘柄</th>
              <th>売買種別</th>
              <th>数量</th>
              <th>価格</th>
              <th>取引日</th>
              <th>相場シグナル</th>
              <th>取引理由</th>
            </tr>
          </thead>
          <tbody>
            {trades.map((trade) => (
              <tr key={trade.id}>
                <td>{trade.id}</td>
                <td>{trade.symbol}</td>
                <td>{trade.tradeType}</td>
                <td>{trade.quantity}</td>
                <td>{trade.price}</td>
                <td>{trade.tradeDate}</td>
                <td>{trade.signalType}</td>
                <td>{trade.entryReason}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}

export default TradesPage;