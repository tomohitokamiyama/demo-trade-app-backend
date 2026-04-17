# Demo Trade App Backend

Spring Boot + PostgreSQL + Docker で開発している、デモトレードWebアプリのバックエンドです。  
シグナルに基づく売買、取引履歴、ポジション管理、日次価格管理、含み損益計算を実装しています。

## 技術構成

- Java 21
- Spring Boot
- PostgreSQL
- Docker
- Maven

## アプリ概要

デモトレードを行うためのバックエンドアプリです。  
シグナルを登録し、シグナル実行によって Trade を生成し、Position を自動更新する構成にしています。

将来的には以下のような画面を想定しています。

- Topページ: 相場感表示
- My取引ページ: ポジション、損益確認
- おすすめ株ページ: 上昇トレンド銘柄
- 日経平均売り建てページ: リバーサル時の売りシグナル表示
- オプション戦略ページ: 将来的に検討

## 設計方針

- API単位ではなくドメイン単位で分割
- Controller / Service / Repository を責務ごとに分離
- Position は Trade を起点に自動更新し、直接操作しない
- DailyPrice は履歴を保持し、最新値の上書きではなく蓄積する
- 日足データは `(symbol, price_date)` をユニーク制約で管理する

## ドメイン構成

- Signal
- Trade
- Position
- DailyPrice
- Instrument

## 現在の実装機能

### Signal
- Signal 一覧取得
- Signal 登録
- Signal 個別実行
- Signal 一括実行
- `NEW / EXECUTED` の状態管理
- 重複実行防止

### Trade
- Trade 履歴保存
- Trade 一覧取得

### Position
- Trade 実行時に Position を自動更新
- LONG / SHORT の管理
- OPEN / CLOSED の管理
- 平均単価方式で更新

### DailyPrice
- 日次価格テーブルを保持
- 銘柄別の日足履歴取得
- 最新価格参照のベースとして利用

### 損益
- 保有ポジションに対する含み損益を API で返却

## API一覧

### Signal
- `GET /signals`
- `GET /signals?status=NEW`
- `POST /signals`
- `POST /signals/{id}/execute`
- `POST /signals/execute`

### Trade
- `GET /trades`
- `POST /trades`

### Position
- `GET /positions`
- `GET /positions/pl`

### DailyPrice
- `GET /daily-prices`
- `GET /daily-prices?symbol=7203`

## 損益計算ルール

### LONG
(currentPrice - avgPrice) × quantity

### SHORT
(avgPrice - currentPrice) × quantity

## DB設計のポイント

### positions
- 現在の保有状態を表すテーブル
- 同一ユーザー、同一銘柄、同一方向の OPEN ポジションは1件

### trades
- 売買履歴を保存するテーブル
- Position 更新の起点となる

### daily_prices
- 1銘柄 × 1日 = 1レコード
- `UNIQUE(symbol, price_date)` を付与
- 5年高値判定やトレンド判定など、過去データの蓄積を前提に設計

## ローカル起動方法

### PostgreSQL起動
```bash
docker compose up -d