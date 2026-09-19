import json
from pathlib import Path

W = Path(__file__).resolve().parent
# Read quotes as they ended up in the BUILT JSON (post-json.dumps) so escaping matches exactly.
d = json.loads((W / ".sdk_openhands_agent_struct_out.json").read_text(encoding="utf-8"))
QUOTES = {}
for s in d["sources"]:
    for p in s.get("supporting_passages", []):
        QUOTES.setdefault(s["index"], []).append(p["quote"])

raw_tok = (W / "evidence" / "tok_Qwen3-0.6B.json").read_text(encoding="utf-8")
for q in QUOTES.get(9, []):
    print("Q9 in raw tok file:", repr(q[:60]), "->", q in raw_tok)

gemma_raw = Path("/tmp/gemma_tok.json")
if gemma_raw.exists():
    raw = gemma_raw.read_text(encoding="utf-8")
    for q in QUOTES.get(26, []):
        print("Gemma quote in raw tok:", repr(q[:60]), "->", q in raw)
    d2 = json.loads(raw)
    print("gemma has chat_template:", bool(d2.get("chat_template", "")))

rd = (W / "evidence" / "readme_huihui-ai_Huihui-Qwen3-4B-abliterated-v2.md").read_text(encoding="utf-8")
for q in QUOTES.get(31, []):
    print("huihui README quote:", repr(q[:60]), "->", q in rd)

print("total quotes in built JSON:", sum(len(v) for v in QUOTES.values()))