#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import datetime as dt
import os
import re
import sys
from pathlib import Path


JST = dt.timezone(dt.timedelta(hours=9))


def today_jst_str():
    return dt.datetime.now(JST).strftime("%Y-%m-%d")


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_text(path: Path, content: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")


def create_daily_from_template(date_str: str, force: bool) -> Path:
    docs = Path("docs")
    template = docs / "daily-template.html"
    if not template.exists():
        print(f"[ERROR] テンプレートが見つかりません: {template}", file=sys.stderr)
        sys.exit(1)

    out_file = docs / f"{date_str}.html"
    if out_file.exists() and not force:
        print(f"[INFO] 既に存在します: {out_file}（--force で上書き可）")
    else:
        html = read_text(template)
        html = html.replace("YYYY-MM-DD", date_str)
        write_text(out_file, html)
        print(f"[OK] 生成: {out_file}")
    return out_file


def update_index(date_str: str):
    index = Path("docs/index.html")
    if not index.exists():
        print(f"[ERROR] index が見つかりません: {index}", file=sys.stderr)
        sys.exit(1)

    html = read_text(index)

    # 1) 最新セクションの「本日の版」リンクを更新
    latest_pattern = re.compile(
        r'<li><a href="\./[0-9]{4}-[0-9]{2}-[0-9]{2}\.html">[0-9]{4}-[0-9]{2}-[0-9]{2}（本日の版）</a></li>'
    )
    latest_repl = f'<li><a href="./{date_str}.html">{date_str}（本日の版）</a></li>'
    if latest_pattern.search(html):
        html = latest_pattern.sub(latest_repl, html, count=1)
    else:
        # まだプレースホルダのままなら置換
        html = html.replace(
            '<li><a href="./YYYY-MM-DD.html">YYYY-MM-DD（本日の版）</a></li>',
            latest_repl,
        )

    # 2) アーカイブに当日リンクを先頭追加（重複回避）
    archive_li = f'<li><a href="./{date_str}.html">{date_str}</a></li>'
    html_no_comments = re.sub(r"<!--.*?-->", "", html, flags=re.DOTALL)
    if archive_li not in html_no_comments:
        # <h2>アーカイブ</h2> セクション内の <ul> 内容にプレペンド
        pattern = re.compile(r"(<h2>アーカイブ</h2>\s*<ul>)(.*?)(</ul>)", re.DOTALL)
        def _inject(match: re.Match) -> str:
            head, body, tail = match.groups()
            # 先頭に当日リンクを追加（元の body を保持）
            prepend = f"\n          {archive_li}"
            return head + prepend + body + tail
        new_html, n = pattern.subn(_inject, html, count=1)
        if n == 1:
            html = new_html
        else:
            # フォールバック: 直後の <ul> の直後に挿入
            ul_pos = html.find("<h2>アーカイブ</h2>")
            if ul_pos != -1:
                ul_open = html.find("<ul>", ul_pos)
                if ul_open != -1:
                    insert_at = ul_open + len("<ul>")
                    html = html[:insert_at] + "\n          " + archive_li + html[insert_at:]

    write_text(index, html)
    print(f"[OK] 更新: {index}")


def main():
    parser = argparse.ArgumentParser(description="docs 用 当日版の自動生成と index 更新")
    parser.add_argument("--date", help="YYYY-MM-DD（未指定はJSTの今日）", default=None)
    parser.add_argument("--force", help="既存の当日版を上書き", action="store_true")
    args = parser.parse_args()

    date_str = args.date or today_jst_str()
    # 軽いバリデーション
    try:
        dt.datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        print("[ERROR] --date は YYYY-MM-DD 形式で指定してください", file=sys.stderr)
        sys.exit(2)

    out_file = create_daily_from_template(date_str, force=args.force)
    update_index(date_str)
    print("[DONE] 完了。GitHubへ push して公開してください。")


if __name__ == "__main__":
    main()
