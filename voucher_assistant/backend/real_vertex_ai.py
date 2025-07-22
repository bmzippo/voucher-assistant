import vertexai
from vertexai.language_models import TextGenerationModel
from google.cloud import aiplatform
import asyncio
import logging
from typing import Dict, Any
from config import settings

logger = logging.getLogger(__name__)

class RealVertexAIService:
    """Real Vertex AI integration for production use"""
    
    def __init__(self):
        # Initialize Vertex AI
        vertexai.init(
            project=settings.GOOGLE_PROJECT_ID,
            location=settings.GOOGLE_REGION
        )
        
        # Initialize the text generation model
        self.model = TextGenerationModel.from_pretrained("text-bison@001")
        
        # Model parameters
        self.generation_config = {
            "max_output_tokens": 1024,
            "temperature": 0.3,
            "top_p": 0.8,
            "top_k": 40
        }
    
    async def generate_summary(self, voucher_context: str, voucher_name: str) -> Dict[str, Any]:
        """Generate summary using real Vertex AI"""
        
        prompt = f"""
Bạn là AI Assistant chuyên về voucher OneU. Hãy tóm tắt voucher sau theo format yêu cầu:

Tên voucher: {voucher_name}

Thông tin chi tiết:
{voucher_context}

Yêu cầu tóm tắt:
1. Giá trị ưu đãi: [Số tiền hoặc % giảm giá cụ thể]
2. Điều kiện áp dụng: [Điều kiện quan trọng nhất, ngắn gọn]
3. Thời hạn sử dụng: [Ngày hết hạn hoặc thời gian có hiệu lực]
4. Hạn chế sử dụng: [Các hạn chế quan trọng]
5. Cách sử dụng: [Hướng dẫn sử dụng ngắn gọn]

Lưu ý:
- Trả lời bằng tiếng Việt
- Mỗi điểm ngắn gọn, dễ hiểu
- Chỉ dựa trên thông tin được cung cấp
- Nếu thiếu thông tin, ghi "Xem chi tiết tại cửa hàng"
"""
        
        try:
            response = await self._call_vertex_ai(prompt)
            key_points = self._parse_summary_response(response)
            
            return {
                "summary": response,
                "key_points": key_points,
                "confidence": self._calculate_summary_confidence(response, voucher_context)
            }
            
        except Exception as e:
            logger.error(f"Error generating summary with Vertex AI: {e}")
            return await self._fallback_summary(voucher_context, voucher_name)
    
    async def answer_question(
        self, 
        question: str, 
        context: str, 
        voucher_name: str
    ) -> Dict[str, Any]:
        """Answer question using real Vertex AI"""
        
        prompt = f"""
Bạn là AI Assistant chuyên về voucher OneU. Khách hàng hỏi về voucher "{voucher_name}".

Thông tin voucher:
{context}

Câu hỏi: {question}

Hướng dẫn trả lời:
1. Chỉ trả lời dựa trên thông tin voucher được cung cấp
2. Trả lời bằng tiếng Việt, thân thiện và chính xác
3. Nếu không có thông tin để trả lời, nói rõ và gợi ý liên hệ hotline 1900 558 865
4. Với câu hỏi về thời gian/ngày, trả lời cụ thể nếu có thông tin
5. Không đề xuất voucher khác
6. Giữ câu trả lời ngắn gọn, tập trung vào câu hỏi

Trả lời:
"""
        
        try:
            response = await self._call_vertex_ai(prompt)
            confidence = self._calculate_qa_confidence(question, context, response)
            
            return {
                "answer": response,
                "confidence": confidence,
                "sources": self._extract_sources(context)
            }
            
        except Exception as e:
            logger.error(f"Error answering question with Vertex AI: {e}")
            return await self._fallback_answer(question)
    
    async def _call_vertex_ai(self, prompt: str) -> str:
        """Call Vertex AI model"""
        try:
            # Run in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.model.predict(
                    prompt,
                    **self.generation_config
                )
            )
            return response.text.strip()
            
        except Exception as e:
            logger.error(f"Vertex AI API call failed: {e}")
            raise
    
    def _parse_summary_response(self, response: str) -> list[str]:
        """Parse summary response to extract key points"""
        lines = response.split('\n')
        key_points = []
        
        for line in lines:
            line = line.strip()
            if line and any(line.startswith(str(i)) for i in range(1, 6)):
                # Extract content after number and colon
                if ':' in line:
                    point = line.split(':', 1)[1].strip()
                    if point and len(point) > 5:  # Meaningful content
                        key_points.append(point)
        
        # Fallback: extract any meaningful lines
        if len(key_points) < 3:
            meaningful_lines = [
                line.strip() for line in lines 
                if line.strip() and len(line.strip()) > 10 and not line.strip().startswith(('Bạn', 'Tôi', 'Hãy'))
            ]
            key_points.extend(meaningful_lines[:5-len(key_points)])
        
        return key_points[:5]
    
    def _calculate_summary_confidence(self, response: str, context: str) -> float:
        """Calculate confidence score for summary"""
        confidence = 0.5  # Base confidence
        
        # Check if response contains specific information
        if any(keyword in response.lower() for keyword in ['giảm', 'ưu đãi', 'voucher', 'áp dụng']):
            confidence += 0.2
        
        # Check response length
        if 100 < len(response) < 1000:
            confidence += 0.1
        
        # Check if response follows format
        if any(str(i) in response for i in range(1, 6)):
            confidence += 0.15
        
        # Check context relevance
        context_keywords = ['voucher', 'giảm', 'ưu đãi', 'áp dụng', 'sử dụng']
        matching_keywords = sum(1 for keyword in context_keywords if keyword in response.lower())
        confidence += min(0.05 * matching_keywords, 0.15)
        
        return min(confidence, 1.0)
    
    def _calculate_qa_confidence(self, question: str, context: str, answer: str) -> float:
        """Calculate confidence score for Q&A"""
        confidence = 0.4  # Base confidence
        
        # Check if answer is relevant to question
        question_words = set(question.lower().split())
        answer_words = set(answer.lower().split())
        overlap = len(question_words & answer_words)
        confidence += min(overlap * 0.05, 0.2)
        
        # Check if answer contains specific information
        if any(keyword in answer.lower() for keyword in ['có thể', 'không thể', 'áp dụng', 'không áp dụng']):
            confidence += 0.2
        
        # Check answer quality
        if 20 < len(answer) < 500:
            confidence += 0.1
        
        # Check if answer avoids generic responses
        generic_phrases = ['xin lỗi', 'không thể trả lời', 'không rõ']
        if not any(phrase in answer.lower() for phrase in generic_phrases):
            confidence += 0.1
        
        return min(confidence, 1.0)
    
    def _extract_sources(self, context: str) -> list[str]:
        """Extract source information from context"""
        sources = []
        
        if 'mô tả' in context.lower():
            sources.append('voucher_description')
        if 'điều khoản' in context.lower() or 'điều kiện' in context.lower():
            sources.append('terms_conditions')
        if 'hướng dẫn' in context.lower() or 'sử dụng' in context.lower():
            sources.append('usage_instructions')
        
        return sources if sources else ['voucher_info']
    
    async def _fallback_summary(self, voucher_context: str, voucher_name: str) -> Dict[str, Any]:
        """Fallback summary when Vertex AI fails"""
        # Simple rule-based summary
        fallback_points = [
            "Voucher có điều khoản và điều kiện áp dụng",
            "Vui lòng đọc kỹ hướng dẫn sử dụng",
            "Liên hệ hotline 1900 558 865 để được hỗ trợ",
            "Kiểm tra thời hạn sử dụng trước khi áp dụng"
        ]
        
        return {
            "summary": "Không thể tạo tóm tắt chi tiết. Vui lòng xem thông tin đầy đủ hoặc liên hệ hỗ trợ.",
            "key_points": fallback_points,
            "confidence": 0.3
        }
    
    async def _fallback_answer(self, question: str) -> Dict[str, Any]:
        """Fallback answer when Vertex AI fails"""
        return {
            "answer": "Xin lỗi, tôi không thể trả lời câu hỏi này lúc này do lỗi hệ thống. Vui lòng liên hệ hotline 1900 558 865 để được hỗ trợ chi tiết.",
            "confidence": 0.0,
            "sources": []
        }

# Function to get appropriate LLM service
def get_llm_service():
    """Get LLM service based on configuration"""
    if settings.VERTEX_AI_ENDPOINT and settings.GOOGLE_PROJECT_ID:
        try:
            return RealVertexAIService()
        except Exception as e:
            logger.warning(f"Failed to initialize Vertex AI, using mock service: {e}")
    
    # Fall back to mock service for development
    from llm_service import VertexAIService
    return VertexAIService()
