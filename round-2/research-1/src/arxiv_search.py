#!/usr/bin/env python3
"""arXiv API phrase search helper for the saturation sweep.
Usage: python3 arxiv_search.py "phrase one" AND "phrase two" [n_results]
Quotes group phrases; AND/or operators between groups. Prints id, title, url, date.
"""
import sys, time, urllib.parse, subprocess, re
import xml.etree.ElementTree as ET

NS = {"a": "http://www.w3.org/2005/Atom", "op": "http://a9.com/-/spec/opensearch/1.1/"}

def build_query(parts):
    """Build arXiv API search_query with proper encoding.
    Phrase tokens ('"a b"') become all:%22a+b%22; bare words become all:word.
    Operators AND/OR passed through."""
    tokens = []
    for p in parts:
        u = p.upper()
        if u in ("AND", "OR", "ANDNOT"):
            tokens.append(u)
        elif p.startswith('"') and p.endswith('"'):
            inner = p[1:-1].replace(" ", "%20")
            tokens.append(f"all:%22{inner}%22")
        else:
            tokens.append("all:" + urllib.parse.quote(p, safe=""))
    return "+".join(tokens)

def search(parts, n=12):
    q = build_query(parts)
    url = "https://export.arxiv.org/api/query?search_query=" + q
    url += f"&start=0&max_results={n}&sortBy=relevance"
    xml = subprocess.run(
        ["curl", "-s", "-A", "Mozilla/5.0 (research-artifact)", url],
        capture_output=True, timeout=60, check=True,
    ).stdout
    root = ET.fromstring(xml)
    out = []
    for e in root.findall("a:entry", NS):
        eid = e.find("a:id", NS).text.strip()
        title = re.sub(r"\s+", " ", e.find("a:title", NS).text.strip())
        pub = e.find("a:published", NS).text[:10]
        out.append((eid, title, pub))
    return out

if __name__ == "__main__":
    args = sys.argv[1:]
    n = 12
    if args and args[-1].isdigit():
        n = int(args[-1]); args = args[:-1]
    for eid, title, pub in search(args, n):
        print(f"{pub} | {eid} | {title[:110]}")
    time.sleep(3)  # arxiv API politeness