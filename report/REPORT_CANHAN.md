# Báo Cáo Cá Nhân — Lab 7: Embedding & Vector Store

**Họ tên:** Phạm Long Nhật (2A202602844)
**Nhóm:** TooSweet
**Ngày:** 20/9/2026

> **Nộp 1 bản / sinh viên.** Phần nhóm (lựa chọn tài liệu, thiết kế chiến lược, bộ câu hỏi đánh giá, demo) nộp chung 1 bản trong `REPORT_NHOM.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần cá nhân: 60** = Khởi động (5) + Hướng tiếp cận (10) + Hoàn thiện code (30) + Dự đoán độ tương tự (5) + Kết quả truy xuất của tôi (10).

---

## 1. Khởi động (Warm-up) — Cá nhân (5 điểm)

### Độ tương tự Cosine (Cosine Similarity) (Bài tập 1.1)

**Độ tương tự cosine cao (High cosine similarity) nghĩa là gì?**
> Hai vector chỉ gần như cùng một hướng trong không gian embedding, nghĩa là hai đoạn văn bản mang ý nghĩa gần nhau. Giá trị chạy từ -1 (ngược hướng) tới 1 (trùng hướng); 0 nghĩa là không liên quan.

**Ví dụ có độ tương tự CAO:**
- Câu A: "Thẻ tín dụng/ghi nợ: 7 - 14 ngày làm việc."
- Câu B: "Tiền hoàn về thẻ tín dụng mất khoảng hai tuần làm việc."
- Tại sao tương đồng: cùng nói về một phương thức hoàn tiền và cùng một khoảng thời gian, chỉ khác cách diễn đạt.

**Ví dụ có độ tương tự THẤP:**
- Câu A: "Thẻ tín dụng/ghi nợ: 7 - 14 ngày làm việc."
- Câu B: "Sản phẩm số và dịch vụ không áp dụng lý do trả hàng Đổi ý."
- Tại sao khác: một câu nói về thời gian hoàn tiền, câu kia nói về điều kiện được trả hàng — khác chủ đề dù cùng thuộc chính sách đổi trả.

**Tại sao độ tương tự cosine (cosine similarity) được ưu tiên hơn khoảng cách Euclid (Euclidean distance) cho text embeddings?**
> Cosine chỉ quan tâm hướng nên không bị độ dài vector chi phối, mà độ dài vector thường phản ánh độ dài văn bản chứ không phải nội dung. Khoảng cách Euclid sẽ coi một chunk dài và một chunk ngắn cùng chủ đề là xa nhau chỉ vì chênh lệch độ lớn.

### Bài toán tính toán Chunking (Bài tập 1.2)

**Tài liệu 10,000 ký tự, chunk_size=500, overlap=50. Bao nhiêu chunks?**
> Bước nhảy giữa hai chunk liên tiếp là `step = chunk_size - overlap = 500 - 50 = 450`.
> Các vị trí bắt đầu là 0, 450, 900, ..., 9900 (vòng lặp dừng khi `start + 500 >= 10000`).
> Số chunk = `ceil((10000 - 500) / 450) + 1 = ceil(21.11) + 1 = 22 + 1 = 23`.
> Đáp án: **23 chunks**, chunk cuối chỉ dài 100 ký tự. Đã kiểm chứng bằng `FixedSizeChunker(chunk_size=500, overlap=50).chunk("a" * 10000)`.

**Nếu độ chồng chéo (overlap) tăng lên 100, số lượng chunk thay đổi thế nào? Tại sao muốn độ chồng chéo nhiều hơn?**
> `step` giảm còn 400 nên số chunk tăng từ 23 lên **25** (đã kiểm chứng bằng code). Overlap lớn hơn giúp một câu bị cắt ngang vẫn xuất hiện trọn vẹn ở ít nhất một chunk, tránh mất ngữ cảnh ngay tại ranh giới — đổi lại tốn thêm chi phí lưu trữ và embedding.

---

## 2. Hướng tiếp cận của tôi (My Approach) — Cá nhân (10 điểm)

Giải thích cách tiếp cận của bạn khi lập trình (implement) các phần chính trong gói `src`.

### Các hàm chia nhỏ (Chunking Functions)

**`SentenceChunker.chunk`** — hướng tiếp cận:
> Tôi tách câu bằng `re.split` với lookbehind `(?<=[.!?])[ \n]+`, tức cắt tại khoảng trắng hoặc xuống dòng ngay sau dấu kết câu. Dùng lookbehind thay vì `split(". ")` để giữ lại dấu chấm cuối câu và gộp được cả 4 trường hợp `. `, `! `, `? `, `.` + xuống dòng vào một biểu thức duy nhất.
> Edge case: text rỗng hoặc chỉ có khoảng trắng trả về `[]`; mỗi mảnh đều `.strip()` và bỏ mảnh rỗng để khoảng trắng thừa không sinh chunk rác; `max_sentences_per_chunk` đã được `max(1, ...)` trong `__init__` nên bước nhảy không bao giờ bằng 0.

**`RecursiveChunker.chunk` / `_split`** — hướng tiếp cận:
> `_split` nhận đoạn text cùng danh sách separator còn lại. Nó cắt theo separator đầu tiên rồi gom dần các mảnh vào một buffer chừng nào buffer còn `<= chunk_size`; khi buffer sắp vượt ngưỡng thì xả buffer ra và đệ quy xuống separator kế tiếp cho phần vẫn còn quá dài. Nhờ vậy ranh giới ngữ nghĩa lớn (đoạn văn) được ưu tiên giữ, chỉ khi bất khả kháng mới cắt ở mức nhỏ hơn.
> Base case có ba nhánh: (1) đoạn rỗng trả về `[]`; (2) đoạn đã `<= chunk_size` thì trả nguyên vẹn; (3) hết separator hoặc gặp separator rỗng `""` thì `_hard_split` cắt cứng theo `chunk_size`. Nhánh (3) là thứ bảo đảm hàm luôn dừng, kể cả khi truyền `separators=[]`.

### Lớp EmbeddingStore

**`add_documents` + `search`** — hướng tiếp cận:
> Mỗi `Document` được `_make_record` chuẩn hóa thành một dict gồm `id`, `doc_id`, `content`, `metadata`, `embedding`, rồi nối vào list `self._store`. Điểm đáng lưu ý: `_make_record` tự chèn `metadata["doc_id"] = doc.id` nếu chưa có, vì `delete_document` cần khóa này trong khi test lại tạo `Document` với `metadata={}`.
> `search` ủy quyền cho `_search_records`: embed câu hỏi đúng một lần, tính `_dot(query_embedding, record_embedding)` cho từng record, sắp xếp giảm dần rồi cắt `top_k`. Dùng tích vô hướng là đủ vì các embedder trong lab đều trả vector đã chuẩn hóa — khi đó tích vô hướng bằng đúng cosine.

**`search_with_filter` + `delete_document`** — hướng tiếp cận:
> Lọc **trước**, rồi mới xếp hạng. Nếu xếp hạng trước rồi lọc sau thì `top_k` sẽ bị các chunk sai `audience` chiếm chỗ, và kết quả trả về có thể ít hơn `top_k` dù kho vẫn còn chunk hợp lệ. Cả hai đường đều đi chung `_search_records`, nên khi `metadata_filter=None` kết quả trùng khít với `search`.
> `delete_document` dựng lại list chỉ gồm record có `metadata["doc_id"] != doc_id`. So sánh độ dài trước/sau để biết có xóa được gì không: bằng nhau thì trả `False`, ngắn đi thì gán lại `self._store` và trả `True`. Cách này xóa mọi chunk cùng một `doc_id` chỉ trong một lượt duyệt.

### Tác tử KnowledgeBaseAgent

**`answer`** — hướng tiếp cận:
> `answer` lấy `top_k` chunk qua `store.search`, nối phần `content` bằng dòng trống rồi đưa vào `_build_prompt`. Prompt gồm 4 phần tách bạch: câu định vai trò, khối `Ngữ cảnh:`, khối `Câu hỏi:`, và một câu ràng buộc yêu cầu chỉ trả lời dựa trên ngữ cảnh và phải nói rõ khi thiếu thông tin — đây là phần chống bịa (hallucination).
> Tôi tách `_build_prompt` thành hàm riêng để in prompt ra kiểm tra mà không phải gọi LLM. Nếu không truy xuất được chunk nào, ngữ cảnh được thay bằng `(không tìm thấy tài liệu liên quan)` thay vì để rỗng, tránh việc mô hình tự bịa khi không thấy ràng buộc nào.

---

## 3. Hoàn thiện code (Core Implementation) — Cá nhân (30 điểm)

Vượt qua bộ kiểm thử là điều kiện tính điểm phần này.

### Kết Quả Kiểm Thử (Test Results)

```
$ pytest tests/ -q
..........................................                               [100%]
42 passed in 0.04s
```

**Số lượng bài test vượt qua (pass):** 42 / 42

---

## 4. Dự đoán độ tương tự (Similarity Predictions) — Cá nhân (5 điểm)

Chạy bằng `LocalEmbedder` (`paraphrase-multilingual-MiniLM-L12-v2`), ngưỡng phân loại cao/thấp đặt ở **0.5**.

| Cặp | Câu A | Câu B | Dự đoán | Điểm thực tế | Đúng? |
|------|-----------|-----------|---------|--------------|-------|
| 1 | Thẻ tín dụng/ghi nợ: 7 - 14 ngày làm việc. | Tiền hoàn về thẻ tín dụng mất khoảng hai tuần làm việc. | cao | 0.727 | Đúng |
| 2 | Người mua có 7 ngày để gửi yêu cầu trả hàng. | Người bán phải phản hồi khiếu nại trong 2 ngày lịch. | thấp | 0.506 | Sai |
| 3 | Sản phẩm số và dịch vụ không được trả hàng. | Thực phẩm tươi sống không áp dụng lý do trả hàng Đổi ý. | cao | 0.204 | Sai |
| 4 | Dung lượng video bằng chứng tối đa là 100 MB. | Ví ShopeePay hoàn tiền trong vòng 24 giờ. | thấp | 0.114 | Đúng |
| 5 | Return and refund policy for buyers on Shopee. (EN) | Chính sách trả hàng và hoàn tiền dành cho người mua trên Shopee. (VI) | cao | 0.768 | Đúng |

**Dự đoán đúng: 3/5**

**Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn ý nghĩa?**
> Cặp 3 bất ngờ nhất: hai câu cùng diễn đạt một quan hệ ("nhóm sản phẩm X bị hạn chế trả hàng") nhưng chỉ đạt 0.204 — thấp hơn cả cặp 2 vốn khác chủ thể. Embedding bám vào **chủ đề bề mặt** (sản phẩm số/dịch vụ so với thực phẩm tươi sống là hai lĩnh vực khác hẳn nhau) chứ không bám vào quan hệ logic chung giữa hai câu; mô hình đo "nói về cùng thứ gì" chứ không đo "nói cùng một luật".
> Cặp 2 cho bài học trực tiếp cho retrieval: câu của người mua và câu của người bán đạt 0.506, tức gần như không phân biệt được bằng embedding. Đây chính là lý do `search_with_filter` với `metadata_filter={"audience": ...}` tồn tại — có những khác biệt quan trọng mà không gian vector đơn giản là không mã hóa, phải xử lý bằng metadata.
> Cặp 5 đạt 0.768 xác nhận mô hình đa ngữ hoạt động: câu hỏi tiếng Anh vẫn truy xuất được corpus tiếng Việt, nên không cần dịch trước khi đưa vào kho.

---

## 5. Kết quả truy xuất của tôi (Competition Results) — Cá nhân (10 điểm)

Chạy **5 câu hỏi đánh giá của nhóm** trên mã nguồn cá nhân của bạn trong gói `src`. **5 câu hỏi này phải trùng với các thành viên cùng nhóm** (xem `REPORT_NHOM.md`).

Chiến lược của tôi: **`HeadingChunker`** — chia theo tiêu đề/mục của điều khoản gốc (nhận cả `#` Markdown lẫn mục đánh số `1.` / `1.1`), mỗi chunk gắn thêm chuỗi tiêu đề cha dạng `Tài liệu > Mục > Mục con`. Corpus 10 tài liệu cho ra **60 chunk**, trung bình 681 ký tự. Embedder: `LocalEmbedder`.

| # | Câu hỏi (Query) | Top-1 Chunk truy xuất được (tóm tắt) | Điểm Score | Có liên quan không? (Relevant) | Câu trả lời của Agent (tóm tắt) |
|---|-------|--------------------------------|-------|-----------|------------------------|
| 1 | Sau khi Shopee chấp nhận yêu cầu THHT, người mua phải gửi trả sản phẩm trong bao lâu? | `Điều kiện và thời hạn trả hàng > 1. Điều kiện Trả hàng/Hoàn tiền của Shopee` | 0.825 | **Không** — chunk đúng nằm ở hạng 13/60 (score 0.717) | Không trả lời được từ top-3; chunk chứa "6 ngày" không lọt top-3 |
| 2 | Với đơn hàng thanh toán bằng thẻ tín dụng/ghi nợ, người mua nhận tiền hoàn trong bao lâu? | `Thời gian nhận tiền hoàn > Thẻ tín dụng/ghi nợ` | 0.824 | Có | 7 - 14 ngày làm việc (tùy theo ngân hàng) |
| 3 | Khi tải bằng chứng cho yêu cầu THHT, dung lượng video tối đa là bao nhiêu? | `Bằng chứng khi yêu cầu trả hàng > 4. Quy định về bằng chứng` | 0.813 | Có | Không quá 100 MB/video (tối đa 1 phút) |
| 4 | Những nhóm sản phẩm nào không áp dụng lý do trả hàng "Đổi ý"? | `Sản phẩm hạn chế trả hàng` | 0.554 | Có | Sức khỏe/Vệ sinh & Đồ cá nhân; Thực phẩm & Hàng mau hỏng; Hàng đặc thù trong vận chuyển; Sản phẩm số và dịch vụ |
| 5 | Nếu không đồng ý với quyết định hoàn tiền, thời hạn phản hồi của người bán là bao lâu? (lọc `audience: seller`) | `Quyền và trách nhiệm của người bán khi trả hàng > Thời hạn phản hồi của người bán` | 0.783 | Có | Phản hồi trong vòng 2 ngày lịch kể từ ngày nhận thông báo |

**Bao nhiêu câu hỏi trả về chunk có liên quan trong top-3?** **4 / 5** (Top-1 đúng: 4/5)

> Cột "Câu trả lời của Agent" ghi thông tin rút ra từ chunk top-1, không phải văn bản do LLM sinh: lab chỉ đi kèm `demo_llm` trong `main.py` — một hàm giả lập in lại đoạn đầu của prompt — nên không có mô hình sinh thật để trích dẫn.

**Phân tích câu trượt (Q1).** Chunk đúng là `Quy trình xử lý yêu cầu trả hàng > 3. Phân loại phương án xử lý Trả hàng/ Hoàn tiền của Shopee`, chứa câu "hoàn tất việc gửi trả hàng... trong vòng 6 ngày". Nó xếp hạng 13/60 với score 0.717, không quá xa top-1 (0.825). Nguyên nhân nằm ở chính điểm mạnh của chiến lược: breadcrumb tiêu đề được ghép vào đầu mỗi chunk, nhưng tiêu đề "Phân loại phương án xử lý" **không hề nhắc tới thời hạn**, trong khi ba chunk đứng đầu đều có chữ "điều kiện và thời hạn" ngay trên tiêu đề. Breadcrumb giúp chunk tự mô tả được ngữ cảnh, nhưng khi tiêu đề mô tả sai trọng tâm của phần thân thì nó lại kéo embedding đi chệch hướng.

**Đề xuất cải thiện cho câu trượt (Bài tập 3.5).** Tôi chạy A/B tắt breadcrumb (`include_parent_headings=False`) trên cùng corpus: chunk đúng của câu 1 lên từ hạng 13/60 lên hạng 9/60 và câu 1 được 1 điểm thay vì 0 — xác nhận đúng chẩn đoán trên. Nhưng câu 4 lại rơi từ 2 điểm xuống 1, tổng vẫn 8/10. Nên hướng sửa đúng không phải tắt breadcrumb, mà là **embed riêng phần thân chunk còn breadcrumb chỉ dùng khi hiển thị** — giữ được ngữ cảnh cho agent mà không để tiêu đề làm nhiễu vector. Hướng thứ hai đã có bằng chứng: `RecursiveChunker` (chunk_size=500) lấy trọn 2 điểm ở chính câu 1 này, nên kết hợp hai kho rồi trộn thứ hạng sẽ ăn được cả hai phía. Tôi đã loại phương án tăng `top_k` vì chunk đúng ở hạng 13, phải nâng `top_k` lên 13 mới cứu được và như vậy kéo quá nhiều nhiễu vào ngữ cảnh.

**Đánh đổi của chiến lược heading.** Điểm được: chunk bám đúng ranh giới điều khoản, không cắt ngang câu, và chunk top-1 của Q2 chỉ dài 171 ký tự nên câu trả lời cực kỳ sắc. Điểm mất: chất lượng phụ thuộc hoàn toàn vào chất lượng tiêu đề của nguồn. Hai tài liệu (`shopee-instant-refund`, `shopee-return-restrictions`) không có mục nào nên vẫn là một chunk nguyên khối hơn 1200 ký tự, và `shopee-refund-timeline` ban đầu là bảng bị crawler làm phẳng, phải làm sạch tay (thêm heading cho từng phương thức hoàn tiền) mới tách được từ 1 chunk thành 11 chunk.

**Điều hay nhất tôi học được từ thành viên khác / nhóm khác (qua demo):**
> *Viết 2-3 câu:*

---

## Tự Đánh Giá (Phần Cá Nhân)

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Khởi động (Warm-up) | 4/ 5 |
| Hướng tiếp cận của tôi (My Approach) | 8/ 10 |
| Hoàn thiện code (Core Implementation — tests) | 30/ 30 |
| Dự đoán độ tương tự (Similarity Predictions) | 4/ 5 |
| Kết quả truy xuất của tôi (Competition Results) | 8/ 10 |
| **Tổng phần cá nhân** | **54/ 60** |
