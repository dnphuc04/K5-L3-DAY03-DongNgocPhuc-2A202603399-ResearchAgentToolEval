"""Build an evidence-based report and a secrets-free submission ZIP."""
from pathlib import Path
import csv
import json
import re
import zipfile

ROOT = Path(__file__).resolve().parents[1]


def read(name):
    return json.loads((ROOT / name).read_text(encoding='utf-8'))


def main():
    report_path = ROOT / 'artifacts/REPORT.md'
    previous = report_path.read_text(encoding='utf-8')
    # Keep B's original failure evidence rather than replacing it with later results.
    b2 = previous.split('## B2. Failure Analysis', 1)[1].split('## B3.', 1)[0]
    b2 = b2.replace('Các đề xuất dưới đây chưa được kiểm chứng bằng v1–v3.',
                    'Đây là phân tích tại thời điểm v0; kết quả các bản cải thiện được ghi tại B1/B3.')
    base_files = [
        ('v0', 'v0_B_base_openai_20261110T100659529223.json', 'Baseline có key tool; đo hành vi starter'),
        ('v1', 'v1_B_base_openai_20261110T103431763218.json', 'Thay đoán thông tin bằng hỏi lại'),
        ('v2', 'v2_B_base_openai_20261110T104542401677.json', 'Thêm declaration dedupe; giữ prompt v1'),
        ('v3', 'v3_B_base_openai_20261110T111133270464.json', 'Thử tối ưu routing và boundary; có regression'),
        ('v3.4', 'v3.4_B_base_openai_20261110T113721523019.json', 'Làm rõ nguồn đang hoạt động, hủy nguồn và carryover; bản cuối'),
    ]
    version_rows = []
    for version, filename, reason in base_files:
        d = read('runs/' + filename)
        s = d['summary']
        version_rows.append(f"| {version} | {reason} | {s['case_accuracy']:.0%} | {s.get('tool_routing_accuracy', 0):.0%} | {s.get('argument_accuracy', 0):.0%} | `runs/{filename}` |")
    cases = read('data/eval_group.json')['cases']
    old = read('runs/v2_B_group_openai_20261110T111141081146.json')
    final = read('runs/v3.4_B_group_openai_20261110T121028534135.json')
    old_map = {c['id']: c['result']['passed'] for c in old['results']}
    final_map = {c['id']: c['result']['passed'] for c in final['results']}
    case_rows = []
    for c in cases:
        calls = c['expect'].get('tool_calls', [])
        expected = ', '.join(x['name'] + '(' + json.dumps(x.get('args', {}), ensure_ascii=False) + ')' for x in calls)
        case_rows.append(f"| {c['id']} | {'Multi' if 'turns' in c else 'Single'} | `{expected}` | {'PASS' if old_map[c['id']] else 'FAIL'} | {'PASS' if final_map[c['id']] else 'FAIL'} |")
    live_paths = sorted((ROOT / 'transcripts').glob('v3.4_submission_live_*.json'))
    live = json.loads(live_paths[-1].read_text(encoding='utf-8'))
    live_name = 'transcripts/' + live_paths[-1].name
    live_rows = []
    for t in live['turns']:
        names = ', '.join(e['tool'] for e in t.get('tool_events', [])) or 'none'
        live_rows.append(f"| {t['turn_index']} | {t['user'].split(':')[0]} | {names} | {t['status']} |")
    declarations = __import__('yaml').safe_load((ROOT / 'artifacts/tools.yaml').read_text(encoding='utf-8'))['tools']
    meanings = {'clarify': 'Hỏi lại khi thiếu thông tin hoặc cần xác nhận gửi', 'timeline': 'Lấy bài đăng từ tài khoản X',
                'social_search': 'Tìm bài đăng theo chủ đề', 'lookup': 'Tìm web/tin tức', 'fetch': 'Đọc URL',
                'format': 'Trình bày danh sách thành bản tin', 'send': 'Gửi Telegram khi đã xác nhận',
                'policy': 'Tra cứu chính sách nội bộ', 'papers': 'Tìm paper arXiv',
                'paper_text': 'Tải/trích text paper arXiv', 'dedupe': 'Bỏ trùng URL/tiêu đề, giữ mục đầu tiên',
                'data_calc': 'Tính toán số liệu', 'text_stats': 'Thống kê văn bản',
                'export_report': 'Lưu báo cáo cục bộ', 'wiki_search': 'Tìm Wikipedia'}
    tool_rows = '\n'.join(f"| {x['name']} | {meanings[x['name']]} | {'Có' if x['name'] in {'dedupe','data_calc','text_stats','export_report','wiki_search'} else 'Có sẵn'} |" for x in declarations)
    report = f'''# Day 03 — Research Agent: Báo cáo nộp bài

## Team

- Repo: dnphuc04/K5-L3-DAY03-DongNgocPhuc-2A202603399-ResearchAgentToolEval.
- Phân công: Phúc tối ưu prompt/tools và version log; A viết dedupe và unit test; B phân tích lỗi, 10 case nhóm và bằng chứng; UI Streamlit đã bổ sung tại app.py.
- Danh sách họ tên đầy đủ của A/B/C: cần trưởng nhóm bổ sung trước khi nộp; không suy đoán từ tên thư mục máy.
- Provider/model: OpenAI / gpt-4o-mini. Snapshot đo chuẩn: `{final['artifact_version']}`; xem kết quả bộ tools mở rộng cuối tại mục B3 bổ sung.

# PHẦN A — Giới thiệu agent

## A1. Agent làm được gì

Trợ lý nghiên cứu chọn nguồn web, mạng xã hội, paper và chính sách nội bộ; đọc tài liệu, loại bỏ nguồn trùng và trình bày bản tin. Agent hỏi lại khi thiếu dữ liệu và yêu cầu xác nhận trước khi gửi Telegram.

UI: http://localhost:8501 — chạy trên máy có server. Chưa có bằng chứng link public trong repo; localhost không phải link để máy khác truy cập.
Khởi động: `python -m streamlit run app.py --server.address 127.0.0.1 --server.port 8501`.
Hướng dẫn: `UI_README.md`. Model và các API lấy dữ liệu cần key riêng trong .env trên máy chạy; không nộp .env.

## A2. Tool agent có

| Tool | Chức năng | Tool mới? |
|---|---|---|
{tool_rows}

## A3. Câu hỏi demo

1. Lấy 3 tweet gần nhất của @NASA.
2. Tìm 4 tin tức web về robotics trong tuần này.
3. Tóm tắt bài báo này (chưa gửi URL) — kiểm tra agent hỏi lại.
4. Bỏ trùng URL, giữ mục đầu tiên: [{{"title":"A","url":"https://www.example.com/post/"}},{{"title":"A copy","url":"https://example.com/post?utm_source=demo#intro"}},{{"title":"B","url":"https://example.com/other"}}].
5. Sau khi tìm tin hôm nay, yêu cầu đổi sang tháng này nhưng giữ chủ đề và số lượng.

# PHẦN B — Chi tiết / Bằng chứng

## B1. Version Evidence

Nguồn đầy đủ: `artifacts/version_log.csv`, các snapshot trong `artifacts/versions/` và JSON trong runs/. Không coi kết quả của các suite khác nhau là cùng một phép đo.

| Version | Thay đổi/giả thuyết | Case accuracy (base) | Routing | Arguments | Run |
|---|---|---:|---:|---:|---|
{chr(10).join(version_rows)}

Baseline chính của nhóm là 65%; B có một lần chạy khác cùng artifact đạt 75% (`runs/v0_B_base_openai_20261110T103030701042.json`). Không thay thế/chọn baseline có lợi; hai lần chạy khác nhau chứng tỏ kết quả model có thể biến động. B2 phân tích lần chạy của B. Các bản v3.1–v3.3 có log và snapshot riêng; không xóa regression. Kết quả cuối 100% trên bộ hữu hạn chưa chứng minh tổng quát hóa.

## B2. Failure Analysis
{b2}
## B3. Team Eval Cases

10 case giữ nguyên giữa lần đo v2 và v3.4: 5 single turn + 5 multi turn, có G05 cho tool mới.

| Case | Loại | Expected calls/args | v2 | v3.4 |
|---|---|---|---|---|
{chr(10).join(case_rows)}

v2: 8/10, routing=100%, args=80%, multi=80%. v3.4: 10/10, routing/args/multi=100%, provider_error=0.
Run v2: `runs/v2_B_group_openai_20261110T111141081146.json`.
Run v3.4 của B: `runs/v3.4_B_group_openai_20261110T121028534135.json`.
So sánh: `analysis/B_v2_v3_4_rerun_comparison.csv`; đối chiếu dữ liệu: `analysis/B_v3_4_rerun_checks.json`.

G04 v2 hỏi đúng nhưng không ghi response_type=text tường minh; runtime có default đúng nên cần phân biệt lỗi chấm args và lỗi hành vi. G09 thiếu topic=news làm runtime dùng general, là lỗi chức năng. Cả hai đã pass tại v3.4.
G05 được kiểm tra input nguyên 3 mục và output giữ A/B, removed=1, item_count=2. Không đưa items dạng list object vào expected args vì harness sorted(list_of_dict) gây TypeError; lưu kiểm tra riêng. Query các case tìm kiếm đã đối chiếu là robotics. Multi turn trong eval chỉ chấm lượt cuối với lịch sử làm ngữ cảnh, khác với chạy chat nhiều lượt thật.

8 case trong run cuối của B có tool error do thiếu key lấy dữ liệu. Vì vậy PASS là bằng chứng routing/arguments, chưa phải lấy dữ liệu live thành công. Nhóm có smoke log riêng `runs/v0_tool_smoke.json`; không dùng smoke log cũ để khẳng định trạng thái key hiện tại.
Lần lỗi mạng `runs/v2_B_group_openai_20261110T111059265125.json` có measured_cases=0; được giữ để truy vết, không dùng làm điểm model.

## B4. Live Chat Evidence

Nguồn: `{live_name}`, artifact `{live['artifact_version']}`. Đây là 3 lượt kiểm tra được script gửi tới model thật, không phải log mô phỏng hoặc buổi người dùng thao tác UI; script: `scripts/submission_live_check.py`. Các transcript CLI/UI thực tế trước đó cũng giữ trong transcripts/.

| Lượt | Yêu cầu | Tool | Trạng thái |
|---|---|---|---|
{chr(10).join(live_rows)}

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
'''
    extended = []
    for suite in ('base', 'group'):
        paths = sorted((ROOT / 'runs').glob(f'v3.4-ui_B_{suite}_openai_*.json'))
        if paths:
            data = json.loads(paths[-1].read_text(encoding='utf-8'))
            extended.append((paths[-1], data))
    if extended:
        report += '\n## B3 bổ sung — Bộ tools mở rộng khi nộp\n\n'
        report += 'Sau commit a8f881e, thêm 4 tool làm thay đổi tools hash. Giữ nguyên dataset, prompt và mọi lần chạy; không chọn riêng kết quả cao.\n\n'
        for path, data in extended:
            s = data['summary']
            report += f"- {data['suite']}: {s['passed_cases']}/{s['total_cases']} PASS; artifact `{data['artifact_version']}`; `runs/{path.name}`.\n"
            for item in data['results']:
                if not item['result']['passed']:
                    report += f"  - {item['id']}: {'; '.join(item['result']['failures'])}.\n"
        report += '\nG08 của bộ tools mở rộng thiếu search_type tường minh; social_search mặc định Latest nên không đồng nhất với sai cách sắp xếp thực tế. Vẫn giữ FAIL theo cách chấm hiện tại. G04/G09 đã PASS. Unit test cuối: **124 passed, 0 failed, 0 skipped**.\n'
        report += 'Snapshot bộ mở rộng tại artifacts/versions/v3.4-ui/. UI hiện dùng bộ mở rộng; không gắn nhãn/hashes của snapshot cũ cho bộ này.\n'
    report_path.write_text(report, encoding='utf-8')
    snapshot = ROOT / 'artifacts/versions/v3.4-ui'
    snapshot.mkdir(parents=True, exist_ok=True)
    for name in ('system_prompt.md', 'tools.yaml'):
        (snapshot / name).write_bytes((ROOT / 'artifacts' / name).read_bytes())
    # Additional measurement row; do not rewrite the lead's experimental history.
    log_path = ROOT / 'artifacts/version_log.csv'
    run_name = 'runs/v3.4_B_group_openai_20261110T121028534135.json'
    with log_path.open(encoding='utf-8-sig', newline='') as f:
        rows = list(csv.DictReader(f))
    if not any(x['run_file'] == run_name for x in rows):
        row = dict.fromkeys(rows[0], '')
        row.update(version='v3.4', author='B', changed_artifact='none; independent group rerun',
                   artifact_version=final['artifact_version'], prompt_hash=final['prompt_hash'], tools_hash=final['tools_hash'],
                   reason='Verify G04/G09 fixes using unchanged 10-case B dataset; 8 tool execution errors due to missing keys',
                   hypothesis='v3.4 fixes explicit clarification args and preserves news topic across turns',
                   metric_before='v2 group case_accuracy=0.8', metric_after=json.dumps(final['summary']), run_file=run_name)
        with log_path.open('a', encoding='utf-8', newline='') as f:
            csv.DictWriter(f, fieldnames=list(row)).writerow(row)
    for path, data in extended:
        if any(x['run_file'] == 'runs/' + path.name for x in rows):
            continue
        row = dict.fromkeys(rows[0], '')
        row.update(version='v3.4-ui', author='submission verification', changed_artifact='tools.yaml: four additional team tools',
                   artifact_version=data['artifact_version'], prompt_hash=data['prompt_hash'], tools_hash=data['tools_hash'],
                   reason=f"Final expanded toolset; suite={data['suite']}; preserve all results including omitted optional args",
                   hypothesis='Expanded toolset retains research routing behavior', metric_before='See v3.4 snapshot runs',
                   metric_after=json.dumps(data['summary']), run_file='runs/' + path.name)
        with log_path.open('a', encoding='utf-8', newline='') as f:
            csv.DictWriter(f, fieldnames=list(row)).writerow(row)
    archive = ROOT.parent / 'ResearchAgent_Submission.zip'
    excluded = {'.venv', '__pycache__', '.pytest_cache', '.git', 'arxiv_papers'}
    files = []
    for path in ROOT.rglob('*'):
        rel = path.relative_to(ROOT)
        if not path.is_file() or any(x in excluded for x in rel.parts):
            continue
        if path.name.startswith('.env') and path.name != '.env.example':
            continue
        if path.suffix in {'.pyc', '.pyo'}:
            continue
        data = path.read_bytes()
        if re.search(rb'sk-(?:proj-|or-v1-)[A-Za-z0-9_-]{20,}', data):
            raise RuntimeError(f'Secret-like key detected in {rel}; archive not created')
        files.append(path)
    with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED) as z:
        for path in files:
            z.write(path, 'starter_v0/' + path.relative_to(ROOT).as_posix())
    with zipfile.ZipFile(archive) as z:
        assert not any('/.venv/' in x or x.endswith('/.env') for x in z.namelist())
        assert z.testzip() is None
    print(f'Report updated. Archive verified: {archive.name}; {len(files)} files.')


if __name__ == '__main__':
    main()
