import { useEffect, useState } from "react";

type SignalStatus = "NEW" | "EXECUTED";
type TradeType = "BUY" | "SELL" | "SHORT" | "COVER";

type Signal = {
  id: number;
  symbol: string;
  type: TradeType;
  quantity: number;
  price: number;
  reason: string;
  status: SignalStatus;
  createdAt: string;
  executedAt: string | null;
};

type SignalCreateRequest = {
  symbol: string;
  type: TradeType;
  quantity: number;
  price: number;
  reason: string;
};

function SignalsPage() {
  const [signals, setSignals] = useState<Signal[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const [form, setForm] = useState<SignalCreateRequest>({
    symbol: "",
    type: "BUY",
    quantity: 100,
    price: 0,
    reason: "",
  });

  const fetchSignals = async () => {
    try {
      setLoading(true);
      setError("");

      const response = await fetch("http://localhost:8080/signals");
      if (!response.ok) {
        throw new Error("シグナル取得に失敗しました");
      }

      const data: Signal[] = await response.json();
      setSignals(data);
    } catch (err) {
      console.error(err);
      setError("シグナル一覧の取得でエラーが発生しました");
    } finally {
      setLoading(false);
    }
  };

  const executeSignal = async (id: number) => {
    try {
      const response = await fetch(`http://localhost:8080/signals/${id}/execute`, {
        method: "POST",
      });

      if (!response.ok) {
        const message = await response.text();
        throw new Error(message || "シグナル実行に失敗しました");
      }

      await fetchSignals();
      alert("シグナルを実行しました");
    } catch (err) {
      console.error(err);
      alert("シグナル実行でエラーが発生しました");
    }
  };

  const createSignal = async (e: React.FormEvent) => {
    e.preventDefault();

    try {
      const response = await fetch("http://localhost:8080/signals", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(form),
      });

      if (!response.ok) {
        const message = await response.text();
        throw new Error(message || "シグナル登録に失敗しました");
      }

      setForm({
        symbol: "",
        type: "BUY",
        quantity: 100,
        price: 0,
        reason: "",
      });

      await fetchSignals();
      alert("シグナルを登録しました");
    } catch (err) {
      console.error(err);
      alert("シグナル登録でエラーが発生しました");
    }
  };

  useEffect(() => {
    fetchSignals();
  }, []);

  return (
    <div>
      <h2>おすすめ株 / Signal</h2>

      <section
        style={{
          marginBottom: "32px",
          padding: "16px",
          border: "1px solid #ccc",
          borderRadius: "8px",
        }}
      >
        <h3>Signal登録</h3>

        <form onSubmit={createSignal}>
          <div style={{ display: "grid", gap: "12px", maxWidth: "480px" }}>
            <input
              type="text"
              placeholder="銘柄コード"
              value={form.symbol}
              onChange={(e) => setForm({ ...form, symbol: e.target.value })}
            />

            <select
              value={form.type}
              onChange={(e) =>
                setForm({ ...form, type: e.target.value as TradeType })
              }
            >
              <option value="BUY">BUY</option>
              <option value="SELL">SELL</option>
              <option value="SHORT">SHORT</option>
              <option value="COVER">COVER</option>
            </select>

            <input
              type="number"
              placeholder="数量"
              value={form.quantity}
              onChange={(e) =>
                setForm({ ...form, quantity: Number(e.target.value) })
              }
            />

            <input
              type="number"
              step="0.01"
              placeholder="価格"
              value={form.price}
              onChange={(e) =>
                setForm({ ...form, price: Number(e.target.value) })
              }
            />

            <input
              type="text"
              placeholder="理由"
              value={form.reason}
              onChange={(e) => setForm({ ...form, reason: e.target.value })}
            />

            <button type="submit">Signalを登録</button>
          </div>
        </form>
      </section>

      <section>
        <h3>Signal一覧</h3>

        {loading && <p>読み込み中...</p>}
        {error && <p style={{ color: "red" }}>{error}</p>}

        {!loading && signals.length === 0 && <p>シグナルがありません</p>}

        {!loading && signals.length > 0 && (
          <table border={1} cellPadding={8} style={{ borderCollapse: "collapse", width: "100%" }}>
            <thead>
              <tr>
                <th>ID</th>
                <th>銘柄</th>
                <th>種別</th>
                <th>数量</th>
                <th>価格</th>
                <th>理由</th>
                <th>状態</th>
                <th>操作</th>
              </tr>
            </thead>
            <tbody>
              {signals.map((signal) => (
                <tr key={signal.id}>
                  <td>{signal.id}</td>
                  <td>{signal.symbol}</td>
                  <td>{signal.type}</td>
                  <td>{signal.quantity}</td>
                  <td>{signal.price}</td>
                  <td>{signal.reason}</td>
                  <td>{signal.status}</td>
                  <td>
                    {signal.status === "NEW" ? (
                      <button onClick={() => executeSignal(signal.id)}>実行</button>
                    ) : (
                      <span>実行済み</span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </section>
    </div>
  );
}

export default SignalsPage;