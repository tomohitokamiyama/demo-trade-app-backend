type RecommendationType = "STOCK" | "OPTION" | "FUTURE";
type MarketType = "UPTREND" | "BOX" | "DOWNTREND";

type TopRecommendation = {
  id: number;
  type: RecommendationType;
  marketType: MarketType;
  title: string;
  actionLabel: string;
  symbol: string;
  reason: string;
};

function TopPage() {
  const recommendations: TopRecommendation[] = [
    {
      id: 1,
      type: "STOCK",
      marketType: "UPTREND",
      title: "おすすめ株を買う",
      actionLabel: "BUY",
      symbol: "7203",
      reason: "5年高値更新",
    },
    {
      id: 2,
      type: "OPTION",
      marketType: "BOX",
      title: "オプションでストラドル",
      actionLabel: "SHORT STRADDLE",
      symbol: "N225",
      reason: "ボックス相場継続",
    },
    {
      id: 3,
      type: "FUTURE",
      marketType: "DOWNTREND",
      title: "日経平均miniを売る",
      actionLabel: "SELL MINI",
      symbol: "N225MINI",
      reason: "ワンポイントリバーサルデイ",
    },
  ];

  const marketLabelMap: Record<MarketType, string> = {
    UPTREND: "上昇トレンド",
    BOX: "ボックス相場",
    DOWNTREND: "下降トレンド",
  };

  return (
    <div>
      <section style={{ marginBottom: "32px" }}>
        <h2 style={{ marginBottom: "8px" }}>Topページ（相場感）</h2>
        <p style={{ marginTop: 0, color: "#555" }}>
          今日の相場状況に応じたおすすめ取引を確認できます。
        </p>
      </section>

      <section style={{ marginBottom: "32px" }}>
        <h3 style={{ marginBottom: "16px" }}>今日のおすすめ取引</h3>

        <div
          style={{
            display: "grid",
            gap: "16px",
            gridTemplateColumns: "repeat(auto-fit, minmax(260px, 1fr))",
          }}
        >
          {recommendations.map((item) => (
            <div
              key={item.id}
              style={{
                border: "1px solid #d9d9d9",
                borderRadius: "12px",
                padding: "20px",
                background: "#fff",
                boxShadow: "0 2px 8px rgba(0,0,0,0.05)",
              }}
            >
              <p style={{ margin: "0 0 8px 0", color: "#666" }}>
                {marketLabelMap[item.marketType]}
              </p>

              <h4 style={{ marginTop: 0, marginBottom: "16px" }}>{item.title}</h4>

              <div style={{ display: "grid", gap: "10px" }}>
                <div>
                  <p style={{ margin: "0 0 4px 0", color: "#666" }}>アクション</p>
                  <p style={{ margin: 0, fontWeight: "bold" }}>{item.actionLabel}</p>
                </div>

                <div>
                  <p style={{ margin: "0 0 4px 0", color: "#666" }}>対象</p>
                  <p style={{ margin: 0, fontWeight: "bold" }}>{item.symbol}</p>
                </div>

                <div>
                  <p style={{ margin: "0 0 4px 0", color: "#666" }}>理由</p>
                  <p style={{ margin: 0, fontWeight: "bold" }}>{item.reason}</p>
                </div>
              </div>

              <button style={{ marginTop: "16px" }}>詳細を見る</button>
            </div>
          ))}
        </div>
      </section>

      <section
        style={{
          border: "1px solid #d9d9d9",
          borderRadius: "12px",
          padding: "20px",
          background: "#fafafa",
        }}
      >
        <h3 style={{ marginTop: 0 }}>ページの見方</h3>
        <ul style={{ lineHeight: 1.8, paddingLeft: "20px", marginBottom: 0 }}>
          <li>上昇トレンドではおすすめ株の買い候補を表示</li>
          <li>ボックス相場ではオプション戦略候補を表示</li>
          <li>下降トレンドでは日経平均miniの売り候補を表示</li>
        </ul>
      </section>
    </div>
  );
}

export default TopPage;