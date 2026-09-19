import json
from pathlib import Path

W = Path(__file__).resolve().parent
s = json.loads((W / ".sdk_openhands_agent_struct_out.json").read_text(encoding="utf-8"))
r = json.loads((W / "research_out.json").read_text(encoding="utf-8"))
assert s["answer"] == r["answer"] and s["sources"] == r["sources"] and s["follow_up_questions"] == r["follow_up_questions"]
for k in ["title", "layman_summary", "summary", "out_expected_files", "upload_ignore_regexes", "answer", "sources", "follow_up_questions"]:
    assert k in s, k
assert s["out_expected_files"]["output"] == "research_out.json"
assert 12 <= len(s["title"]) <= 90 and 80 <= len(s["layman_summary"]) <= 250 and len(s["summary"]) >= 500
assert all(1 <= x["index"] <= 44 for x in s["sources"]) and len({x["index"] for x in s["sources"]}) == 44
assert all(x.get("url", "").startswith("http") and x.get("title") and x.get("summary") for x in s["sources"])
assert len(s["follow_up_questions"]) == 3
print("FINAL VALIDATION PASSED — title:", s["title"], "| sources:", len(s["sources"]), "| answer chars:", len(s["answer"]))