#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Replicate the aii_web_tools__verify_quotes fetch+match logic EXACTLY; check every
source passage; report invalid ones with matched-context suggestions.
Run: <ability venv python> repair_quotes.py
"""
import json, sys, os, re
import requests
import fitz
import html2text

WS = "/ai-inventor/aii_data/runs/run_fEjgpc8BQoQS/3_invention_loop/iter_2/gen_art/gen_art_research_1"
sys.path.insert(0, WS)
from sources_data import SOURCES

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
        print("  fetch error for", url, ":", e)
    return None

def find_match(quote, content):
    qn = " ".join(quote.split()).lower()
    cn = " ".join(content.split()).lower()
    idx = cn.find(qn)
    if idx == -1:
        return None
    start = max(0, idx - 80)
    end = min(len(cn), idx + len(qn) + 80)
    ctx = cn[start:end]
    if start > 0:
        ctx = "..." + ctx
    if end < len(cn):
        ctx = ctx + "..."
    return ctx

def main():
    cache = {}
    invalid = []
    for s in SOURCES:
        url = s["url"]
        passages = s.get("supporting_passages", [])
        if not passages:
            continue
        if url not in cache:
            cache[url] = fetch_content(url)
            print(f"[fetch] {s['index']} {url[:90]} -> {'OK' if cache[url] is not None else 'NONE'}")
        content = cache[url]
        for p in passages:
            q = p["quote"]
            if content is None:
                invalid.append((s["index"], q, "UNFETCHABLE", None))
                continue
            ctx = find_match(q, content)
            if ctx is None:
                invalid.append((s["index"], q, "NO-MATCH", None))
            else:
                pass  # matched
    print("\n===== INVALID PASSAGES:", len(invalid), "=====")
    for idx, q, why, _ in invalid:
        print(f"[{idx}] {why} :: {q[:140]!r}")
    # context suggestions: for NO-MATCH, find distinctive keyword hits
    for idx, q, why, _ in invalid:
        if why != "NO-MATCH":
            continue
        s = SOURCES[idx - 1]
        content = cache.get(s["url"])
        if not content:
            continue
        cn = " ".join(content.split())
        # take first 3 significant words of the quote as probe
        words = [w for w in re.split(r"\W+", q.lower()) if len(w) > 3][:4]
        probe = " ".join(words[:3])
        pid = cn.lower().find(probe)
        if pid != -1:
            print(f"\n[{idx}] probe {probe!r} at {pid} -> ...{cn[max(0,pid-60):pid+220]}...")
        else:
            print(f"\n[{idx}] probe {probe!r} NOT FOUND in content (len={len(cn)})")

if __name__ == "__main__":
    main()