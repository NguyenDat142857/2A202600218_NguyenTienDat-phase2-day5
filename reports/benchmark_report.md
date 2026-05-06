
```markdown
# 📊 Benchmark Report — Multi-Agent Research System

## 👤 Author
2A202600218_Nguyễn Tiến Đạt  
Course: AI Systems / Multi-Agent Lab  

---

## 🧠 1. Tổng quan

Trong bài lab này, mục tiêu chính là xây dựng và đánh giá một hệ thống **Multi-Agent Research System** bao gồm nhiều agent chuyên biệt (Supervisor, Researcher, Analyst, Writer), đồng thời so sánh với cách tiếp cận truyền thống sử dụng **Single-Agent (một LLM duy nhất)**.

Hai hướng tiếp cận này đại diện cho hai triết lý thiết kế khác nhau:

- **Single-Agent**: đơn giản, nhanh, trực tiếp — tất cả logic nằm trong một lần gọi LLM
- **Multi-Agent**: phân tách vai trò, mô phỏng quy trình tư duy nhiều bước (research → analysis → synthesis)

Báo cáo này tập trung phân tích các khía cạnh quan trọng:

- Hiệu năng (Latency)
- Chi phí (Cost)
- Chất lượng câu trả lời (Answer Quality)
- Khả năng suy luận (Reasoning Capability)
- Các lỗi phát sinh (Failure Modes) và cách khắc phục

---

## ⚙️ 2. Cấu hình thực nghiệm

### 🔹 Query sử dụng

```

Explain GraphRAG and compare it with traditional RAG

```

Đây là một câu hỏi mang tính **so sánh + giải thích**, yêu cầu:
- Hiểu khái niệm (GraphRAG)
- So sánh với RAG truyền thống
- Tổng hợp thông tin từ nhiều nguồn

👉 Phù hợp để test khả năng **multi-step reasoning**

---

### 🔹 Model & Infrastructure

- Provider: OpenRouter
- Model: `openai/gpt-oss-120b:free`
- Python: 3.11
- Môi trường: VSCode Terminal (Windows)
- Search: Mock (không sử dụng Tavily API)

---

### 🔹 Kiến trúc hệ thống

#### Single-Agent
- 1 lần gọi LLM
- Input: Query
- Output: Final Answer

#### Multi-Agent
Pipeline gồm 4 bước:

```

Supervisor → Researcher → Analyst → Writer → Done

```

- Researcher: thu thập & tóm tắt thông tin
- Analyst: phân tích & so sánh
- Writer: tổng hợp thành câu trả lời hoàn chỉnh

---

## 🧪 3. Kết quả tổng quan

| Run | Latency (s) | Tokens (in/out) | Cost (USD) | Quality | Nhận xét |
|-----|------------:|----------------:|-----------:|--------:|---------|
| Single-Agent | 35.54 | 92 / 831 | 0.0005 | 7.5 | Nhanh, đủ đúng nhưng chưa sâu |
| Multi-Agent | 98.36 | ~2700 / ~2400 | ~0.0020 | 9.2 | Sâu hơn, có reasoning, cấu trúc tốt |

---

## 📈 4. Phân tích chi tiết

### 4.1 ⏱ Hiệu năng (Latency)

Hệ thống Single-Agent hoàn thành trong khoảng **35 giây**, trong khi Multi-Agent mất khoảng **98 giây**, tức là chậm hơn gần **3 lần**.

Nguyên nhân chính đến từ:
- Multi-Agent thực hiện **nhiều lần gọi LLM liên tiếp**
- Mỗi agent phụ trách một bước riêng:
  - Research (~23s)
  - Analysis (~39s)
  - Writing (~36s)
- Các bước được thực thi **tuần tự**, chưa có cơ chế song song

👉 Điều này phản ánh rõ trade-off:
> Multi-Agent đánh đổi tốc độ để lấy chất lượng

---

### 4.2 💰 Chi phí (Cost)

Chi phí của Multi-Agent cao hơn khoảng **4 lần** so với Single-Agent.

Lý do:
- Tổng số token tăng mạnh qua từng bước
- Context được truyền và mở rộng liên tục
- Mỗi agent đều gọi LLM riêng biệt

👉 Đây là vấn đề quan trọng trong production:
- Nếu không tối ưu, Multi-Agent có thể rất tốn kém

---

### 4.3 🧠 Chất lượng câu trả lời

#### 🔹 Single-Agent

Câu trả lời từ Single-Agent có các đặc điểm:
- Nội dung chính xác về mặt kiến thức
- Trình bày rõ ràng
- Dễ hiểu

Tuy nhiên:
- Thiếu bước phân tích rõ ràng
- So sánh chưa sâu
- Không thể hiện quá trình suy luận

👉 Nói cách khác, nó “trả lời đúng”, nhưng chưa “nghĩ sâu”

---

#### 🔹 Multi-Agent

Multi-Agent tạo ra câu trả lời chất lượng cao hơn nhờ:

- Có pipeline rõ ràng:
```

Research → Analysis → Writing

```
- Phân tách rõ:
- Thu thập thông tin
- Phân tích
- Tổng hợp
- So sánh GraphRAG vs RAG chi tiết hơn
- Có cấu trúc (sections, bảng, bullet points)

👉 Quan trọng nhất:
> Multi-Agent thể hiện được **quá trình reasoning**, không chỉ là kết quả

---

## 🔍 5. Phân tích vai trò từng Agent

### 🧑‍🔬 Researcher Agent

Agent này chịu trách nhiệm:
- Gọi SearchClient để lấy dữ liệu (mock)
- Tóm tắt các nguồn thành research_notes

Vai trò của nó tương tự một **người thu thập tài liệu**.

👉 Điểm hạn chế:
- Do dùng mock data nên chất lượng nguồn chưa cao

---

### 🧠 Analyst Agent

Đây là agent quan trọng nhất trong pipeline.

Nhiệm vụ:
- Phân tích research_notes
- Rút ra:
- Key claims
- Điểm giống & khác
- Trade-offs

👉 Đây chính là bước biến dữ liệu thô thành **tri thức có cấu trúc**

---

### ✍️ Writer Agent

Agent này:
- Tổng hợp tất cả thông tin
- Viết thành câu trả lời hoàn chỉnh

Vai trò tương tự một **người viết báo cáo**

👉 Output rõ ràng hơn Single-Agent nhờ đã có phân tích từ trước

---

### 🧭 Supervisor Agent

Supervisor điều phối toàn bộ pipeline:

```

researcher → analyst → writer → done

```

Hiện tại logic còn đơn giản (rule-based), nhưng:
- Đảm bảo flow đúng
- Ngăn vòng lặp vô hạn

---

## ⚠️ 6. Failure Modes & Cách khắc phục

Trong quá trình phát triển, một số lỗi phổ biến đã xảy ra:

### ❌ Thiếu API Key
- Nguyên nhân: chưa set `.env`
- Cách fix: thêm `OPENAI_API_KEY` và load bằng `dotenv`

---

### ❌ Sai schema SourceDocument
- Thiếu field `snippet`
- Fix: đảm bảo đúng schema khi tạo object

---

### ❌ Sai attribute (`content`)
- Code dùng `doc.content` trong khi schema là `snippet`
- Fix: thay bằng `doc.snippet`

---

### ❌ Workflow bị crash
- Do exception trong agent
- Fix:
  - Thêm try/catch
  - Fallback → stop workflow

---

## 🧠 7. Insight quan trọng

### 🔥 1. Multi-Agent = Structured Thinking

Điểm mạnh của Multi-Agent không nằm ở việc “gọi nhiều model hơn”, mà ở:

> **Chia nhỏ quá trình suy nghĩ thành nhiều bước rõ ràng**

---

### 🔥 2. Trade-off không thể tránh

| Yếu tố | Single-Agent | Multi-Agent |
|--------|-------------|------------|
| Speed | Nhanh | Chậm |
| Cost | Thấp | Cao |
| Quality | Trung bình | Cao |

---

### 🔥 3. Hướng đi thực tế (Production)

Giải pháp tối ưu không phải chọn 1 trong 2, mà là kết hợp:

```

Query đơn giản → Single-Agent
Query phức tạp → Multi-Agent

```

👉 Đây gọi là **Hybrid Architecture**

---

## 🚀 8. Hướng cải tiến

Một số hướng phát triển tiếp theo:

### 1. Parallel Execution
- Chạy nhiều agent song song
- Giảm latency đáng kể

---

### 2. Real Search Integration
- Tích hợp Tavily / SerpAPI
- Tăng độ chính xác thực tế

---

### 3. Smart Supervisor
- Routing động (dynamic)
- Có thể skip agent không cần thiết

---

### 4. Caching
- Cache kết quả LLM
- Cache search

---

### 5. Evaluation nâng cao
- Factual accuracy
- Hallucination detection
- Citation coverage

---

## 🧾 9. Kết luận

Hệ thống Multi-Agent đã chứng minh được rằng:

- Có thể cải thiện đáng kể chất lượng câu trả lời
- Thể hiện rõ quá trình reasoning
- Phù hợp với các bài toán phức tạp

Tuy nhiên, đổi lại:
- Tăng latency
- Tăng chi phí

👉 Do đó, giải pháp tốt nhất trong thực tế là:

> **Kết hợp Single-Agent và Multi-Agent để cân bằng giữa tốc độ và chất lượng**

---

## 📎 10. Execution Trace

```

Supervisor → Researcher → Analyst → Writer → Done

```

---

## 🎯 Final Takeaway

> Multi-agent systems không chỉ là kiến trúc kỹ thuật,  
> mà là cách mô phỏng **quy trình tư duy của con người**:
>
> - Tìm thông tin  
> - Phân tích  
> - Tổng hợp  
>
> 👉 Đây chính là lý do tại sao chúng tạo ra câu trả lời chất lượng hơn.
```

---


