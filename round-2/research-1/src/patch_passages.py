#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Manual polish of repaired passages: replace awkward spans with cleaner exact
substrings where they verify, add the N-GLARE Qwen3-4B quote to source 30 and a
short pin quote to source 46. Every replacement is checked with find_match."""
import json, sys, os, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, "/ai-inventor/aii_data/runs/run_fEjgpc8BQoQS/3_invention_loop/iter_2/gen_art/gen_art_research_1")

import requests
import html2text
import fitz
from difflib import SequenceMatcher

WS = "/ai-inventor/aii_data/runs/run_fEjgpc8BQoQS/3_invention_loop/iter_2/gen_art/gen_art_research_1"
PATH = os.path.join(WS, "sources_repaired.json")
data = json.load(open(PATH, encoding="utf-8"))

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

_cache = {}
def content_of(url):
    if url not in _cache:
        try:
            r = _session.get(url, allow_redirects=True, timeout=60)
            _cache[url] = extract(r, url) if r.status_code == 200 else None
        except Exception:
            _cache[url] = None
    return _cache[url]

def norm(s):
    return " ".join(s.split()).lower()

def ok(quote, content):
    return content is not None and norm(quote) in norm(content)

def lcs_from(quote, content, minlen=30):
    qn, cn = norm(quote), norm(content)
    sm = SequenceMatcher(None, qn, cn, autojunk=False)
    best = max(sm.get_matching_blocks(), key=lambda b: b.size)
    if best.size < minlen:
        return None
    frag = cn[best.b:best.b + best.size]
    tokens = re.findall(r"\S+", frag)
    pat = r"\s+".join(re.escape(t) for t in tokens)
    m = re.search(pat, content.lower(), re.S)
    if not m:
        return None
    return content[m.start():m.end()].strip()

def rec(idx):
    return data[idx - 1] if False else data[idx - 1]

def set_passages(idx, new_quotes):
    pass

def main():
    log = []

    # ---- index helpers ----
    by_index = {s["index"]: s for s in data}

    # [1] q1: nicer exact substrings on the github HTML page
    c1 = content_of(by_index[1]["url"])
    cands1 = ["HarmBench provide 3 classifier models:",
              "is a validation classifier and support standard, contextual and multimodal behaviors"]
    keep1 = []
    for cand in cands1:
        if ok(cand, c1):
            keep1.append({"quote": cand, "locator": "README.md rendered on the repo page, 'Classifiers' section"})
    if keep1:
        others = [p for p in by_index[1]["supporting_passages"] if "provide 3 classifier" not in norm(p["quote"])]
        by_index[1]["supporting_passages"] = others + keep1
        log.append("[1] replaced classifier-list passages")

    # [2] q1: exact JSON fragment
    c2 = content_of(by_index[2]["url"])
    cand2 = '"sha":"8e1604d1171fe8a48d8febecd22f600e462bdcdd"'
    if ok(cand2, c2):
        by_index[2]["supporting_passages"] = [{"quote": cand2, "locator": "GET /repos/centerforaisafety/HarmBench/commit/main"}]
        log.append("[2] replaced sha passage")

    # [4] q1: prompt opening (avoid html2text-mangled angle tags)
    c4 = content_of(by_index[4]["url"])
    cand4 = "You are a classifier for red teaming large language models (LLMs). Given a generation, determine whether it counts as an instance of the following behavior"
    if ok(cand4, c4):
        newp = [{"quote": cand4, "locator": "eval_utils.py, LLAMA2_CLS_PROMPT['prompt'] (verbatim, first paragraph)"}]
        newp += [p for p in by_index[4]["supporting_passages"] if "generations must be in english" not in norm(p["quote"])]
        by_index[4]["supporting_passages"] = newp
        log.append("[4] replaced judge-prompt opening")

    # [5] q1: drop link-markup-heavy span, keep clean sentence parts
    c5 = content_of(by_index[5]["url"])
    cand5a = "The harmful behaviors dataset comprises of 100 distinct misuse behaviors"
    cand5b = "divided into ten broad categories corresponding to"
    keep5 = []
    for cand in (cand5a, cand5b):
        if ok(cand, c5):
            keep5.append({"quote": cand, "locator": "README.md, 'Accessing the JBB-Behaviors datasets'"})
    if keep5:
        others = [p for p in by_index[5]["supporting_passages"] if "comprises of 100" not in norm(p["quote"])]
        by_index[5]["supporting_passages"] = others + keep5
        log.append("[5] replaced harmful-dataset passages")

    # [47] nicer doc quote
    c47 = content_of(by_index[47]["url"])
    cand47 = "Compute Cohen's kappa: a statistic that measures inter-annotator agreement"
    if ok(cand47, c47):
        by_index[47]["supporting_passages"] = [{"quote": cand47, "locator": "sklearn API reference (function description)"}]
        log.append("[47] replaced kappa passage")

    # [46] add passage via LCS extraction from the pingouin page
    c46 = content_of(by_index[46]["url"])
    frag46 = lcs_from("Returns: r float, Partial correlation coeffisient", c46)
    if frag46:
        byp_index46 = by_index[46]
        byp_index46["supporting_passages"].append({"quote": frag46, "locator": "Pingouin API reference"})
        log.append("[46] added partial_corr passage: " + frag46[:90])

    # [30] add the Qwen3-4B figure quote (ACL PDF)
    c30 = content_of(by_index[30]["url"])
    frag30 = lcs_from("multiple variants of the same base model RL-aligned, base, and safety-removed versions of Qwen3-4B", c30)
    if frag30:
        by_index[30]["supporting_passages"].append({"quote": frag30, "locator": "ACL PDF, p.2 'Figure 1 supports the core intuition'"})
        log.append("[30] added Qwen3-4B figure quote: " + frag30[:100])

    # ---- final verification of the whole list ----
    fails = []
    for s in data:
        c = content_of(s["url"])
        for p in s.get("supporting_passages", []):
            if not ok(p["quote"], c):
                fails.append((s["index"], p["quote"][:70]))
    if fails:
        print("FAILS remain:"); [print(f) for f in fails]
    else:
        print("ALL PASSAGES VERIFIEED:", sum(len(s.get('supporting_passages', [])) for s in data), "passages")
    json.dump(data, open(PATH, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print("\n".join(log))

main()