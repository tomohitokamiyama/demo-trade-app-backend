# Demo Trade App

Spring Boot + PostgreSQL + Docker + React で開発している、デモトレードWebアプリです。  
相場状況に応じたおすすめ取引の表示、売買履歴管理、保有ポジション管理、含み損益確認ができる構成を目指しています。

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

## アプリ概要

相場状況をもとに、おすすめ株・日経平均mini売り・オプション戦略などの取引候補を提示し、  
実際の売買履歴や保有ポジション、損益を確認できるデモトレードアプリです。

## 現在の画面構成

- Topページ
- おすすめ株ページ
- My取引ページ
- 取引履歴ページ

## ページ概要

### Topページ
- 上昇トレンド
- ボックス相場
- 下降トレンド

の3つの相場パターンを前提に、おすすめ取引の方向性を表示します。

### おすすめ株ページ
Python で抽出した安定株候補を表示することを想定したページです。  
現時点では仮データを用いて、候補銘柄を一覧表示し、売買フローにつなげるUIを作成しています。

### My取引ページ
- 現在保有しているポジション
- 含み損益
- 保有銘柄数
- 合計含み損益

を確認できます。

### 取引履歴ページ
実際に行った取引履歴を確認できます。  
取引には `signalType` と `entryReason` を保持しており、

- 相場シグナルが出ていた時に行った取引
- シグナルが出ていない状態で行った取引

を比較しやすい構成にしています。

## ドメインの考え方

### Signal
このアプリにおけるシグナルは、以下の3種類の相場シグナルを想定しています。

- 強気相場シグナル
- 下降シグナル
- ボックスシグナル

### Trade
実際に行った売買履歴です。  
`signalType` と `entryReason` を持たせることで、  
その取引がどの相場シグナルに基づいて行われたか、あるいはシグナルなしで行われたかを後から確認できるようにしています。

### Position
Trade の結果として現在保有している状態です。

### DailyPrice
日次価格データを保持するテーブルです。  
価格履歴を蓄積し、現在価格や含み損益計算の元データとして使用します。

## 現在の実装機能

### バックエンド
- Signal 一覧取得
- Signal 登録
- Signal 実行
- Trade 保存
- Position 自動更新
- DailyPrice 参照
- 含み損益 API
- 損益サマリ API
- 取引履歴に `signalType` / `entryReason` を保持

### フロントエンド
- Topページ表示
- おすすめ株ページ表示
- My取引ページ表示
- 取引履歴ページ表示
- 画面からの Signal 登録・実行
- API 連携による Position / 損益 / 履歴表示

## API 一覧

## バックエンド主要クラス一覧

### エントリーポイント
- `DemoTradeAppApplication.java`  
  Spring Boot の起動クラス

### Signal関連
- `Signal.java`  
  Signal エンティティ。売買候補データを保持するクラス
- `SignalStatus.java`  
  Signal の状態（NEW / EXECUTED）を表す enum
- `SignalRepository.java`  
  Signal テーブルにアクセスする Repository
- `SignalService.java`  
  Signal の取得・登録・TradeRequest 変換を担当
- `SignalExecutionService.java`  
  Signal 実行処理を担当し、Trade 作成までつなぐ
- `SignalController.java`  
  Signal API を提供する Controller
- `SignalCreateRequest.java`  
  Signal 登録時のリクエストDTO

### Trade関連
- `Trade.java`  
  実際に行った売買履歴を保持するエンティティ
- `TradeType.java`  
  売買種別（BUY / SELL / SHORT / COVER）を表す enum
- `SignalType.java`  
  相場シグナル種別（BULL / BEAR / BOX / NONE）を表す enum
- `TradeRequest.java`  
  Trade 作成時のリクエストDTO
- `TradeRepository.java`  
  Trade テーブルにアクセスする Repository
- `TradeService.java`  
  Trade 保存処理と Position 更新連携を担当
- `TradeController.java`  
  Trade API を提供する Controller

### Position関連
- `Position.java`  
  現在保有しているポジションを保持するエンティティ
- `PositionType.java`  
  ポジション方向（LONG / SHORT）を表す enum
- `PositionStatus.java`  
  ポジション状態（OPEN / CLOSED）を表す enum
- `PositionRepository.java`  
  Position テーブルにアクセスする Repository
- `PositionService.java`  
  Position の更新・取得・含み損益計算を担当
- `PositionController.java`  
  Position API を提供する Controller
- `PositionPlResponse.java`  
  含み損益表示用のレスポンスDTO
- `PositionPlSummaryResponse.java`  
  含み損益サマリ表示用のレスポンスDTO

### DailyPrice関連
- `DailyPrice.java`  
  日次価格データを保持するエンティティ
- `DailyPriceRepository.java`  
  DailyPrice テーブルにアクセスする Repository
- `DailyPriceService.java`  
  日次価格取得ロジックを担当
- `DailyPriceController.java`  
  DailyPrice API を提供する Controller

### Instrument関連
- `Instrument.java`  
  銘柄情報を表すクラス
- `InstrumentService.java`  
  銘柄情報の取得処理を担当
- `InstrumentController.java`  
  銘柄情報 API を提供する Controller

## DB設計のポイント

### daily_prices
1銘柄 × 1日 = 1レコードで管理しています。

- `UNIQUE(symbol, price_date)`

を付与し、同じ日の価格データを二重登録しないようにしています。  
履歴を残す設計にしており、5年高値判定やトレンド判定に活用できる形を意識しています。

### trade
売買履歴テーブルです。  
以下の情報を持たせています。

- symbol
- tradeType
- quantity
- price
- tradeDate
- signalType
- entryReason

これにより、後から履歴を見たときに、  
「シグナルが出ていたから売買したのか」  
「シグナルが出ていないのに売買したのか」  
を比較しやすくしています。

## ローカル起動方法

### バックエンド
```bash
docker compose up -d
./mvnw spring-boot:run