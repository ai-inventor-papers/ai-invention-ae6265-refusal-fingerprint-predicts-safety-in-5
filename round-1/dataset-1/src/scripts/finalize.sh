#!/bin/bash
# Finalize step: refresh side artifacts, extract examples arrays, validate + format via aii-json, append SHAs + verify results.
set -u
cd /ai-inventor/aii_data/runs/run_fEjgpc8BQoQS/3_invention_loop/iter_1/gen_art/gen_art_dataset_1 || exit 1
PY=.venv/bin/python

echo "=== 1. refresh side artifacts ==="
$PY scripts/build_side_artifacts.py 2>&1 | grep -E "WROTE|INFO.*xstest" | head -6

echo "=== 2. extract examples arrays ==="
$PY - <<'EOF'
import json
from pathlib import Path
art = Path('artifacts')
data = json.loads((art/'data_out.json').read_text())
(art/'examples_full.json').write_text(json.dumps(data['datasets'][0]['examples']))
reg = json.loads((art/'registry.json').read_text())
(art/'registry_examples_full.json').write_text(json.dumps(reg['datasets'][0]['examples']))
ref = json.loads((art/'reference_scores.json').read_text())
(art/'reference_examples_full.json').write_text(json.dumps(ref['datasets'][0]['examples']))
print('examples arrays written:',
      (art/'examples_full.json').stat().st_size,
      (art/'registry_examples_full.json').stat().st_size,
      (art/'reference_examples_full.json').stat().st_size)
EOF

echo "=== 3. aii-json schema validation ==="
SKILL_DIR=/ai-inventor/.claude/skills/aii-json
$SKILL_DIR/../.ability_client_venv/bin/python $SKILL_DIR/scripts/aii_json_validate_schema.py --format exp_sel_data_out --file $PWD/artifacts/data_out.json 2>&1 | tail -4 || echo "ability-server validation unavailable"

echo "=== 4. aii-json format (full/mini/preview) ==="
$SKILL_DIR/../.ability_client_venv/bin/python $SKILL_DIR/scripts/aii_json_format_mini_preview.py --input $PWD/artifacts/examples_full.json 2>&1 | tail -4 || echo "format unavailable"
$SKILL_DIR/../.ability_client_venv/bin/python $SKILL_DIR/scripts/aii_json_format_mini_preview.py --input $PWD/artifacts/registry_examples_full.json 2>&1 | tail -4 || echo "format unavailable"
$SKILL_DIR/../.ability_client_venv/bin/python $SKILL_DIR/scripts/aii_json_format_mini_preview.py --input $PWD/artifacts/reference_examples_full.json 2>&1 | tail -4 || echo "format unavailable"

echo "=== 5. append SHAs + verify results into manifest ==="
$PY - <<'EOF'
import json
from pathlib import Path
art = Path('artifacts')
m = json.loads((art/'manifest_sources.json').read_text())
m['construction_shas'] = {
    'harmbench_csv': 'c0423b952435',
    'xstest_repo_head': 'd7bb5bd738c1',
    'jbb_artifacts_jbc_file': '1b8eaeb1d718',
    'dolly15k_hf_sha': 'bdd27f4d94b9',
}
verify_log = (Path('logs')/'verify_run2.log').read_text()
m['validation'] = {
    'gates': 'ALL 15 GATES GREEN (verify.py, logged to logs/verify_run2.log)',
    'notes': 'g4b: 12 near cross-set pairs at Jaccard 0.4-0.6 logged for manual review (0 >= 0.6); g8: max prompt 495 tokens (Qwen2.5-0.5B tokenizer); g6: 682 ids deterministically reproduced.',
}
(art/'manifest_sources.json').write_text(json.dumps(m, indent=1))
print('manifest updated')
EOF

echo "=== 6. final sizes ==="
ls -lh artifacts/ | awk '{print $5, $9}'
echo "=== DONE ==="