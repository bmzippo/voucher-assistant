import pytest
from backend.llm_service import VertexAIService
from backend.models import VoucherData

class TestLLMService:
    """Test cases for LLM Service functionality"""
    
    @pytest.fixture
    def llm_service(self):
        """Create LLM service for testing"""
        return VertexAIService()
    
    @pytest.fixture
    def sample_context(self):
        """Sample voucher context for testing"""
        return """
        Voucher RuNam Café - Giảm 200,000 VND
        
        Mô tả: Cafe RuNam đã không ngừng nghiên cứu và phát triển cà phê mang đậm thương hiệu Việt.
        
        Hướng dẫn sử dụng: Khách hàng đổi điểm để lấy voucher trên App   sau đó đến cửa hàng 
        xuất trình voucher cho thu ngân trước khi thanh toán.
        
        Điều khoản: 
        - Voucher áp dụng tại tất cả các cửa hàng RuNam
        - Áp dụng tối đa 30 voucher trên 01 hóa đơn
        - Voucher chỉ có giá trị sử dụng một lần
        - Không chấp nhận voucher quá hạn sử dụng
        """
    
    @pytest.mark.asyncio
    async def test_generate_summary(self, llm_service, sample_context):
        """Test summary generation"""
        result = await llm_service.generate_summary(
            sample_context, 
            "Voucher RuNam Café"
        )
        
        assert "summary" in result
        assert "key_points" in result
        assert "confidence" in result
        assert isinstance(result["key_points"], list)
        assert len(result["key_points"]) <= 5
        assert result["confidence"] >= 0.0
    
    @pytest.mark.asyncio
    async def test_answer_question(self, llm_service, sample_context):
        """Test question answering"""
        questions = [
            "Voucher này có thời hạn sử dụng không?",
            "Tôi có thể sử dụng bao nhiều voucher cùng lúc?",
            "Làm sao để sử dụng voucher này?",
            "Voucher áp dụng ở đâu?"
        ]
        
        for question in questions:
            result = await llm_service.answer_question(
                question, 
                sample_context, 
                "Voucher RuNam Café"
            )
            
            assert "answer" in result
            assert "confidence" in result
            assert "sources" in result
            assert isinstance(result["answer"], str)
            assert len(result["answer"]) > 0
            assert 0.0 <= result["confidence"] <= 1.0
    
    @pytest.mark.asyncio
    async def test_confidence_calculation(self, llm_service):
        """Test confidence score calculation"""
        # Test with good context
        good_context = "Voucher có hiệu lực đến 31/12/2024. Áp dụng tối đa 1 voucher/hóa đơn."
        result1 = await llm_service.answer_question(
            "Voucher này có thời hạn đến khi nào?",
            good_context,
            "Test Voucher"
        )
        
        # Test with poor context
        poor_context = "Thông tin không rõ ràng."
        result2 = await llm_service.answer_question(
            "Voucher này có thời hạn đến khi nào?",
            poor_context,
            "Test Voucher"
        )
        
        # Good context should have higher confidence
        assert result1["confidence"] >= result2["confidence"]
    
    @pytest.mark.asyncio
    async def test_parse_summary_response(self, llm_service):
        """Test summary response parsing"""
        mock_response = """
        1. Giá trị ưu đãi: Giảm 200,000 VND
        2. Điều kiện áp dụng: Tất cả cửa hàng RuNam
        3. Thời hạn sử dụng: Có thời hạn cụ thể
        4. Hạn chế sử dụng: Tối đa 30 voucher/hóa đơn
        5. Cách sử dụng: Xuất trình tại quầy thanh toán
        """
        
        key_points = llm_service._parse_summary_response(mock_response)
        
        assert len(key_points) == 5
        assert "Giảm 200,000 VND" in key_points[0]
        assert "Tất cả cửa hàng RuNam" in key_points[1]
    
    @pytest.mark.asyncio
    async def test_vietnamese_language_handling(self, llm_service, sample_context):
        """Test Vietnamese language specific handling"""
        vietnamese_questions = [
            "Thứ 7 này tôi có thể sử dụng voucher không?",
            "Voucher có được áp dụng cho đồ uống không?",
            "Tôi cần mang gì khi đến cửa hàng?",
            "Có thể sử dụng voucher vào ngày lễ không?"
        ]
        
        for question in vietnamese_questions:
            result = await llm_service.answer_question(
                question, 
                sample_context, 
                "Voucher RuNam"
            )
            
            # Response should be in Vietnamese
            assert any(vn_word in result["answer"].lower() for vn_word in 
                      ["không", "có", "được", "tại", "để", "sử dụng", "voucher"])
            assert result["confidence"] > 0.0

class TestLLMErrorHandling:
    """Test error handling in LLM service"""
    
    @pytest.mark.asyncio
    async def test_empty_context_handling(self):
        """Test handling of empty context"""
        llm_service = VertexAIService()
        
        result = await llm_service.answer_question(
            "Test question", 
            "", 
            "Test Voucher"
        )
        
        assert "answer" in result
        assert result["confidence"] == 0.0
    
    @pytest.mark.asyncio
    async def test_malformed_question_handling(self):
        """Test handling of malformed questions"""
        llm_service = VertexAIService()
        
        malformed_questions = ["", "???", "abc123", "............"]
        
        for question in malformed_questions:
            result = await llm_service.answer_question(
                question, 
                "Some context", 
                "Test Voucher"
            )
            
            assert "answer" in result
            assert result["confidence"] >= 0.0
