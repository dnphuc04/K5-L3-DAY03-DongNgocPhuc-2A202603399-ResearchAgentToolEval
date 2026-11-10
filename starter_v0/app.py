"""Run: .venv/Scripts/python -m streamlit run app.py"""
from pathlib import Path
import json
import os

import streamlit as st

from demo_runtime import DemoSession, redact
from env_loader import load_lab_env
from providers import make_provider

ROOT = Path(__file__).resolve().parent
load_lab_env(ROOT)
st.set_page_config(page_title="Research Desk · AI20k", page_icon="◈", layout="wide")
st.markdown("""<style>
.stApp {background: #0b1017; color: #edf2f7;}
.block-container {max-width: 1120px; padding-top: 2.4rem;}
h1 {letter-spacing: -0.055em; font-weight: 750 !important;}
[data-testid="stSidebar"] {background: #111923; border-right: 1px solid #263242;}
[data-testid="stChatMessage"] {background: #141e2a; border: 1px solid #253347; border-radius: 16px;}
.eyebrow {color: #80d4bd; font-size: .78rem; letter-spacing: .2em; font-weight: 700;}
.intro {color: #a8b7ca; font-size: 1.05rem; max-width: 720px;}
.stButton > button {border-radius: 10px; border-color: #34465d;}
</style>""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### ◈ Research Desk")
    st.caption("AI20k · Day 03 / Research Agent")
    st.divider()
    st.markdown("**Môi trường demo**")
    st.caption("OpenAI · gpt-4o-mini · v3.4")
    keys = {"OpenAI": "OPENAI_API_KEY", "Web / Tavily": "TAVILY_API_KEY",
            "Đọc URL / Firecrawl": "FIRECRAWL_API_KEY", "Twitter / RapidAPI": "RAPIDAPI_KEY"}
    for label, key in keys.items():
        st.caption(f"{'●' if os.getenv(key) else '○'} {label} · {'sẵn sàng' if os.getenv(key) else 'chưa có key'}")
    st.caption("Key được đọc trên server từ .env.")
    st.divider()
    st.markdown("**Công cụ**")
    st.caption("Web · Twitter · Đọc URL · Paper arXiv · Policy · Loại trùng · Định dạng")
    st.caption("Telegram: tắt gửi trong demo.")
    if st.button("＋ Cuộc trò chuyện mới", use_container_width=True):
        st.session_state.pop("demo", None)
        st.rerun()

st.markdown('<div class="eyebrow">RESEARCH, WITH EVIDENCE</div>', unsafe_allow_html=True)
st.title("Từ câu hỏi đến nguồn tin.")
st.markdown('<p class="intro">Tìm trên web và Twitter, đọc tài liệu, lọc trùng và tổng hợp. '
            'Mỗi bước đều có nhật ký để kiểm chứng.</p>', unsafe_allow_html=True)

if "demo" not in st.session_state:
    st.session_state.demo = DemoSession(ROOT, provider=make_provider("openai"))
demo = st.session_state.demo
turns = demo.transcript["turns"]
columns = st.columns(3)
columns[0].metric("Lượt trò chuyện", len(turns))
columns[1].metric("Lần thực thi tool", sum(len(t["tool_events"]) for t in turns))
columns[2].metric("Nhật ký", "Tự động lưu")

examples = ["Tìm 3 tin tức AI hôm nay trên web.", "Tóm tắt 3 tweet mới nhất giúp mình.",
            'Loại URL trùng: [{"title":"A","url":"https://example.com/a"}, '
            '{"title":"Bản sao","url":"https://example.com/a"}].']
prompt = None
if not turns:
    st.caption("BẮT ĐẦU VỚI MỘT CÂU HỎI")
    for index, col in enumerate(st.columns(3)):
        label = ["Tìm tin AI hôm nay", "Thử tình huống thiếu tài khoản", "Loại kết quả trùng"][index]
        if col.button(label, key=f"example_{index}", use_container_width=True):
            prompt = examples[index]

for turn in turns:
    with st.chat_message("user"):
        st.markdown(redact(turn["user"]))
    with st.chat_message("assistant"):
        st.markdown(redact(turn["assistant_text"]))
        st.caption(f"{turn['status']} · {turn.get('duration_seconds', 0):.1f}s · {len(turn['tool_events'])} tool calls")
        with st.expander("Xem tool calls, arguments và kết quả"):
            st.json(redact({"rounds": turn["rounds"], "error": turn.get("error")}))

typed = st.chat_input("Bạn muốn nghiên cứu điều gì?", disabled=not bool(os.getenv("OPENAI_API_KEY")))
prompt = typed or prompt
if prompt:
    if not os.getenv("OPENAI_API_KEY"):
        st.error("Điền OPENAI_API_KEY trong .env trên máy chạy UI.")
    else:
        with st.chat_message("user"):
            st.markdown(prompt)
        with st.chat_message("assistant"):
            with st.status("Đang nghiên cứu…", expanded=True) as status:
                demo.on_progress = lambda message: status.update(label=message)
                turn = demo.ask(prompt)
                status.update(label="Đã lưu nhật ký", state="complete", expanded=False)
                demo.on_progress = lambda _: None
        st.rerun()

with st.sidebar:
    st.divider()
    st.download_button("↓ Tải transcript JSON", data=json.dumps(redact(demo.transcript), ensure_ascii=False,
                        indent=2, default=str), file_name=demo.path.name, mime="application/json",
                        use_container_width=True)
    with st.expander("Phiên bản & file log"):
        st.code(demo.transcript["artifact_version"])
        st.caption(str(demo.path))
        st.caption("Log gồm thời gian UTC+7, model, hash/snapshot prompt-tools, từng vòng gọi tool và lỗi.")
