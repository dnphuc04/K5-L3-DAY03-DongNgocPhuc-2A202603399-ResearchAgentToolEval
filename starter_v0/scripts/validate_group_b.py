"""Offline evidence for B's dataset and dedupe case; does not call model APIs."""
from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools import TOOL_FUNCTIONS, load_tool_declarations
from run_eval import load_cases, validate_expected_tools, evaluate_phase_b

cases = load_cases(ROOT / 'data/eval_group.json', 'B')
assert len(cases) == 10
assert sum('turns' in c for c in cases) == 5
assert len({c['id'] for c in cases}) == 10
assert all(c.get('metadata', {}).get('what_it_tests') for c in cases)
print('PASS: 10 unique cases, 5 single turn + 5 multi turn, valid failure types and metadata.')
declared = load_tool_declarations(ROOT / 'artifacts/tools.yaml')
if 'dedupe' not in {t['name'] for t in declared}:
    declared += load_tool_declarations(ROOT / 'artifacts/dedupe_declaration.proposed.yaml')
    print('PENDING: tools.yaml lacks dedupe; validating against proposed declaration as well.')
validate_expected_tools(cases, declared, ROOT / 'data/eval_group.json')
print('PASS: expected tools match combined declarations and registry.')
c = next(c for c in cases if c['id'].startswith('G05'))
query = c['query']
items = json.loads(query[query.index('['):query.rindex(']') + 1])
call = {'name': 'dedupe', 'args': {'items': items, 'by': 'url'}}
assert evaluate_phase_b(c, [call], None)['passed']
out = TOOL_FUNCTIONS['dedupe'](**call['args'])
assert out['item_count'] == 2 and out['removed'] == 1
assert out['items'] == [items[0], items[2]]
print('PASS: G05 expected call is gradeable; local output keeps first/third items, count=2, removed=1.')
print('NOT RUN: live model group eval. Offline checks do not measure model accuracy.')
