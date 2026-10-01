#!/usr/bin/env python3
"""Check whether MVP Summit registration has opened.

Fetches the Summit home page, reduces it to a normalized snapshot (visible text
plus links/buttons), compares it with the committed snapshot.txt and writes
results for the workflow to act on.

Outputs (GITHUB_OUTPUT): changed, opened, reasons
Files: snapshot.txt (updated in place), issue_body.md (diff + signals)
"""
import difflib
import os
import re
import sys
import urllib.request
from html.parser import HTMLParser

URL = "https://summit.microsoft.com/en-us/"
SNAPSHOT = "snapshot.txt"
SKIP_TAGS = {"script", "style", "noscript", "svg", "head"}
BLOCK_TAGS = {"p", "div", "h1", "h2", "h3", "h4", "h5", "h6", "li", "br", "section", "main", "footer", "header", "nav"}
REGISTER_RE = re.compile(r"regist", re.I)


class Extractor(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.skip = 0
        self.lines = []
        self.buf = []
        self.controls = []   # (kind, text, href/id)
        self.stack = []      # open <a>/<button>: [kind, href, id, text_parts]

    def flush(self):
        text = " ".join("".join(self.buf).split())
        if text:
            self.lines.append("TEXT: " + text)
        self.buf = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag in SKIP_TAGS:
            self.skip += 1
            return
        if tag in BLOCK_TAGS:
            self.flush()
        if tag in ("a", "button"):
            href = re.sub(r"\?v=[\w-]+", "", a.get("href") or "")
            self.stack.append([tag, href, a.get("id") or "", []])
        elif a.get("id") and REGISTER_RE.search(a["id"]):
            self.controls.append(("element-id", "", a["id"]))

    def handle_endtag(self, tag):
        if tag in SKIP_TAGS:
            self.skip = max(0, self.skip - 1)
            return
        if tag in BLOCK_TAGS:
            self.flush()
        if tag in ("a", "button") and self.stack:
            kind, href, id_, parts = self.stack.pop()
            text = " ".join(" ".join(parts).split())
            self.controls.append((kind, text, href or id_))

    def handle_data(self, data):
        if self.skip:
            return
        self.buf.append(data)
        if self.stack:
            self.stack[-1][3].append(data)


def fetch():
    req = urllib.request.Request(URL, headers={"User-Agent": "Mozilla/5.0 (summit-tracker)"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8", "replace")


def main():
    html = fetch()
    p = Extractor()
    p.feed(html)
    p.flush()

    text = "\n".join(p.lines)
    if "MVP Summit" not in text or len(p.lines) < 3:
        sys.exit("Fetched page looks wrong (blocked or error page?); not touching state.")

    links = sorted({f"{k.upper()}: {t} | {h}" for k, t, h in p.controls})
    snapshot = "\n".join(p.lines + links) + "\n"

    reasons = []
    if "registration coming soon" not in text.lower():
        reasons.append('"Registration coming soon." text is gone')
    for kind, t, ref in p.controls:
        if REGISTER_RE.search(t) or REGISTER_RE.search(ref):
            reasons.append(f"registration {kind} found: '{t}' -> {ref}")

    old = open(SNAPSHOT, encoding="utf-8").read() if os.path.exists(SNAPSHOT) else None
    changed = old is not None and old != snapshot
    first_run = old is None
    diff = ""
    if changed:
        diff = "".join(difflib.unified_diff(
            old.splitlines(True), snapshot.splitlines(True), "previous", "current", n=1))

    if changed or first_run:
        open(SNAPSHOT, "w", encoding="utf-8", newline="\n").write(snapshot)

    with open("issue_body.md", "w", encoding="utf-8") as f:
        f.write(f"Page: {URL}\n\n")
        if reasons:
            f.write("**Registration signals:**\n" + "\n".join(f"- {r}" for r in reasons) + "\n\n")
        if diff:
            f.write("**Changes since last snapshot:**\n```diff\n" + diff + "```\n")

    out = {
        "changed": str(changed or first_run).lower(),
        "first_run": str(first_run).lower(),
        "opened": str(bool(reasons)).lower(),
    }
    print(out, reasons)
    if os.environ.get("GITHUB_OUTPUT"):
        with open(os.environ["GITHUB_OUTPUT"], "a") as f:
            for k, v in out.items():
                f.write(f"{k}={v}\n")


if __name__ == "__main__":
    main()
