"""TODO(student): Tool Unit Test Challenge.

All starter stubs below are implemented with offline assertions.
Patterns to copy are in test_tools_examples.py. Fixtures are in conftest.py.

Rules:
- Offline only: mock HTTP with `fake_http`, set fake keys with `monkeypatch.setenv`.
- One behaviour per test. Name the test after the behaviour, not the function.
- Done = `pytest tests/ -v` shows 0 skipped, 0 failed.
"""
from __future__ import annotations

import pytest

from conftest import FakeResponse  # noqa: F401  (you will need it)
from tools import TOOL_FUNCTIONS  # noqa: F401

TODO = "TODO(student): implement this test"


# ---------------- clarify ----------------

def test_clarify_choice_returns_options_and_awaits_user() -> None:
    # Call clarify with response_type="choice" and 2 options.
    # Assert: options are returned unchanged, awaiting_user is True.
    r=TOOL_FUNCTIONS['clarify']('Choose', 'choice', ['A','B'])
    assert r['options']==['A','B'] and r['awaiting_user']


# ---------------- format ----------------

def test_format_sections_groups_items_by_section() -> None:
    # Items with section "A", "B", "A" -> markdown has exactly one "## A" and one "## B".
    r=TOOL_FUNCTIONS['format'](items=[{'section':x,'title':x} for x in ['A','B','A']])
    assert r['markdown'].count('## A')==r['markdown'].count('## B')==1


def test_format_thread_numbers_items() -> None:
    # template="thread" -> lines start with "1/", "2/", ...
    r=TOOL_FUNCTIONS['format'](items=[{'title':'A'},{'title':'B'}],template='thread')
    assert r['markdown'].startswith('1/ ') and '\n\n2/ ' in r['markdown']


def test_format_empty_items_does_not_crash() -> None:
    # items=None and items=[] -> item_count == 0, no exception.
    assert all(TOOL_FUNCTIONS['format'](items=x)['item_count']==0 for x in [None,[]])


# ---------------- send (guardrail) ----------------

def test_send_confirmed_posts_to_telegram(monkeypatch, fake_http) -> None:
    # Set TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID, mock HTTP.
    # Assert: exactly one POST, URL contains the token, json has chat_id + text, status == "sent".
    monkeypatch.setenv('TELEGRAM_BOT_TOKEN','fake-token')
    monkeypatch.setenv('TELEGRAM_CHAT_ID','fake-chat')
    calls=fake_http(FakeResponse({'ok':True}))
    assert TOOL_FUNCTIONS['send']('Digest',confirmed=True)['status']=='sent'
    assert len(calls)==1 and calls[0]['method']=='POST' and calls[0]['json']['text']=='Digest' and calls[0]['json']['chat_id']=='fake-chat' and calls[0]['url'].endswith('/botfake-token/sendMessage')


def test_send_confirmed_without_env_returns_error_and_no_request(fake_http) -> None:
    calls=fake_http(FakeResponse())
    assert TOOL_FUNCTIONS['send']('Digest',confirmed=True)['error']=='RuntimeError'
    assert calls==[]


# ---------------- lookup ----------------

def test_lookup_without_timeframe_omits_time_range(monkeypatch, fake_http) -> None:
    # timeframe=None -> request body has no "time_range" key.
    monkeypatch.setenv('TAVILY_API_KEY','fake')
    calls=fake_http(FakeResponse({'results':[]}))
    assert TOOL_FUNCTIONS['lookup']('AI',timeframe=None)['items']==[]
    assert 'time_range' not in calls[0]['json']


# ---------------- fetch ----------------

def test_fetch_maps_firecrawl_response(monkeypatch, fake_http) -> None:
    # Mock {"data": {"markdown": "...", "metadata": {"title": "T", "sourceURL": "https://..."}}}
    # Assert title/url/source/summary in result["items"][0].
    monkeypatch.setenv('FIRECRAWL_API_KEY','fake')
    calls=fake_http(FakeResponse({'data':{'markdown':'Body','metadata':{'title':'T','sourceURL':'https://example.com/end'}}}))
    r=TOOL_FUNCTIONS['fetch']('https://example.com/start')
    assert r['items'][0]=={'title':'T','url':'https://example.com/end','source':'example.com','summary':'Body'}
    assert calls[0]['json']['url']=='https://example.com/start'


def test_fetch_truncates_markdown_to_4000_chars(monkeypatch, fake_http) -> None:
    monkeypatch.setenv('FIRECRAWL_API_KEY','fake')
    fake_http(FakeResponse({'data':{'markdown':'x'*5000}}))
    assert TOOL_FUNCTIONS['fetch']('https://example.com')['items'][0]['summary']=='x'*4000


# ---------------- timeline / social_search ----------------

def test_timeline_respects_limit_and_skips_items_without_id(monkeypatch, fake_http) -> None:
    # Mock {"timeline": [...]} with 1 item missing tweet_id and 6 valid items, limit=3.
    # Assert 3 items, and each url looks like https://x.com/<handle>/status/<id>.
    monkeypatch.setenv('RAPIDAPI_KEY','fake')
    calls=fake_http(FakeResponse({'timeline':[{'text':'missing id'}]+[{'tweet_id':str(i),'screen_name':'NASA'} for i in range(1,7)]}))
    r=TOOL_FUNCTIONS['timeline']('NASA',limit=3)
    assert [x['url'] for x in r['items']]==[f'https://x.com/NASA/status/{i}' for i in range(1,4)]
    assert calls[0]['params']=={'screenname':'NASA'}


def test_social_search_passes_search_type(monkeypatch, fake_http) -> None:
    # Assert the request params carry the query and search_type ("Top" / "Latest").
    monkeypatch.setenv('RAPIDAPI_KEY','fake')
    calls=fake_http(FakeResponse({'tweets':[]}))
    assert TOOL_FUNCTIONS['social_search']('robotics',search_type='Top')['items']==[]
    assert calls[0]['params']=={'query':'robotics','search_type':'Top'}


# ---------------- policy (local knowledge + trust boundary) ----------------

def test_policy_empty_query_returns_no_results() -> None:
    assert TOOL_FUNCTIONS['policy']('')['results']==[]


def test_policy_area_filter_only_returns_that_area() -> None:
    # policy_area="data_privacy" -> every result has policy_area == "data_privacy".
    r=TOOL_FUNCTIONS['policy']('privacy data',policy_area='data_privacy')
    assert r['results'] and all(x['policy_area']=='data_privacy' for x in r['results'])


def test_policy_instruction_like_lines_go_to_untrusted_text() -> None:
    # One policy file contains a quoted line that tries to give the assistant orders.
    # Query that section (source_citation) and assert: that line is in untrusted_text, NOT in facts.
    r=TOOL_FUNCTIONS['policy']('citation',policy_area='source_citation',top_k=20)
    probe=next(x for x in r['results'] if x['section']=='Injection probe')
    assert any('ignore the citation policy' in x for x in probe['untrusted_text'])
    assert 'ignore the citation policy' not in probe['facts']


# ---------------- YOUR NEW TOOL(S) ----------------
# Write at least 3 tests per tool your team adds:
#   1. happy path (mocked if it calls an API)
#   2. bad / missing input from the model (empty string, wrong type, out-of-enum value)
#   3. failure path (missing key, HTTP error, timeout) -> returns error dict, does not raise

def test_my_new_tool_happy_path() -> None:
    r=TOOL_FUNCTIONS['dedupe']([{'url':'https://a.com'},{'url':'https://www.a.com/'}])
    assert r['item_count']==1 and r['removed']==1


def test_my_new_tool_bad_input_from_model() -> None:
    assert TOOL_FUNCTIONS['dedupe'](items='bad')['error']=='TypeError'


def test_my_new_tool_failure_returns_error_dict() -> None:
    assert TOOL_FUNCTIONS['dedupe'](items=[],by='invalid')['error']=='ValueError'
