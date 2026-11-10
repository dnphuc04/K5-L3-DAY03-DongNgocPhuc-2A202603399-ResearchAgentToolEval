# UI Streamlit

Chạy tại starter_v0, sau khi kích hoạt môi trường ảo:

```powershell
python -m pip install -r requirements.txt
python -m streamlit run app.py --server.address 127.0.0.1 --server.port 8501
```

Mở http://localhost:8501. Key được đọc từ .env trên máy chạy server.
UI app.py của nhóm mặc định demo offline, không gọi model. Để bật live, thêm RESEARCH_AGENT_ENABLE_LIVE_MODE=true vào .env rồi khởi động lại và tắt toggle offline.
Giao diện live bổ sung (có nút tải JSON) chạy bằng `python -m streamlit run app_live.py --server.port 8502`.
Transcript tự lưu vào transcripts/. Nhãn version chỉ là nhãn: prompt/tools thực tế vẫn lấy từ artifacts/ và có hash để đối chiếu. Bộ tools hiện tại đã mở rộng sau snapshot v3.4.
Chưa có link public; localhost chỉ dùng trên máy chạy server.
