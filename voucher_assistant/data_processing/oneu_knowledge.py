"""
  Knowledge Base - Vietnamese specific information for voucher assistant
"""

UPOINT_RULES = {
    "exchange_rate": "1 Upoint = 1 VND",
    "earning_rules": [
        "Mỗi 1 VND chi tiêu = 1 Upoint",
        "Giao dịch tối thiểu 50,000 VND mới được tích điểm",
        "Điểm tích lũy sẽ có hiệu lực sau 24h",
        "Điểm có thời hạn sử dụng 2 năm kể từ ngày tích"
    ],
    "usage_rules": [
        "Tối thiểu đổi 100 Upoint",
        "Tối đa đổi 500,000 Upoint/tháng",
        "Không áp dụng với một số sản phẩm đặc biệt",
        "Điểm đã đổi không thể hoàn lại"
    ]
}

PAYMENT_METHODS = {
    "supported_methods": [
        "Upoint (điểm tích lũy)",
        "Thẻ tín dụng/ghi nợ",
        "Ví điện tử (MoMo, ZaloPay, ViettelPay)",
        "Chuyển khoản ngân hàng",
        "Tiền mặt (tại cửa hàng)"
    ],
    "payment_notes": [
        "Có thể kết hợp nhiều phương thức thanh toán",
        "Ưu tiên sử dụng Upoint trước",
        "Kiểm tra số dư trước khi giao dịch"
    ]
}

ONEU_TERMS = {
    "general_terms": [
        "Voucher chỉ sử dụng được 1 lần",
        "Không hoàn lại tiền thừa",
        "Không có giá trị quy đổi thành tiền mặt",
        "  có quyền thay đổi điều khoản mà không báo trước",
        "Voucher có thể được sử dụng cùng các khuyến mãi khác trừ khi có quy định riêng"
    ],
    "user_responsibilities": [
        "Bảo mật thông tin voucher",
        "Kiểm tra thời hạn sử dụng",
        "Đọc kỹ điều khoản trước khi sử dụng",
        "Xuất trình voucher đúng cách tại điểm bán"
    ],
    "restrictions": [
        "Không áp dụng cho sản phẩm đã giảm giá",
        "Một số sản phẩm có thể được loại trừ",
        "Không áp dụng cho phí vận chuyển",
        "Có thể có hạn chế về thời gian sử dụng"
    ]
}

COMMON_QUESTIONS = {
    "usage": [
        "Làm sao để sử dụng voucher?",
        "Voucher này dùng được khi nào?",
        "Có cần đặt trước không?",
        "Sử dụng voucher ở đâu?"
    ],
    "validity": [
        "Voucher có hạn sử dụng đến khi nào?",
        "Còn hiệu lực không?",
        "Hết hạn chưa?",
        "Thời gian sử dụng?"
    ],
    "conditions": [
        "Điều kiện áp dụng là gì?",
        "Có hạn chế gì không?",
        "Áp dụng cho ai?",
        "Số lượng tối đa?"
    ],
    "combination": [
        "Có dùng được với khuyến mãi khác không?",
        "Kết hợp với voucher khác?",
        "Dùng chung với ưu đãi thành viên?",
        "Áp dụng cùng giảm giá?"
    ]
}

RESPONSE_TEMPLATES = {
    "no_information": "Xin lỗi, tôi không tìm thấy thông tin cụ thể về vấn đề này trong điều khoản voucher. Vui lòng liên hệ hotline 1900 558 865 để được hỗ trợ chi tiết.",
    "contact_support": "Để được hỗ trợ tốt nhất, bạn có thể liên hệ:\n- Hotline: 1900 558 865\n- Email: support@oneu.vn\n- Thời gian hỗ trợ: 8:00 - 22:00 hàng ngày",
    "general_usage": "Để sử dụng voucher:\n1. Mở ứng dụng  \n2. Tìm và chọn voucher\n3. Đến cửa hàng/nhà hàng\n4. Xuất trình voucher cho nhân viên\n5. Thanh toán theo hướng dẫn"
}

MERCHANT_INFO = {
    "restaurant_chains": [
        "Highlands Coffee", "The Coffee House", "Starbucks",
        "KFC", "McDonald's", "Pizza Hut", "Domino's",
        "Lotteria", "Burger King", "Popeyes"
    ],
    "retail_chains": [
        "Circle K", "FamilyMart", "B's Mart",
        "BigC", "Coopmart", "Lotte Mart"
    ],
    "service_providers": [
        "CGV Cinemas", "Lotte Cinema", "Galaxy Cinema",
        "Spa", "Gym", "Beauty salon"
    ]
}
