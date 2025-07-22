Instruction for GitHub Copilot: Phát triển AI Trợ Lý Voucher cho   (Giai đoạn 1 - Responsive AI)
1. Mục tiêu và Bối cảnh (Overall Goal and Context)
• Mục tiêu chính: Xây dựng một AI Assistant thông minh ngay trên trang chi tiết voucher (PDP) của ứng dụng  . Mục tiêu là giúp người dùng dễ dàng hiểu và áp dụng các điều khoản & điều kiện (T&C) phức tạp của voucher, từ đó nâng cao trải nghiệm người dùng tại điểm bán.
• Bối cảnh  :   là một hệ sinh thái đa chiều tập trung vào dịch vụ FnB, xử lý khối lượng dữ liệu khổng lồ từ triệu người dùng và merchant, bao gồm dữ liệu tài chính, hành vi và dữ liệu phi cấu trúc (UGC, video, review). AI được xem là hệ điều hành cốt lõi chứ không chỉ là một tính năng "nice-to-have".
2. Các Tính năng Cốt lõi của AI Trợ Lý Voucher (Core Features) GitHub Copilot, hãy tập trung phát triển các tính năng sau:
• Tóm tắt điểm chính (Key Point Summary):
    ◦ Phát triển khả năng cho AI để tự động đọc và tóm tắt các điều kiện quan trọng nhất của voucher từ nội dung chi tiết. Ví dụ: "Áp dụng cho hóa đơn trên 500K", "Không dùng cuối tuần", "Cần đặt bàn trước".
    ◦ Kết quả tóm tắt phải ngắn gọn, dễ hiểu và hiển thị nổi bật trên trang chi tiết voucher.
• Hỏi-đáp tự nhiên (Natural Language Q&A):
    ◦ Xây dựng một giao diện chat cho phép người dùng đặt câu hỏi bằng ngôn ngữ tự nhiên về voucher.
    ◦ AI phải có khả năng hiểu và trả lời trực tiếp các câu hỏi như: "Thứ 7 này dùng được không?", "Đi 2 người có áp dụng không?", "Có được sử dụng kết hợp với các khuyến mãi khác không?".
    ◦ Câu trả lời cần chính xác và trực tiếp dựa trên thông tin đã cung cấp.
3. Công nghệ và Nền tảng cần triển khai (Technologies and Platforms to Implement) Để phát triển AI Trợ Lý Voucher, GitHub Copilot cần chú ý sử dụng và tích hợp các công nghệ sau:
• LLM (Large Language Model) Service:
    ◦ Lựa chọn: Triển khai LLM trên Vertex Endpoint. Đây là lựa chọn được ưu tiên để tiết kiệm chi phí, vì tác vụ hỏi-đáp và tóm tắt trong giai đoạn này gói gọn trong thông tin đã được cung cấp (RAG).
    ◦ Kỹ thuật: Tập trung vào việc triển khai Retrieval Augmented Generation (RAG).
• RAG (Retrieval Augmented Generation):
    ◦ Embedding thông tin: Áp dụng kỹ thuật embedding để chuyển đổi thông tin chi tiết voucher (bao gồm PDP, các điều khoản chung, hướng dẫn sử dụng, và các "knowhow" riêng của   như Upoint, phương thức thanh toán) thành các vector số.
    ◦ Knowledge Base: Lưu trữ toàn bộ các vector embedding này trong một Vector Database.
    ◦ Luồng xử lý: Khi người dùng đặt câu hỏi, hệ thống sẽ thực hiện tìm kiếm ngữ nghĩa (semantic search) trong Vector Database để tìm kiếm các thông tin liên quan nhất. Sau đó, các thông tin liên quan này sẽ được cung cấp cho LLM cùng với câu hỏi của người dùng để tạo ra câu trả lời chính xác, giảm thiểu hiện tượng "ảo giác" (hallucinations).
• Vector Database:
    ◦ Sử dụng Elasticsearch với khả năng Vector Search để lưu trữ và truy vấn nhanh chóng các vector embedding. Đây sẽ là xương sống cho việc tìm kiếm ngữ nghĩa trong Knowledge Base.
4. Các Giai đoạn Phát triển (Phased Development for AI Voucher Assistant)
GitHub Copilot, hãy thực hiện phát triển theo các bước sau trong Giai đoạn 1 (Responsive AI):
• Giai đoạn 1.1: Chuẩn bị Dữ liệu và Xây dựng Knowledge Base
    ◦ Mô tả: Thu thập và chuẩn hóa tất cả dữ liệu liên quan đến voucher từ các nguồn nội bộ của   (PDP, T&C, quy định Upoint, thanh toán).
    ◦ Thực hiện:
        ▪ Viết script để trích xuất dữ liệu voucher từ các hệ thống hiện có.
        ▪ Xây dựng pipeline để làm sạch, cấu trúc hóa dữ liệu.
        ▪ Sử dụng các thư viện embedding (ví dụ: Sentence Transformers hoặc các model từ Vertex AI) để tạo vector embedding cho từng đoạn thông tin voucher.
        ▪ Ingest các vector này vào Elasticsearch được cấu hình với Vector Search.
• Giai đoạn 1.2: Triển khai LLM Service và RAG Logic
    ◦ Mô tả: Thiết lập LLM và phát triển logic RAG để xử lý các câu hỏi của người dùng.
    ◦ Thực hiện:
        ▪ Deploy một LLM phù hợp (ưu tiên tiếng Việt) trên Vertex Endpoint.
        ▪ Phát triển một API Gateway hoặc service trung gian nhận yêu cầu từ người dùng.
        ▪ Trong service này, khi nhận câu hỏi:
            • Thực hiện embedding câu hỏi của người dùng.
            • Gọi tới Elasticsearch (Vector Search) để truy vấn các vector gần nhất (nearest neighbors) trong Knowledge Base đã xây dựng.
            • Lấy về các đoạn văn bản gốc tương ứng với các vector tìm được.
            • Gửi câu hỏi của người dùng và các đoạn văn bản liên quan này (context) tới LLM để tạo ra câu trả lời.
            • Đảm bảo cấu hình LLM để ưu tiên sử dụng ngữ cảnh được cung cấp để giảm thiểu "ảo giác".
• Giai đoạn 1.3: Tích hợp Giao diện người dùng (UI Integration)
    ◦ Mô tả: Đưa AI Assistant vào trang chi tiết voucher trên ứng dụng  .
    ◦ Thực hiện:
        ▪ Thiết kế và triển khai một component UI (ví dụ: một widget chat) trên trang chi tiết voucher (PDP).
        ▪ Đảm bảo component này có thể hiển thị phần tóm tắt chính của voucher tự động.
        ▪ Tích hợp ô nhập liệu cho người dùng đặt câu hỏi và hiển thị câu trả lời từ AI.
        ▪ Kết nối UI với API/service của LLM và RAG đã phát triển.
• Giai đoạn 1.4: Kiểm thử và Tối ưu hóa
    ◦ Mô tả: Đảm bảo tính chính xác, hiệu quả và an toàn của AI Assistant.
    ◦ Thực hiện:
        ▪ Viết test cases toàn diện cho cả chức năng tóm tắt và hỏi-đáp, bao gồm các câu hỏi thông thường và các trường hợp biên (edge cases).
        ▪ Giám sát hiệu suất của LLM và Vector Database.
        ▪ Thu thập phản hồi từ người dùng để liên tục cải thiện chất lượng câu trả lời.
        ▪ Lưu ý quan trọng: Trong giai đoạn này, không cho phép AI giới thiệu các voucher khác (đi ra ngoài Knowledge Base đã được cung cấp) trong cùng một phiên hội thoại để đảm bảo an toàn và kiểm soát chi phí.

--------------------------------------------------------------------------------
Analogy: Hãy hình dung AI Trợ Lý Voucher như một người thủ thư siêu thông minh trong một thư viện khổng lồ (Knowledge Base) chứa đầy thông tin chi tiết về từng cuốn sách (voucher). Thay vì bạn phải tự mình đọc hết các cuốn sách để tìm kiếm thông tin, người thủ thư này (AI Assistant) có thể nhanh chóng đọc lướt qua (tóm tắt điểm chính) hoặc lắng nghe câu hỏi của bạn bằng ngôn ngữ tự nhiên (hỏi-đáp tự nhiên) và ngay lập tức tìm đến đúng phần thông tin trong cuốn sách đó để trả lời bạn một cách chính xác. Thư viện này được sắp xếp một cách khoa học (Vector Database với Elasticsearch) để người thủ thư có thể tìm kiếm thông tin nhanh nhất có thể.

Dữ liệu mẫu lấy từ file: /data/temp voucher.xlsx. 