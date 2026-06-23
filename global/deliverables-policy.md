# 成果物・アプローチポリシー

## 1. リンク品質ルール（最重要）

### 1.1 必須形式
- **Markdownリンク `[表示名](URL)` 形式のみ許可**。plain text URL は違反。
- URL は以下のいずれか：
  - **Markdown / コード / テキスト**: `https://github.com/OWNER/REPO/blob/BRANCH/path/to/file.ext`
  - **PPT / PDF / DOCX / XLSX 等バイナリ**: 同じ `/blob/` パス（GitHub UIが自動ビューワを起動）。`?raw=true` や `raw.githubusercontent.com` は使わない。
  - **画像（PNG/JPG）**: `/blob/` パス（プレビュー表示される）
  - **ディレクトリ**: `/tree/BRANCH/path` 形式

### 1.2 違反例（NG）
- `https://github.com/...` をそのまま plain text 記載 → NG
- `https://github.com/OWNER/REPO` のみ（リポジトリトップ）→ NG
- `/blob/master/...` だが実ブランチが `main` → 404、NG
- push する前に URL を記載 → 404、NG
- `raw.githubusercontent.com/.../file.pptx` → プレビュー不可、NG

### 1.3 検証プロトコル（報告前に必ず実行）
報告前にすべてのリンクで以下を実行：

```powershell
# 方法A（gh CLI 認証済み時）
gh api repos/OWNER/REPO/contents/PATH?ref=BRANCH 2>$null; if ($?) { "OK" } else { "NG" }

# 方法B（gh CLI 未認証・パブリックリポ — KazuyaMurayama/NASDAQ_backtest はこちらを使用）
(Invoke-WebRequest -Uri "https://api.github.com/repos/OWNER/REPO/contents/PATH?ref=BRANCH" -UseBasicParsing -ErrorAction SilentlyContinue).StatusCode -eq 200
```

すべて `OK` / `True` を確認してから報告メッセージを送る。
- プライベートリポの場合は権限の有無をURLと併記（例: 「※閲覧にはGitHubアカウントの権限が必要」）。

### 1.4 URL生成の正規手順
1. `git status` で uncommitted が無いことを確認
2. `git push` 完了
3. `git remote get-url origin` → OWNER/REPO 抽出
4. `git rev-parse --abbrev-ref HEAD` → BRANCH 取得
5. ファイル相対パスを取得（`git ls-files <pattern>`）
6. URL 組み立て: `https://github.com/{OWNER}/{REPO}/blob/{BRANCH}/{PATH}`
7. 1.3 で検証（OK 確認）
8. Markdownリンク化して3列表に記載

### 1.5 失敗時の自己修正
- 404やリンク切れをユーザーに指摘されたら、謝罪より先に検証＆訂正：
  1. 即座に 1.3 のコマンドで全リンク再検証
  2. 訂正版を3列表で再提示
  3. 原因を1行で報告（例:「ブランチ名が master ではなく main でした」）
- 同セッション内で2回以上 404 を出した場合、以降は全リンクを必ず方法Aで事前検証してから提示。

## 2. 成果物の3列表テンプレート

```markdown
| 成果物 | 説明 | リンク |
|---|---|---|
| report.md | 月次売上レポート | [開く](https://github.com/USER/repo/blob/main/reports/2026-05/report.md) |
| slides.pptx | 提案資料 | [開く](https://github.com/USER/repo/blob/main/slides/proposal.pptx) |
```

複数ファイルでもすべて表に列挙する。「ほか3ファイル」のような省略は禁止。

## 3. ファイル形式別の規約

### 3.1 Word (.docx)
- ページ番号を右下に追加。

### 3.2 PowerPoint (.pptx)
- GitHub UIで自動プレビュー可能なため `/blob/` URL で問題なし。
- ファイルサイズが100MB超の場合は Git LFS を検討。

### 3.3 Markdown
- GitHub Flavored Markdown 準拠。
- 画像参照は相対パス推奨（リポジトリ内移動でも壊れない）。

## 4. エージェントチーム編成（大タスク時）
フェーズ別構成で議論しクオリティ向上：
- スコープ定義: アーキテクト + PM
- 調査: リサーチャー + アナリスト
- 実装: 開発者 + テスター
- レビュー: セキュリティ + コードレビュー
- レポーティング: ドキュメンター（**リンク検証プロトコル 1.3 を必ず実行**）

## 5. チェックリスト（報告直前に必ず確認）
- [ ] すべての成果物が3列表に列挙されている
- [ ] すべてのリンクが `[表示名](URL)` 形式
- [ ] すべてのURLが `/blob/<実ブランチ>/` 形式
- [ ] すべてのURLを 1.3 のコマンドで OK 確認済み
- [ ] push完了済み（未pushファイルが無い）
- [ ] ブランチ名は `git rev-parse --abbrev-ref HEAD` の実値
## レポート・ドキュメント生成時の日付記載ルール

### 必須記載項目
レポート系 .md ファイルを新規生成する際は、H1タイトル直下に必ず以下を記載する:

```
作成日: YYYY-MM-DD
最終更新日: YYYY-MM-DD
```

### 更新時のルール
- 既存ファイルを更新する際は **最終更新日のみ** を当日付に書き換える
- 作成日は変更しない（作成時の日付に固定）

### 対象ファイル
- 分析レポート・調査結果・提案書・議事録など「時点の情報」を含む文書
- 除外: README.md / CLAUDE.md / FILE_INDEX.md / tasks.md / CHANGELOG.md / LICENSE.md

### ファイル名規則（v2.0 / 2026-06-03 改訂）

#### 基本形式
- `<TOPIC>_YYYYMMDD.md`（**サフィックス・ハイフンなし**・作成日を反映）
  - 例: `STRATEGY_COMPARISON_20260603.md`、`MONTHLY_REPORT_20260603.md`

#### 同日中の追加更新（バージョン管理）
同名ファイルを上書きせず、別ファイルとして残す場合:
- 1回目: `<TOPIC>_20260603.md`
- 2回目: `<TOPIC>_20260603-v2.md`
- 3回目: `<TOPIC>_20260603-v3.md`

#### 日付が変わったらリセット
- 翌日1回目: `<TOPIC>_20260604.md`（v なし）
- 翌日2回目: `<TOPIC>_20260604-v2.md`

#### 表記の区別
- **ファイル名**: ハイフン**なし** `YYYYMMDD`（例: `20260603`）
- **本文中の日付表記**: ハイフン**あり** `YYYY-MM-DD`（例: `2026-06-03`）

#### 旧形式（廃止・新規禁止）
- ❌ `2026-05-08_report-name.md`（プレフィックス・ハイフン区切り — 旧ISO 8601形式）
- ❌ `report-name_2026-05-08.md`（サフィックス・ハイフン区切り）
- ✅ `report-name_20260508.md`（**現行ルール**）

#### 対象外
- README.md / CLAUDE.md / FILE_INDEX.md / tasks.md / CHANGELOG.md / LICENSE.md / SPEC.md / HYPOTHESES.md
- `CURRENT_*.md`（常に最新で参照される単一ファイル）
- パイプライン自動生成ファイル（例: `REPORT.md`、`outputs/*.md`）

## 6. ファクトチェックルール（UI・設定・コマンド記述時）
- UIパス・設定名・コマンドを記述する前に WebFetch/WebSearch で公式ドキュメントを確認。
- 確認できない場合は「[要確認: 公式ドキュメントで検証してください]」と明記し、推測で記載しない。
- 他ツール・IDEの慣習を流用しない（例: VS CodeのUIパターンをWarpに適用しない）。

## 7. OS・環境制約の遵守
- タスク開始時に「OS」「言語」「ツール」等の制約を明示的に抽出する（例: "Windows専用"）。
- ドキュメント完成後: `brew` / `Cmd` / `Option` / `macOS` / `Finder` をgrepし、違反記述を除去。
- 制約が明示されていない場合も、環境の前提（Windowsなら `winget`/`Ctrl`/`PowerShell` 等）を確認してから記述。
