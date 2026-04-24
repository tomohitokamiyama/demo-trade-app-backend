import { Link, Route, Routes } from "react-router-dom";
import TopPage from "./pages/TopPage";
import SignalsPage from "./pages/SignalsPage";
import MyTradesPage from "./pages/MyTradesPage";
import TradesPage from "./pages/TradesPage";
import RecommendedStocksPage from "./pages/RecommendedStocksPage";
import NikkeiMiniShortPage from "./pages/NikkeiMiniShortPage";
import ShortStraddlePage from "./pages/ShortStraddlePage";

function App() {
  return (
    <div style={{ fontFamily: "sans-serif" }}>
      <header
        style={{
          padding: "16px 24px",
          borderBottom: "1px solid #ddd",
          marginBottom: "24px",
        }}
      >
        <h1 style={{ margin: 0, marginBottom: "12px" }}>デモトレードアプリ</h1>

        <nav style={{ display: "flex", gap: "16px", flexWrap: "wrap" }}>
          <Link to="/">Top</Link>
          <Link to="/recommended-stocks">おすすめ株</Link>
          <Link to="/nikkei-mini-short">日経mini売り</Link>
          <Link to="/short-straddle">売りストラドル</Link>
          <Link to="/signals">Signal</Link>
          <Link to="/my-trades">My取引</Link>
          <Link to="/trades">取引履歴</Link>
        </nav>
      </header>

      <main style={{ padding: "0 24px 24px" }}>
        <Routes>
          <Route path="/" element={<TopPage />} />
          <Route path="/recommended-stocks" element={<RecommendedStocksPage />} />
          <Route path="/nikkei-mini-short" element={<NikkeiMiniShortPage />} />
          <Route path="/short-straddle" element={<ShortStraddlePage />} />
          <Route path="/signals" element={<SignalsPage />} />
          <Route path="/my-trades" element={<MyTradesPage />} />
          <Route path="/trades" element={<TradesPage />} />
        </Routes>
      </main>
    </div>
  );
}

export default App;