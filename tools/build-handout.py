# -*- coding: utf-8 -*-
"""レジュメ用HTML（phaseN.html）から、受講者に見せたくない部分を落とした配布版を生成する。

落とすもの:
  - <details> のうち summary が講師用ノート・解答例にあたるもの（DROP_PATTERNS）
  - 上記だけを中身にしていた見出し（残すと空見出しになるため）

残すもの:
  - 進行表、自習用の補足、任意の追加課題など、受講者が見てよい <details>
"""
import os
import re
import shutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_DIR = os.path.join(ROOT, "slides")
OUT_DIR = os.path.join(ROOT, "handout")

PAGES = [
    ("step1", "phase1.html"),
    ("step1", "phase2.html"),
    ("step1", "phase3.html"),
    ("step2", "phase4.html"),
    ("step2", "phase5.html"),
    ("step2", "phase6.html"),
]
INDEXES = [("step1", "index.html"), ("step2", "index.html")]

# summary がこのいずれかに当たる <details> を丸ごと削除する
DROP_PATTERNS = [
    r"講師用",
    r"解答例",
    r"質問リストの例と、優先度の付け方を見る",
    r"観点リストの例を見る",
    r"発表が終わってから開く",
]

# details を消したあとに残ると意味をなさない見出し（ファイル名 -> 見出しテキスト）
DROP_HEADINGS = {
    "phase3.html": ["各カードの読み解き"],
}


def find_details(html):
    """<details> ブロックを入れ子込みで列挙する。 -> [(start, end, summary, depth)]"""
    blocks = []
    stack = []
    for tok in re.finditer(r"<details\b[^>]*>|</details>", html):
        if tok.group().startswith("<details"):
            stack.append(tok.start())
        else:
            start = stack.pop()
            end = tok.end()
            m = re.search(r"<summary[^>]*>(.*?)</summary>", html[start:end], re.S)
            summary = re.sub(r"<[^>]+>", "", m.group(1)).strip() if m else ""
            blocks.append((start, end, summary, len(stack)))
    return blocks


def should_drop(summary):
    return any(re.search(p, summary) for p in DROP_PATTERNS)


def strip_details(html):
    """削除対象の details を除去する。入れ子は外側優先（外側を消せば内側も消える）。"""
    targets = []
    for start, end, summary, depth in find_details(html):
        if not should_drop(summary):
            continue
        # すでに削除対象に含まれている（＝親が対象）ならスキップ
        if any(s <= start and end <= e for s, e, _ in targets):
            continue
        targets.append((start, end, summary))

    removed = []
    for start, end, summary in sorted(targets, key=lambda t: -t[0]):
        # 直前の空白・改行も一緒に落として詰める
        head = start
        while head > 0 and html[head - 1] in " \t":
            head -= 1
        html = html[:head] + html[end:]
        removed.append(summary)
    return html, list(reversed(removed))


def strip_headings(html, filename):
    for text in DROP_HEADINGS.get(filename, []):
        html = re.sub(
            r"[ \t]*<h3>\s*" + re.escape(text) + r"\s*</h3>\n", "", html
        )
    return html


def main():
    for step, name in PAGES + INDEXES:
        stale = os.path.join(OUT_DIR, step, name)
        if os.path.exists(stale):
            os.remove(stale)

    for step, name in INDEXES:
        dst_dir = os.path.join(OUT_DIR, step)
        os.makedirs(dst_dir, exist_ok=True)
        shutil.copyfile(os.path.join(SRC_DIR, step, name), os.path.join(dst_dir, name))
        print("copy   %s/%s" % (step, name))

    for step, name in PAGES:
        src = os.path.join(SRC_DIR, step, name)
        html = open(src, encoding="utf-8").read()
        html, removed = strip_details(html)
        html = strip_headings(html, name)
        # 削除跡の空行が続くのを1行にまとめる
        html = re.sub(r"\n{3,}", "\n\n", html)

        dst = os.path.join(OUT_DIR, step, name)
        with open(dst, "w", encoding="utf-8", newline="") as f:
            f.write(html)

        print("build  %s/%s  (%d blocks removed)" % (step, name, len(removed)))
        for summary in removed:
            print("         - " + summary)

        left = [s for _, _, s, _ in find_details(html)]
        for summary in left:
            print("         + kept: " + summary)


if __name__ == "__main__":
    main()
