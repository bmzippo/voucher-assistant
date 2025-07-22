from google.cloud import aiplatform
from google.oauth2 import service_account
import json
from typing import List, Dict, Any
import logging
from config import settings

logger = logging.getLogger(__name__)

class VertexAIService:
    """Service for interacting with Vertex AI LLM"""
    
    def __init__(self):
        self.project_id = settings.GOOGLE_PROJECT_ID
        self.region = settings.GOOGLE_REGION
        self.endpoint_name = settings.VERTEX_AI_ENDPOINT
        
        # Initialize Vertex AI
        aiplatform.init(
            project=self.project_id,
            location=self.region
        )
    
    async def generate_summary(self, voucher_context: str, voucher_name: str) -> Dict[str, Any]:
        """Generate key points summary for voucher"""
        
        prompt = f"""
Bạn là một AI Assistant chuyên về voucher cho ứng dụng OneU. Hãy tóm tắt các điểm chính của voucher sau đây:

Tên voucher: {voucher_name}

Thông tin chi tiết:
{voucher_context}

Hãy tóm tắt thành các điểm chính theo định dạng sau:
1. Giá trị ưu đãi: [số tiền hoặc phần trăm giảm giá]
2. Điều kiện áp dụng: [điều kiện quan trọng nhất]
3. Thời hạn sử dụng: [thời gian có hiệu lực]
4. Hạn chế sử dụng: [các hạn chế quan trọng]
5. Cách sử dụng: [hướng dẫn ngắn gọn]

Trả lời bằng tiếng Việt, ngắn gọn và dễ hiểu.
"""
        
        try:
            # Here you would call the actual Vertex AI endpoint
            # For now, we'll implement a mock response
            response = await self._call_vertex_ai(prompt)
            
            # Parse response to extract key points
            key_points = self._parse_summary_response(response)
            
            return {
                "summary": response,
                "key_points": key_points,
                "confidence": 0.9
            }
            
        except Exception as e:
            logger.error(f"Error generating summary: {e}")
            return {
                "summary": "Không thể tạo tóm tắt tại thời điểm này.",
                "key_points": [],
                "confidence": 0.0
            }
    
    async def answer_question(
        self, 
        question: str, 
        context: str, 
        voucher_name: str
    ) -> Dict[str, Any]:
        """Answer user question about voucher"""
        
        prompt = f"""
Bạn là một AI Assistant chuyên về voucher cho ứng dụng OneU. Một khách hàng đang hỏi về voucher "{voucher_name}".

Thông tin voucher:
{context}

Câu hỏi của khách hàng: {question}

Hướng dẫn trả lời:
1. Chỉ trả lời dựa trên thông tin được cung cấp về voucher
2. Nếu không có thông tin để trả lời, hãy nói rõ và gợi ý liên hệ hotline
3. Trả lời bằng tiếng Việt, thân thiện và dễ hiểu
4. Nếu câu hỏi về thời gian, ngày tháng, hãy trả lời cụ thể
5. Không đề xuất voucher khác hoặc thông tin ngoài voucher này

Trả lời:
"""
        
        try:
            response = await self._call_vertex_ai(prompt)
            confidence = self._calculate_confidence(question, context, response)
            
            return {
                "answer": response,
                "confidence": confidence,
                "sources": ["voucher_terms", "voucher_description"]
            }
            
        except Exception as e:
            logger.error(f"Error answering question: {e}")
            return {
                "answer": "Xin lỗi, tôi không thể trả lời câu hỏi này lúc này. Vui lòng liên hệ hotline 1900 558 865 để được hỗ trợ.",
                "confidence": 0.0,
                "sources": []
            }
    
    async def _call_vertex_ai(self, prompt: str) -> str:
        """Call Vertex AI endpoint (mock implementation)"""
        # This is a mock implementation
        # In production, you would call the actual Vertex AI endpoint
        
        # Mock responses based on common patterns
        if "tóm tắt" in prompt.lower() or "điểm chính" in prompt.lower():
            return """1. Giá trị ưu đãi: Giảm theo mức được quy định trong voucher
2. Điều kiện áp dụng: Áp dụng theo điều khoản và điều kiện của từng voucher
3. Thời hạn sử dụng: Có thời hạn sử dụng cụ thể
4. Hạn chế sử dụng: Một số hạn chế về số lượng và cách sử dụng
5. Cách sử dụng: Xuất trình voucher tại cửa hàng khi thanh toán"""
        
        return "Tôi sẽ trả lời dựa trên thông tin voucher được cung cấp."
    
    def _parse_summary_response(self, response: str) -> List[str]:
        """Parse summary response to extract key points"""
        lines = response.split('\n')
        key_points = []
        
        for line in lines:
            line = line.strip()
            if line and (line.startswith(('1.', '2.', '3.', '4.', '5.')) or line.startswith('-')):
                # Remove numbering and extract the key point
                point = line.split(':', 1)
                if len(point) > 1:
                    key_points.append(point[1].strip())
                else:
                    key_points.append(line)
        
        return key_points[:5]  # Return top 5 key points
    
    def _calculate_confidence(self, question: str, context: str, response: str) -> float:
        """Calculate confidence score for the response"""
        # Simple heuristic-based confidence calculation
        # In production, you might use more sophisticated methods
        
        confidence = 0.7  # Base confidence
        
        # Increase confidence if response contains specific information
        if any(keyword in response.lower() for keyword in ['áp dụng', 'không áp dụng', 'được', 'không được']):
            confidence += 0.1
        
        # Decrease confidence if response is too generic
        if len(response) < 50:
            confidence -= 0.2
        
        # Ensure confidence is between 0 and 1
        return max(0.0, min(1.0, confidence))
