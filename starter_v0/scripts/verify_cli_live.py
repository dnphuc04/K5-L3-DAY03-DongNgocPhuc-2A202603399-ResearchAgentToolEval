"""Drive the real chat.py CLI with scripted input and a real model; never mock replies."""
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]

if __name__ == '__main__':
    inputs = [
        'Chỉ bỏ trùng URL, giữ mục đầu tiên: [{"title":"A","url":"https://www.example.com/post/"},{"title":"Copy","url":"https://example.com/post?utm_source=demo#intro"},{"title":"B","url":"https://example.com/other"}]. Chưa định dạng.',
        'Đọc bài báo này giúp mình, mình chưa gửi link hay nội dung.',
        'Hủy yêu cầu đọc bài. Chỉ bỏ trùng tiêu đề trong danh sách mới: [{"title":"Tin AI hôm nay"},{"title":"tin ai hom nay"},{"title":"Robot mới"}]. Chưa định dạng.',
        '/exit',
    ]
    before = set((ROOT / 'transcripts').glob('v3.5_openai_*.json'))
    env = dict(os.environ, PYTHONIOENCODING='utf-8')
    result = subprocess.run([sys.executable, str(ROOT / 'chat.py'), '--provider', 'openai', '--version', 'v3.5'],
                            input='\n'.join(inputs) + '\n', capture_output=True, text=True, encoding='utf-8',
                            cwd=ROOT, env=env, timeout=240)
    (ROOT / 'analysis/cli_v3_5_console.txt').write_text(result.stdout + result.stderr, encoding='utf-8')
    result.check_returncode()
    created = set((ROOT / 'transcripts').glob('v3.5_openai_*.json')) - before
    assert len(created) == 1
    path = created.pop()
    d = json.loads(path.read_text(encoding='utf-8'))
    assert len(d['turns']) == 3
    assert [x['status'] for x in d['turns']] == ['answered', 'waiting_for_user', 'answered']
    assert d['turns'][0]['tool_events'][0]['result']['removed'] == 1
    assert d['turns'][2]['tool_events'][0]['result']['removed'] == 1
    checks = {'source': 'real chat.py subprocess with scripted input and live OpenAI replies',
              'transcript': 'transcripts/' + path.name, 'functional_turns': 3,
              'url_dedupe_correct': True, 'missing_url_waits': True, 'title_dedupe_correct': True}
    (ROOT / 'analysis/cli_v3_5_checks.json').write_text(json.dumps(checks, indent=2), encoding='utf-8')
    print('PASS: chat.py completed 3 real model turns; transcript:', path.name)
