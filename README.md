# デモトレードアプリ

## アプリ概要

相場状況をもとに、局面ごとに異なる戦略を試し、その結果を履歴として残して検証するデモトレードアプリです。

- 強気相場では、すでに強さが確認できた安定株に順張りで乗る
- 下降相場では、崩れや再下落の兆候を見て日経平均mini売りを検討する
- ボックス相場では、方向を当てにいかず、停滞を前提に売りストラドルを検討する

また、毎日大量の銘柄を人手で監視するのは難しいため、Python による条件抽出を使っておすすめ株候補を一覧化し、売買判断を補助する構成を目指しています。

---

## このアプリを作ろうと思ったきっかけ

私は、誰しもが毎日主要銘柄を数百種類モニタリングし、記録を取り続ければ、相場の法則が見えてきて投資判断の精度を上げられると考えています。

ただし、それを個人で継続するのは現実的に難しいため、代わりに監視・記録・抽出をしてくれるサイトがあれば便利だと思い、このアプリを作り始めました。

---

## ディレクトリ構成


demo-trade-app/
├─ backend/ # Spring Boot
├─ frontend/ # React
├─ python/ # 銘柄抽出・シグナル判定
├─ docker-compose.yml
└─ README.md


---

## 技術構成

### バックエンド
- Java 21
- Spring Boot
- Spring Data JPA
- PostgreSQL
- Docker

### フロントエンド
- React
- TypeScript
- Vite
- React Router

### Python
- yfinance
- pandas
- JSON出力

---

## フロントエンド

### 役割
- APIデータの可視化
- 売買操作
- 履歴確認
- シグナルの可視化

---

## ページ構成

### Topページ
- 相場シグナル（BULL / BEAR / BOX）表示
- 取引方針の提示

---

### おすすめ株ページ


Python → signals_output.json
↓
Spring Boot → /market-signals/latest
↓
React → 表示


- 銘柄コード
- 会社名
- 現在価格
- 理由
- シグナル種別

→ BUY可能

---

### 日経平均mini売りページ

- BEARシグナル表示
- 売り判断補助


SHORT（売り建て）


- シグナルなしでも取引可能
- signalType = NONE で記録

---

### 売りストラドルページ

- BOXシグナル表示
- 停滞相場向け戦略


SHORT（売り建て）


---

### My取引ページ

- 現在ポジション
- 含み損益
- 合計損益


LONG → SELL
SHORT → COVER


---

### 取引履歴ページ

- 全取引履歴

保持情報：

- tradeType
- signalType
- entryReason

---

## シグナルの考え方

このアプリでは、シグナルは「売買候補」ではなく


相場局面を表す情報


として扱います。

### 種類

- 強気シグナル（BULL）
- 下降シグナル（BEAR）
- ボックスシグナル（BOX）

---

## エンティティ設計

### Trade
売買履歴

- symbol
- tradeType（BUY / SELL / SHORT / COVER）
- quantity
- price
- tradeDate
- signalType
- entryReason

---

### Position
保有状態

- LONG
- SHORT

---

### DailyPrice
価格履歴


UNIQUE(symbol, price_date)


---

## API一覧

### Trade
- GET /trades
- POST /trades

### Position
- GET /positions
- GET /positions/pl
- GET /positions/pl/summary

### Market Signal
- GET /market-signals/latest

---

## Pythonスクリプト

`python/pick_stocks.py`

役割：

- おすすめ株抽出
- 相場シグナル判定
- JSON生成

---

## 現在の実装機能

### バックエンド
- Trade保存
- Position更新
- 含み損益計算

### フロント
- 各ページ表示
- 売買操作

### Python
- 銘柄抽出
- シグナル判定

---

## 今後やりたいこと

- シグナルロジック改善
- シグナル別成績分析
- Lambdaによる自動化
- オプション取引強化
- AWS移行

---

## 起動方法

### バックエンド
```bash
docker compose up -d
./mvnw spring-boot:run
フロントエンド
cd frontend
npm install
npm run dev
今後の方向性
シグナルあり vs シグナルなし
の成績比較