# Day 03 — Research Agent: Báo cáo nộp bài

## Team

- Repo: dnphuc04/K5-L3-DAY03-DongNgocPhuc-2A202603399-ResearchAgentToolEval.
- Phân công: Phúc tối ưu prompt/tools và version log; A viết dedupe và unit test; B phân tích lỗi, 10 case nhóm và bằng chứng; UI Streamlit đã bổ sung tại app.py.
- Danh sách họ tên đầy đủ của A/B/C: cần trưởng nhóm bổ sung trước khi nộp; không suy đoán từ tên thư mục máy.
- Provider/model: OpenAI / gpt-4o-mini. Snapshot đo chuẩn: `v3.4+p41ab063811a5+t3b41d41b278e`; xem kết quả bộ tools mở rộng cuối tại mục B3 bổ sung.

# PHẦN A — Giới thiệu agent

## A1. Agent làm được gì

Trợ lý nghiên cứu chọn nguồn web, mạng xã hội, paper và chính sách nội bộ; đọc tài liệu, loại bỏ nguồn trùng và trình bày bản tin. Agent hỏi lại khi thiếu dữ liệu và yêu cầu xác nhận trước khi gửi Telegram.

UI: http://localhost:8501 — chạy trên máy có server. Chưa có bằng chứng link public trong repo; localhost không phải link để máy khác truy cập.
Khởi động: `python -m streamlit run app.py --server.address 127.0.0.1 --server.port 8501`.
Hướng dẫn: `UI_README.md`. Model và các API lấy dữ liệu cần key riêng trong .env trên máy chạy; không nộp .env.

## A2. Tool agent có

| Tool | Chức năng | Tool mới? |
|---|---|---|
| clarify | Hỏi lại khi thiếu thông tin hoặc cần xác nhận gửi | Có sẵn |
| timeline | Lấy bài đăng từ tài khoản X | Có sẵn |
| social_search | Tìm bài đăng theo chủ đề | Có sẵn |
| lookup | Tìm web/tin tức | Có sẵn |
| fetch | Đọc URL | Có sẵn |
| format | Trình bày danh sách thành bản tin | Có sẵn |
| send | Gửi Telegram khi đã xác nhận | Có sẵn |
| policy | Tra cứu chính sách nội bộ | Có sẵn |
| papers | Tìm paper arXiv | Có sẵn |
| paper_text | Tải/trích text paper arXiv | Có sẵn |
| dedupe | Bỏ trùng URL/tiêu đề, giữ mục đầu tiên | Có |
| text_stats | Thống kê văn bản | Có |
| wiki_search | Tìm Wikipedia | Có |
| export_report | Lưu báo cáo cục bộ | Có |
| data_calc | Tính toán số liệu | Có |

## A3. Câu hỏi demo

1. Lấy 3 tweet gần nhất của @NASA.
2. Tìm 4 tin tức web về robotics trong tuần này.
3. Tóm tắt bài báo này (chưa gửi URL) — kiểm tra agent hỏi lại.
4. Bỏ trùng URL, giữ mục đầu tiên: [{"title":"A","url":"https://www.example.com/post/"},{"title":"A copy","url":"https://example.com/post?utm_source=demo#intro"},{"title":"B","url":"https://example.com/other"}].
5. Sau khi tìm tin hôm nay, yêu cầu đổi sang tháng này nhưng giữ chủ đề và số lượng.

# PHẦN B — Chi tiết / Bằng chứng

## B1. Version Evidence

Nguồn đầy đủ: `artifacts/version_log.csv`, các snapshot trong `artifacts/versions/` và JSON trong runs/. Không coi kết quả của các suite khác nhau là cùng một phép đo.

| Version | Thay đổi/giả thuyết | Case accuracy (base) | Routing | Arguments | Run |
|---|---|---:|---:|---:|---|
| v0 | Baseline có key tool; đo hành vi starter | 65% | 75% | 65% | `runs/v0_B_base_openai_20261110T100659529223.json` |
| v1 | Thay đoán thông tin bằng hỏi lại | 85% | 90% | 85% | `runs/v1_B_base_openai_20261110T103431763218.json` |
| v2 | Thêm declaration dedupe; giữ prompt v1 | 85% | 90% | 85% | `runs/v2_B_base_openai_20261110T104542401677.json` |
| v3 | Thử tối ưu routing và boundary; có regression | 75% | 80% | 75% | `runs/v3_B_base_openai_20261110T111133270464.json` |
| v3.4 | Làm rõ nguồn đang hoạt động, hủy nguồn và carryover; bản cuối | 100% | 100% | 100% | `runs/v3.4_B_base_openai_20261110T113721523019.json` |

Baseline chính của nhóm là 65%; B có một lần chạy khác cùng artifact đạt 75% (`runs/v0_B_base_openai_20261110T103030701042.json`). Không thay thế/chọn baseline có lợi; hai lần chạy khác nhau chứng tỏ kết quả model có thể biến động. B2 phân tích lần chạy của B. Các bản v3.1–v3.3 có log và snapshot riêng; không xóa regression. Kết quả cuối 100% trên bộ hữu hạn chưa chứng minh tổng quát hóa.

## B2. Failure Analysis





Phân tích bởi B, nguồn: `runs/v0_B_base_openai_20261110T103030701042.json`.
Provider/model: OpenAI / gpt-4o-mini. Artifact: `v0+peb1c8179815b+t5b22a2476d41`.
Baseline: 15/20 case pass (75%), routing 80%, arguments 75%, multi turn 100%, provider errors 0.
Đây là phân tích tại thời điểm v0; kết quả các bản cải thiện được ghi tại B1/B3.

| Case ID | Failure Type | Actual Tool Calls | What Failed | Fix |
|---|---|---|---|---|
| R08_out_of_scope | out_of_scope | send(text=đáp án bài toán), không truyền confirmed | Yêu cầu ngoài phạm vi nhưng vẫn gọi tool gửi | Đề xuất: quy tắc phạm vi research và không dùng send để trả lời trực tiếp |
| R10_missing_handle | missing_info | timeline(screenname=sama) | Tự đoán tài khoản; thiếu clarify(response_type=text) | Đề xuất: thiếu handle thì hỏi lại, không chọn tài khoản thay người dùng |
| R11_missing_url | missing_info | fetch(url=https://example.com/article) | Tạo URL khi người dùng chưa cung cấp; thiếu clarify | Đề xuất: chỉ đọc URL có trong ngữ cảnh, thiếu thì hỏi lại |
| R12_confirm_before_send | wrong_boundary | send(text=Bản tin này), không truyền confirmed | Gọi action trước bước clarify(response_type=yes_no) | Đề xuất: hỏi xác nhận trước khi gọi send |
| R13_parallel_web_and_tweets | Case gắn nhãn wrong_tool; lỗi quan sát là wrong_arg_value | lookup(query=AI news, timeframe=day, max_results=5) và social_search(query=AI, search_type=Latest, limit=5) | Gọi đủ 2 tool; lookup thiếu topic=news, query khác chuỗi AI mà eval yêu cầu | Đề xuất: làm rõ args cho tin tức; ghi nhận query gần nghĩa vẫn fail do bộ chấm so khớp chuỗi |

R08/R12 không thực sự gửi Telegram: tool trả `needs_confirmation`. R10/R11/R13 có lỗi tool do thiếu RAPIDAPI_KEY, FIRECRAWL_API_KEY hoặc TAVILY_API_KEY. Không có provider_error không có nghĩa API tool đã hoạt động. Các lỗi setup này cần theo dõi riêng với lỗi chọn tool/args.





## B3. Team Eval Cases

10 case giữ nguyên giữa lần đo v2 và v3.4: 5 single turn + 5 multi turn, có G05 cho tool mới.

| Case | Loại | Expected calls/args | v2 | v3.4 |
|---|---|---|---|---|
| G01_handle_without_at | Single | `timeline({"screenname": "NASA", "limit": 3})` | PASS | PASS |
| G02_news_week | Single | `lookup({"topic": "news", "timeframe": "week", "max_results": 4})` | PASS | PASS |
| G03_top_social | Single | `social_search({"search_type": "Top", "limit": 2})` | PASS | PASS |
| G04_missing_link | Single | `clarify({"response_type": "text"})` | FAIL | PASS |
| G05_dedupe_existing_items | Single | `dedupe({"by": "url"})` | PASS | PASS |
| G06_fill_handle | Multi | `timeline({"screenname": "NASA", "limit": 4})` | PASS | PASS |
| G07_correct_handle | Multi | `timeline({"screenname": "SpaceX", "limit": 2})` | PASS | PASS |
| G08_correct_limit | Multi | `social_search({"search_type": "Latest", "limit": 2})` | PASS | PASS |
| G09_change_timeframe | Multi | `lookup({"topic": "news", "timeframe": "month", "max_results": 3})` | FAIL | PASS |
| G10_switch_source | Multi | `lookup({"topic": "news", "timeframe": "day", "max_results": 3})` | PASS | PASS |

v2: 8/10, routing=100%, args=80%, multi=80%. v3.4: 10/10, routing/args/multi=100%, provider_error=0.
Run v2: `runs/v2_B_group_openai_20261110T111141081146.json`.
Run v3.4 của B: `runs/v3.4_B_group_openai_20261110T121028534135.json`.
So sánh: `analysis/B_v2_v3_4_rerun_comparison.csv`; đối chiếu dữ liệu: `analysis/B_v3_4_rerun_checks.json`.

G04 v2 hỏi đúng nhưng không ghi response_type=text tường minh; runtime có default đúng nên cần phân biệt lỗi chấm args và lỗi hành vi. G09 thiếu topic=news làm runtime dùng general, là lỗi chức năng. Cả hai đã pass tại v3.4.
G05 được kiểm tra input nguyên 3 mục và output giữ A/B, removed=1, item_count=2. Không đưa items dạng list object vào expected args vì harness sorted(list_of_dict) gây TypeError; lưu kiểm tra riêng. Query các case tìm kiếm đã đối chiếu là robotics. Multi turn trong eval chỉ chấm lượt cuối với lịch sử làm ngữ cảnh, khác với chạy chat nhiều lượt thật.

8 case trong run cuối của B có tool error do thiếu key lấy dữ liệu. Vì vậy PASS là bằng chứng routing/arguments, chưa phải lấy dữ liệu live thành công. Nhóm có smoke log riêng `runs/v0_tool_smoke.json`; không dùng smoke log cũ để khẳng định trạng thái key hiện tại.
Lần lỗi mạng `runs/v2_B_group_openai_20261110T111059265125.json` có measured_cases=0; được giữ để truy vết, không dùng làm điểm model.

## B4. Live Chat Evidence

Nguồn: `transcripts/v3.4_submission_live_20261110T121557.transcript.json`, artifact `v3.4+p41ab063811a5+t3b41d41b278e`. Đây là 3 lượt kiểm tra được script gửi tới model thật, không phải log mô phỏng hoặc buổi người dùng thao tác UI; script: `scripts/submission_live_check.py`. Các transcript CLI/UI thực tế trước đó cũng giữ trong transcripts/.

| Lượt | Yêu cầu | Tool | Trạng thái |
|---|---|---|---|
| 1 | Chỉ bỏ trùng URL, giữ mục đầu tiên, chưa định dạng | dedupe | answered |
| 2 | Đọc bài báo này và tóm tắt giúp mình. Mình chưa gửi URL hoặc nội dung. | clarify | waiting_for_user |
| 3 | Thôi không đọc bài nữa. Chỉ bỏ trùng theo tiêu đề trong danh sách mới này | dedupe | answered |

Lượt 1 xác minh bỏ trùng URL; lượt 2 agent dừng để xin URL; lượt 3 nhận yêu cầu thay thế và bỏ trùng tiêu đề. Không tính tin nhắn “exit” ở transcript cũ là lượt demo chức năng. Các transcript cũ ghi đúng v2, không đổi nhãn thành v3.4.

## B5. Tool tests, UI và bonus

- Toàn bộ suite: xem số lượng cuối trong `analysis/submission_pytest.txt`, không còn stub skip. 17 stub đã thay bằng assert chạy offline với fake HTTP, bao gồm guardrail gửi, mapping request/response, lỗi thiếu key, boundary và policy injection probe. `tests/test_tool_dedupe.py` có 8 test của A; 3 test dedupe bổ sung trong test_tools_todo.py. Bốn tool tích hợp cùng UI có 12 test tại tests/test_added_tools.py.
- dedupe có TOOL.md, registry và declaration. Test kiểm tra chuẩn hóa URL/tiêu đề, thứ tự, missing field, input rỗng và input sai. List chứa phần tử không phải object hiện vẫn được giữ lại: giới hạn cần làm rõ nếu mở rộng contract.
- UI Streamlit chính của nhóm tại app.py có chế độ offline và live (bật RESEARCH_AGENT_ENABLE_LIVE_MODE=true). Offline là chạy tool theo quy tắc/mẫu, không phải model routing. Giao diện live bổ sung giữ tại app_live.py: chat, xem tool và tải transcript. Chưa có link public. Hash ghi nhận prompt/tools thực tế.
- Telegram chưa có bằng chứng gửi thật được xác nhận; chỉ khẳng định guardrail trong test offline và needs_confirmation ở log v0. Không thực hiện gửi ngoài để tạo bằng chứng.
- arXiv/policy là tool starter; không tính chúng là tool mới của nhóm. Commit a8f881e bổ sung data_calc, text_stats, export_report, wiki_search cùng UI: tổng cộng 5 tool mới gồm dedupe. Cần người chấm đối chiếu chất lượng và điều kiện bonus.

Lưu ý phiên bản: các điểm v3.4 phía trên dùng tools snapshot trước khi thêm 4 tool UI. Bộ tools hiện tại có hash mới, không được gán các điểm đó cho bộ tools mở rộng nếu chưa chạy lại. Có thể tái lập bằng --system-prompt artifacts/versions/v3.4/system_prompt.md --tools artifacts/versions/v3.4/tools.yaml.

## B6. Reflection

System prompt chịu trách nhiệm về thiếu dữ liệu, phạm vi, xác nhận gửi và giữ/đổi/hủy thông tin qua nhiều lượt. Tool declarations làm rõ nguồn nào dùng khi nào và conventions của topic/timeframe/search_type/handle.
R13 v0 cho thấy nhãn failure_type của dataset khác lỗi thực tế; cần đọc observed_mismatch và arguments. Query gần nghĩa có thể fail so khớp chuỗi. G04 cho thấy default đúng vẫn có thể fail khi chấm tham số tường minh.
Unit test bắt lỗi request gửi sai hoặc guardrail hoạt động sai mà routing eval có thể bỏ qua. Probe chính sách kiểm tra instruction-like text nằm ở untrusted_text thay vì facts; đây không phải bảo đảm chống mọi prompt injection.
Bước tiếp theo: kiểm tra tổng quát hóa trên case chưa thấy, sửa harness xử lý list object, bổ sung báo cáo độ tin cậy nhiều lần chạy, và xác nhận dữ liệu live trên môi trường đủ key.

## B7. Small Local Model Challenge

Không thực hiện bonus local model; không có số liệu Ollama để báo cáo.

## Kiểm tra trước khi nộp

- Có code, prompt/tools cuối và snapshots, version log, 10 case, tests, run JSON, transcript, analysis, UI và hướng dẫn.
- Chưa có danh sách họ tên đầy đủ và URL public. Trưởng nhóm cần bổ sung hai mục này nếu dùng link triển khai để chấm.
- Không nộp .env, API key, .venv, cache hoặc .git. Gói ZIP được script quét mẫu key và kiểm tra danh sách file.

## B3 bổ sung — Bộ tools mở rộng khi nộp

Sau commit a8f881e, thêm 4 tool làm thay đổi tools hash. Giữ nguyên dataset, prompt và mọi lần chạy; không chọn riêng kết quả cao.

- base: 20/20 PASS; artifact `v3.4-ui+p41ab063811a5+t68b452aec41f`; `runs/v3.4-ui_B_base_openai_20261110T122038144115.json`.
- group: 9/10 PASS; artifact `v3.4-ui+p41ab063811a5+t68b452aec41f`; `runs/v3.4-ui_B_group_openai_20261110T122021056394.json`.
  - G08_correct_limit: search_type: expected 'Latest', got None.

G08 của bộ tools mở rộng thiếu search_type tường minh; social_search mặc định Latest nên không đồng nhất với sai cách sắp xếp thực tế. Vẫn giữ FAIL theo cách chấm hiện tại. G04/G09 đã PASS. Unit test cuối: **124 passed, 0 failed, 0 skipped**.
Snapshot bộ mở rộng tại artifacts/versions/v3.4-ui/. UI hiện dùng bộ mở rộng; không gắn nhãn/hashes của snapshot cũ cho bộ này.
