#!/usr/bin/env python3
"""
Demo script để test OneU AI Voucher Assistant
"""

import asyncio
import sys
import os
sys.path.append('backend')

from backend.vector_store import VectorStore
from backend.llm_service import VertexAIService
from backend.models import VoucherData
import json

async def test_voucher_assistant():
    """Test the voucher assistant functionality"""
    
    print("=== OneU AI Voucher Assistant Demo ===\n")
    
    # Initialize services
    vector_store = VectorStore()
    llm_service = VertexAIService()
    
    try:
        # Create index
        await vector_store.create_index()
        print("✓ Elasticsearch index created")
        
        # Sample voucher data
        sample_voucher = VoucherData(
            name="Giảm VND 200,000 - RuNam",
            description="Cafe RuNam đã không ngừng nghiên cứu, tìm hiểu và phát triển cà phê mang đậm thương hiệu Việt. Thực đơn đa dạng, món ăn được trình bày đẹp mắt và hương vị đậm đà sẽ đem đến cho thực khách một trải nghiệm tuyệt vời.",
            usage_instructions="Khách hàng đổi điểm để lấy voucher trên App OneU sau đó đến cửa hàng xuất trình voucher cho thu ngân trước khi thanh toán để sử dụng ưu đãi.",
            terms_of_use="Voucher áp dụng tại tất cả các cửa hàng Runam. Áp dụng tối đa 30 voucher trên 01 hóa đơn. Voucher chỉ có giá trị sử dụng một lần. Không chấp nhận voucher quá hạn sử dụng.",
            tags="cafe, food, runam",
            price=150000,
            unit=1,
            merchant="Runam"
        )
        
        voucher_id = "demo_voucher_runam"
        
        # Add voucher to knowledge base
        await vector_store.add_document(
            content=sample_voucher.description,
            voucher_id=voucher_id,
            voucher_name=sample_voucher.name,
            merchant=sample_voucher.merchant,
            section="description",
            metadata={"price": sample_voucher.price}
        )
        
        await vector_store.add_document(
            content=sample_voucher.usage_instructions,
            voucher_id=voucher_id,
            voucher_name=sample_voucher.name,
            merchant=sample_voucher.merchant,
            section="usage",
            metadata={"price": sample_voucher.price}
        )
        
        await vector_store.add_document(
            content=sample_voucher.terms_of_use,
            voucher_id=voucher_id,
            voucher_name=sample_voucher.name,
            merchant=sample_voucher.merchant,
            section="terms",
            metadata={"price": sample_voucher.price}
        )
        
        print("✓ Sample voucher added to knowledge base")
        
        # Test search functionality
        print("\n=== Testing Search ===")
        search_results = await vector_store.search_similar(
            "cách sử dụng voucher", 
            voucher_id=voucher_id,
            top_k=3
        )
        
        for i, result in enumerate(search_results):
            print(f"{i+1}. Score: {result['score']:.3f}")
            print(f"   Section: {result['section']}")
            print(f"   Content: {result['content'][:100]}...")
            print()
        
        # Test summary generation
        print("=== Testing Summary Generation ===")
        context = await vector_store.get_voucher_context(voucher_id)
        summary_result = await llm_service.generate_summary(context, sample_voucher.name)
        
        print("Generated Summary:")
        print(summary_result["summary"])
        print("\nKey Points:")
        for point in summary_result["key_points"]:
            print(f"• {point}")
        
        # Test Q&A
        print("\n=== Testing Q&A ===")
        questions = [
            "Voucher này có thời hạn sử dụng không?",
            "Tôi có thể sử dụng bao nhiều voucher cùng lúc?",
            "Làm sao để sử dụng voucher này?"
        ]
        
        for question in questions:
            print(f"\nQ: {question}")
            answer_result = await llm_service.answer_question(
                question, context, sample_voucher.name
            )
            print(f"A: {answer_result['answer']}")
            print(f"Confidence: {answer_result['confidence']:.2f}")
        
        print("\n=== Demo Complete ===")
        print("✓ All functionality tested successfully!")
        
    except Exception as e:
        print(f"❌ Error during demo: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_voucher_assistant())
