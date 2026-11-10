"""Three scripted live model turns for reproducible submission evidence (API billed)."""
import json
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from chat import run_model_tool_loop, now_iso, write_transcript
from env_loader import load_lab_env
from providers import make_provider
from tools import load_tool_declarations, to_openai_tools
from versioning import build_artifact_version, artifact_version_dict

if __name__ == '__main__':
    load_lab_env(ROOT)
    prompt = ROOT / 'artifacts/system_prompt.md'
    tools = ROOT / 'artifacts/tools.yaml'
    provider = make_provider('openai')
    identifier = f'v3.4_submission_live_{datetime.now():%Y%m%dT%H%M%S}'
    output = ROOT / 'transcripts' / f'{identifier}.transcript.json'
    transcript = {'transcript_id': identifier,
                  **artifact_version_dict(build_artifact_version('v3.4', prompt, tools)),
                  'provider': 'openai', 'model': provider.default_model,
                  'interface': 'scripted_live_verification', 'created_at': now_iso(), 'turns': []}
    queries = [
        'Chỉ bỏ trùng URL, giữ mục đầu tiên, chưa định dạng: [{"title":"A","url":"https://www.example.com/post/"},{"title":"A copy","url":"https://example.com/post?utm_source=demo#intro"},{"title":"B","url":"https://example.com/other"}]',
        'Đọc bài báo này và tóm tắt giúp mình. Mình chưa gửi URL hoặc nội dung.',
        'Thôi không đọc bài nữa. Chỉ bỏ trùng theo tiêu đề trong danh sách mới này: [{"title":"Tin AI hôm nay"},{"title":"tin ai hom nay"},{"title":"Robot mới"}]. Chưa cần định dạng.',
    ]
    history = []
    for index, query in enumerate(queries, 1):
        record = {'turn_index': index, 'user': query, 'started_at': now_iso()}
        result = run_model_tool_loop(provider=provider,
            messages=[{'role': 'system', 'content': prompt.read_text(encoding='utf-8')},
                      *history, {'role': 'user', 'content': query}],
            tools=to_openai_tools(load_tool_declarations(tools)), model=None, max_tool_rounds=4)
        record.update(result)
        record['ended_at'] = now_iso()
        transcript['turns'].append(record)
        write_transcript(output, transcript)
        history.extend([{'role': 'user', 'content': query},
                        {'role': 'assistant', 'content': result['assistant_text']}])
        print(f'Turn {index}: {result["status"]}', flush=True)
    print(f'Saved: {output}')
