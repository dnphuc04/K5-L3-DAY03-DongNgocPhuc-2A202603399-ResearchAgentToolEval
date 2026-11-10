# Hướng dẫn kiểm tra gói nộp

1. Đọc artifacts/REPORT.md, đặc biệt phần kết quả bộ tools mở rộng ở cuối.
2. Chạy `python -m pip install -r requirements.txt` trong môi trường ảo.
3. Chạy `python -m pytest -q -p no:cacheprovider`: kết quả đã ghi là 124 passed.
4. UI chính: `python -m streamlit run app.py`. Mặc định demo offline, không chứng minh model routing. Live cần cấu hình RESEARCH_AGENT_ENABLE_LIVE_MODE=true trong .env, restart rồi tắt toggle offline.
5. UI live bổ sung: `python -m streamlit run app_live.py --server.port 8502`.
6. Eval nộp cuối (API thật, có tính phí):

```powershell
python run_eval.py --provider openai --version v3.4-ui --suite base --eval-cases data/eval_base.json
python run_eval.py --provider openai --version v3.4-ui --suite group --eval-cases data/eval_group.json
```

Mỗi lần gọi model có thể cho kết quả khác nhau. Giữ mọi run và phân biệt điểm routing/args với lỗi thực thi tool do thiếu key.

Các snapshot prompt/tools cũ ở artifacts/versions/. Dùng --system-prompt và --tools để tái lập đúng snapshot; nhãn --version không tự đổi file.

Gói ZIP được tạo bằng `python scripts/finalize_submission.py`, gồm starter_v0 và các bằng chứng; không có .env, .venv hoặc cache. Script này cập nhật REPORT từ log, nên bổ sung tên thành viên/link public sau khi tạo gói lần cuối hoặc cập nhật script trước.

Trước khi nộp: trưởng nhóm điền tên/họ tên thành viên và URL public vào REPORT rồi cập nhật ZIP tương ứng. Không đưa API key vào báo cáo, ảnh hoặc ZIP.
