# 🌈 やることリスト (kklab-flet-todo)

[Flet](https://flet.dev/)（Python）で作ったカラフルな日本語ToDoアプリです。
タスクの追加・編集・完了切り替え・削除・絞り込みができ、データはブラウザに永続化されます。

🔗 **公開URL**: https://katzkawai.github.io/kklab-flet-todo/ （カスタムドメイン: http://katzkawai.org/kklab-flet-todo/ ）

## 機能

- タスクの追加 / 編集 / 削除
- 完了・未完了のチェック切り替え
- 「すべて / 未完了 / 完了」での絞り込み表示
- 「完了済みを削除」で一括削除
- 残り件数の表示
- タスクごとにカラフルな背景色
- **データ永続化**: ブラウザの localStorage に保存され、リロードしてもタスクが残ります

## 技術スタック

- **言語**: Python 3.10+
- **フレームワーク**: Flet 0.85.2（Flutterベースの UI）
- **パッケージ管理**: [uv](https://github.com/astral-sh/uv)
- **配信**: GitHub Pages（Flet の Web ビルド = ブラウザ内 Python / Pyodide）

## ローカルでの実行

```bash
# 依存関係のインストール
uv sync

# アプリを起動（http://localhost:8080 で開きます）
uv run python main.py
```

起動するとサーバーモード（Python がローカルで動き、ブラウザが WebSocket で接続）で
http://localhost:8080/ にアクセスできます。停止は `Ctrl+C`。

## プロジェクト構成

```
kklab-flet-todo/
├── main.py            # アプリ本体（UI とロジック、データ永続化）
├── pyproject.toml     # プロジェクト定義・依存関係
├── uv.lock            # 依存のロックファイル
├── docs/              # GitHub Pages で配信する Web ビルド成果物
│   ├── index.html     # エントリーポイント（base href を設定）
│   ├── assets/app/app.zip   # アプリの Python コード一式（Pyodide が実行）
│   └── ...            # Flutter / Pyodide ランタイム
└── README.md
```

## データ永続化について

タスクは Flet の `SharedPreferences` サービス経由でブラウザの **localStorage** に保存されます
（キー: `kklab.todo.tasks.v1`）。そのため:

- 同じブラウザならリロード・再訪問してもタスクは残ります
- 別の端末・別のブラウザとはデータは共有されません
- ブラウザのサイトデータを消去すると消えます

---

## GitHub Pages の作成・更新手順

このリポジトリは **`main` ブランチの `/docs` フォルダ** を GitHub Pages の公開元にしています。
`http://katzkawai.org/kklab-flet-todo/` のように **サブパス配信** になる点が重要です。

### ビルド方式: `flet build web` と `flet publish` の違い

Flet で静的 Web サイトを作る方法は2つあります。**どちらもブラウザ内 Python（Pyodide）で動く**点は同じで、
違いは「ビルド方法」と「拡張性・カスタマイズ性」です。**このリポジトリは `flet build web` を使用しています。**

| 観点 | `flet publish`（軽量） | `flet build web`（フルビルド・本リポジトリ採用） |
|------|----------------------|------------------------------|
| 仕組み | `flet_web` 内の**プリビルド済み** Flutter 資産をコピー | Flutter プロジェクトを生成し **Flutter SDK でコンパイル** |
| **Flutter SDK** | **不要**（Python だけで完結） | **必要**（Flutter/Dart のインストールが前提） |
| ビルド速度 | 速い・軽い | 遅い・重い（初回は特に） |
| サードパーティ拡張 | ❌ 使えない（標準コントロールのみ） | ✅ **使える**（カスタム Flutter ウィジェット/Flet 拡張を同梱可能） |
| ビルド時カスタマイズ | 限定的 | アイコン・スプラッシュ・PWA 設定・フォント等を細かく指定可 |
| Web レンダラー選択 | 限定的 | `--web-renderer auto/canvaskit/skwasm` を選べる |
| 位置づけ | 旧来の方式 | **現在の推奨・主流** |

**`flet build web` を選ぶ利点**

1. **サードパーティの Flet 拡張が使える**（最大の差）。標準にない Flutter ウィジェットを組み込める。
2. **見た目・メタ情報のカスタマイズ**（アプリ名/説明、アイコン、スプラッシュ、PWA テーマ色など）。
   実際 `docs/` の `splash/`・`icons/`・`manifest.json` はこの機能で生成されたもの。
3. **レンダラーや最適化を選べる**（本物の Flutter コンパイルのため）。
4. **将来性・一貫性**。アクティブにメンテされている主流パス。

**`flet publish` を選ぶ利点**

- **Flutter SDK が不要**で環境構築が楽・速い。CI やちょっとした静的公開に手軽。

**このアプリにとっての結論**

現状は**標準コントロールのみ**なので `build` でも `publish` でも**動作・機能は実質同じ**です。それでも `build`
を採用しているのは、(1) 今後の拡張ウィジェットや凝ったアイコン/スプラッシュ/PWA 化に備えられること、
(2) すでに `docs/` が `build` 構造なので**方式を統一**しておくと `index.html` の設定差による不具合
（base href 問題など）を避けられること、が理由です。
途中で方式を切り替えると成果物構造が変わるため、その際は `docs/` を作り直してください。

> 補足: Pyodide（ブラウザ内 Python）はどちらでも必要です。初回ロードの重さや Python の実行速度を
> 改善したい場合は、静的配信ではなくサーバーモード（`flet serve` 等を Python が動くホストにデプロイ）が選択肢になります。

### なぜ Pyodide + 静的ホスティングなのか

Pyodide（ブラウザ内 Python）の最大の利点は、**サーバー側で Python を動かす環境が不要になること**です。
そこから次のメリットが得られます。

1. **無料の静的ホスティングで公開できる** — GitHub Pages 等にファイルを置くだけ。Python サーバーの用意・契約が不要。
2. **運用コスト・保守がほぼゼロ** — 常時稼働サーバーがないので、費用・アップデート・障害対応・スケール設定が不要。
3. **自動的にスケールする** — 処理は各利用者のブラウザで動くため、アクセスが増えてもサーバー負荷が増えない。
4. **プライバシー・オフライン性** — データや計算がブラウザ内で完結する（本アプリの localStorage 永続化のように外部送信なし）。

一方で、サーバーモードと比べた弱点もあります。

| 項目 | Pyodide（ブラウザ内） | サーバーモード |
|------|----------------------|----------------|
| 初回ロード | **重い**（Pyodide 本体＋WASM で数MB〜十数MB DL） | 軽い |
| 実行速度 | ネイティブ Python より遅め | サーバーの CPU で高速 |
| 使えるライブラリ | WASM 対応 or 純 Python に限られる（一部の C 拡張は不可） | 何でも可（DB, NumPy 系, 任意） |
| 秘密情報・API キー | **置けない**（全てクライアントに渡る） | サーバー側に安全に保持できる |
| 共有 DB・サーバー処理 | 不可（各ブラウザで独立） | 可（中央 DB、認証、課金処理など） |

**結論**: 本アプリは「個人向けで、データもローカルで完結する小さなアプリ」なので、Pyodide + GitHub Pages が最適です。
逆に「複数ユーザーでデータを共有」「サーバー側で秘密情報を扱う」「重い計算をする」場合はサーバーモードが向いています。

### 1. Web ビルドを生成する

Flet の Web ビルドは Flutter SDK を使うため、初回は [Flet のビルド要件](https://flet.dev/docs/publish/web/static-website/)
（Flutter SDK 等）を満たしておきます。サブパス配信なので **`--base-url` にリポジトリ名を指定する**のが必須です。

```bash
# 出力先 build/web に、base href = /kklab-flet-todo/ で生成される
uv run flet build web --base-url kklab-flet-todo
```

### 2. 成果物を docs/ に配置する

```bash
rm -rf docs
cp -r build/web docs
touch docs/.nojekyll          # Jekyll 処理を無効化（pyodide 等のフォルダ対策）
```

### 3. app.zip のサイズに注意（重要）

`docs/assets/app/app.zip` にはアプリの Python コードが入りますが、**ビルド環境の `.venv` や
`.git` が誤って同梱されると 100MB を超え、GitHub にプッシュできず Pages も配信できません**。
中身を確認し、不要物が入っていたら除去します（必要なのは `main.py` と `__pypackages__/` など）。

```bash
# 中身の確認（.venv や .git が無いこと、サイズが小さいことを確認）
unzip -l docs/assets/app/app.zip | tail -5

# 万一 .venv / .git が混入していたら除去
zip -d docs/assets/app/app.zip ".venv/*" ".git/*" "build/*"
```

### 4. コミット & プッシュ

```bash
git add docs
git commit -m "Update GitHub Pages web build"
git push origin main
```

### 5. GitHub 側の設定（初回のみ）

リポジトリの **Settings → Pages** で以下を設定します。

- **Source**: `Deploy from a branch`
- **Branch**: `main` / フォルダ `/docs`
- （任意）**Custom domain**: `katzkawai.org`

プッシュ後、数分でビルドが走り公開されます。ビルド状況は次で確認できます。

```bash
gh api repos/katzkawai/kklab-flet-todo/pages/builds/latest
```

### トラブルシューティング

| 症状 | 原因 | 対処 |
|------|------|------|
| 画面が真っ白 / リソースが 404 | `base href` がルート `/` のまま | `--base-url kklab-flet-todo` でビルド、または `docs/index.html` の `<base href>` を `/kklab-flet-todo/` に修正 |
| `git push` が拒否される | `app.zip` が 100MB 超（`.venv` 混入） | 上記「3.」で `.venv`/`.git` を除去 |
| アプリは出るがデータが消える | localStorage 未保存 | `SharedPreferences` の利用を確認（本リポジトリは対応済み） |
| 更新したのに古い版が表示される | ブラウザの HTTP キャッシュ（後述） | スーパーリロード or シークレット or 10分待つ |

### キャッシュについて（「更新が反映されない」とき）

「スーパーリロードでは直るが、再アクセスすると古い版に戻る」場合、原因はほぼ **ブラウザの HTTP キャッシュ**です。
GitHub Pages のキャッシュは3層あり、本リポジトリでの実測結果は次の通りです。

| 層 | 場所 | 本リポジトリの状態 | 対処 |
|----|------|-------------------|------|
| ① GitHub の CDN（Fastly） | GitHub 側 | TTL 約10分。手動 purge 不可 | 再デプロイ（空コミット可）で更新 |
| ② Service Worker | ブラウザ | **登録0個**（自己解除型で無害） | 通常は対処不要 |
| ③ ブラウザ HTTP キャッシュ | ブラウザ | 全ファイル `Cache-Control: max-age=600`（10分） | スーパーリロード / シークレット / DevTools の Disable cache |

**ポイント**

- **Service Worker は原因ではありません**。本アプリの `flutter_service_worker.js` は `fetch` ハンドラを持たず、
  `activate` で自分自身を `unregister()` する「自己解除型」です（実測でも登録0個・Cache Storage 空）。
- 古い版が出る正体は **③ の HTTP キャッシュ（`max-age=600`）**。GitHub Pages はこの `Cache-Control`
  ヘッダを**変更できない**ため、リピート訪問者には最大10分間、古い版がブラウザキャッシュから配信されます。
- ただし **10分経てば etag 再検証で自動的に最新化**されるので、古い版が永久に固定されることはありません。

**開発・確認時のおすすめ**

```text
- DevTools (F12) → Network → ☑ Disable cache  … 開発中はこれが最も確実
- シークレット / プライベートウィンドウで開く … キャッシュの影響を受けない
- 10分待つ … 放置でも自動的に最新化される
```

GitHub の配信内容そのものを直接確認したいときは、キャッシュ回避クエリ付きで取得します。

```bash
curl -sIL "https://katzkawai.github.io/kklab-flet-todo/?cb=$(date +%s)" | grep -iE "^HTTP|cache-control|etag"
```

**即時反映が必須な場合**

`max-age=600` の10分が許容できない場合、GitHub Pages ではヘッダを制御できないため、
`_headers` ファイルでキャッシュ制御できる **Cloudflare Pages** や **Netlify** へ同じ `docs/` を配信するのが確実です
（例: `index.html` は `no-cache`、ハッシュ付き資産は長期キャッシュ）。
