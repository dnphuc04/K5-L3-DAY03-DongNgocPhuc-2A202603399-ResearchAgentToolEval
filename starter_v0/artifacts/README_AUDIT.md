# Đối chiếu README khi hoàn thiện v3.5

| Yêu cầu | Bằng chứng / trạng thái |
|---|---|
| Provider thật, preflight | OpenAI gpt-4o-mini, các run JSON API thật; OpenRouter trong ví dụ không bắt buộc |
| API lấy dữ liệu | runs/v0_tool_smoke.json có lookup/fetch/timeline/social_search thành công sau retry; lỗi thiếu key ở máy B được giữ riêng, không coi routing PASS là lấy dữ liệu thành công |
| Ít nhất 5 tool | tools.yaml có 15 tool, registry tương ứng |
| Base eval, baseline v0 | runs/v0_B_base_*.json; version_log.csv ghi rõ các lần chạy |
| v1/v2/v3, giả thuyết và metric | version_log.csv; artifacts/versions/; không xóa regression |
| Prompt bỏ đoán/gửi ngay/ép một bước, có routing | system_prompt.md bản cuối; prompt không đổi trong v3.5 |
| Description mỗi tool, điều kiện dùng/không dùng | Hoàn thiện cả 15 tool tại tools.yaml v3.5 |
| Conventions handle/news/timeframe/Top/Latest | Mô tả tham số tường minh, bảo toàn context và sửa đổi mới nhất |
| send chỉ khi confirmed=true | Description + confirmed parameter; prompt hỏi yes_no trước. Không gửi thật để tạo log |
| Tool mới và TOOL.md/registry/declaration | dedupe, text_stats, data_calc, wiki_search, export_report |
| Ít nhất 3 test/tool mới | test_tool_dedupe.py, test_tools_todo.py, test_added_tools.py |
| 10 eval case 5 single/5 multi, có tool mới | eval_group.json G01–G10; G05 cho dedupe |
| 0 failed/0 skipped | analysis/submission_pytest.txt: 124 passed |
| Base/group cuối | v3.5: base 20/20, group 10/10; JSON trong runs/ |
| UI Streamlit chạy được | app.py của nhóm; app_live.py bổ sung; AppTest kiểm tra khởi động; UI_README.md |
| Link dùng thử | Hoãn theo yêu cầu người dùng, không đánh dấu hoàn tất |
| chat.py >=3 lượt live | transcripts/v3.5_openai_*.transcript.json; analysis/cli_v3_5_checks.json; input scripted qua subprocess nhưng chạy đúng chat.py/model thật |
| REPORT A/B | REPORT.md có giới thiệu, tool, câu hỏi demo, versions, failure, cases, live, reflection |
| Phần A trước 16:30 | Không khẳng định hồi tố vì chưa xác minh được thời điểm hoàn thiện |
| Nộp code/artifacts/log/transcript/tests | ResearchAgent_Submission.zip; kiểm tra ZIP CRC và loại .env/.venv/cache |
| Tên thành viên | Người dùng yêu cầu điền sau |

README có nơi ghi 5 case nhưng Scope/REPORT yêu cầu 10: đã chọn mức 10.
Challenge TODO đã hoàn thành; poster, extension eval và Small Local Model là tùy chọn, không thiếu phần bắt buộc vì chưa làm các mục này.
Bonus UI và >3 tool mới có code/tài liệu/test; quyền công nhận điểm thuộc người chấm. Chưa có bằng chứng bonus gửi Telegram thật và không khai đã hoàn thành bonus đó.
