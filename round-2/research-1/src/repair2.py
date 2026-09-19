#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Repair passages to exact spans of the fetched source text (verifier-compatible).
1) Remaps source URLs where quotes are body text (abs -> pdf).
2) Fetches each URL exactly like aii_verify_quotes (requests + html2text / fitz).
3) Verifies each passage; replaces NO-MATCH passages with the longest common
   character block of the normalized content, extended to sentence boundaries.
4) Drops passages whose best block is < 40 chars.
Writes sources_repaired.json + repair2_report.txt.
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
    qn = norm(quote); cn = norm(content)
    idx = cn.find(qn)
    if idx == -1:
        return None
    return cn[idx:idx+len(qn)]

def sentence_extend(txt, start, end, cap=600):
    # extend within normalized (whitespace-collapsed) text to sentence boundaries
    while start > 0 and txt[start-1] not in ".!?;:" and (end - start) < cap:
        start -= 1
    while end < len(txt) and txt[end] not in ".!?;" and (end - start) < cap:
        end += 1
    if end < len(txt):
        end += 1
    return txt[start:end]

def lcs_span(quote, content):
    qn = norm(quote); cn = norm(content)
    if len(cn) > 120000:
        # constrain search window to a sliding band around the first occurrence of a distinctive 12-char fragment
        frag = qn[:min(25, len(qn))]
        i = cn.find(frag)
        if i != -1:
            cn = cn[max(0, i - 4000): i + 4000]
    sm = SequenceMatcher(None, qn, cn, autojunk=False)
    blocks = sm.get_matching_blocks()
    best = max(blocks, key=lambda b: b.size)
    if best.size < 40:
        return None
    return sentence_extend(cn, best.b, best.b + best.size)

def main():
    out = []
    report = []
    for s in SOURCES:
        idx = s["index"]
        url = URL_REMAP.get(idx, s["url"])
        rec = dict(s)
        rec["url"] = url
        passages = s.get("supporting_passages", [])
        if not passages:
            out.append(rec); continue
        print(f"[{idx}] fetching {url[:95]}...", flush=True)
        content = fetch_content(url)
        if content is None:
            rec["supporting_passages"] = []
            report.append(f"[{idx}] UNFETCHABLE {url}")
            out.append(rec); continue
        newp = []
        for p in passages:
            q = p["quote"]
            if find_match(q, content) is not None:
                newp.append(p)
                continue
            repl = lcs_span(q, content)
            if repl is None:
                report.append(f"[{idx}] DROPPED: {q[:100]!r}")
            else:
                newp.append({"quote": repl, "locator": p.get("locator", None)})
                report.append(f"[{idx}] REPLACED ({len(repl)} chars): {repl[:120]!r}")
        rec["supporting_passages"] = newp
        out.append(rec)

    with open(os.path.join(WS, "sources_repaired.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    with open(os.path.join(WS, "repair2_report.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(report))
    print("\n".join(report[:60]))
    print(f"\nrepaired sources → sources_repaired.json; changed lines: {len(report)}")

if __name__ == "__main__":
    main()