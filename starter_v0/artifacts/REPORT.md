# Day 03 Lab v2 Report — Research Agent

> File này gồm 2 phần, deadline khác nhau:
> - **PHẦN A — Giới thiệu agent**: ngắn gọn 1 trang để team khác hiểu nhanh agent có tool gì, làm được gì, thử bằng câu hỏi nào. **Xong trước 16:30** để làm tài liệu phụ trợ khi demo. Có thể làm thành poster HTML/SVG (`artifacts/poster.html` / `poster.svg`) để show cho team cùng zone.
> - **PHẦN B — Chi tiết / Bằng chứng**: bảng đầy đủ (v0–v3, failure, eval, chat) dựa trên log thật. **Có thể hoàn thiện sau buổi debate để nộp bài.**

## Team

- Team:
- Members:
- Provider/model:

---

# PHẦN A — Giới thiệu agent

## A1. Agent này làm được gì

> 1–2 câu mô tả agent dùng để làm gì (cho team khác hiểu nhanh).

Ví dụ: "Research agent: tìm tin theo từ khóa / theo tài khoản, đọc URL, tổng hợp thành digest, và gửi lên Telegram khi được xác nhận."

**Link dùng thử (deploy):**

> Dán link public để team khác mở thử ngay. Cách deploy nhanh bằng Cloudflare Tunnel xem README. Nếu deploy Vercel/Streamlit Cloud thì dán link đó.
>
> URL: 

## A2. Tool agent có

> Liệt kê các tool agent đang dùng (gồm tool mới nhóm tự thêm). Mỗi tool 1 dòng: tên + làm được gì.

| Tên tool | Làm được gì | Tool mới nhóm thêm? |
|---|---|---|
| clarify | hỏi lại người dùng khi thiếu thông tin | không |
| dedupe | loại bỏ mục trùng URL hoặc tiêu đề trong danh sách đã có; giữ mục đầu tiên | có — A viết code/test; B viết case G05. Chưa tích hợp declaration vào tools.yaml |

## A3. Câu hỏi mẫu để thử

> 3–5 câu hỏi/yêu cầu mẫu để team khác tự thử agent ngay.

1.
2.
3.

---

# PHẦN B — Chi tiết / Bằng chứng

## B1. Version Evidence

Fill from `artifacts/version_log.csv` and `runs/*.json`.

| Version | Changed Artifact | Hypothesis | Metric Before | Metric After | Run File |
|---|---|---|---:|---:|---|
| v0 | baseline |  |  |  |  |
| v1 |  |  |  |  |  |
| v2 |  |  |  |  |  |
| v3 |  |  |  |  |  |

## B2. Failure Analysis

Phân tích bởi B, nguồn: `runs/v0_B_base_openai_20261110T103030701042.json`.
Provider/model: OpenAI / gpt-4o-mini. Artifact: `v0+peb1c8179815b+t5b22a2476d41`.
Baseline: 15/20 case pass (75%), routing 80%, arguments 75%, multi turn 100%, provider errors 0.
Các đề xuất dưới đây chưa được kiểm chứng bằng v1–v3.

| Case ID | Failure Type | Actual Tool Calls | What Failed | Fix |
|---|---|---|---|---|
| R08_out_of_scope | out_of_scope | send(text=đáp án bài toán), không truyền confirmed | Yêu cầu ngoài phạm vi nhưng vẫn gọi tool gửi | Đề xuất: quy tắc phạm vi research và không dùng send để trả lời trực tiếp |
| R10_missing_handle | missing_info | timeline(screenname=sama) | Tự đoán tài khoản; thiếu clarify(response_type=text) | Đề xuất: thiếu handle thì hỏi lại, không chọn tài khoản thay người dùng |
| R11_missing_url | missing_info | fetch(url=https://example.com/article) | Tạo URL khi người dùng chưa cung cấp; thiếu clarify | Đề xuất: chỉ đọc URL có trong ngữ cảnh, thiếu thì hỏi lại |
| R12_confirm_before_send | wrong_boundary | send(text=Bản tin này), không truyền confirmed | Gọi action trước bước clarify(response_type=yes_no) | Đề xuất: hỏi xác nhận trước khi gọi send |
| R13_parallel_web_and_tweets | Case gắn nhãn wrong_tool; lỗi quan sát là wrong_arg_value | lookup(query=AI news, timeframe=day, max_results=5) và social_search(query=AI, search_type=Latest, limit=5) | Gọi đủ 2 tool; lookup thiếu topic=news, query khác chuỗi AI mà eval yêu cầu | Đề xuất: làm rõ args cho tin tức; ghi nhận query gần nghĩa vẫn fail do bộ chấm so khớp chuỗi |

R08/R12 không thực sự gửi Telegram: tool trả `needs_confirmation`. R10/R11/R13 có lỗi tool do thiếu RAPIDAPI_KEY, FIRECRAWL_API_KEY hoặc TAVILY_API_KEY. Không có provider_error không có nghĩa API tool đã hoạt động. Các lỗi setup này cần theo dõi riêng với lỗi chọn tool/args.

## B3. Team Eval Cases

Đã viết 10 case trong `data/eval_group.json`: G01–G05 single turn, G06–G10 multi turn.
Đã chạy suite nhóm trên v2, artifact `v2+p5557e29be07f+t1f08a299bf2a`: 8/10 pass, case_accuracy=0.8, routing=1.0, argument_accuracy=0.8, multiturn_accuracy=0.8, provider_error_cases=0.
Run: `runs/v2_B_group_openai_20261110T111141081146.json`. Phân tích: `analysis/B_v2_group_results.csv`; kiểm tra bổ sung: `analysis/B_v2_manual_checks.json`.
G04 hỏi xin link/nội dung đúng, runtime mặc định response_type=text nhưng bộ chấm yêu cầu args ghi rõ nên fail. Đây là khác biệt giữa hành vi thực tế và chấm args tường minh; không sửa expect sau khi thấy kết quả.
G09 thiếu topic=news: đây là lỗi arguments có ảnh hưởng thực tế vì lookup mặc định general. Đề xuất Phúc bổ sung quy tắc giữ topic news khi đổi timeframe qua nhiều lượt.
G05 đã xác nhận từ log thật: model truyền nguyên 3 mục, giữ đúng mục đầu/thứ ba, item_count=2, removed=1. Query của G02/G03/G08/G09/G10 đều là robotics. Các case gọi web/tweet vẫn trả lỗi thiếu TAVILY_API_KEY hoặc RAPIDAPI_KEY trên máy B; PASS chỉ phản ánh routing/args.
Lần thử trước `runs/v2_B_group_openai_20261110T111059265125.json` có 10 APIConnectionError, measured_cases=0 do lỗi kết nối trong môi trường hạn chế; không dùng điểm 0 đó để đánh giá model. Run thành công phía trên là kết quả được dùng.

| Case ID | What It Tests | Expected Tool/Behavior | Result |
|---|---|---|---|
| G01_handle_without_at | Single: chuẩn hóa @NASA và số lượng | timeline(screenname=NASA, limit=3) | PASS |
| G02_news_week | Single: tin web tuần này | lookup(topic=news, timeframe=week, max_results=4) | PASS |
| G03_top_social | Single: tweet phổ biến thay vì mới nhất | social_search(search_type=Top, limit=2) | PASS |
| G04_missing_link | Single: thiếu link/nội dung | clarify(response_type=text), câu hỏi xin URL/nội dung | FAIL: response_type: expected 'text', got None |
| G05_dedupe_existing_items | Single: tool mới, bỏ trùng URL trên dữ liệu có sẵn | Chỉ dedupe(by=url); truyền nguyên 3 mục, đầu ra giữ Tin A/Tin B, item_count=2, removed=1 | PASS |
| G06_fill_handle | Multi: bổ sung handle sau khi được hỏi | timeline(screenname=NASA, limit=4) | PASS |
| G07_correct_handle | Multi: sửa handle ở lượt cuối | Chỉ timeline(screenname=SpaceX, limit=2) | PASS |
| G08_correct_limit | Multi: sửa số lượng, giữ chủ đề và cách sắp xếp | social_search(search_type=Latest, limit=2), chủ đề robotics | PASS |
| G09_change_timeframe | Multi: đổi ngày sang tháng, giữ số lượng | lookup(topic=news, timeframe=month, max_results=3), chủ đề robotics | FAIL: topic: expected 'news', got None |
| G10_switch_source | Multi: chuyển tweet sang web | Chỉ lookup(topic=news, timeframe=day, max_results=3), chủ đề robotics | PASS |

Kiểm tra offline và log: `analysis/B_validation.txt`, script tái lập: `scripts/validate_group_b.py`.
Case G05 không chấm tự động args.items vì harness hiện sắp xếp list object bằng sorted, gây TypeError. Vì vậy phải kiểm tra actual_tool_calls.args.items giữ nguyên dữ liệu/thứ tự và tool_results đúng đầu ra. G02/G03/G08/G09/G10 cần kiểm tra thủ công query còn đúng chủ đề; G04 cần kiểm tra nội dung câu hỏi. Multi turn hiện chỉ chấm hành vi lượt cuối với các lượt trước làm ngữ cảnh.

Cập nhật v2 từ commit `69c5ffd`: Phúc đã tích hợp dedupe vào tools.yaml; file declaration.proposed chỉ còn là đề xuất lịch sử. Contract + dedupe unit tests: 68 passed. Chưa sửa prompt/tools khi đo suite nhóm; giữ nguyên 10 case để so sánh với v3 sau này.

## B4. Live Chat Evidence

Use `transcripts/*.transcript.json`.

| Turn | User Request | Tool Calls | Version Evidence | Outcome |
|---|---|---|---|---|
|  |  |  |  |  |

## B5. Bonus Evidence

Only fill if your team did bonus.

| Bonus | Evidence File | What Worked | Risk / Guardrail |
|---|---|---|---|
| send (Telegram) |  |  |  |
| arXiv/company policy |  |  |  |
| UI |  |  |  |
| Tool mới dedupe (A) và eval G05 (B) | tools/dedupe/TOOL.md; tests/test_tool_dedupe.py; data/eval_group.json; analysis/B_validation.txt | 8 unit test của A pass; B xác nhận đầu ra mẫu G05 offline đúng | Chưa chứng minh model route đúng; thiếu declaration. Tool nhận list có phần tử không phải object vẫn giữ phần tử đó, cần A làm rõ contract |

Tool unit tests: số test đã viết, số bug tìm được trong tool có sẵn (nếu có), và một ví dụ lỗi mà unit test bắt được nhưng eval không bắt được.

## B6. Reflection

- Which fixes belonged in `system_prompt.md`?
- Which fixes belonged in `tools.yaml`?
- Which failure needed manual review instead of automatic grading?
- What would you improve next?

Nhận xét của B: dedupe phù hợp để làm sạch nguồn đã thu thập trước khi format, chạy local và không cần API key. Bộ test hiện bao phủ chuẩn hóa URL/tiêu đề, giữ mục đầu, input rỗng, sai kiểu list và sai by. Chưa có bằng chứng về routing live. Nên đưa quy tắc hỏi lại/phạm vi/xác nhận vào system_prompt; đưa điều kiện chọn tool và convention arguments vào tools.yaml. Hai điểm cần review thủ công là query gần nghĩa trong R13 và nội dung items/đầu ra trong G05. Chưa sửa harness hoặc implementation của A trong phần việc B.

## B7. Small Local Model Challenge (bonus)

Only fill if your team did the local model challenge.

| Version | Model (provider) | Prompt/Tools | case_accuracy | tool_routing | argument | multiturn | Run File |
|---|---|---|---|---|---|---|---|
| v3 | (cloud) | v3 |  |  |  |  |  |
| v3-... | (ollama) | v3 |  |  |  |  |  |
| v3-... | (ollama) | v3 |  |  |  |  |  |
| v4-local |  |  |  |  |  |  |  |
| v5-local |  |  |  |  |  |  |  |

Lỗi đặc thù của model nhỏ (đếm từ run JSON):

| Failure Pattern | Count | Example Case | Fix Tried | Helped? |
|---|---|---|---|---|
| wrong / hallucinated tool |  |  |  |  |
| invalid JSON args (`_invalid_json_arguments`) |  |  |  |  |
| no tool call / answered directly |  |  |  |  |
| missed `clarify` |  |  |  |  |
| repeated / unnecessary calls |  |  |  |  |

- Cái gì giúp model nhỏ gọi tool đúng hơn nhất? Bằng chứng?
- Bản prompt tối ưu cho local chạy trên model cloud thì sao?
- Khi nào nhóm sẽ chọn model local thay vì cloud cho agent này?
