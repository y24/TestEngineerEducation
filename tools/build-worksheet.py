# -*- coding: utf-8 -*-
"""レジュメ用HTML（slides/phaseN.html）から、ワークの問題文だけを抜き出した
1ワーク1ファイルのワークシートを生成する。講義中にその場でURLを渡す用途。

各ファイルに入るのは「題材」「設問」「記入枠」だけ。
解答例・講師用ノート・講義の解説パートは一切含めない。
"""
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_DIR = os.path.join(ROOT, "slides")
OUT_DIR = os.path.join(ROOT, "worksheet")

# ---------------------------------------------------------------- ワーク定義
# blocks: (取り出し方, 引数, 何番目か, 見出しを差し替える文言 or None)
#   cls       … そのセクション内の class=... なブロック
#   table_after … その class のブロックの直後にある <table>
#   figure    … そのセクション内の <figure>
#   details   … summary にこの文字列を含む <details>（中身だけ取り出す）
# ref: 別セクションから持ってくる場合の (セクション見出しの一部, blocks)

WORKS = [
    dict(
        wid="phase1-work1", step="step1", src="phase1.html",
        phase="第1回", phase_title="テストとは何か — マインドセットと基礎",
        label="ワーク①", title='その"バグ"は、どこにあったのか', time="個人5分 → 全体共有10分",
        lead="題材を読み、故障・欠陥・エラーに分解して表を埋めてください。",
        blocks=[("2. ワーク①", "cls", "work", 0),
                ("2. ワーク①", "table_after", "work", 0)],
    ),
    dict(
        wid="phase1-work2", step="step1", src="phase1.html",
        phase="第1回", phase_title="テストとは何か — マインドセットと基礎",
        label="ワーク②", title="観測メモを不具合チケットにする", time="ペア10分",
        lead="走り書きのメモから、開発者が動ける不具合チケットを1件起こします。",
        blocks=[("6. ワーク②", "cls", "work", 0)],
    ),
    dict(
        wid="phase2-work1", step="step1", src="phase2.html",
        phase="第2回", phase_title="仕様を読み、テストを設計する",
        label="ワーク①", title="曖昧な仕様から質問リストを作る", time="個人7分 → グループ共有8分",
        lead="仕様書の抜粋を読み、確認すべき質問を5つ書き出して優先度を付けます。",
        blocks=[("3. ワーク①", "cls", "work", 0),
                ("3. ワーク①", "cls", "spec", 0)],
    ),
    dict(
        wid="phase2-work2", step="step1", src="phase2.html",
        phase="第2回", phase_title="仕様を読み、テストを設計する",
        label="ワーク②", title="観点ブレスト", time="グループ10分",
        lead="ワーク①と同じ仕様を題材に、7つの引き出しからテスト観点を出します。",
        blocks=[("5. ワーク②", "cls", "work", 0),
                ("3. ワーク①", "cls", "spec", 0)],
    ),
    dict(
        wid="phase2-work3", step="step1", src="phase2.html",
        phase="第2回", phase_title="仕様を読み、テストを設計する",
        label="ワーク③", title="境界値とデシジョンテーブルでケース化", time="ペア: 作成9分 → 相互レビュー3分",
        lead="観点「金額の範囲・境界」を、境界値一覧とデシジョンテーブルに落とします。",
        blocks=[("7. ワーク③", "cls", "work", 0),
                ("3. ワーク①", "cls", "spec", 0),
                ("7. ワーク③", "details", "時間が余った", 0)],
    ),
    dict(
        wid="phase3-work1", step="step1", src="phase3.html",
        phase="第3回", phase_title="テストを管理し、品質を語る",
        label="ワーク①", title="このプロジェクト、リリースしてよい？", time="グループ15分 → 発表5分",
        lead="担当するB曲線と状況カードを読み、リリース判定会議への説明をまとめます。",
        blocks=[("2. 進捗と品質を読む", "figure", None, 0),
                ("3. ワーク①", "cls", "work", 0),
                ("3. ワーク①", "cls", "sit-common", 0),
                ("3. ワーク①", "cls", "sit-cards", 0)],
    ),
    dict(
        wid="phase4-work1", step="step2", src="phase4.html",
        phase="第4回", phase_title="テスト戦略とリスクベースドテスト",
        label="ワーク①", title="リスク分析（2ステップ）", time="全25分（Step A 13分 / Step B 12分）",
        lead="4つのレンズ（データの流れ／変更点／品質特性／過去と現場）でリスクを出し切り、評価して濃淡に翻訳します。",
        blocks=[("5. ワーク①", "cls", "example", 0),
                ("5. ワーク①", "cls", "work", 0),
                ("5. ワーク①", "cls", "work", 1)],
    ),
    dict(
        wid="phase5-work1", step="step2", src="phase5.html",
        phase="第5回", phase_title="シフトレフトと上流品質",
        label="ワーク①", title="要件レビュー演習", time="個人7分 → グループ共有8分",
        lead="観点フレームと曖昧語アンテナで要件定義書ドラフトをレビューし、指摘を質問の形にします。",
        blocks=[("4. ワーク①", "cls", "example", 0),
                ("4. ワーク①", "cls", "work", 0)],
    ),
    dict(
        wid="phase5-work2", step="step2", src="phase5.html",
        phase="第5回", phase_title="シフトレフトと上流品質",
        label="ワーク②", title="実例マッピング", time="グループ12分 → 共有3分",
        lead="受け入れ条件から、具体例（ルール・例・疑問）を洗い出します。",
        blocks=[("6. ワーク②", "cls", "example", 0),
                ("6. ワーク②", "cls", "work", 0)],
    ),
    dict(
        wid="phase6-work1", step="step2", src="phase6.html",
        phase="第6回", phase_title="テスト自動化とAI時代のQA",
        label="ミニ演習", title="AI生成テストケースをレビューしてみる", time="個人8分 →（任意）ペアで確認",
        lead="AIが出したテストケース一覧を、このまま使ってよいか判定します。（任意／自習にも使えます）",
        blocks=[("3. AI×QAの現在地マップ", "cls", "example", 0),
                ("3. AI×QAの現在地マップ", "cls", "example", 1),
                ("3. AI×QAの現在地マップ", "cls", "work", 0)],
    ),
    dict(
        wid="phase6-work2", step="step2", src="phase6.html",
        phase="第6回", phase_title="テスト自動化とAI時代のQA",
        label="ワーク", title="AIに任せたい仕事・握り続けたい仕事", time="個人5分 → 共有5分",
        lead="自分の業務を3つに仕分けし、「握り続けたい」理由を言葉にします。",
        blocks=[("5. ワーク", "cls", "work", 0)],
    ),
]

# ---------------------------------------------------------------- HTML 部品

STYLE = """
  :root {
    --ink: #1f2937;
    --accent: #1e3a5f;
    --accent-light: #eef3f9;
    --muted: #6b7280;
    --work: #b45309;
    --work-bg: #fff7ed;
    --ex-bg: #f3f4f6;
    --spec-bg: #fffbeb;
  }
  * { box-sizing: border-box; }
  body {
    margin: 0;
    font-family: "Hiragino Kaku Gothic ProN", "Yu Gothic UI", "Meiryo", sans-serif;
    color: var(--ink);
    background: #f6f7f9;
    line-height: 1.9;
  }
  .wrap { max-width: 860px; margin: 0 auto; padding: 32px 24px 80px; }
  nav.crumb { font-size: .85rem; margin-bottom: 14px; }
  nav.crumb a { color: var(--accent); text-decoration: none; }
  header.hero {
    background: var(--accent); color: #fff;
    border-radius: 12px; padding: 28px 32px; margin-bottom: 26px;
  }
  header.hero .label { font-size: .82rem; letter-spacing: .08em; opacity: .85; }
  header.hero h1 { margin: 6px 0 10px; font-size: 1.5rem; line-height: 1.4; }
  header.hero .time {
    display: inline-block; font-size: .82rem; background: rgba(255,255,255,.18);
    border-radius: 999px; padding: 2px 14px;
  }
  header.hero p { margin: 12px 0 0; opacity: .92; font-size: .95rem; }
  .work, .example, .spec, .sit-common, .extra {
    border-radius: 10px; padding: 18px 24px; margin: 20px 0;
  }
  .work { background: var(--work-bg); border-left: 5px solid var(--work); }
  .work .tag { color: var(--work); font-weight: 700; font-size: .82rem; letter-spacing: .05em; display: block; margin-bottom: 4px; }
  .example { background: var(--ex-bg); border-left: 5px solid #9ca3af; }
  .example .tag { color: #4b5563; font-weight: 700; font-size: .82rem; letter-spacing: .05em; display: block; margin-bottom: 4px; }
  .spec { background: var(--spec-bg); border: 1px solid #fcd34d; }
  .spec .tag { font-weight: 700; color: #92400e; font-size: .82rem; display: block; margin-bottom: 6px; }
  .sit-common { background: #fffbeb; border: 1px solid #fcd34d; font-size: .92rem; }
  .sit-common .tag { font-weight: 700; color: #92400e; font-size: .82rem; display: block; margin-bottom: 6px; }
  .sit-cards { display: grid; grid-template-columns: repeat(auto-fit, minmax(340px, 1fr)); gap: 16px; margin: 18px 0; }
  .sit-card { border: 1px solid #d1d5db; border-radius: 10px; background: #fff; overflow: hidden; font-size: .9rem; line-height: 1.7; }
  .sit-card .head { padding: 8px 16px; color: #fff; font-weight: 700; }
  .sit-card .body { padding: 6px 16px 14px; }
  .sit-card dl { margin: 0; }
  .sit-card dt { font-weight: 700; color: var(--accent); margin-top: 10px; font-size: .8rem; letter-spacing: .03em; }
  .sit-card dd { margin: 2px 0 0; }
  .extra { background: #fff; border: 1px dashed #9ca3af; }
  .extra .tag { color: var(--muted); font-weight: 700; font-size: .82rem; display: block; margin-bottom: 4px; }
  .memo {
    background: #fff; border: 1px dashed #b45309; border-radius: 8px;
    padding: 16px 22px; margin: 14px 0;
    font-size: .88rem; line-height: 1.85; color: #374151;
    white-space: pre-wrap;
  }
  .memo .memo-head { font-weight: 700; color: var(--work); display: block; margin-bottom: 6px; }
  table { border-collapse: collapse; width: 100%; margin: 14px 0; font-size: .92rem; background: #fff; }
  th, td { border: 1px solid #d1d5db; padding: 9px 13px; text-align: left; vertical-align: top; }
  th { background: var(--accent-light); color: var(--accent); }
  td.c, th.c { text-align: center; }
  figure { margin: 20px 0; text-align: center; background: #fff; border: 1px solid #e5e7eb; border-radius: 10px; padding: 16px; }
  figure figcaption { font-size: .85rem; color: var(--muted); margin-top: 6px; }
  figure svg { max-width: 100%; height: auto; }
  em { font-style: normal; background: linear-gradient(transparent 65%, #fde68a 65%); }
  code { background: #f3f4f6; padding: 1px 6px; border-radius: 4px; font-size: .9em; }
  .sheet { border-top: 1px dashed #d1d5db; margin-top: 34px; padding-top: 18px; }
  .sheet h2 { font-size: 1rem; color: var(--accent); margin: 0 0 10px; }
  .sheet textarea {
    width: 100%; min-height: 260px; padding: 14px 16px;
    border: 1px solid #d1d5db; border-radius: 10px; background: #fff;
    font-family: inherit; font-size: .95rem; line-height: 1.8; color: inherit; resize: vertical;
  }
  .sheet .note { font-size: .82rem; color: var(--muted); margin: 8px 0 0; }
  @media print {
    body { background: #fff; }
    .wrap { max-width: none; padding: 0; }
    nav.crumb, .sheet .note { display: none; }
    header.hero { background: #fff; color: var(--ink); border: 2px solid var(--accent); }
    header.hero .time { background: var(--accent-light); }
    .sheet textarea { min-height: 340px; }
  }
"""

PAGE = """<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{phase} {label} {title} — ワークシート</title>
<style>{style}</style>
</head>
<body>
<div class="wrap">
  <nav class="crumb"><a href="../index.html">← ワーク一覧</a></nav>

  <header class="hero">
    <div class="label">{phase} {phase_title}</div>
    <h1>{label} {title}</h1>
    <span class="time">{time}</span>
    <p>{lead}</p>
  </header>

{body}
  <div class="sheet">
    <h2>メモ・記入欄</h2>
    <textarea placeholder="ここに書き込めます（このページを閉じると消えます）"></textarea>
    <p class="note">※ 保存されません。残したい場合はコピーするか、ブラウザの印刷（Ctrl+P）で紙／PDFにしてください。</p>
  </div>
</div>
</body>
</html>
"""

INDEX = """<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>ワークシート一覧 — テストエンジニア育成講座</title>
<style>{style}
  .card {{
    display: block; background: #fff; border: 1px solid #e5e7eb;
    border-left: 6px solid var(--work); border-radius: 10px;
    padding: 16px 22px; margin-bottom: 12px;
    text-decoration: none; color: inherit;
  }}
  .card:hover {{ box-shadow: 0 4px 14px rgba(30,58,95,.15); }}
  .card .no {{ color: var(--work); font-weight: 700; font-size: .82rem; letter-spacing: .05em; }}
  .card h3 {{ margin: 2px 0 4px; font-size: 1.05rem; }}
  .card p {{ margin: 0; color: var(--muted); font-size: .9rem; }}
  .group {{ margin-top: 30px; }}
  .group > h2 {{ font-size: 1.05rem; color: var(--accent); margin: 0 0 12px; }}
</style>
</head>
<body>
<div class="wrap">
  <header class="hero">
    <div class="label">テストエンジニア育成講座</div>
    <h1>ワークシート一覧</h1>
    <p>講義中に配布するワーク用のページです。各ワークは題材と設問だけを載せています。</p>
  </header>
{groups}
</div>
</body>
</html>
"""

# ---------------------------------------------------------------- 抽出処理

DROP_SUMMARY = [r"講師用", r"解答例", r"質問リストの例と、優先度の付け方を見る",
                r"観点リストの例を見る", r"発表が終わってから開く"]


def match_element(html, start):
    """start 位置の開始タグに対応する終了タグまでの範囲を返す。"""
    tag = re.match(r"<([a-zA-Z0-9]+)", html[start:]).group(1)
    pos = start
    depth = 0
    pattern = re.compile(r"<%s\b[^>]*?(/?)>|</%s>" % (tag, tag))
    while True:
        m = pattern.search(html, pos)
        if not m:
            raise ValueError("unclosed <%s> at %d" % (tag, start))
        if m.group().startswith("</"):
            depth -= 1
            if depth == 0:
                return html[start:m.end()]
        elif m.group(1) != "/":
            depth += 1
        pos = m.end()


def drop_answer_details(html):
    """解答例・講師用ノートの <details> を落とす（誤って混ざらないための保険）。"""
    while True:
        for m in re.finditer(r"<details\b[^>]*>", html):
            block = match_element(html, m.start())
            s = re.search(r"<summary[^>]*>(.*?)</summary>", block, re.S)
            text = re.sub(r"<[^>]+>", "", s.group(1)) if s else ""
            if any(re.search(p, text) for p in DROP_SUMMARY):
                html = html[:m.start()] + html[m.start() + len(block):]
                break
        else:
            return html


def get_section(html, h2_substr):
    for m in re.finditer(r"<section\b[^>]*>", html):
        block = match_element(html, m.start())
        h2 = re.search(r"<h2[^>]*>(.*?)</h2>", block, re.S)
        if h2 and h2_substr in re.sub(r"<[^>]+>", "", h2.group(1)):
            return block
    raise LookupError("section not found: " + h2_substr)


def pick(section, kind, arg, n):
    if kind == "cls":
        hits = [m.start() for m in
                re.finditer(r'<div class="%s"[^>]*>' % re.escape(arg), section)]
        return match_element(section, hits[n])

    if kind == "table_after":
        hits = [m.start() for m in
                re.finditer(r'<div class="%s"[^>]*>' % re.escape(arg), section)]
        block = match_element(section, hits[n])
        after = hits[n] + len(block)
        m = re.compile(r"<table\b").search(section, after)
        return match_element(section, m.start())

    if kind == "figure":
        hits = [m.start() for m in re.finditer(r"<figure\b", section)]
        return match_element(section, hits[n])

    if kind == "details":
        for m in re.finditer(r"<details\b[^>]*>", section):
            block = match_element(section, m.start())
            s = re.search(r"<summary[^>]*>(.*?)</summary>", block, re.S)
            text = re.sub(r"<[^>]+>", "", s.group(1)) if s else ""
            if arg in text:
                inner = re.sub(r"^<details\b[^>]*>|</details>$", "", block).strip()
                inner = re.sub(r"<summary[^>]*>(.*?)</summary>", "", inner, flags=re.S).strip()
                return ('<div class="extra"><span class="tag">%s</span>\n%s\n</div>'
                        % (text, inner))
        raise LookupError("details not found: " + arg)

    raise ValueError(kind)


def indent(block, spaces="  "):
    return "\n".join(spaces + line if line.strip() else line
                     for line in block.split("\n"))


def main():
    cache = {}
    for step in ("step1", "step2"):
        os.makedirs(os.path.join(OUT_DIR, step), exist_ok=True)

    for w in WORKS:
        key = (w["step"], w["src"])
        if key not in cache:
            path = os.path.join(SRC_DIR, w["step"], w["src"])
            cache[key] = drop_answer_details(open(path, encoding="utf-8").read())
        html = cache[key]

        parts = []
        for h2_substr, kind, arg, n in w["blocks"]:
            parts.append(indent(pick(get_section(html, h2_substr), kind, arg, n)))
        body = "\n\n".join(parts) + "\n"

        page = PAGE.format(style=STYLE, body=body, **{
            k: w[k] for k in ("phase", "phase_title", "label", "title", "time", "lead")})
        out = os.path.join(OUT_DIR, w["step"], w["wid"] + ".html")
        with open(out, "w", encoding="utf-8", newline="") as f:
            f.write(page)
        print("build  %s/%s.html" % (w["step"], w["wid"]))

    # 一覧ページ
    groups = []
    for step, heading in (("step1", "Step1 — テスターの土台を作る"),
                          ("step2", "Step2 — 設計者として一段上がる")):
        cards = []
        for w in WORKS:
            if w["step"] != step:
                continue
            cards.append(
                '    <a class="card" href="{step}/{wid}.html">\n'
                '      <span class="no">{phase} ／ {label}（{time}）</span>\n'
                '      <h3>{title}</h3>\n'
                '      <p>{lead}</p>\n'
                '    </a>'.format(**w))
        groups.append('  <div class="group">\n    <h2>%s</h2>\n%s\n  </div>'
                      % (heading, "\n".join(cards)))

    with open(os.path.join(OUT_DIR, "index.html"), "w",
              encoding="utf-8", newline="") as f:
        f.write(INDEX.format(style=STYLE, groups="\n".join(groups)))
    print("build  index.html")


if __name__ == "__main__":
    main()
