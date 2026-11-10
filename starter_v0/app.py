from __future__ import annotations

import json
import os
import re
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any

import streamlit as st

from chat import run_model_tool_loop
from env_loader import load_lab_env
from providers import make_provider
from tools import TOOL_FUNCTIONS, load_tool_declarations, to_openai_tools
from versioning import artifact_version_dict, build_artifact_version


ROOT = Path(__file__).parent
ARTIFACTS_DIR = ROOT / "artifacts"
TRANSCRIPTS_DIR = ROOT / "transcripts"
TRANSCRIPTS_DIR.mkdir(parents=True, exist_ok=True)
load_lab_env(ROOT)
LIVE_MODE_ALLOWED = os.getenv("RESEARCH_AGENT_ENABLE_LIVE_MODE", "").strip().casefold() in {"1", "true", "yes"}

PROMPT_PATH = ARTIFACTS_DIR / "system_prompt.md"
TOOLS_PATH = ARTIFACTS_DIR / "tools.yaml"
st.set_page_config(page_title="Research Agent", page_icon="🔎", layout="wide")

st.markdown(
    """
    <style>
    .block-container { max-width: 1120px; padding-top: 2.2rem; padding-bottom: 4rem; }
    [data-testid="stSidebar"] { border-right: 1px solid rgba(120,130,150,.18); }
    .hero { padding: 1.2rem 1.4rem; border: 1px solid rgba(120,130,150,.22);
            border-radius: 18px; background: linear-gradient(120deg, #f4f7ff, #fbfcff); }
    .hero h1 { margin: 0; font-size: 2rem; letter-spacing: -.03em; }
    .hero p { margin: .45rem 0 0; color: #596579; }
    .muted { color: #697586; font-size: .9rem; }
    div[data-testid="stChatMessage"] { border: 1px solid rgba(120,130,150,.14); border-radius: 14px; }
    </style>
    """,
    unsafe_allow_html=True,
)


def now_iso() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def init_session() -> None:
    st.session_state.setdefault("turns", [])
    st.session_state.setdefault("session_id", uuid.uuid4().hex[:10])
    st.session_state.setdefault("pending_input", "")


def transcript_path() -> Path:
    return TRANSCRIPTS_DIR / f"ui_{st.session_state['session_id']}.transcript.json"


def save_transcript(turns: list[dict[str, Any]], mode: str, provider: str, model: str | None) -> Path:
    version = build_artifact_version("ui", PROMPT_PATH, TOOLS_PATH)
    transcript = {
        "transcript_id": f"ui_{st.session_state['session_id']}",
        **artifact_version_dict(version),
        "mode": mode,
        "provider": provider,
        "model": model,
        "created_at": st.session_state.setdefault("created_at", now_iso()),
        "updated_at": now_iso(),
        "turns": turns,
    }
    path = transcript_path()
    path.write_text(json.dumps(transcript, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    return path


def result_text(tool: str, result: dict[str, Any]) -> str:
    if result.get("error"):
        return f"Tool `{tool}` trả về lỗi: {result.get('message', result['error'])}"
    if tool == "text_stats":
        return (
            f"Văn bản có **{result.get('word_count', 0)} từ**, "
            f"{result.get('sentence_count', 0)} câu và thời gian đọc khoảng "
            f"**{result.get('reading_time_min', 0)} phút**."
        )
    if tool == "data_calc":
        return f"Kết quả phép tính **{result.get('operation')}** là **{result.get('result')}**."
    if tool == "dedupe":
        return f"Đã loại **{result.get('removed', 0)} mục trùng**; còn {result.get('item_count', 0)} mục."
    return "Đã chạy công cụ cục bộ. Xem chi tiết kết quả bên dưới."


def run_offline_demo(query: str) -> tuple[str, list[dict[str, Any]]]:
    """Run deterministic local tools, with no model or network request."""
    lowered = query.casefold()
    if any(word in lowered for word in ("trùng", "dedupe", "duplicate")):
        tool, args = "dedupe", {
            "by": "url",
            "items": [
                {"title": "Báo cáo AI", "url": "https://example.org/report?utm_source=demo"},
                {"title": "Báo cáo AI (bản lặp)", "url": "https://www.example.org/report"},
                {"title": "Ghi chú nghiên cứu", "url": "https://example.org/notes"},
            ],
        }
    elif any(word in lowered for word in ("tính", "trung bình", "doanh thu", "tăng trưởng")) or re.search(
        r"\b(?:mean|sum|calculate|calculation|percentage|percent|growth|change)\b", lowered
    ):
        numbers = [float(n) for n in re.findall(r"(?<!\w)-?\d+(?:\.\d+)?", query)]
        if not numbers:
            numbers = [200.0, 300.0]
        op = "mean" if "trung bình" in lowered or "mean" in lowered else "change"
        tool, args = "data_calc", {"numbers": numbers, "operation": op}
    else:
        text = query.split(":", 1)[1].strip() if ":" in query else query
        if len(text.split()) < 3:
            text = "Trí tuệ nhân tạo giúp nhóm nghiên cứu phân tích dữ liệu và kiểm tra nguồn thông tin."
        tool, args = "text_stats", {"text": text}

    result = TOOL_FUNCTIONS[tool](**args)
    event = {"tool": tool, "args": args, "result": result}
    return result_text(tool, result), [{"round": 1, "assistant_text": None, "tool_calls": [{"name": tool, "args": args}], "tool_results": [event]}]


def run_live_turn(
    query: str,
    history: list[dict[str, str]],
    provider_name: str,
    model: str | None,
    max_tool_rounds: int,
) -> dict[str, Any]:
    provider = make_provider(provider_name)
    prompt = PROMPT_PATH.read_text(encoding="utf-8") if PROMPT_PATH.exists() else ""
    declarations = load_tool_declarations(TOOLS_PATH)
    messages = [{"role": "system", "content": prompt}, *history, {"role": "user", "content": query}]
    return run_model_tool_loop(
        provider=provider,
        messages=messages,
        tools=to_openai_tools(declarations),
        model=model,
        max_tool_rounds=max_tool_rounds,
    )


def tool_events(turn: dict[str, Any]) -> list[dict[str, Any]]:
    return turn.get("tool_events", [event for round_info in turn.get("rounds", []) for event in round_info.get("tool_results", [])])


init_session()
artifacts = build_artifact_version("ui", PROMPT_PATH, TOOLS_PATH)
declarations = load_tool_declarations(TOOLS_PATH)

with st.sidebar:
    st.markdown("### ⚙️ Cài đặt")
    offline = st.toggle(
        "Demo offline (không cần API key)",
        value=not LIVE_MODE_ALLOWED,
        disabled=not LIVE_MODE_ALLOWED,
        help="Dùng tool cục bộ. Live model chỉ bật khi chủ máy đặt RESEARCH_AGENT_ENABLE_LIVE_MODE=true.",
    )
    providers = ["openrouter", "openai", "gemini", "anthropic", "ollama"]
    default_provider = "openai" if os.getenv("OPENAI_API_KEY") else "openrouter"
    provider_name = st.selectbox("Nhà cung cấp model", providers, index=providers.index(default_provider), disabled=offline)
    model = st.text_input("Model tùy chọn", placeholder="Để trống dùng model mặc định", disabled=offline).strip() or None
    max_rounds = st.slider("Số vòng gọi tool tối đa", 1, 8, 4, disabled=offline)
    st.divider()
    st.caption(f"Phiên bản artifact: `{artifacts.artifact_version}`")
    st.caption(f"Tools đã khai báo: **{len(declarations)}**")
    with st.expander("External service key status", expanded=False):
        external_services = [
            ("Web search (lookup)", "TAVILY_API_KEY"),
            ("Read URL (fetch)", "FIRECRAWL_API_KEY"),
            ("Social search / timeline", "RAPIDAPI_KEY"),
        ]
        for label, env_name in external_services:
            if os.getenv(env_name):
                st.success(f"{label}: configured")
            else:
                st.warning(f"{label}: add `{env_name}` to `starter_v0/.env`")
        st.caption("Only key names are shown here. Restart Streamlit after editing .env.")
    with st.expander("Danh sách tool"):
        for item in declarations:
            st.markdown(f"- `{item['name']}`")
    if st.button("Xóa transcript và bắt đầu phiên mới", use_container_width=True):
        st.session_state["turns"] = []
        st.session_state["session_id"] = uuid.uuid4().hex[:10]
        st.session_state["created_at"] = now_iso()
        st.rerun()

st.markdown(
    '<section class="hero"><h1>🔎 Research Agent</h1>'
    '<p>Tra cứu, phân tích và tổng hợp thông tin với các công cụ có thể kiểm tra được.</p></section>',
    unsafe_allow_html=True,
)
if offline:
    st.info("Đang ở chế độ demo offline: yêu cầu mẫu chạy trực tiếp tool cục bộ, không dùng model và không truy cập mạng.")
else:
    st.caption(f"Đang dùng provider: **{provider_name}** · Kiểm tra `.env` để cấu hình API key trước khi gửi.")

st.markdown("#### Thử nhanh")
sample_cols = st.columns(3)
samples = [
    "Đếm từ trong đoạn này: AI hỗ trợ nhóm nghiên cứu phân tích dữ liệu nhanh hơn.",
    "Tính phần trăm tăng trưởng doanh thu từ 200 lên 300.",
    "Loại bỏ mục trùng URL khỏi danh sách kết quả nghiên cứu.",
]
for col, sample in zip(sample_cols, samples):
    if col.button(sample, use_container_width=True, disabled=not offline):
        st.session_state["pending_input"] = sample
        st.rerun()

for turn in st.session_state["turns"]:
    with st.chat_message("user"):
        st.markdown(turn["user"])
    with st.chat_message("assistant"):
        st.markdown(turn.get("assistant_text") or "Chưa có câu trả lời.")
        events = tool_events(turn)
        if events:
            with st.expander(f"Chi tiết {len(events)} lần gọi tool", expanded=False):
                for event in events:
                    st.markdown(f"**`{event['tool']}`**")
                    st.code(json.dumps(event.get("args", {}), ensure_ascii=False, indent=2), language="json")
                    st.json(event.get("result", {}))
        if turn.get("error"):
            st.error(turn["error"])

typed = st.chat_input("Nhập yêu cầu nghiên cứu…")
query = typed or st.session_state.pop("pending_input", "")
if query:
    history = [
        message
        for item in st.session_state["turns"]
        for message in ({"role": "user", "content": item["user"]}, {"role": "assistant", "content": item.get("assistant_text", "")})
    ]
    with st.chat_message("user"):
        st.markdown(query)
    with st.chat_message("assistant"):
        try:
            with st.spinner("Đang xử lý yêu cầu…"):
                if offline:
                    answer, rounds = run_offline_demo(query)
                    turn = {"status": "answered", "assistant_text": answer, "rounds": rounds}
                    # Keep the full tool call record consistent with live transcripts.
                    turn["tool_events"] = [event for round_info in rounds for event in round_info["tool_results"]]
                else:
                    turn = run_live_turn(query, history, provider_name, model, max_rounds)
            st.markdown(turn.get("assistant_text") or "Mô hình không trả về nội dung.")
            events = tool_events(turn)
            if events:
                with st.expander(f"Chi tiết {len(events)} lần gọi tool", expanded=True):
                    for event in events:
                        st.markdown(f"**`{event['tool']}`**")
                        st.code(json.dumps(event.get("args", {}), ensure_ascii=False, indent=2), language="json")
                        st.json(event.get("result", {}))
            turn_record = {"turn_index": len(st.session_state["turns"]) + 1, "timestamp": now_iso(), "user": query, **turn}
            st.session_state["turns"].append(turn_record)
            path = save_transcript(st.session_state["turns"], "offline_demo" if offline else "live", provider_name, model)
            st.caption(f"Transcript ghi nhận: `{path.relative_to(ROOT).as_posix()}`")
        except Exception as exc:
            message = f"{type(exc).__name__}: {exc}"
            st.error(message)
            error_turn = {"turn_index": len(st.session_state["turns"]) + 1, "timestamp": now_iso(), "user": query, "assistant_text": "Lượt này gặp lỗi khi chạy.", "status": "error", "error": message, "rounds": [], "tool_events": []}
            st.session_state["turns"].append(error_turn)
            path = save_transcript(st.session_state["turns"], "offline_demo" if offline else "live", provider_name, model)
            st.caption(f"Lượt lỗi cũng đã ghi transcript: `{path.relative_to(ROOT).as_posix()}`")

if st.session_state["turns"]:
    st.markdown(f'<p class="muted">Số lượt đã ghi: {len(st.session_state["turns"])} · Transcript: <code>{transcript_path().relative_to(ROOT).as_posix()}</code></p>', unsafe_allow_html=True)
