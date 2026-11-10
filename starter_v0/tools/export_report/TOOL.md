---
name: export_report
track: bonus
kind: action
requires_env: []
inputs: [filename, content, format_type]
outputs: [status, filepath, bytes_written]
side_effect: local_file_write
---
# export_report

Lưu báo cáo tổng hợp nghiên cứu hoặc bản tin ra file trên ổ đĩa nội bộ (thư mục reports/).
Hỗ trợ định dạng markdown hoặc json.
Dùng khi người dùng yêu cầu 'lưu ra file', 'export báo cáo', hoặc 'ghi lại kết quả vào file'.
