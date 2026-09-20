# Báo Cáo Nhóm — Lab 7: Embedding & Vector Store

**Nhóm:** TooSweet
**Thành viên:** [Họ tên từng thành viên]
**Ngày:** [Ngày nộp]

> **Nộp 1 bản / nhóm.** Phần cá nhân (hướng tiếp cận, kết quả riêng, dự đoán…) mỗi thành viên nộp riêng trong `REPORT_CANHAN.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần nhóm: 40** = Lựa chọn tài liệu (10) + Thiết kế chiến lược (15) + Chất lượng truy xuất (10) + Thuyết trình (5).

---

## 1. Lựa chọn tài liệu (Document Set Quality) — Nhóm (10 điểm)

### Chủ đề (Domain) & Lý Do Chọn

**Chủ đề:** Chính sách Trả hàng/Hoàn tiền của sàn thương mại điện tử Shopee Việt Nam (nguồn: Trung tâm trợ giúp `help.shopee.vn`).

**Tại sao nhóm chọn chủ đề này?**
> Chính sách đổi trả là loại văn bản có cấu trúc điều khoản rõ ràng, nhiều con số cụ thể (thời hạn, dung lượng, phí) nên câu trả lời chuẩn kiểm chứng được tuyệt đối — không phải diễn giải cảm tính. Đây là điều kiện cần để chấm điểm truy xuất một cách khách quan.
> Chủ đề này còn có sẵn hai đối tượng đọc tách bạch là người mua và người bán, cho phép gán `audience` làm trường lọc thật sự có việc để làm, đúng yêu cầu riêng của lớp L3B.
> Cuối cùng, toàn bộ nội dung nằm ở trang trợ giúp công khai, không cần đăng nhập, nên thỏa ràng buộc quản trị dữ liệu trong `docs/DATA_COLLECTION.md`.

### Danh sách tài liệu (Data Inventory)

| # | Tên tài liệu | Nguồn (Source URL) | Ngày lấy / Phiên bản | Số ký tự | Metadata đã gán |
|---|--------------|------------|--------------------|----------|-----------------|
| 1 | Chính sách trả hàng dành cho người mua | `help.shopee.vn/portal/4/article/77251` | 2026-09-20 / 2026-03-11 | 3.655 | `audience: buyer`, `category: return-policy`, `language: vi` |
| 2 | Quyền và trách nhiệm của người bán khi trả hàng | `help.shopee.vn/portal/4/article/77251` | 2026-09-20 / 2026-03-11 | 2.725 | `audience: seller`, `category: return-policy`, `language: vi` |
| 3 | Điều kiện và thời hạn trả hàng | `help.shopee.vn/portal/4/article/188931` | 2026-09-20 / not-stated | 6.203 | `audience: buyer`, `category: return-conditions`, `language: vi` |
| 4 | Hướng dẫn gửi yêu cầu trả hàng | `help.shopee.vn/portal/4/article/79233` | 2026-09-20 / not-stated | 2.367 | `audience: buyer`, `category: return-request`, `language: vi` |
| 5 | Quy trình xử lý yêu cầu trả hàng | `help.shopee.vn/portal/4/article/190242` | 2026-09-20 / not-stated | 7.982 | `audience: buyer`, `category: return-process`, `language: vi` |
| 6 | Bằng chứng khi yêu cầu trả hàng | `help.shopee.vn/portal/4/article/79467` | 2026-09-20 / not-stated | 3.331 | `audience: buyer`, `category: return-evidence`, `language: vi` |
| 7 | Phương thức và phí gửi hàng hoàn trả | `help.shopee.vn/portal/4/article/189477` | 2026-09-20 / not-stated | 5.811 | `audience: buyer`, `category: return-shipping`, `language: vi` |
| 8 | Thời gian nhận tiền hoàn | `help.shopee.vn/portal/4/article/189473` | 2026-09-20 / not-stated | 4.049 | `audience: buyer`, `category: refund-timeline`, `language: vi`, `cleaning: manual-table-restructured` |
| 9 | Sản phẩm hạn chế trả hàng | `help.shopee.vn/portal/4/article/79465` | 2026-09-20 / not-stated | 1.354 | `audience: buyer`, `category: return-restrictions`, `language: vi` |
| 10 | Phản hồi đề xuất hoàn tiền ngay | `help.shopee.vn/portal/4/article/190387` | 2026-09-20 / not-stated | 1.224 | `audience: buyer`, `category: instant-refund`, `language: vi` |

Tổng 10 tài liệu, 38.701 ký tự nội dung (không tính front matter). Kiểm kê đầy đủ ở `data/shopee-returns/sources.csv`; danh sách URL để tái lập lượt crawl ở `data/urls.csv`.

> **Ghi chú về tài liệu 1 và 2.** Trang gốc `article/77251` gộp điều khoản cho cả người mua lẫn người bán. Nhóm tách thành hai file, mỗi file một `audience`, theo đúng hướng dẫn tại `docs/DATA_COLLECTION.md` §4 — nếu để chung thì `search_with_filter()` không có gì để lọc.
>
> **Ghi chú về tài liệu 8.** Bản crawl gốc là một bảng bị công cụ trích xuất làm phẳng thành các dòng rời rạc, không còn tiêu đề nào. Nhóm làm sạch tay, tái cấu trúc thành heading cho từng phương thức hoàn tiền; đã đối chiếu lại toàn bộ mốc thời gian để chắc chắn không con số nào bị thêm, sửa hay mất. Trường `cleaning: manual-table-restructured` đánh dấu việc này.

**Danh sách kiểm tra quản trị dữ liệu (Data governance checklist):**
- [x] Tập tài liệu (Corpus) chỉ chứa nguồn công khai/được phép dùng và không chứa dữ liệu cá nhân, thông tin đăng nhập hoặc tài liệu nội bộ. Toàn bộ 10 trang đều mở công khai trên Trung tâm trợ giúp Shopee, không trang nào nằm sau đăng nhập.
- [x] Mỗi tài liệu có `source_url`, `retrieved_at`, `document_version` (hoặc ngày hiệu lực) trong metadata. Đã kiểm bằng script: 10/10 file đủ 6 trường bắt buộc, `doc_id` trùng tên file, `sources.csv` khớp một-một với thư mục.

### Cấu trúc Metadata (Metadata Schema)

| Trường metadata | Kiểu | Ví dụ giá trị | Tại sao hữu ích cho truy xuất (retrieval)? |
|----------------|------|---------------|-------------------------------|
| `audience` | enum `buyer` / `seller` | `seller` | Trường lọc chính. Embedding gần như không phân biệt được câu của người mua với câu của người bán (nhóm đo được 0.506 giữa hai câu như vậy), nên phải lọc bằng metadata. |
| `category` | chuỗi | `refund-timeline` | Thu hẹp theo chủ đề con khi câu hỏi đã rõ loại (thời gian hoàn tiền, điều kiện, bằng chứng...), tránh chunk cùng từ khóa nhưng khác mục đích. |
| `language` | mã ISO | `vi` | Cho phép mở rộng corpus sang tiếng Anh mà không trộn lẫn; hiện cả 10 tài liệu đều `vi`. |
| `source_url` | URL | `help.shopee.vn/portal/4/article/77251` | Truy vết nguồn để agent trích dẫn và để kiểm chứng câu trả lời chuẩn. |
| `retrieved_at` | ngày `YYYY-MM-DD` | `2026-09-20` | Biết dữ liệu cũ tới mức nào; chính sách sàn thay đổi thường xuyên. |
| `document_version` | ngày hiệu lực hoặc `not-stated` | `2026-03-11` | Phân biệt phiên bản điều khoản. Dùng `not-stated` khi nguồn không nêu — không bịa số hiệu. |
| `doc_id` | chuỗi không dấu | `shopee-return-policy-seller` | Khóa để `delete_document()` xóa toàn bộ chunk của một tài liệu trong một lượt. |

---

## 2. Thiết kế chiến lược (Strategy Design) — Nhóm (15 điểm)

> Mỗi thành viên thử **một chiến lược khác nhau** trên cùng bộ tài liệu; nhóm tổng hợp và so sánh ở đây.

### Phân tích đường cơ sở (Baseline Analysis)

Chạy `ChunkingStrategyComparator().compare()` trên 2-3 tài liệu:

Chạy `ChunkingStrategyComparator().compare(text, chunk_size=500)` trên 3 tài liệu đại diện. Cột cuối là đánh giá định tính khi đọc trực tiếp các chunk sinh ra.

| Tài liệu | Chiến lược (Strategy) | Số lượng Chunk | Độ dài trung bình | Giữ được ngữ cảnh không? |
|-----------|----------|-------------|------------|-------------------|
| Chính sách trả hàng cho người mua (3.655 ký tự) | FixedSizeChunker (`fixed_size`) | 8 | 456 | Không — cắt giữa câu, nhiều chunk mở đầu bằng nửa vế |
| | SentenceChunker (`by_sentences`) | 11 | 330 | Một phần — câu trọn vẹn nhưng mất mục cha, không biết điều khoản nào |
| | RecursiveChunker (`recursive`) | 10 | 363 | Khá — bám ranh giới đoạn, hiếm khi cắt giữa câu |
| | **HeadingChunker (chiến lược của nhóm)** | **6** | **609** | **Tốt — trùng khít ranh giới mục, có breadcrumb tiêu đề cha** |
| Phương thức và phí gửi hàng hoàn trả (5.811 ký tự) | FixedSizeChunker (`fixed_size`) | 12 | 484 | Không |
| | SentenceChunker (`by_sentences`) | 9 | 643 | Một phần — chunk dài vì nhiều câu ghép |
| | RecursiveChunker (`recursive`) | 14 | 413 | Khá |
| | **HeadingChunker** | **10** | **581** | **Tốt — tách đúng các mục 1.1 đến 3** |
| Thời gian nhận tiền hoàn (4.049 ký tự) | FixedSizeChunker (`fixed_size`) | 9 | 449 | Không — cắt ngang bảng, một chunk lẫn nhiều phương thức |
| | SentenceChunker (`by_sentences`) | 10 | 401 | Kém — bảng đã làm phẳng nên "câu" là các dòng rời rạc |
| | RecursiveChunker (`recursive`) | 9 | 448 | Kém — cùng lý do |
| | **HeadingChunker** | **11** | **387** | **Tốt — mỗi phương thức hoàn tiền một chunk, sau khi làm sạch tay** |

**Nhận xét đường cơ sở.** Ba chiến lược có sẵn cho số chunk và độ dài khá giống nhau (8–14 chunk, 330–643 ký tự) vì cả ba đều chia theo độ dài hoặc dấu câu — tức đều mù với cấu trúc điều khoản. Khác biệt chỉ lộ ra khi đọc nội dung chunk: `fixed_size` cắt giữa câu, còn `by_sentences` và `recursive` tuy giữ câu trọn vẹn nhưng chunk không mang thông tin nó thuộc mục nào, nên khi truy xuất ra một đoạn nói "trong vòng 6 ngày" thì không biết 6 ngày cho việc gì.

### Chiến lược của từng thành viên

> Mỗi thành viên điền một khối dưới đây (copy thêm nếu nhóm có nhiều hơn 3 người).

**Thành viên 1 — Phạm Long Nhật**
- **Loại chiến lược:** custom — `HeadingChunker` (chia theo tiêu đề/mục)
- **Mô tả & lý do chọn cho chủ đề này:** Văn bản chính sách vốn đã được soạn theo điều khoản đánh số, nên ranh giới ngữ nghĩa tự nhiên nhất chính là tiêu đề mục — không phải 500 ký tự hay 3 câu. Chunker nhận cả tiêu đề Markdown (`#` đến `######`) lẫn mục đánh số (`1.`, `1.1`, `2.3.1.`), vì crawler chỉ sinh đúng một `# tiêu đề` cho mỗi trang còn mục của điều khoản bị đổ xuống thành dòng văn bản thường — nếu chỉ bắt `#` thì 8/10 tài liệu sẽ ra đúng một chunk, tức không chia nhỏ gì cả.
- **Điểm khác biệt chính:** mỗi chunk được ghép thêm chuỗi tiêu đề cha dạng `Tài liệu > Mục > Mục con`, để một chunk lẻ vẫn tự nói được nó thuộc điều khoản nào. Corpus 10 tài liệu cho ra 60 chunk, trung bình 681 ký tự.
- **Code snippet:**
```python
_ATX_HEADING = re.compile(r"^(#{1,6})\s+(\S.*)$")
_NUMBERED_HEADING = re.compile(r"^(\d+(?:\.\d+)+\.?|\d+\.)\s+(\S.*)$")


class HeadingChunker:
    def __init__(self, include_parent_headings: bool = True) -> None:
        self.include_parent_headings = include_parent_headings

    def _heading(self, line: str) -> tuple[int, str] | None:
        atx = _ATX_HEADING.match(line)
        if atx:
            return len(atx.group(1)), atx.group(2).strip()
        numbered = _NUMBERED_HEADING.match(line)
        if numbered:
            # muc danh so nam thap hon tieu de ATX cung do sau mot bac
            return numbered.group(1).rstrip(".").count(".") + 2, line.strip()
        return None

    def chunk(self, text: str) -> list[str]:
        if not text or not text.strip():
            return []
        sections: list[tuple[int, str, list[str]]] = []
        preamble: list[str] = []
        for line in text.splitlines():
            heading = self._heading(line)
            if heading is None:
                (sections[-1][2] if sections else preamble).append(line)
            else:
                sections.append((heading[0], heading[1], []))

        chunks: list[str] = []
        if preamble and "".join(preamble).strip():
            chunks.append("\n".join(preamble).strip())

        trail: list[tuple[int, str]] = []
        for level, title, body in sections:
            trail = [item for item in trail if item[0] < level]
            trail.append((level, title))
            heading_line = " > ".join(t for _, t in trail) if self.include_parent_headings else title
            content = "\n".join(body).strip()
            chunks.append(f"{heading_line}\n\n{content}" if content else heading_line)
        return chunks
```

> **Một lỗi đã gặp và sửa, đáng nói trong demo.** Biểu thức nhận mục đánh số lúc đầu là `^(\d+(?:\.\d+)*)\.?\s+`, khớp mọi dòng mở đầu bằng số và khoảng trắng. Tài liệu "Thời gian nhận tiền hoàn" là bảng đã làm phẳng nên có nhiều dòng dạng `7 - 14 ngày làm việc (tùy theo ngân hàng)` — những dòng này bị nhận nhầm thành tiêu đề mục số 7, sinh ra 9 chunk rác. Siết lại thành `^(\d+(?:\.\d+)+\.?|\d+\.)\s+` (bắt buộc có dấu chấm hoặc nhiều cấp) thì hết.

**Thành viên 2 — [Tên]**
- **Loại chiến lược:**
- **Mô tả & lý do chọn:**
- **Code snippet (nếu custom):**

**Thành viên 3 — [Tên]**
- **Loại chiến lược:**
- **Mô tả & lý do chọn:**
- **Code snippet (nếu custom):**

### So Sánh Giữa Các Thành Viên

| Thành viên | Chiến lược (Strategy) | Điểm truy xuất (/10) | Điểm mạnh | Điểm yếu |
|-----------|----------|----------------------|-----------|----------|
| | | | | |
| | | | | |
| | | | | |

**Chiến lược nào tốt nhất cho chủ đề này? Tại sao?**
> *Viết 2-3 câu — đây là phần được đánh giá cao nhất (khả năng suy nghĩ & giải thích):*

---

## 3. Câu hỏi đánh giá & Chất lượng truy xuất (Retrieval Quality) — Nhóm (10 điểm)

### Câu hỏi đánh giá & Câu trả lời chuẩn (nhóm thống nhất)

> **Đúng 5 câu hỏi**, đa dạng, có thể kiểm chứng; **ít nhất 1 câu** cần lọc metadata mới trả lời tốt. Đây là bộ câu hỏi chung cho mọi thành viên chạy.

| # | Câu hỏi (Query) | Câu trả lời chuẩn (Gold Answer) | Chunk nào chứa thông tin? |
|---|-------|-------------------------------|--------------------------|
| 1 | Sau khi Shopee chấp nhận yêu cầu Trả hàng & Hoàn tiền, người mua phải gửi trả sản phẩm trong bao lâu? | "Nếu Shopee đồng ý cho bạn Trả hàng & Hoàn tiền: Bạn cần chọn hình thức trả hàng và hoàn tất việc gửi trả hàng về kho Shopee/Người bán trong vòng **6 ngày** kể từ thời điểm nhận được thông báo gửi trả hàng từ Shopee." | `shopee-return-process`, mục `3. Phân loại phương án xử lý Trả hàng/ Hoàn tiền của Shopee` |
| 2 | Với đơn hàng thanh toán bằng thẻ tín dụng/ghi nợ, người mua nhận tiền hoàn trong bao lâu? | "Thẻ tín dụng/ghi nợ: **7 - 14 ngày làm việc** (tùy theo ngân hàng)." | `shopee-refund-timeline`, mục `Thẻ tín dụng/ghi nợ` |
| 3 | Khi tải bằng chứng cho yêu cầu Trả hàng/Hoàn tiền, dung lượng video tối đa được Shopee quy định là bao nhiêu? | "Dung lượng tối đa: Hình ảnh: Không quá 5MB/ảnh. Video: **Không quá 100 MB/video** (tối đa 1 phút)." | `shopee-return-evidence`, mục `4. Quy định về bằng chứng` |
| 4 | Những nhóm sản phẩm nào không áp dụng lý do trả hàng "Đổi ý"? | "Đối với nhóm sản phẩm này, Shopee không áp dụng lý do trả hàng 'Đổi ý (Sản phẩm còn nguyên tem, nhãn mác, bao bì)'." Bốn nhóm được liệt kê: "Sức khỏe, Vệ sinh & Đồ cá nhân", "Thực phẩm & Hàng mau hỏng", "Hàng đặc thù trong vận chuyển", "Sản phẩm số và dịch vụ". | `shopee-return-restrictions`, chunk duy nhất của tài liệu |
| 5 | Nếu không đồng ý với quyết định hoàn tiền, thời hạn phản hồi của người bán là bao lâu? | "Người Bán cần **phản hồi trong vòng 2 ngày lịch** kể từ ngày nhận thông báo nếu không đồng ý với quyết định hoàn tiền; chưa nhận được sản phẩm hoàn trả; sản phẩm không thuộc trường hợp được hoàn; hoặc sản phẩm bị hư hỏng, mất mát trong quá trình hoàn trả." | `shopee-return-policy-seller`, mục `Thời hạn phản hồi của người bán` — **cần `metadata_filter={"audience": "seller"}`** |

Cả 5 câu trả lời chuẩn đã được đối chiếu ngược lại corpus bằng `grep`, trích nguyên văn, không câu nào là suy đoán chính sách.

### Tổng hợp chất lượng truy xuất của nhóm

> Cách chấm (theo `docs/SCORING.md`): **2 điểm/câu** — top-3 chứa chunk liên quan + agent trả lời đúng (2), có liên quan nhưng thiếu/không ở top-1 (1), không có trong top-3 (0).

| # | Câu hỏi | Chiến lược tốt nhất cho câu này | Có chunk liên quan trong top-3? | Ghi chú |
|---|---------|-------------------------------|-------------------------------|---------|
| 1 | | | | |
| 2 | | | | |
| 3 | | | | |
| 4 | | | | |
| 5 | | | | |

**Lọc bằng metadata có giúp ích không? Ở câu hỏi nào?**
> Có, rõ nhất ở câu 5 — câu duy nhất hỏi về nghĩa vụ của người bán. Với `metadata_filter={"audience": "seller"}`, không gian tìm kiếm thu từ 60 chunk xuống còn 6 chunk của `shopee-return-policy-seller`, và cả top-3 đều nằm trong tài liệu đúng đối tượng.
> Lý do cần lọc chứ không phó mặc cho embedding: nhóm đo độ tương tự giữa "Người mua có 7 ngày để gửi yêu cầu trả hàng" và "Người bán phải phản hồi khiếu nại trong 2 ngày lịch" được **0.506** — gần như không phân biệt nổi. Hai câu này cùng chủ đề, cùng cấu trúc, cùng nói về một mốc thời gian; thứ khác nhau là *ai* phải làm, mà đó đúng là thứ embedding không mã hóa tốt. Không lọc thì câu 5 rất dễ trả về điều khoản dành cho người mua.
> Mặt trái cần nói thật: corpus hiện lệch 9 `buyer` / 1 `seller`, nên khi lọc `seller` thì chỉ còn đúng một tài liệu — câu 5 gần như chắc chắn trúng, và vì thế nó không phân biệt được chiến lược chunking giữa các thành viên. Nếu mở rộng corpus, nhóm nên bổ sung tài liệu `seller` để phép lọc vừa có ý nghĩa vừa còn tính cạnh tranh.

---

## 4. Thuyết trình (Demo) & Bài học nhóm — Nhóm (5 điểm)

**Những phân tích (insights) hay nhất nhóm sẽ trình bày:**
> *Liệt kê 2-3 ý:*

**Bài học rút ra khi so sánh trong nhóm:**
> *Viết 2-3 câu — cùng tài liệu nhưng chiến lược khác nhau dẫn tới khác biệt gì?*

**Nếu làm lại, nhóm sẽ thay đổi gì trong chiến lược dữ liệu (data strategy)?**
> *Viết 2-3 câu:*

---

## Tự Đánh Giá (Phần Nhóm)

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Lựa chọn tài liệu (Document Set Quality) | / 10 |
| Thiết kế chiến lược (Strategy Design) | / 15 |
| Chất lượng truy xuất (Retrieval Quality) | / 10 |
| Thuyết trình (Demo) | / 5 |
| **Tổng phần nhóm** | **/ 40** |
