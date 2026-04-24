import { useEffect, useState } from "react";

type PositionType = "LONG" | "SHORT";
type PositionStatus = "OPEN" | "CLOSED";

type Position = {
  id: number;
  userId: number;
  symbol: string;
  positionType: PositionType;
  quantity: number;
  avgPrice: number;
  status: PositionStatus;
  openedAt: string;
  closedAt: string | null;
  createdAt: string;
  updatedAt: string;
};

type PositionPlResponse = {
  symbol: string;
  positionType: PositionType;
  quantity: number;
  avgPrice: number;
  currentPrice: number;
  profitLoss: number;
};

type PositionPlSummaryResponse = {
  totalProfitLoss: number;
  positionCount: number;
};

function MyTradesPage() {
  const [positions, setPositions] = useState<Position[]>([]);
  const [positionPlList, setPositionPlList] = useState<PositionPlResponse[]>([]);
  const [summary, setSummary] = useState<PositionPlSummaryResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [closingPositionId, setClosingPositionId] = useState<number | null>(null);

  const fetchData = async () => {
    try {
      setLoading(true);
      setError("");

      const [positionsRes, plRes, summaryRes] = await Promise.all([
        fetch("http://localhost:8080/positions"),
        fetch("http://localhost:8080/positions/pl"),
        fetch("http://localhost:8080/positions/pl/summary"),
      ]);

      if (!positionsRes.ok) {
        throw new Error("ポジション取得に失敗しました");
      }
      if (!plRes.ok) {
        throw new Error("損益取得に失敗しました");
      }
      if (!summaryRes.ok) {
        throw new Error("損益サマリ取得に失敗しました");
      }

      const positionsData: Position[] = await positionsRes.json();
      const plData: PositionPlResponse[] = await plRes.json();
      const summaryData: PositionPlSummaryResponse = await summaryRes.json();

      setPositions(positionsData);
      setPositionPlList(plData);
      setSummary(summaryData);
    } catch (err) {
      console.error(err);
      setError("My取引データの取得でエラーが発生しました");
    } finally {
      setLoading(false);
    }
  };

  const findPl = (position: Position) => {
    return positionPlList.find(
      (item) =>
        item.symbol === position.symbol &&
        item.positionType === position.positionType
    );
  };

  const closePosition = async (position: Position) => {
    const ok = window.confirm(
      `${position.symbol} の ${position.positionType} ポジションを決済しますか？`
    );

    if (!ok) return;

    try {
      setClosingPositionId(position.id);

      const pl = findPl(position);

      const tradeType = position.positionType === "LONG" ? "SELL" : "COVER";

      const closePrice = pl?.currentPrice ?? position.avgPrice;

      const response = await fetch("http://localhost:8080/trades", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          symbol: position.symbol,
          tradeType,
          quantity: position.quantity,
          price: closePrice,
          tradeDate: new Date().toISOString().slice(0, 10),
          signalType: "NONE",
          entryReason:
            position.positionType === "LONG"
              ? "LONGポジションの手動決済"
              : "SHORTポジションの手動決済",
        }),
      });

      if (!response.ok) {
        const message = await response.text();
        throw new Error(message || "決済に失敗しました");
      }

      alert(`${position.symbol} を決済しました`);

      await fetchData();
    } catch (err) {
      console.error(err);
      alert("決済でエラーが発生しました");
    } finally {
      setClosingPositionId(null);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  return (
    <div>
      <h2>My取引</h2>

      {loading && <p>読み込み中...</p>}
      {error && <p style={{ color: "red" }}>{error}</p>}

      {!loading && (
        <>
          {summary && (
            <section
              style={{
                marginBottom: "24px",
                display: "grid",
                gap: "16px",
                gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))",
              }}
            >
              <div
                style={{
                  border: "1px solid #ccc",
                  borderRadius: "8px",
                  padding: "16px",
                }}
              >
                <h3 style={{ marginTop: 0 }}>合計含み損益</h3>
                <p style={{ fontSize: "24px", fontWeight: "bold", margin: 0 }}>
                  {summary.totalProfitLoss}
                </p>
              </div>

              <div
                style={{
                  border: "1px solid #ccc",
                  borderRadius: "8px",
                  padding: "16px",
                }}
              >
                <h3 style={{ marginTop: 0 }}>保有銘柄数</h3>
                <p style={{ fontSize: "24px", fontWeight: "bold", margin: 0 }}>
                  {summary.positionCount}
                </p>
              </div>
            </section>
          )}

          <section style={{ marginBottom: "32px" }}>
            <h3>現在のポジション</h3>

            {positions.length === 0 ? (
              <p>保有ポジションがありません</p>
            ) : (
              <table
                border={1}
                cellPadding={8}
                style={{ borderCollapse: "collapse", width: "100%" }}
              >
                <thead>
                  <tr>
                    <th>ID</th>
                    <th>銘柄</th>
                    <th>方向</th>
                    <th>数量</th>
                    <th>平均単価</th>
                    <th>現在価格</th>
                    <th>含み損益</th>
                    <th>状態</th>
                    <th>建玉日時</th>
                    <th>操作</th>
                  </tr>
                </thead>
                <tbody>
                  {positions.map((position) => {
                    const pl = findPl(position);

                    return (
                      <tr key={position.id}>
                        <td>{position.id}</td>
                        <td>{position.symbol}</td>
                        <td>{position.positionType}</td>
                        <td>{position.quantity}</td>
                        <td>{position.avgPrice}</td>
                        <td>{pl?.currentPrice ?? "-"}</td>
                        <td>{pl?.profitLoss ?? "-"}</td>
                        <td>{position.status}</td>
                        <td>{position.openedAt}</td>
                        <td>
                          <button
                            onClick={() => closePosition(position)}
                            disabled={closingPositionId === position.id}
                          >
                            {closingPositionId === position.id
                              ? "決済中..."
                              : position.positionType === "LONG"
                              ? "SELLで決済"
                              : "COVERで決済"}
                          </button>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            )}
          </section>

          <section>
            <h3>含み損益</h3>

            {positionPlList.length === 0 ? (
              <p>損益表示対象のポジションがありません</p>
            ) : (
              <table
                border={1}
                cellPadding={8}
                style={{ borderCollapse: "collapse", width: "100%" }}
              >
                <thead>
                  <tr>
                    <th>銘柄</th>
                    <th>方向</th>
                    <th>数量</th>
                    <th>平均単価</th>
                    <th>現在価格</th>
                    <th>含み損益</th>
                  </tr>
                </thead>
                <tbody>
                  {positionPlList.map((item) => (
                    <tr key={`${item.symbol}-${item.positionType}`}>
                      <td>{item.symbol}</td>
                      <td>{item.positionType}</td>
                      <td>{item.quantity}</td>
                      <td>{item.avgPrice}</td>
                      <td>{item.currentPrice}</td>
                      <td>{item.profitLoss}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </section>
        </>
      )}
    </div>
  );
}

export default MyTradesPage;