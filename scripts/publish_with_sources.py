#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import json
import re
from pathlib import Path


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write(path: Path, content: str):
    path.write_text(content, encoding="utf-8", newline="\n")


def remove_draft_note(html: str) -> str:
    return re.sub(r'\n\s*<p class="note">本稿はドラフト（一次情報確認待ち）。.*?</p>', "", html, flags=re.DOTALL)


def replace_item_body(html: str, idx: int, body: str) -> str:
    # Find the section for item number idx (e.g., '1) ' in <h3> tag), then replace the first <p> that follows this <h3>
    pattern = re.compile(rf"(<h3>\s*{idx}\) [^<]+</h3>)(\s*<p>.*?</p>)", re.DOTALL)
    def _repl(m):
        return m.group(1) + f"\n          <p>{body}</p>"
    return pattern.sub(_repl, html, count=1)


def replace_item_sources(html: str, idx: int, sources: list[dict]) -> str:
    # Build sources HTML: e.g., 一次情報: <a href="URL">Label</a> / <a href="URL">Label</a>
    links = " / ".join([f'<a href="{s.get("url")}">{s.get("label")}</a>' for s in sources if s.get("url") and s.get("label")])
    if not links:
        return html
    new_li = f"<li>一次情報: {links}</li>"
    # Replace the existing line that starts with 一次情報:
    pattern = re.compile(rf"(<h3>\s*{idx}\) [^<]+</h3>.*?<ul>.*?)(<li>一次情報: .*?</li>)(.*?</ul>)", re.DOTALL)
    def _repl(m):
        return m.group(1) + new_li + m.group(3)
    return pattern.sub(_repl, html, count=1)


def main():
    ap = argparse.ArgumentParser(description="Dailyページに一次情報URLと本文を差し込み、ドラフト注記を削除")
    ap.add_argument("--date", required=True, help="YYYY-MM-DD 対象日付")
    ap.add_argument("--json", required=True, help="ソース定義JSONファイルのパス")
    args = ap.parse_args()

    doc_path = Path("docs") / f"{args.date}.html"
    if not doc_path.exists():
        raise SystemExit(f"docs/{args.date}.html が見つかりません。先に generate_daily.py を実行してください。")

    data = json.loads(read(Path(args.json)))
    items = data.get("items", [])
    if len(items) != 10:
        raise SystemExit("JSONの items は10件である必要があります。")

    html = read(doc_path)
    html = remove_draft_note(html)

    for i, item in enumerate(items, start=1):
        body = item.get("body")
        if body:
            html = replace_item_body(html, i, body)
        sources = item.get("sources", [])
        if sources:
            html = replace_item_sources(html, i, sources)

    write(doc_path, html)
    print(f"[OK] 確定差し込み完了: {doc_path}")


if __name__ == "__main__":
    main()

