---
name: wiki_search
track: bonus
kind: live_api
provider: Wikipedia
requires_env: []
inputs: [query, limit]
outputs: [items, query]
side_effect: false
---
# wiki_search

Tìm kiếm thông tin bách khoa toàn thư trên Wikipedia.
Dùng khi người dùng cần tra cứu định nghĩa, tiểu sử nhân vật, lịch sử, hoặc khái niệm khoa học chuẩn mực.
Không dùng cho tin tức nóng trong ngày (dùng lookup topic=news thay thế).
