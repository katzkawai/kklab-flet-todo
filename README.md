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
