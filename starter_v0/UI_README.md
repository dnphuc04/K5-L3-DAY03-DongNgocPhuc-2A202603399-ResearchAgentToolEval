# UI Streamlit

Chạy tại starter_v0, sau khi kích hoạt môi trường ảo:

```powershell
python -m pip install -r requirements.txt
python -m streamlit run app.py --server.address 127.0.0.1 --server.port 8501
```

Mở http://localhost:8501. Key được đọc từ .env trên máy chạy server.
UI app.py đã tích hợp bộ chạy DemoSession: nếu có OPENAI_API_KEY thì mặc định live; vẫn có thể bật toggle offline để chạy tool mẫu không gọi model. RESEARCH_AGENT_ENABLE_LIVE_MODE=false buộc chế độ offline; true cho phép live với provider đã cấu hình.
Giao diện live bổ sung (có nút tải JSON) chạy bằng `python -m streamlit run app_live.py --server.port 8502`.
Transcript tự lưu vào transcripts/. Nhãn version chỉ là nhãn: prompt/tools thực tế vẫn lấy từ artifacts/ và có hash để đối chiếu. Bộ tools hiện tại đã mở rộng sau snapshot v3.4.
UI app.py có nút tải JSON, lưu từng bước gọi model/tool kể cả khi lỗi, snapshot prompt/tools và thời gian UTC+7; key được che trước khi ghi log. Telegram bị chặn gửi trong demo. Mở cuộc trò chuyện mới vẫn giữ file log của phiên cũ.
Sau khi pull code mới, dừng hẳn Streamlit bằng Ctrl+C rồi chạy lại lệnh trên để tránh module/session cũ còn trong bộ nhớ (ví dụ lỗi unexpected keyword argument provider_name).
Chưa có link public; localhost chỉ dùng trên máy chạy server.
