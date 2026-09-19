#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Final passage-repair pipeline (verifier-exact):
1. Remap body-quote sources to PDF URLs.
2. Fetch each URL exactly like aii_verify_quotes (requests + html2text / fitz).
3. Passage matches? keep. Else reconstruct from the longest common block,
   mapped back to ORIGINAL case/punctuation of the fetched text, trimmed to
   sentence boundaries (any contiguous substring of the fetched text matches
   the verifier's whitespace-collapsed, lowercased search).
4. Drop a passage only if the best block is < 30 chars or unmappable.
5. Final pass: re-verify every passage; report failures.
Writes sources_repaired.json and repair3_report.txt.
"""
import json, sys, os, re
import requests
import fitz
import html2text
from difflib import SequenceMatcher

WS = "/ai-inventor/aii_data/runs/run_fEjgpc8BQoQS/3_invention_loop/iter_2/gen_art/gen_art_research_1"
sys.path.insert(0, WS)
from sources_data import SOURCES

URL_REMAP = {
    7:  "https://arxiv.org/pdf/2404.01318",
    16: "https://arxiv.org/pdf/2607.01854v2",
    23: "https://arxiv.org/pdf/2406.11717",
    24: "https://arxiv.org/pdf/2609.04721",
    28: "https://arxiv.org/pdf/2404.15255",
    30: "https://aclanthology.org/2026.acl-long.1334.pdf",
    56: "https://arxiv.org/pdf/2402.04249",
}

_session = requests.Session()
_session.headers.update({"User-Agent": "Mozilla/5.0"})


def extract(resp, url):
    ct = resp.headers.get("content-type", "").lower()
    is_pdf = "pdf" in ct or url.lower().endswith(".pdf")
    if is_pdf:
        doc = fitz.open(stream=resp.content, filetype="pdf")
        content = "\n".join(page.get_text() for page in doc)
        doc.close()
        return content
    h = html2text.HTML2Text()
    h.ignore_links = False
    h.ignore_images = True
    h.body_width = 0
    return h.handle(resp.text)


def fetch_content(url):
    try:
        resp = _session.get(url, allow_redirects=True, timeout=60)
        if resp.status_code == 200:
            return extract(resp, url)
    except Exception as e:
        print("  fetch error", url, e)
    return None


def norm(s):
    return " ".join(s.split()).lower()


def find_match(quote, content):
    qn, cn = norm(quote), norm(content)
    idx = cn.find(qn)
    if idx == -1:
        return None
    return cn[idx:idx + len(qn)]


def map_back(fragment_norm, content):
    """Map a whitespace-collapsed fragment back to an original-case contiguous span."""
    tokens = re.findall(r"\S+", fragment_norm)
    pat = r"\s+".join(re.escape(t) for t in tokens)
    m = re.search(pat, content.lower(), re.S)
    if not m:
        return None
    return content[m.start():m.end()]


def sentence_extend_orig(text, start, end, cap=700):
    while start > 0 and text[start - 1] not in ".!?;:" and (end - start) < cap:
        start -= 1
    while end < len(text) and text[end] not in ".!?;" and (end - start) < cap:
        end += 1
    if end < len(text) and text[end] in ".!?;":
        end += 1
    return text[start:end].strip()


def lcs_replacement(quote, content):
    qn, cn = norm(quote), norm(content)
    if len(cn) > 150000:
        frag = qn[:20]
        i = cn.find(frag)
        if i != -1:
            cn = cn[max(0, i - 3000): i + 3000]
    sm = SequenceMatcher(None, qn, cn, autojunk=False)
    best = max(sm.get_matching_blocks(), key=lambda b: b.size)
    if best.size < 30:
        return None
    frag = cn[best.b:best.b + best.size]
    sp = map_back(frag, content)
    if sp is None:
        return None
    start = content.find(sp)
    end = start + len(sp)
    return sentence_extend_orig(content, start, end)


def main():
    out, report = [], []
    for s in SOURCES:
        idx = s["index"]
        url = URL_REMAP.get(idx, s["url"])
        rec = dict(s)
        rec["url"] = url
        passages = s.get("supporting_passages", [])
        if not passages:
            out.append(rec)
            continue
        print(f"[{idx}] fetching {url[:95]}...", flush=True)
        content = fetch_content(url)
        if content is None:
            rec["supporting_passages"] = []
            report.append(f"[{idx}] UNFETCHABLE {url}")
            out.append(rec)
            continue
        newp = []
        for p in passages:
            q = p["quote"]
            if find_match(q, content) is not None:
                newp.append(p)
                continue
            repl = lcs_replacement(q, content)
            if repl is None or len(repl) < 30:
                report.append(f"[{idx}] DROPPED: {q[:90]!r}")
            else:
                newp.append({"quote": repl, "locator": p.get("locator", None)})
                report.append(f"[{idx}] REPLACED ({len(repl)} chars): {repl[:110]!r}")
        rec["supporting_passages"] = newp
        out.append(rec)

    # final verification pass
    fails = []
    for r_ in out:
        c = fetch_content(r_["url"])
        for p in r_.get("supporting_passages", []):
            if c is None or find_match(p["quote"], c) is None:
                fails.append((r_["index"], p["quote"][:80]))

    with open(os.path.join(WS, "sources_repaired.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    with open(os.path.join(WS, "repair3_report.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(report) + f"\n\nFINAL FAILS: {len(fails)}\n")
        for x in fails:
            f.write(str(x) + "\n")
    print("\n".join(report[:80]))
    print(f"\nFINAL FAILS: {len(fails)}")
    for x in fails[:20]:
        print(x)
    print("sources_repaired.json written")


if __name__ == "__main__":
    main()