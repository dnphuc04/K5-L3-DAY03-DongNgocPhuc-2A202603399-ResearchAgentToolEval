---
name: data_calc
track: bonus
kind: local_formatter
requires_env: []
inputs: [numbers, operation]
outputs: [result, operation, count]
side_effect: false
---
# data_calc

Tính toán các chỉ số thống kê cơ bản từ danh sách số liệu thu thập trong nghiên cứu.
Hỗ trợ các phép tính: summary, mean, sum, min, max, change.
Dùng khi người dùng yêu cầu tính trung bình, tổng hợp số liệu, hoặc tính tốc độ tăng trưởng.
