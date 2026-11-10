"""Run with: python -m streamlit run app.py"""
from datetime import datetime
import json
import os
from pathlib import Path
from uuid import uuid4

import streamlit as st

from chat import now_iso, run_model_tool_loop, trim_history, write_transcript
from env_loader import load_lab_env
from providers import make_provider
from tools import load_tool_declarations, to_openai_tools
from versioning import artifact_version_dict, build_artifact_version

ROOT = Path(__file__).resolve().parent
load_lab_env(ROOT)
st.set_page_config(page_title="Research Agent", page_icon="🔎", layout="wide")
st.title("🔎 Research Agent")
st.caption("Tìm nguồn, đọc tài liệu và làm sạch dữ liệu — có log tool để kiểm tra.")

with st.sidebar:
    st.header("Phiên làm việc")
    provider_name = st.selectbox("Provider", ["openai", "openrouter", "anthropic", "gemini", "ollama"])
    version = st.text_input("Nhãn phiên bản", "v3.4")
    model = st.text_input("Model (để trống dùng mặc định)", "")
    rounds = st.slider("Số vòng tool tối đa", 1, 8, 4)
    st.caption("Dùng prompt/tools hiện có trong artifacts/. Nhãn phiên bản không tự đổi nội dung file.")
    st.subheader("API lấy dữ liệu")
    for name in ["TAVILY_API_KEY", "FIRECRAWL_API_KEY", "RAPIDAPI_KEY"]:
        st.caption(f"{'✅ Có cấu hình' if os.getenv(name) else '⚠️ Chưa cấu hình'}: {name}")
    st.caption("Có cấu hình chưa đồng nghĩa key hợp lệ. dedupe/format/policy không cần các key này.")
    if st.button("Bắt đầu hội thoại mới"):
        st.session_state.pop("session", None)
        st.rerun()

prompt_path = ROOT / "artifacts/system_prompt.md"
tools_path = ROOT / "artifacts/tools.yaml"
artifact = build_artifact_version(version.strip() or "demo", prompt_path, tools_path)
fingerprint = (provider_name, model, artifact.artifact_version)
if "session" not in st.session_state or st.session_state.session["fingerprint"] != fingerprint:
    identifier = f"ui_{datetime.now():%Y%m%dT%H%M%S}_{uuid4().hex[:8]}"
    st.session_state.session = {
        "fingerprint": fingerprint,
        "path": str(ROOT / "transcripts" / f"{identifier}.transcript.json"),
        "transcript": {
            "transcript_id": identifier, **artifact_version_dict(artifact),
            "provider": provider_name, "model": model or getattr(make_provider(provider_name), "default_model", None),
            "created_at": now_iso(), "system_prompt": str(prompt_path), "tools": str(tools_path),
            "interface": "streamlit", "turns": [],
        },
    }
session = st.session_state.session
transcript = session["transcript"]
st.caption(f"Artifact: {artifact.artifact_version}")


def render_turn(turn):
    with st.chat_message("user"):
        st.write(turn["user"])
    with st.chat_message("assistant"):
        if turn.get("status") == "provider_error":
            st.error(turn["error"])
        else:
            st.markdown(turn.get("assistant_text") or "Không có nội dung trả lời.")
        if turn.get("status") == "waiting_for_user":
            st.info("Agent đang chờ bạn bổ sung thông tin.")
        if turn.get("status") == "max_tool_rounds":
            st.warning("Đã đạt giới hạn vòng tool. Xem log để kiểm tra.")
        for event in turn.get("tool_events", []):
            with st.expander(f"Tool: {event['tool']}"):
                st.json(event)
            if isinstance(event.get("result"), dict) and event["result"].get("error"):
                st.warning(f"Tool {event['tool']} báo lỗi; chưa xác nhận có dữ liệu thật.")


if not transcript["turns"]:
    st.info('Thử: “Tóm tắt bài này” để kiểm tra hỏi lại; hoặc yêu cầu bỏ trùng danh sách URL bằng dedupe.')
for turn in transcript["turns"]:
    render_turn(turn)

if user_text := st.chat_input("Nhập yêu cầu nghiên cứu hoặc danh sách cần bỏ trùng…"):
    history = []
    for previous in transcript["turns"]:
        if previous.get("status") != "provider_error":
            history.extend([{"role": "user", "content": previous["user"]},
                            {"role": "assistant", "content": previous.get("assistant_text", "")}])
    record = {"turn_index": len(transcript["turns"]) + 1, "started_at": now_iso(), "user": user_text}
    try:
        with st.spinner("Agent đang xử lý…"):
            result = run_model_tool_loop(
                provider=make_provider(provider_name),
                messages=[{"role": "system", "content": prompt_path.read_text(encoding="utf-8")},
                          *trim_history(history, 5), {"role": "user", "content": user_text}],
                tools=to_openai_tools(load_tool_declarations(tools_path)),
                model=model.strip() or None, max_tool_rounds=rounds,
            )
        record.update(result)
    except Exception as exc:
        # Avoid exposing request URLs/tokens in provider exceptions on a shared UI.
        record.update(status="provider_error", error=f"{type(exc).__name__}: Không kết nối được provider. Kiểm tra key, mạng và model.")
    record["ended_at"] = now_iso()
    transcript["turns"].append(record)
    write_transcript(Path(session["path"]), transcript)
    st.rerun()

if transcript["turns"]:
    st.download_button("Tải transcript JSON", json.dumps(transcript, ensure_ascii=False, indent=2, default=str),
                       file_name=Path(session["path"]).name, mime="application/json")
    st.caption(f"Đã lưu: transcripts/{Path(session['path']).name}")
