# Phần việc của B — phân tích baseline và eval nhóm

## Bản bàn giao khi chuẩn bị nộp

Đọc REPORT.md để xem trạng thái cuối; các mục phía dưới giữ làm lịch sử làm bài.
- Đủ 10 case, dữ liệu giữ nguyên giữa v2 và các bản v3.
- Snapshot v3.4 của B: 10/10 PASS. Sau khi tích hợp 4 tool cùng UI, bản v3.4-ui: base 20/20, group 9/10; G08 thiếu search_type=Latest tường minh (runtime có default Latest), G04/G09 vẫn PASS.
- Bộ tools mở rộng có snapshot riêng artifacts/versions/v3.4-ui; không đồng nhất điểm/hash với snapshot v3.4.
- Unit tests cuối: 124 passed, không failed/skipped. Log analysis/submission_pytest.txt.
- Có transcript 3 lượt gọi model thật được script chạy, ghi rõ scripted_live_verification; không coi là bằng chứng người dùng thao tác UI.
- ZIP nộp ResearchAgent_Submission.zip ở thư mục gốc, loại trừ .env, .venv và cache.
- Còn cần trưởng nhóm xác nhận họ tên thành viên và link UI public. UI local tại localhost:8501; live mode của app.py cần RESEARCH_AGENT_ENABLE_LIVE_MODE=true và tắt toggle offline.

## Cập nhật sau khi kéo v2

Đã fast-forward tới commit 69c5ffd. dedupe đã được khai báo trong tools.yaml, không còn chờ tích hợp. Các ghi chú chờ khai báo bên dưới là lịch sử chuẩn bị.
Chạy 10 case nhóm trên artifact v2+p5557e29be07f+t1f08a299bf2a: 8/10 pass, routing 100%, arguments 80%, multi turn 80%, không provider error trong run thành công.
Run: runs/v2_B_group_openai_20261110T111141081146.json.
G04 hỏi lại đúng nhưng không truyền response_type=text tường minh; runtime vẫn mặc định text. G09 thiếu topic=news, runtime mặc định general: cần Phúc sửa carryover topic khi thay timeframe.
G05 pass và đã đối chiếu nguyên input/đầu ra bỏ trùng trong log thật; bằng chứng analysis/B_v2_manual_checks.json. Bảng case tại analysis/B_v2_group_results.csv và REPORT B3 đã cập nhật.
Contract + dedupe tests: 68 passed. Tool web/tweet tại máy B vẫn thiếu key; kết quả này đo routing/args, không xác nhận lấy dữ liệu live thành công.
Lần chạy kết nối lỗi trước đó được giữ lại trong runs/v2_B_group_openai_20261110T111059265125.json; measured=0, không dùng làm điểm model.

## Bằng chứng v0

Nguồn: `runs/v0_B_base_openai_20261110T103030701042.json`.
20 case, 15 pass; case_accuracy=0.75, tool_routing_accuracy=0.8,
argument_accuracy=0.75, multiturn_accuracy=1.0; provider_error_cases=0.

| Case | Mong đợi | Thực tế trong log | Nhận xét và đề xuất cho Phúc |
|---|---|---|---|
| R08_out_of_scope | Không gọi tool | Gọi send để trả lời bài toán, không truyền confirmed | Sai phạm vi và dùng send như tool trả lời. Thêm quy tắc không gọi tool cho yêu cầu ngoài phạm vi research. Tool chặn gửi bằng needs_confirmation. |
| R10_missing_handle | clarify(response_type=text) | timeline(screenname=sama) | Tự chọn tài khoản khi chưa được cung cấp. Bỏ chỉ dẫn tự đoán, yêu cầu hỏi lại handle. |
| R11_missing_url | clarify(response_type=text) | fetch(url=https://example.com/article) | Tự tạo URL. Chỉ fetch URL người dùng đã cung cấp trong ngữ cảnh; thiếu thì hỏi lại. |
| R12_confirm_before_send | clarify(response_type=yes_no) | send(text=Bản tin này), không truyền confirmed | Gọi action trước khi xác nhận. Yêu cầu hỏi xác nhận; tool thực tế đã chặn gửi bằng needs_confirmation. |
| R13_parallel_web_and_tweets | lookup(query=AI, topic=news, timeframe=day) và social_search(query=AI) | Đã gọi cả hai tool; lookup dùng query=AI news và bỏ topic; social_search đúng | Đây thực chất là sai args: routing_correct=true, observed_mismatch=wrong_arg_value. Nhãn wrong_tool là nhãn cố định của case, không mô tả chính xác lỗi lần chạy này. Làm rõ topic=news. Query AI news gần nghĩa AI nhưng bộ chấm so khớp chuỗi nên vẫn fail; cần ghi nhận giới hạn đó. |

Các lỗi tool do thiếu key là vấn đề setup riêng: R10 thiếu RAPIDAPI_KEY,
R11 thiếu FIRECRAWL_API_KEY, R13 thiếu TAVILY_API_KEY và RAPIDAPI_KEY.
Không có provider_error không đồng nghĩa tool API đã hoạt động.
Các giả thuyết trên chưa được kiểm chứng bằng v1–v3.

## Eval nhóm hiện tại

`data/eval_group.json` đã có 10 case: G01–G05 single turn, G06–G10 multi turn.
G05 kiểm tra tool mới dedupe. Chưa chạy model để đo kết quả.
Không ép nguyên văn query tìm kiếm khi cách diễn đạt tương đương vẫn hợp lệ.
Vì vậy cần đọc actual_tool_calls để kiểm tra thủ công chủ đề còn đúng ở G02/G03/G08/G09/G10.
G04 cần kiểm tra câu hỏi thực sự xin URL/nội dung. Bộ chấm không tự kiểm tra các ý nghĩa này.
Multi turn chỉ chấm tool call của lượt cuối, không chạy toàn bộ hội thoại từng bước.

## Phân tích tool mới dedupe

Đã lấy commit `3b7aed0` từ origin/main. Implementation và registry đã có; tools.yaml chưa khai báo nên model chưa nhìn thấy tool này.
Tool local, không cần API key, không gọi mạng và không gửi dữ liệu ra ngoài.
Nhận `items` (list object) và `by` (url/title, mặc định url).
Trả `items`, `item_count`, `removed`, `by`; giữ mục xuất hiện đầu tiên.
URL được chuẩn hóa host/www/slash cuối/utm/fragment/thứ tự query; tiêu đề được chuẩn hóa hoa thường/dấu/khoảng trắng.
Mục thiếu trường so sánh được giữ lại. items không phải list hoặc by không hợp lệ trả error dict.
Code hiện giữ cả phần tử không phải object thay vì trả lỗi; unit test hiện chưa bao phủ trường hợp này. Đây là điểm A có thể làm rõ, không thay đổi implementation trong phần việc B.
8 unit test của A đã pass offline. G05 dùng 3 mục, hai URL đầu tương đương; kết quả đúng là giữ Tin A và Tin B, item_count=2, removed=1.

### Giới hạn bộ chấm phát hiện khi chuẩn bị G05

`run_eval.normalize_value` gọi sorted cho list; nếu expected args chứa items là nhiều dict, so sánh gây TypeError. Vì vậy G05 tự động chấm tên dedupe và by=url; đọc actual_tool_calls.args.items để xác nhận nguyên 3 mục, đúng thứ tự và đọc tool_results để xác nhận đầu ra. Không suy ra PASS tự động đồng nghĩa tool đã xử lý đúng dữ liệu. B chưa sửa harness dùng chung.

## Bàn giao cho Phúc và bước tiếp theo

> B đã hoàn thành 10 case (5 single, 5 multi), có G05 cho dedupe. Tool đã có code/registry nhưng thiếu declaration. Mình chuẩn bị artifacts/dedupe_declaration.proposed.yaml; Phúc ghép object dedupe vào tools.yaml ở phiên bản phù hợp, ghi nhận thay đổi trong version log. Lưu ý giới hạn chấm list object trong harness nêu trên.

1. Phúc tích hợp declaration; file đề xuất không tự động được agent đọc.
2. Chạy contract test rồi chạy group eval trên phiên bản prompt/tools thực tế đang dùng; không cần chờ v3 để bắt đầu đo.
3. Nếu prompt vẫn nguyên bản v0, dùng lệnh v0 dưới đây. Nếu đã đổi, đặt nhãn khác và ghi nhận việc thêm tool. Hash sẽ phản ánh tools mới, không coi là cùng artifact baseline cũ.
4. Sau các phiên bản tối ưu, chạy lại suite group để so sánh, giữ nguyên case.
5. Cung cấp run JSON và kiểm tra thủ công cho REPORT B3; dùng bảng v0 ở trên cho B2.

```powershell
python -m pytest tests/test_tool_contract.py -q
python run_eval.py --provider openai --version v0 --suite group --eval-cases data/eval_group.json
```

Không sửa `eval_base.json`, không sửa prompt/tools của Phúc, không ghi kết quả chưa chạy.
