# TODO — 卒業論文（案B）

_Last updated: 2026-07-07 / session: 矢印演出をB案（伸びて→再入場）へ刷新（3デッキ共通・時差付き）。main 統合済み_

## 🔥 最優先タスク（先行研究調査の深掘り・2026-07-07 追加）
- What: **識別戦略まわりの先行研究調査を深める**。方法論学習セッションの引き継ぎメモ `tasks/先行研究_識別戦略ハンドオフ_20260707.md` を**まず読む**。
- なぜ最優先: 識別が脆弱（β exposure-robust p=0.089）で「類例なし」と断念しかけた部分を、shift-share(Bartik) 識別の枠に載せ直せる見込み。ここを固めると先行研究・方法論章の土台になる。
- 進め方（ハンドオフ §8）: ① shift-share/Bartik 識別（Adão-Kolesár-Morales / Goldsmith-Pinkham et al. / Borusyak-Hull-Jaravel）② 弱い識別の感度分析（E-value / Rosenbaum bounds）③ 現代 event study/DID の負の重み是正 ④ 財政乗数の状態依存。
- Done when: 卒論の識別戦略（share外生 or shock外生のどちらに乗るか）を1段落で言語化し、`paper/` の先行研究/方法論章に反映。

## 🎯 Next action（1つだけ、具体的に）
- What: **論文執筆着手**（実証3本柱を結果章に統合）。⚠️**数値は必ず DEC-023 の暦年再生成値を使う**（DEC-021 の年度値は撤回）: 交易損失 中心~35兆/**2025年24.8兆**・Q1-Q5 **+2.01pp**(2022)/**+3.36pp**(2025)・β=**0.373 (p=0.089)**・Shapiro 0.41→0.70→0.83（不変）・Koyck RMSE **9.24pp**。goods-services分解（DEC-022）も暦年再生成済（S0 shock +0.08〜+0.41）。全 golden 値は decision-log DEC-023 参照
- Where: `paper/`（outline.md が章割り。01-introduction はドラフト済・DEC-015 準拠に修正済）
- Done when: 先行研究 or 方法論の章が1本ドラフトされ、数値が全て repo 再現値と一致
- 別線: ① ~~main push~~（完了・origin=09ff542） ② ~~AKM SE の R 再実行~~（DEC-021補遺で消化・p≈0.15 再現） ③ ~~財/サービス分解（DEC-022）~~（実装・doc反映・§4官公表突合とも完了。突合2件差異は価格決定メカニズム基準の事前定義として意図的差異と明記しクローズ済＝09ff542） ④ shapiro_decomp の e-Stat 品目名をキャッシュ化（現状 API キー必須＝再現性の残穴） ⑤ GDP 561兆の vintage 確定（trade_loss.py TODO） ⑥ data/processed_stale_20260706/ の削除判断（新キャッシュ安定後。※DEC-023 セッションで main の data/processed を暦年で再生成済） ⑦ ~~第2回スライド s7 改行位置が不自然~~（完了＝bdc15c2） ⑧ ~~第2〜4回スライド・原稿の暦年値（DEC-023）同期~~（**全完了・2026-07-07**: 第3・4回デッキ+原稿を暦年刷新・2025年延長。**第2回はユーザー確認で「未発表」と判明＝凍結対象外**としてデッキ+原稿も暦年値へ更新済み・stale grep 0）

## ✅ 直近完了（2026-07-07・矢印演出の刷新・ユーザー選定B案）
- **flow-arrow を3デッキ共通で「伸びる→一拍→消えて再入場」に変更**: 旧・破線コンベア（dashflow）への「イメージと違う」указ摘を受け、5案の動く比較デモ（現行/伸びて再入場/一回描画/コメット/シェブロン）を提示 → **B案をユーザー選定**。stroke-dashoffset 56→0 で描画(42%)→矢頭点灯で保持(72%)→フェード(86%)→再入場、周期2.4s
- 複数矢印スライドは `--ad`（0.35s刻み）で波状に時差（第2回2本・第3回3本・第4回1本に付与）。reduced-motion では最終状態（実線+矢頭）に固定し矢印が消えないよう手当て
- 検証: checker 3デッキ OK・実ブラウザで第2回 s7 のサイクル動作を目視+GIF（`arrow-b-s7.gif`）。デモは scratchpad/arrow-variants.html

## ✅ 直近完了（2026-07-07・第2回暦年更新 + モーション再監査）
- **第2回は未発表と判明（ユーザー確認）→ 凍結対象外として暦年値へ更新**: デッキ s6 hook +2.14→**+2.01**・2023/24/25 系列 +2.06/+2.45/+3.36・s4 に 2025年約25兆 追記・s8 β 0.425→**0.373**（exposure-robust の平易言い換えも第3回と統一）。原稿も同期（⑥⑧⑩・補足メモ golden を暦年化・ヘッダに「未発表のため凍結対象外」明記）。checker OK・headless 全13枚 overflow 0・count 着地一致・stale grep 0
- **第3・4回のモーション再監査（DEC-023 更新後）**: 取りこぼしなしを機械監査で確認 — 新設 s7c=frag 4送り・五分位図は2025グループ追加後も4送り・交易損失2025行は既存 yr グループ+スタガー(--rd 1.2s)+count 同期済み・References のみ静的（規律どおり）。全スライド送り≦4

## ✅ 直近完了（2026-07-07・DEC-023 スライド/原稿同期セッション）
- **第3・4回デッキを暦年値（DEC-023）へ刷新**: Q1-Q5 gap +2.14/1.96/2.67 → **+2.01/2.06/2.45**・β 0.425(p0.047)→**0.373(p0.089)**・政策 b1 を「残る gap 比率」表示に変更（baseline 0.92pp・−44.8/−12.9/−57.7%＝正準は DEC-023 本文。旧 policy CSV は消滅・tex は stale なので pp レベルの転記をやめ比率化）
- **2025年を延長掲載**: 交易損失バーに 2025=24.8兆（エネ12.2兆・GDP比4.4%・フロー減衰）、五分位図に 2025 グループ（Q1 14.8%〜Q5 11.5%・gap **+3.36pp=観測期間最大**）。図タイトルを「差は2025年に最大の+3.36pp」に。2025 caveat（電気・ガス補助の間欠実施=政策込み）を両図 note に明記
- **provenance 注記**: s7 note に「第2回の +2.14pp は年度集計・以降は暦年に統一（結論不変）」。原稿⑦にも聴衆向け説明を追加＋Q&A「なぜ数字が変わった?」を用意
- **原稿2本を全面同期**: DEC-023 値＋前回の平易化（三角測量 s7c の新セクション⑨・コストプッシュ/デマンドプル定義・exposure-robust の言い換え）＋2025年の語り＋golden 値表を暦年に更新。第3回 18〜19分/全18枚・第4回 14〜15分/全15枚
- 検証: checker OK・headless 全33枚 overflow 0・count 着地一致・stale 値 grep=0（provenance 記載のみ）


## ✅ 直近完了（2026-07-07・2025年延長 + 暦年統一 DEC-023 セッション）
- **2025年データ取り込み**: 調査の結果、輸入物価(2026-03まで)・CPI月次(2025まで)は既に手元にあり、真に不足していたのはCPIの集計方法だけと判明。Phase1交易損失 **+2025=24.8兆(GDP比4.4%・フロー減衰)**、Phase2 Q1-Q5格差 **+2025=3.36pp(拡大継続)**。Phase3(IO2020表)は延長不可。詳細=`docs/data-sources/2025-data-availability.md`
- **潜在バグ発見→暦年統一(DEC-023)**: CPI月次抽出 `str[4:6]`(6桁YYYYMM前提)が実データ10桁YYYY00MMMMでは年度行だけ拾い、記載値は実は「年度ベース」だった。GDP・Phase1が暦年ゆえ**暦年へ統一(ユーザー承認)**。3コード修正(cost_push_id/cost_push_panel/quintile)+trade_lossに不完全年ガード
- **全下流を暦年再生成**: Q1-Q5格差 2.14/1.96/2.67→**2.01/2.06/2.45**、β(iii) 0.425/p.047→**0.373/p.089**(cluster p .002→.366・同一仕様プラセボ -0.226→-1.38 ill-cond=識別さらに脆弱化・貢献③補強・結論不変)、Koyck RMSE 10.00→**9.24**、Phase3 gap 0.37-1.33→0.32-1.17(補助率44.8%/57.7%不変)、DEC-022 S0 shock +0.06-0.39→+0.08-0.41(判定(a)不変)、Shapiro 0.41/0.70/0.83 不変(月次分解ゆえ無関係)
- **伝播**: 16ファイル(paper/outline・README・CLAUDE・docs 11件・code2)へ暦年値。design-review.md は歴史記録として非改変+DEC-023ポインタ、inflation-timeline は前年比YoYゆえ対象外。DEC-023 起票
- **安全策**: 出力回帰ガード(交易損失2022-24=35.3/28.4/29.1兆 完全一致)、check_golden PASS、旧値残存grep=ゼロ(「旧年度X」provenance注記のみ)。取りこぼし2件(×0.425・literature β=0.431)も是正
- **merge + main整合**: --no-ff で main統合(90069b7)→ main の stale processed キャッシュを暦年で再生成し headline一致確認(格差2.01/2.06/2.45/3.36・交易損失35.3/28.4/29.1/24.8・β(iii)0.373・golden OK)→ worktree削除

## ✅ 直近完了（2026-07-07・スライドデザイン基盤セッション）
- **ppt-master（MIT）/ budoux（Apache-2.0）調査**: 前者から数値化された暗黙知（用途別本文px・ramp比率・60-30-10・影の二層opacity・page rhythm）を蒸留、後者は「ZWSP+keep-all」の本質を吸収しビルド時焼き込み方式を採用
- **グローバル slide-design スキル新設**（`~/.claude/skills/slide-design/`）: SKILL.md + references 5本（typography/color-shadow/layout-rhythm/cjk-text/**html-slide-pitfalls**）+ scripts（apply_budoux.py / check_slides.py）。DESIGN.md は数値委譲の参照節のみ（二重管理禁止・presentation=本文32px基準を宣言）
- **第2回デッキ監査→全修正**: budoux ZWSP 361箇所・パレット統一（直書き#c0392b/#27ae60→--crimson/--green新設）・コントラスト是正（--text-light/--blue-soft を4.5:1+）・本文16→18px・極小10-13px引上げ・偶数スナップ・s7/s8 ぶら下げインデント（.hang）・**bullets の flex 分断バグ根治**（li の display:flex はインライン混在で語順崩壊→絶対配置ダッシュ）・p2 橋渡し文の文節改行整形・散布図の回帰直線 orange 化+ノルウェーラベル移動。全て Chrome 実レンダで overflow 検証
- **第3/4回へ横展開**（同じテンプレ由来の同問題を一括修正・全28枚検証）→ その後のモーションセッションの編集後も check_slides.py 3デッキ OK を handoff 時に再確認
- **再発防止**: `check_slides.py`（E1 li flex/E2 禁止hex/E3 フォント下限・端数/E4 コントラスト/E5 budoux未適用）+ 本 repo `.claude/settings.json` の PostToolUse hook（slides/*.html 編集直後に自動検査→違反を編集セッションへ exit 2 で返す。違反注入テスト済）。第1回デッキ（発表済み）は意図的に未修正＝編集するとエラーが出る仕様

## ✅ 直近完了（2026-07-07・第3・4回スライド完成形セッション）
- **第3回デッキ（15→17枚）**: s6 交易損失の年次推移バー（35.3/28.4/29.1兆・エネ寄与重ね棒＝`trade_loss_total.csv` 転記）／s7b 五分位別実効インフレ縦棒図 新設（2022-24×Q1-Q5・gap +2.14/+1.96/+2.67pp＝`quintile_inflation_burden.csv` 転記）／s8 Shapiro 2023 (0.60) 追記／s10 比較表の「数値要照合」ph 解消（Yagi=品目別転嫁率の異質性・Amiti=自社コスト弾力性≈0.6・Amores=EUROMOD逆進性、docs/literature 照合。βの同一 estimand 直接比較対象なしと明記）／巻末 b1 政策シナリオ例示チャート新設（`policy_comparison_2022.csv`: gap 1.05→エネ0.58(−44.8%)/食料0.91(−13.0%)/複合0.44(−57.7%)pp・incidence accounting caveat 明記＝DEC-014 準拠で絶対値は結論にしない）
- **第4回デッキ（13→15枚）**: s1/s2 draft-flag 除去・s5 年次推移バー＋ph解消・s6b 五分位図 新設・s9 の政策数値 ph→補足b1参照・b1 新設。**s11（第3回フィードバック応答）のみ placeholder 維持＝第3回実施後に執筆（構造上未確定が正）**
- **検証**: check_slides.py 両デッキ OK（budoux 再適用で中黒 ZWSP 手動2件が消える既知 trap → 再挿入）・headless Chrome ハーネスで全32枚 overflow 0・count-up 着地値一致・新チャート4種スクリーンショット目視
- 前セッション方針「別セッションで内容確定 → frag 割当てやり直し」を本セッションで消化。新規要素の frag/count は slide-motion スキル経由で割当て
- **平易化＋三角測量説明スライド（同日・後続・ユーザー指摘）**: 第3回に s7c「三角測量とは」を新設（17→18枚。測量アナロジー＋3証拠→収束の図＋識別との対比・frag 4送り）。経済学部2年生を想定した言い換え: s2-s4（wet→書きかけ・第一次所得収支に括弧補足・コストプッシュ/デマンドプル初出定義・清浄な単離の言い換え）＋内部用語の漏出除去（**Tier 1・DEC-022・estimand・universe・near-zero をスライドから排除**）＋exposure-robust に一行注記。第4回も同水準（Tier 1 除去・s7 note に三角測量定義・恒等式/符号の言い換え）。クレーム階層（断定/整合的/例示）は不変。**⚠ 原稿（script.md）は未同期 — 次タスク**
- **発表原稿を新規作成（同日・後続）**: `20261101-seminar3-script.md`（17〜18分・s7b/b1 含む全17枚対応）・`20270115-seminar4-script.md`（14〜15分・全15枚対応、⑫=s11 応答は第3回後に執筆と明記）。第2回原稿と同形式（▶転換合図・→キー段階表示cue・トーン指示・補足メモ=ペース配分/断定の線引き/想定問答/削る候補）。断定可（恒等式・会計・Shapiro）と「整合的」止まり（β=0.425）と例示扱い（政策%）の3層を原稿レベルで固定
- **モーション仕上げ（同日・後続）**: 新チャートにスタガー演出を追加（交易損失バー=行ごと位相ずらし+総額→エネ寄与の2段掃引、五分位バー=Q1→Q5 順成長、カウント開始をバー成長に同期 data-delay）。全スライド監査で静的なのは References のみ（規律どおり）を確認、キー送り5回の2枚（第3回s11・第4回s9）は先頭2項目を束ねて4回以内に。実ブラウザ（Chrome 拡張・http 経由）でキー送り実走・カウント着地確認・`seminar3-motion-check.gif` 収録（~/Downloads）。⚠ EnterWorktree は origin/main 起点＝ローカル main の未 push マージを含まない → `git reset --hard main` で追随してから作業（今回踏んだ）

## ✅ 直近完了（2026-07-07・前セッション・スライド動化）
- **第2回デッキのモーション実装**: フラグメント段階表示・カウントアップ・TED風フック演出・バー成長・SVGフローアロー。ランキング/散布図を PNG→データ駆動 SVG/HTML に再構築（`xc_2022.csv` 転記・OLS 0.7165+0.021541x R²=0.64・散布図注記 46→45ヶ国に訂正）
- **第3回・第4回デッキに同基盤を移植**: ロードマップ/研究の弧/三角測量の段階点灯・現在地/背骨リングハイライト・比較表の行frag・太字2段階強調（emph navy/orange/crimson・rq-box白→黄）。check_slides.py 3デッキ全て OK（第3回は budoux 再適用+中黒 ZWSP 手動2件）
- **count-up watchdog**: 非表示タブ等で rAF 停止しても最終値を確定する仕組みを3デッキに実装（trap lesson 化済み）
- **グローバル slide-motion スキル新設**（`~/.claude/skills/slide-motion/`）: 基盤コード正本 references/motion-base.md＋適用ルール・落とし穴6件。slide-design と対
- **方針決定**: 第3・4回は内容が草案のため、別セッションで内容確定 → slide-motion で frag 割当てをやり直す運用（基盤は本文と直交なので残置）

## ✅ 直近完了（2026-07-06・セッション後半・スキル/検収/修正）
- **thesis-writing スキル作成**（`.claude/skills/thesis-writing/SKILL.md`）: 執筆視点（パラグラフ/章役割/クレーム階層言い分け表）＋推敲7視点チェックリスト＋golden値表＋章手順。paper/ 作業で自動発動
- **スキル試運転が事実誤りを検出→修正**: 「貿易開放度は中位」→ 実データは46ヶ国中下から3番目（米中に次ぐ低さ）。序論・04a・第2回デッキ/原稿の4箇所修正（論旨は強化）
- **DEC-022 実装の検収**: 受け入れ基準7項目を独立再実行で全通過確認（golden/決定論/doc突合/スコープ）。官公表突合2件は意図的相違として DEC-022 でクローズ
- **識別断念の再検証（DEC-021補遺）**: 3テスト再実行で DEC-013 の結論を数値レベルで再現（AKM0 p≈0.15 等）＝「やり直しても識別はできない」を確定
- **第2〜4回スライドを確定値に更新**（第2回は未発表・+2.14pp/β=0.425/プラセボ言い回し注意/DEC-022 を反映）

## ✅ 直近完了（2026-07-06・このセッション・goods-services contrast分析実装・DEC-022）
- **設計書どおり実装**: `src/analysis/goods_services_contrast.py`（新規319行）。41カテゴリ財/サービス分類×S0-S3の4仕様で年次相関＋pooled β 算出。golden突合・決定論再現・バケットサイズassert全通過
- **事前登録判定結果**: S1 goodsのショック期4年中2021年が負のため **(a) 消える**（全体コントラストの相当部分は財/サービス構成差で説明される）
- **doc反映3箇所**: research-design.md・decision-log.md（DEC-022新設）・第2回スライド補足メモ。全てCSV値と突合済（手打ちゼロ）
- **§4公式分類突合**: 総務省「品目から類への合算表(財・サービス分類)」（4-4.pdf）と照合し2件の齟齬（上下水道料=公式は財・設備修繕維持=公式は全サービス）を検出、設計書末尾に記録。→ **別セッションで意図的差異としてクローズ済み**（decision-log.md DEC-022補遺・commit `09ff542`。価格決定メカニズム基準の事前定義であり官公表準拠に組み替えても判定(a)は覆らない旨を明記）
- **`/review-code light`**: correctness-critic が major 1件検出（S1図右パネルのプラセボ/ショック境界線 axvline が1インデックスずれ・2019年がショック側に食い込んで見える描画バグ）→ 修正・再検証・再commit済。security/removed-behaviorはpass
- **worktree運用**: `worktree-20260707-goods-services-contrast` で実装 → main へ `--no-ff` マージ（commit `9be8ab9`）→ worktree削除済

## ✅ 直近完了（2026-07-06・全体監査 DEC-019/020/021）
- **監査**: 3系統並列（整合性/数値出典/ハードコード）→ 齊藤2022「GNI比4.6%」がAI混入数値と確定（JCER原文に不存在）→ 内閣府SNA一次値（2022年度 −16.4兆円）に差し替え。paper序論の撤回済み識別主張・34.6兆混用値・Phase3旧値3系統・G-4表記ゆれを一括修正
- **再現性強化**: β/δ/GDP単一ソース化・全compute_*にforce・fetch_worldbank.py新設（ページング/ボディ検証込み）・_a4_akm_prep.py新設・uv.lock・setuptools修正・README再現手順
- **再現性ゲート（DEC-021・最重要）**: rawから全再生成→golden突合で、+1.42pp が**DEC-011で除去済みバグ時代のシェアローダー出力**と特定（正= **+2.14pp**）。β仕様表はB-4前のstaleキャッシュ（正= 0.425/p=0.047・プラセボ有意負・FD null・年次相関 +0.06〜+0.39 vs 全年負）。ユーザー承認のうえ再生成値を正として全doc更新・本体data/processedを置換（旧= processed_stale_20260706/ に退避）。Shapiro 0.41/0.70/0.83・35兆系・H1/H2・国際比較は完全再現＝無傷
- **/review-code ゲート通過**: blocker(README旧値残存)検出→修正済。verify 3値判定・self-tuningログ記録済（.review/code-review-main-HEAD.md）
- **main統合済（ローカル merge 25cfa3c・未push）**

## ✅ 直近完了（2026-06-26・このセッション・原稿同期＋恒等式追加）
- **第2回原稿を全13枚デッキに同期（PR#11 マージ済）**: 統合で追加された問題意識2枚(p1=国際比較9位・p2=エネ依存R²=0.64)＋巻末補足B1(交易条件−17.9%)の読み上げ原稿を新規追記。s1導入を「一つの数字」→「二枚の国際比較で問題意識」に差替え、既存②〜⑩を④〜⑫へ通し番号繰下げ、補足メモ(ペース配分/削る候補)のスライド参照番号も全更新。想定時間 15分→16-17分
- **s6背骨スライドに実効インフレ恒等式を追加（PR#12 マージ済）**: 柱③(+1.42pp)の空きスペースに数式 **π_q = Σ_i w_{q,i} × Δπ_i** ＋変数凡例(w=支出シェア/家計調査2019固定、Δπ=実績CPI変化率/2015-19基準)を従属要素として配置。焦点(+1.42pp・120px)は維持、数式は30px・navy で階層化。重複説明(takeaway-sub)を整理。headless Chrome で描画検証(オーバーフロー無し・凡例2行整列)。恒等式実装は `src/analysis/quintile_impact.py` の `compute_quintile_inflation_burden()`(94-153行)

## ✅ 直近完了（2026-06-25・統合mainマージ＋Issue#8）
- **ブランチ統合をmainへ（PR#9 マージ済）**: 本筋 `0613`（Phase2/三角測量/seminar2-4デッキ）＋副産物 `0621`（産業空洞化探索の反証＋国際比較）を consolidate 経由で main へ統合。祖先 `0526`/`0531` 含む**全 feature ブランチを削除**（local+origin）→ ブランチは main のみ。競合は `todo.md` 1ファイルのみ解消
- **Issue #8 解消（最終）**: 産業空洞化の副産物（国際比較・日本9位/46・3.28%GDP・-17.9%最大級・エネ依存R²=0.64）を問題意識2枚スライドにし、**第2回デッキ `20260626-seminar2-results.html` 冒頭の動機づけに統合**。散布図の橋渡し(①規模→②帰着→③政策)が35兆hook→3本柱へ接続。-17.9%曝露は巻末バックアップ。独立デッキ `20260625-...` は廃止（図資産 `s2b-*.png`・生成 `deindustrialization_fig_slide.py` は保全）。論文序論にも組込み済
- **ランキング図の可読化**: 縦長46行→2カラム横長（`deindustrialization_fig_slide.py`）でスライド尺でも国名可読。日本注記は棒位置に「◀ 日本 3.28%GDP」、縦軸ラベル左揃え
- **方針確定（第2回=中間発表-1）**: 第2回/3回/4回=中間-1/中間-2/最終。中間発表は研究全体アーク再提示の場＝動機づけ必須。国際比較の枚数は発表が進むほど縮小（中間-1で2枚→以降1枚→巻末）、フルは論文序論
- **副産物の探索記録**: 単一国時系列×コストプッシュ比率DVは分母≈0で不成立（DEC-IDEA-01）。クロスカントリー46ヶ国×交易損失DVは製造業シェア係数が正で頑健＝仮説と逆（DEC-IDEA-02）。反証仮説（製造業=耐性）は本論に持ち込まない。証跡 `docs/research-ideas/deindustrialization-inflation.md`

## ✅ 直近完了（2026-06-13・このセッション・3回分のスライド草案）
- **第2回ゼミ発表スライド完成（6/26発表・〜15分）**: `slides/20260626-seminar2-results.html`（10枚）+ `slides/20260626-seminar2-script.md`（原稿・Q&A準備込み）。DEC-017 Tier1/Tier2 を背骨に「3本の硬い柱＋正直なピボット」を構成。advisor の框A/B/C を反映（①ピボットを正面から所有 ②+1.42pp=実効インフレ逆進性≠cost-push単独 ③「識別でなく三角測量」明示）。headless Chrome で全枚描画検証。s7/s8 のレイアウト修正（3カラム枠統一・ブロック縦中央化）も実施
- **第3回ドラフト作成（論文ドラフト全体・15枚）**: `slides/20261101-seminar3-draft.html`（日程未定で日付暫定）。章構造（背景→RQ→方法→結果→考察→限界→結論）で seminar2 と差別化。ADD=考察・先行研究数値比較(placeholder)・ロバストネス・限界形式化・未解決点提示。トーン「完成形だが wet」
- **第4回骨格作成（最終・結論・13枚）**: `slides/20270115-seminar4-final.html`（骨格＋placeholder）。ナラティブの弧「約束→ピボット→届けた答え」を背骨に、4貢献確定・政策含意・結論。第3回フィードバック応答は placeholder スライドで枠だけ。未確定数値は ph バッジ
- **全3デッキ共通の framing**: RQ は DEC-015 再定義版（clean識別を前提にしない）で統一。seminar2 CSS フレームワーク流用
- **重要**: 全作業がブランチ `claude/20260613-seminar2-slides` に集約・**未push**。seminar1 hook 34.6 は提示記録として保持、35兆は seminar2 以降に適用（凍結方針通り）

## ✅ 直近完了（2026-06-03・仮説×証拠 監査→クレーム階層化）
- **DEC-017 provable 優先のクレーム階層化（ユーザー承認）**: 全クレームを証拠ステータスで監査し2層化。**Tier 1（背骨・全て repo 証明済・回帰/消費応答識別に非依存）**: 交易損失~35兆（会計）→ H1/H2 必需品=高輸入含有（食料 Q1-Q5 +8.3pp・光熱 +4.8pp・**今回 repo 実測**）→ +1.42pp 実現インフレ逆進性（恒等式）→ Shapiro 層1 供給主導(0.70)。**Tier 2（誠実な副次）**: 識別限界(2a/層2 null=貢献③)、統合シミュ(Phase3=④)。
- **doc 整合済**: decision-log DEC-017 / overview「貢献の核」に Tier1 連鎖 / research-design 仮説節に H1-H4 ステータス＋repo 証拠 / contribution.md 空白②再文言＋冒頭バナー（β=0.431 を Tier2 に降格明示）。
- **要点**: +1.42pp は**実現インフレ逆進性**（最頑健）であって cost-push 単離でない（不可能・DEC-013）。H2＋層1 で cost-push へ三角測量的に橋渡し。heterogeneity の核は +1.42pp 1本依存＝意識的決定。

## ✅ 直近完了（2026-06-01・このセッション・層2 Shapiro）
- **層2 group-specific 実装完了（DEC-016 層2・`src/analysis/shapiro_quintile.py`）**: ν^p 共通を GATE assert で確認（設計 crux 成立）。**判定=INCONCLUSIVE**: pre-registered 仮説 Q1>Q5 は per-year で 2/4 shock years のみ成立（2022-23 コア cost-push 年で逆転）、pooled +0.043 は 2021+2024 由来。年次×五分位の粗さで数量応答マージン解像不能＝誠実な null。**Phase 2b（実効インフレ gap・ウェイトベース）は無傷**。crux framing: 「Q1 がより収縮的消費応答」も robust に言えず（≠ cost-push exposure・ν^p 共通）

## ✅ 直近完了（2026-06-01・このセッション・層1 Shapiro）
- **層1 Shapiro 実装完了（DEC-016 層1・詳細 `docs/shapiro-decomposition.md`）**: `src/analysis/shapiro_decomp.py`。crosswalk 116品目・VAR残差化+月連続性マスク・**インフレ寄与加重**集計（Shapiro P081）。バスケット=116 物理数量 食料+家庭用エネルギー品目。**headline=supply-driven SHARE**: 2021 0.41(需要主導)→2022 0.70(供給surge)→2024 0.83。**2021需要→2022供給転換が Shapiro米国・timeline と整合**、月次で侵攻(2022/2)から跳ね上がり。2022 supply 寄与 broad(top5=43%・筆頭ガソリン/鶏肉/さけ)。5 spec・balanced 105(0.42→0.72)・生鮮除外(0.42→0.76)で robust。
- **framing 訂正（advisor reconcile）**: 当初「price-YoY が食料CPI一致」は buggy calc 由来で**撤回**。basket は公式食料CPIを構造上 tracking しない（2023 公式+8.06 vs basket+3.99）＝外食/調理/加工欠落・エネ含む。**乖離は feature**＝ラグ付き転嫁＝cost-push 整合。スコープ厳守:「basket 内 2022 供給surge」ship／「食料インフレ X% 供給駆動」書かない。pp 寄与=内部denominator(Dec-to-Dec)。
- **pre-registration 記録（DEC-016 補遺）**: 価格=CPI主/unit-value頑健性、残差化=月次VAR+季節（advisor で AR→VAR 精緻化）、framing「供給駆動≠輸入cost-push」。split を見る前に固定

## ✅ 直近完了（2026-05-31〜06-01・このセッション・実験ブランチ未push）
- **案2 却下（DEC-013/A-5）**: 両 estimand とも期間延長は識別を救わない。FD-Koyck δ=0.55 two-way FE で両窓非有意。再現: `tasks/_an2_shock_independence.py`, `_an2_pooled_fd.py`
- **Phase 3 降格（DEC-014）**: overshoot(5.2pp>実績2.5%)・政策率 IC依存(101.6%→44.7%)・β-invariant≠robust → 定性/例示。符号レベルのみ結論。再現: `tasks/_phase3_recalib_check.py`
- **貢献を再定義（DEC-015）**: cost-push/demand-pull 識別は不可能と判明→識別限界の方法論的提示を貢献に転化。4貢献に再定義。docs統一・CLAUDE.md Phase2 反映済(承認済)
- **ウクライナ小麦 LATE（KEEP）**: 事前ルールで判定。ITS で小麦 pre-trend flat(+0.037%/月)＋2022/2 break +4.62%＋post単調→ 存在証明成立。米controlは非平行ゆえ ITS。副産物=cost-push 食料全般に広い。再現: `tasks/_ukraine_eventstudy.py`, `_ukraine_wheat_scope.py`
- **インフレ時系列整理**（`docs/inflation-timeline.md`）: 日本は2020-21デマンドプル不在(財vsサービス・実質賃金3年連続マイナス・需給ギャップ)＝cost-push主導。エネは2021先行・2023補助で抑制
- **Shapiro 採用（DEC-016）**: 文献(P081-084)で cost/demand 分離は Shapiro で清浄control不要と判明→採用。2層(national月次/quintile年次=novel)。データ表ID特定・構造検証済

## ✅ 直近完了（2026-05-31・このセッション）
- **案2 却下（DEC-013/A-5）**: 両 estimand とも期間延長は識別を救わない。①group-specific β_g は共線性で分離不能、②pooled β は CPI 2005延長で直接再推定→FD-Koyck δ=0.55・two-way FE で両窓非有意（level-anchoring・単一集計shifterは time FE が時間変動吸収し識別が IC固定依存）。途中2誤りを advisor catch で訂正（pr_group のみ測り誤却下しかけ／CPI を e-Stat 全 tab_code 平均で汚染→overlap照合 tab_code==1 で修正）。再現: `tasks/_an2_shock_independence.py`, `tasks/_an2_pooled_fd.py`
- **Phase 3 を定性・例示に降格（DEC-014）**: G-3 は既に解消済（fresh再生成=cache 完全一致）。モデルが overshoot（cost-push 平均5.2pp > 実績~2.5%＝C-4 構造ミスマッチ・β=0.431 でも残る）、政策削減率が B-4 IC是正で ~101.6%→44.7% と IC依存で激変（β はキャンセルするが β-invariant≠robust）。**特定%・pp 絶対値は結論にせず incidence accounting/例示で appendix**。結論に残すのは符号レベル（Q1>Q5・energy 最大寄与・補助は方向として gap 縮小）。再現: `tasks/_phase3_recalib_check.py`
- **重要な含意**: headline を支えていた Phase 2a(回帰)と Phase 3(IO sim)が想定より弱いと連続判明＝硬い背骨は Phase 1(会計)+Phase 2b(恒等式)。合意方針の正しさが裏付けられた
- **貢献を再定義（DEC-015）**: DEC-008 が掲げた「コストプッシュ/デマンドプル識別」は本設計・データで不可能と判明→**失敗でなく識別限界の方法論的提示という貢献に転化**。再定義した4貢献=①交易損失の会計的定量化②逆進性の恒等式記述(背骨)③識別限界の方法論的提示(exposure-robust shift-share+期間延長テスト)④統合シミュレーション(例示)。overview/research-design/decision-log 更新済。**project `.claude/CLAUDE.md` Phase2 サマリーの更新は self-modification 判定で保留＝ユーザー承認待ち**

## 📍 State snapshot
- ✅ Done（メインブランチ `claude/20260526-seminar1-script`・**origin push済**）:
  - `docs/design-review.md` 学術監査（A/B/C/D/G項目）、G-2(家計universe=二人以上, DEC-011)、G-1(交易損失中心~35兆/上限40.7兆, DEC-012)、Phase 2a framing整理(因果→整合的・プラセボsupported撤回)、Phase3 caveat、文献P077-P080
- ✅ Done（実験ブランチ `claude/20260531-a4-groupspecific-shiftshare`・**未push**・f9e9b21）:
  - B-4(IC>1是正・競争輸入型 μ^T(I-(I-M̂)A)^-1) + A-4(group-specific shift-share) + AKM SE(R `ShiftShareSE` を `~/.Rlib` にインストール済)
  - **結論: βの点推定は頑健(0.43・energy/food主導)だが AKM0 で有意性崩壊(p≈0.15)。根本=独立な輸入物価ショックが実質1つ(少数実効ショック)**
- 🟡 In progress: なし（案2 却下・Phase 3 降格 済・次は論文執筆）
- 🔴 Blocked: なし

## 🧠 Context not in code（次セッション必読）
- **βの正体**: 年・費目FEで二元除去後の**単一スロープ**（IC/P_importは単独で入らず交差項のみ）。β=転嫁率。有意取れない根本は計算でなく「独立ショックが実質1つ(2021-24サージ)」＝**設定に内在・別の回帰では直らない**。
- **立っているもの（β/回帰に非依存・無傷）**: Phase 2b(Q1-Q5 +1.42pp逆進性＝実績CPI×実シェアの恒等式)、Phase 1(~35兆＝会計)。**卒論の実証背骨はこれ**。
- **方針合意**: 重心を Phase 2b(記述・堅い)に、Phase 2a は識別限界を正直に明記、Phase 3 は較正して例示的に。「レベル下げ」でなく誠実で高度な構成。
- **案2 は却下（DEC-013・実データ検証済）**: ①group-specific β_g は共線性で分離不能。②pooled β を CPI 2005延長で直接再推定→FD-Koyck δ=0.55・two-way FE で両窓非有意（level-anchoring現象）。単一集計 shifter は time FE が時間変動を吸収し識別が IC(2020固定)依存のため、期間延長は効かない。重心は Phase 2b（恒等式・β非依存）/Phase 1（会計）。Phase 2a は識別限界を鋭利化して明記。

## ❌ Don't do (this task)

## ❓ Open questions for user
- [x] 実験ブランチ `claude/20260531-...` を push/PR するか → **2026-06-25 consolidate に統合**（0531/0526 は 0613 内包。全作業を consolidate→main で main系に集約）。group-specific 負の結果と 2軸 feasibility は識別限界節の根拠として残す
- [x] 案2 を進めるか → 実データで検証し **却下**（DEC-013）。次は ③ Phase 3 再較正(C-4)

## 📂 Key files
- `docs/design-review.md`（全監査・A-5案2判定）/ `docs/decision-log.md`（DEC-011/012/013）
- `src/utils/io_utils.py`（B-4 IC是正・実験ブランチ）/ `src/analysis/cost_push_panel.py`（β回帰）
- `tasks/_a4_groupspec.py` `tasks/_a4_akm.R`（A-4・AKM再現）/ `tasks/_an2_shock_independence.py`（案2ショック独立性検証）
- `docs/literature/papers/{moreno-louzada-etal-2025,borusyak-hull-jaravel-2024,bhattarai...,cicero...}`（P077-P080）

## ❌ Out of scope（当面）
- seminar2/3/final 用スライド（時期到来時に slide-brushup）
- Paasche化・G-4価格表記・スライド運用ルール（下記残タスク）

---

## 残タスク

### 設計レビュー由来（`docs/design-review.md` / DEC-011・012）
- ✅ G-2 家計調査 universe を二人以上に確定・cat02 明示フィルタ＋潜在バグ除去（DEC-011, 負担数値は不変）
- ✅ G-1 交易損失を中心推計C（2015-19正常基準）に統一・中心~35兆／上限40.7兆（DEC-012）
- ✅ ① Phase 2a 識別の framing 整理（因果→整合的関連、プラセボ supported 撤回→年次相関主証拠、goods-services 交絡明記）。research-design.md に「識別の到達点と限界」節を新設し INDEX/overview/contribution/feasibility/CLAUDE/decision-log を統一
- ✅ B-4 輸入含有率 IC>1 是正（競争輸入型 μ^T(I-(I-M̂)A)^-1, `io_utils.py` 修正・IC>1解消）【実験ブランチ f9e9b21】
- ✅ ② A-4 group-specific shift-share 実装（IC_{c,g}×P_{g,t}）+ AKM exposure-robust SE。**結論: energy/food はクリーン識別だが点推定のみ頑健、AKM0 で有意性崩壊(p≈0.15)＝少数実効ショック**【実験ブランチ・未push】
- ❌ **案2: 識別の立て直し（期間延長）→ 却下（DEC-013/A-5・2026-05-31・実データ検証済）**。group-specific は共線性で分離不能、pooled は CPI 2005延長で直接再推定し FD-Koyck δ=0.55・two-way FE で両窓非有意。単一集計 shifter は time FE が時間変動を吸収し識別が IC(2020固定)依存→期間延長は効かない。IO表3版再構築(D-3)は識別改善せず不着手。再現: `tasks/_an2_shock_independence.py`, `tasks/_an2_pooled_fd.py`
- ✅ **③ Phase 3 → 定性・例示に降格で完了（DEC-014）**。点較正/財別較正は A-5（β_g 識別不能）と循環性で却下。代わりに minimal-honest-fix（C-1 incidence accounting・C-4 β=1上限/×0.431例示・C-2 RMSE分解・C-3 δ calibration）＋数値降格。特定%・pp は結論にせず符号レベル(Q1>Q5・energy 最大寄与・補助は方向)のみ結論。再現: `tasks/_phase3_recalib_check.py`
- ✅ **Koyck整合性（G-3+C-2+C-3）→ 既に解消済を確認（DEC-014）**。io cache を δ=0.55 で force 再生成→現 cache と完全一致(diff=0)・koyck≠empirical 確認。実験ブランチ f9e9b21 が既に正しく再生成済で design-review G-3 のテキストが stale だった。下流(policy/microsim) は coherent δ=0.55 で再生成済
- [ ] **【別セッション】Paasche/Fisher 化**: `trade_loss.py` を固定数量(Laspeyres, 2020輸入額固定)→実数量へ精緻化。前提＝**財務省貿易統計の数量データ取得**（現状 raw は衣類のみ）。`src/data/fetch_trade_stats.py` を拡張し5グループの品目別 数量×価額を取得 → 価格効果を q_t ベースで再計算
- [ ] **【別セッション】G-4 エネルギー価格上昇率の表記ゆれ**: +203%（年平均集計・再現可）vs +213〜286%（research-design.md/slides・品目別ピーク?・リポジトリのデータで再現不能、286は集計月次ピーク268超）。品目別ピークの一次ソースを示すか +203%(年平均)/+268%(月次ピーク) に統一
- [ ] **スライド運用ルールの策定**: 現状 `slides/` に HTML 直置きで命名規則・格納が未定。決めること = ①命名規則（`YYYYMMDD-<発表名>.html` 等・版管理）②格納構成（回ごとサブディレクトリ／`assets/` の配置）③proposal.html・script.md・brushup-plan.md の対応関係の規約化 ④**発表済スライドの凍結方針**（例: seminar1 の hook は提示記録として 34.6 のまま保持、35兆は seminar2 以降に適用）。規約は `docs/DESIGN.md` か `.claude/slide-context.yaml` に記録

### 執筆前準備
- [ ] 非線形モデルの扱いを明確化（research-design.md に「線形・非線形を比較」と記載。結果は線形のみ → 非線形を試した結果を記録するか、未実施の理由を DEC に追記）
- [ ] Koyck δ=0.55 の選定根拠を文書化（新規DEC として decision-log.md に追記。design-review C-3: 独立gridでは RMSE最小は δ=0.60、曲面は[0.5,0.7]で平坦＝弱識別。「推定」でなく calibration と明記し半減期≈10.4ヶ月の根拠を示す）
- [ ] 先行研究との数値比較表を作成（β=0.431 vs Yagi et al. / Amiti-Itskhoki-Konings、交易損失 中心35兆円（上限40.7）vs 齊藤 2022 / 内閣府推計。ロバストネス appendix 用）
- [ ] 政策シナリオ選定の透明性確保（なぜエネルギー・食料補助であり、賃金補助・産業政策ではないのかをスコープ限定として論文内で明記）

### スライド（任意・5/20 直前）
- [ ] s10 に貿易統計（概況品別国別表）を追加（任意・第1回は省略）
- [ ] 実機 1200×675 で全 14 枚リハーサル

### 論文執筆
- [ ] 先行研究レビューの執筆
- [ ] 方法論の執筆
- [ ] 結果の記述
- [ ] 考察・政策含意の執筆
- [ ] 図表の整備
- [ ] 指導教員フィードバック対応

---

## スライドレイアウト修正（`slides/20260520-seminar1-proposal.html`）

### 課題

| # | 現象 | 原因 |
|---|---|---|
| 1 | 枠（ボックス）内の余白が多く、図として締まりがない | `.fw-box`・`.hyp-step`・`.col-box`・`.rq-main` 等の padding が 20–32px と大きい。スライド外周 padding も 50px/68px で二重に余白が生じている |
| 2 | 文字が小さくスライド全体のバランスが悪い／余白が目立つ | ボックス内テキストが 11–14px（DESIGN.md の最小 15px ルール違反）。小さな文字 + 大きな padding の組み合わせが「空箱に豆文字」状態を作っている |

### 修正方針

1. **テキストサイズの底上げ**
   - ボックス内本文（`.flow-box ul li`・`.fw-box ul li`・`.col-box ul li`・`.lit-card ul li`・`.hyp-step p` 等）: 13–14px → 15px
   - セクションラベル（`.flow-box h3`・`.fw-box .fw-phase`・`.section-tag`・`anchor-label` 等）: 11px → 13px
   - サブタイトル・カード見出し: 13px → 14–15px

2. **ボックス padding の圧縮**
   - `.fw-box`・`.flow-box`・`.hyp-step`: `20–22px 18px` → `14px 16px`
   - `.col-box`: `20px 22px` → `14px 16px`
   - `.lit-card`: `16px 18px` → `12px 15px`
   - `.rq-main`: `28px 32px` → `18px 24px`
   - `.sub-rq-card`: `16px 15px` → `12px 14px`

3. **スライド外周 padding の調整**
   - 現在: `50px 68px 40px` → `40px 56px 32px`（左右の二重余白を緩和）

4. **修正後の検証観点**
   - 各スライドで枠とテキストの密度バランスが取れているか
   - DESIGN.md「最小 15px」ルールをすべての本文要素が満たしているか
   - スライドを 80% 縮小しても読めるか

### タスク

- [ ] ブランチ `claude/fix-slide-layout` で修正 HTML を作成
- [ ] 全 12 スライドを目視確認
- [ ] DESIGN.md Final Check を実施
- [ ] main へマージ

---

## 研究アイデア

_（産業空洞化→インフレの質 のアイデアは探索完了・反証。`tasks/done/2026-06.md` 参照）_

- [ ] # claude-brain
情報の引き出し方が上手くできてるかの調査とアップデート
RAGにおける先行研究の調査も併用する。（Slack #todo より _2026-06-23_）
