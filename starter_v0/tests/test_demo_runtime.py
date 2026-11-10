from pathlib import Path
import json
import shutil

import pytest

from demo_runtime import DemoSession
from providers.base import ModelResponse, ToolCall

ROOT = Path(__file__).resolve().parents[1]


class FakeProvider:
    def __init__(self, *responses):
        self.responses = iter(responses)
        self.requests = []

    def complete(self, messages, tools, **kwargs):
        self.requests.append(messages.copy())
        response = next(self.responses)
        if isinstance(response, Exception):
            raise response
        return response


@pytest.fixture
def demo_root(tmp_path):
    (tmp_path / "artifacts").mkdir()
    for name in ["system_prompt.md", "tools.yaml"]:
        shutil.copyfile(ROOT / "artifacts" / name, tmp_path / "artifacts" / name)
    return tmp_path


def test_clarification_pauses_and_next_turn_retains_context(demo_root):
    provider = FakeProvider(ModelResponse(tool_calls=[ToolCall("clarify", {
        "question": "Tài khoản nào?", "response_type": "text"})]),
        ModelResponse(text="Đã nhận tài khoản."))
    demo = DemoSession(demo_root, provider=provider)
    assert demo.ask("Lấy 3 tweet")['status'] == 'waiting_for_user'
    assert demo.ask("NASA")['status'] == 'answered'
    assert any(m['content'] == 'Lấy 3 tweet' for m in provider.requests[1])
    saved = json.loads(demo.path.read_text(encoding='utf-8'))
    assert len(saved['turns']) == 2
    assert saved['turns'][0]['tool_events'][0]['result']['awaiting_user'] is True
    assert saved['runtime_policy'] in saved['turns'][0]['rounds'][0]['request_messages'][0]['content']


def test_provider_failure_keeps_prior_tool_evidence(demo_root):
    provider = FakeProvider(ModelResponse(tool_calls=[ToolCall('dedupe', {
        'items': [{'url': 'https://a.com'}, {'url': 'https://a.com'}], 'by': 'url'})]),
        RuntimeError('provider unavailable'))
    demo = DemoSession(demo_root, provider=provider)
    result = demo.ask('Loại trùng URL')
    assert result['status'] == 'provider_error'
    saved = json.loads(demo.path.read_text(encoding='utf-8'))['turns'][0]
    assert saved['tool_events'][0]['result']['removed'] == 1
    assert len(saved['rounds']) == 2
    assert saved['rounds'][1]['request_messages']


def test_secrets_redacted_from_download_and_saved_errors(demo_root, monkeypatch):
    secret = 'test-sensitive-key-0123456789'
    monkeypatch.setenv('OPENAI_API_KEY', secret)
    demo = DemoSession(demo_root, provider=FakeProvider(RuntimeError('failed '+secret)))
    result = demo.ask('Question '+secret)
    assert secret not in json.dumps(result)
    assert secret not in demo.path.read_text(encoding='utf-8')
    assert '[REDACTED]' in result['error']


def test_delivery_is_blocked_even_if_model_sets_confirmed(demo_root, monkeypatch):
    import demo_runtime
    def forbidden(call):
        raise AssertionError('Delivery must not execute')
    monkeypatch.setattr(demo_runtime, 'execute_tool_call', forbidden)
    demo = DemoSession(demo_root, provider=FakeProvider(
        ModelResponse(tool_calls=[ToolCall('send', {'text': 'demo', 'confirmed': True})]),
        ModelResponse(text='Gửi bị tắt trong demo.')))
    result = demo.ask('Gửi đi')
    assert result['tool_events'][0]['result']['error'] == 'delivery_disabled'


def test_clarification_skips_simultaneous_other_calls(demo_root):
    demo = DemoSession(demo_root, provider=FakeProvider(ModelResponse(tool_calls=[
        ToolCall('send', {'text': 'demo', 'confirmed': True}),
        ToolCall('clarify', {'question': 'Xác nhận?', 'response_type': 'yes_no'})])))
    result = demo.ask('Đăng bản tin')
    assert result['status'] == 'waiting_for_user'
    assert [e['tool'] for e in result['tool_events']] == ['clarify']
    assert result['rounds'][0]['skipped_calls'][0]['name'] == 'send'
