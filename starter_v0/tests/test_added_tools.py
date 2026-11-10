"""Offline contracts for the four tools integrated with the team's UI."""
import importlib
import json

from conftest import FakeResponse
from tools import TOOL_FUNCTIONS as T


def test_data_calc_mean():
    assert T['data_calc']([2, 4, 6], 'mean')['result'] == 4


def test_data_calc_empty():
    assert T['data_calc']([], 'sum')['result'] is None


def test_data_calc_invalid_type_returns_error():
    assert T['data_calc'](numbers=123)['error'] == 'TypeError'


def test_text_stats_counts_and_frequency():
    r = T['text_stats']('Robot robot. Science!')
    assert r['word_count'] == 3 and r['sentence_count'] == 2
    assert r['top_words'][0] == {'word': 'robot', 'count': 2}


def test_text_stats_empty():
    assert T['text_stats']('')['word_count'] == 0


def test_text_stats_bad_type_returns_error():
    assert T['text_stats'](123)['error'] == 'AttributeError'


def test_export_writes_json_in_target_directory(monkeypatch, tmp_path):
    mod = importlib.import_module('tools.export_report.tool')
    monkeypatch.setattr(mod, 'REPORTS_DIR', tmp_path)
    r = T['export_report']('../demo', 'Research body', 'json')
    assert r['status'] == 'saved'
    assert json.loads((tmp_path / 'demo.json').read_text(encoding='utf-8')) == {'report': 'Research body'}


def test_export_missing_content_does_not_write(monkeypatch, tmp_path):
    mod = importlib.import_module('tools.export_report.tool')
    monkeypatch.setattr(mod, 'REPORTS_DIR', tmp_path)
    assert T['export_report']('empty', '')['status'] == 'error'
    assert list(tmp_path.iterdir()) == []


def test_export_write_failure_returns_error(monkeypatch, tmp_path):
    mod = importlib.import_module('tools.export_report.tool')
    blocked = tmp_path / 'file'
    blocked.write_text('not directory')
    monkeypatch.setattr(mod, 'REPORTS_DIR', blocked)
    assert T['export_report']('demo', 'body')['error'] == 'FileExistsError'


def test_wiki_request_and_mapping(fake_http):
    calls = fake_http(FakeResponse({'query': {'search': [{'title': 'AI science', 'snippet': '<b>Text</b>', 'pageid': 1}]}}))
    r = T['wiki_search']('AI', limit=2)
    assert calls[0]['params']['srsearch'] == 'AI' and calls[0]['params']['srlimit'] == 2
    assert r['items'][0]['summary'] == 'Text'
    assert r['items'][0]['url'] == 'https://en.wikipedia.org/wiki/AI_science'


def test_wiki_empty_does_not_call_network(fake_http):
    calls = fake_http(FakeResponse())
    assert T['wiki_search']('')['items'] == [] and calls == []


def test_wiki_http_failure_returns_error(fake_http):
    fake_http(FakeResponse(status_code=429))
    assert T['wiki_search']('AI')['error'] == 'HTTPError'
