# 📊 BÁO CÁO THU HOẠCH NGHIỆM THU BÀI LAB 3 (BƯỚC 3 — SUBMISSION ARTIFACT)

> **Cập nhật 13/09/2026:** Công cụ chuyển sang E01–E03 Hà Nội, nguồn trong `config/hanoi_routes.json`. Trace và kết quả 5/5 bên dưới thuộc dữ liệu DEMO cũ; cần chạy lại bộ test và thay bằng chứng trước khi nộp. Đăng ký vẫn mô phỏng.

> **Họ và Tên Học viên:** Cao Đức Hiếu 
> **Mã Sinh Viên / Mã Học viên:** 2A202602701  
> **Chủ đề Lựa chọn:** Trợ lý Dịch vụ Khách hàng VinBus — Tra cứu lộ trình và đăng ký vé tháng.

---

## 1. BẢNG CHẤM ĐIỂM AGENTIC FIT SCORING MATRIX (ĐÁNH GIÁ CHỦ ĐỀ)

| Tiêu chí Đánh giá | Mức độ (1 - 5) | Giải trình chi tiết lý do chọn điểm |
| :--- | :---: | :--- |
| **1. Multi-step Reasoning** | 4 / 5 | Với yêu cầu tìm tuyến và đăng ký vé tháng, Agent cần tra cứu tuyến phù hợp với điểm đi–đến, lấy mã tuyến từ kết quả rồi thực hiện đăng ký. |
| **2. Tool Interaction** | 5 / 5 | Agent cần sử dụng hai công cụ qua MCP Server: tra cứu lộ trình và đăng ký vé tháng. LLM không thể tự xác nhận dữ liệu tuyến hoặc kết quả đăng ký nếu chưa gọi công cụ. |
| **3. Dynamic Decision** | 4 / 5 | Bước tiếp theo phụ thuộc kết quả tra cứu: tìm thấy một tuyến thì tiếp tục đăng ký nếu đủ thông tin; có nhiều tuyến thì hỏi người dùng chọn; không tìm thấy thì thông báo và đề nghị điều chỉnh yêu cầu. |
| **4. Long Horizon Goal** | 2 / 5 | Agent cần giữ mục tiêu đăng ký vé trong chuỗi tra cứu và thực hiện hành động, nhưng nhiệm vụ ngắn, chưa yêu cầu lập kế hoạch dài hạn hoặc bộ nhớ qua nhiều phiên. |
| **TỔNG ĐIỂM AGENTIC FIT** | **15/ 20** | Đề tài phù hợp triển khai ReAct Agent vì cần phối hợp công cụ và quyết định dựa trên kết quả thực thi. |

---

## 2. TRÍCH XUẤT KẾT QUẢ WATERFALL TRACE LOG (SAU KHI CHẠY TEST SUITE TRÊN API THẬT)

> ⚠️ **YÊU CẦU NGHIỆM THU:** Mở tệp `.env` điền `GEMINI_API_KEY` (hoặc `OPENAI_API_KEY`) để kết nối LLM thật trước khi thực thi `python src/app.py --all`. Bài nộp chỉ dùng Mock Offline Provider sẽ không đạt điểm nghiệm thực tế.

Dán 1 đoạn trích xuất log tiêu biểu từ file `docs/trace_waterfall.json` sinh ra từ phản hồi LLM API thật:

```json
[
  {
    "step": 1,
    "query": "Tìm tuyến đi từ Bến xe D đến Bệnh viện F rồi đăng ký vé tháng 2026-10 cho tôi trên tuyến tìm được. Tên hành khách là Khách Kiểm Thử, số điện thoại 0900000001.",
    "action_type": "TOOL_EXECUTION",
    "decision_summary": "LLM yêu cầu gọi công cụ lookup_bus_route.",
    "tool_name": "lookup_bus_route",
    "arguments": {
      "origin": "Bến xe D",
      "destination": "Bệnh viện F"
    },
    "observation": {
      "status": "SUCCESS",
      "simulation": true,
      "count": 1,
      "routes": [
        {
          "route_id": "DEMO02",
          "route_name": "Tuyến mô phỏng Bến xe – Bệnh viện",
          "stops": [
            "Bến xe D",
            "Trung tâm E",
            "Bệnh viện F"
          ],
          "monthly_pass_price_vnd": 180000
        }
      ],
      "requires_selection": false
    },
    "llm_latency_ms": 1058.83,
    "tool_latency_ms": 0.14,
    "latency_ms": 1058.97,
    "test_case_id": "TC04"
  },
  {
    "step": 2,
    "query": "Tìm tuyến đi từ Bến xe D đến Bệnh viện F rồi đăng ký vé tháng 2026-10 cho tôi trên tuyến tìm được. Tên hành khách là Khách Kiểm Thử, số điện thoại 0900000001.",
    "action_type": "TOOL_EXECUTION",
    "decision_summary": "LLM yêu cầu gọi công cụ register_monthly_pass.",
    "tool_name": "register_monthly_pass",
    "arguments": {
      "passenger_name": "Khách Kiểm Thử",
      "phone": "0900000001",
      "route_id": "DEMO02",
      "month": "2026-10"
    },
    "observation": {
      "status": "SUCCESS",
      "simulation": true,
      "registration": {
        "registration_id": "VB-DEMO-BA2779D495",
        "passenger_name": "Khách Kiểm Thử",
        "phone": "0900000001",
        "route_id": "DEMO02",
        "month": "2026-10",
        "price_vnd": 180000
      },
      "message": "Đăng ký vé tháng mô phỏng thành công. Đây không phải vé thật."
    },
    "llm_latency_ms": 1171.51,
    "tool_latency_ms": 0.06,
    "latency_ms": 1171.57,
    "test_case_id": "TC04"
  },
  {
    "step": 3,
    "query": "Tìm tuyến đi từ Bến xe D đến Bệnh viện F rồi đăng ký vé tháng 2026-10 cho tôi trên tuyến tìm được. Tên hành khách là Khách Kiểm Thử, số điện thoại 0900000001.",
    "action_type": "FINAL_ANSWER",
    "output": "Bạn đã đăng ký vé tháng mô phỏng thành công trên tuyến xe với thông tin như sau:\n\n- **Mã đăng ký:** VB-DEMO-BA2779D495\n- **Tuyến:** DEMO02 - Tuyến mô phỏng Bến xe – Bệnh viện\n- **Tháng sử dụng:** 2026-10\n- **Giá vé:** 180,000 VNĐ\n\nXin lưu ý rằng đây không phải là vé thật. Nếu bạn cần thêm thông tin gì khác, hãy cho tôi biết!",
    "latency_ms": 1895.89,
    "test_case_id": "TC04"
  },
]
```
**Nhận xét TC04:** Agent gọi `lookup_bus_route` để tìm tuyến từ
Bến xe D đến Bệnh viện F. Sau khi nhận được tuyến DEMO02, Agent dùng
mã tuyến này cùng thông tin hành khách để gọi `register_monthly_pass`.
Công cụ trả về trạng thái SUCCESS, sau đó Agent tổng hợp mã đăng ký,
tháng sử dụng và giá vé 180.000 đồng trong câu trả lời cuối.
Kết quả thể hiện Agent sử dụng Observation của bước tra cứu để
thực hiện hành động tiếp theo. Đăng ký được thực hiện trên dữ liệu mô phỏng.
---

## 3. TỔNG KẾT KẾT QUẢ NGHIỆM THU & NỘP BÀI

- [X] Đã điền API Key thật trong `.env` và xác nhận Agent chạy mượt mà trên LLM API thật (Gemini/OpenAI).
- **Tổng số Test Cases đã chạy thành công:** 5 / 5 test cases.
- **Số lượt gọi Tool qua MCP Server chính xác:** 5 lượt, gồm 3 lượt tra cứu và 2 lượt đăng ký.
- **Tổng số sự kiện Waterfall Trace:** 10 sự kiện, gồm 5 sự kiện thực thi công cụ và 5 câu trả lời cuối.
- **Kết quả đẩy Repo nộp bài:** [ ] Đã Commit và Push mã nguồn thành công lên GitHub cá nhân.

| Test case | Kết quả quan sát | Đánh giá |
| :--- | :--- | :---: |
| TC01 | Giới thiệu chức năng, không gọi công cụ. | Đạt |
| TC02 | Tra cứu DEMO01, trả lộ trình và giá vé 150.000 đồng. | Đạt |
| TC03 | Đăng ký DEMO01, trả mã đăng ký và xác nhận mô phỏng. | Đạt |
| TC04 | Tra cứu được DEMO02 rồi đăng ký vé tháng đúng thông tin. | Đạt |
| TC05 | Nhận NOT_FOUND, thông báo không tìm thấy và không đăng ký. | Đạt |
---

> ✅ **HOÀN TẤT NỘP BÀI:** Sao chép đường link GitHub Repository cá nhân của bạn và dán vào ô nộp bài trên hệ thống LMS VLearn để hoàn tất Bài Lab 3!
