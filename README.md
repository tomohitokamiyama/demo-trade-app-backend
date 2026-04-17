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

### 進捗度
完成形の認識

最終的には、「日次価格データを自動取得し、それをもとにおすすめ株を出し、仮想売買と損益確認までできるWebアプリ」 です。

流れでいうとこうです。

Lambda + EventBridge で日次価格取得
yfinance系ソースから価格取得
S3 / RDS に保存
Spring Boot が業務APIを提供
React が画面表示
おすすめ株抽出結果を Signal に登録
Signal を実行すると Trade / Position が更新
Position と DailyPrice から損益確認

つまり完成形は、データ取得基盤 + 売買管理 + 表示UI がつながった状態です。

今の現在地の認識

今は バックエンドのコア部分がかなりできている段階 です。

実装済みとして認識しているのはこれです。

できているもの
Signal 登録
Signal 一覧取得
Signal 個別実行
Signal 一括実行
Signal の NEW / EXECUTED 管理
重複実行防止
Trade 保存
Position 自動更新
LONG / SHORT 管理
OPEN / CLOSED 管理
DailyPrice テーブル作成
DailyPrice API
含み損益 API

つまり今は、

Signal → Trade → Position → DailyPrice → PL

のバックエンドの芯が通っています。

まだ未完成の部分

未完成として見ているのはこのへんです。

1. フロント
React 未接続
画面なし
2. 自動データ取得
Lambda 未実装
EventBridge 未実装
yfinance 取得結果の自動投入未接続
3. おすすめ株の自動連携
Pythonの抽出ロジックはある
でも Spring Boot の signals へ自動投入はまだ
4. 損益の広がり
今は含み損益のみ
合計損益
評価額
実現損益
損益推移
は未実装
5. 業務的な整え
例外ハンドリングの共通化
README 強化
テストコード強化
認証/ユーザー管理
はまだこれから
一言でいうと
完成形

自動で価格を取り込み、売買判断・仮想売買・損益確認までできるアプリ

現在

そのうち「売買管理と価格参照のバックエンドコア」はかなり完成している状態

体感でいう完成度

ざっくりですが、今の認識はこうです。

バックエンドコア: 70〜80%
アプリ全体: 45〜55%

理由は、コアロジックはかなりある一方で、

フロント
自動取得基盤
運用っぽい部分

がまだ残っているからです。

## ローカル起動方法

### PostgreSQL起動
```bash
docker compose up -d