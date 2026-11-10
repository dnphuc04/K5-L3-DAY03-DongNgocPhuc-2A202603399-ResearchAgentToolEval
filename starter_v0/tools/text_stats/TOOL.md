---
name: text_stats
track: bonus
kind: local_formatter
requires_env: []
inputs: [text]
outputs: [word_count, char_count, sentence_count, reading_time_min, top_words]
side_effect: false
---
# text_stats

Phân tích số liệu thống kê cơ bản của văn bản (đếm từ, đếm câu, thời gian đọc ước tính và từ khóa nổi bật).
Hữu ích khi cần tóm lược độ dài và mật độ thông tin của tài liệu nghiên cứu.
