#!/usr/bin/env python3
"""
Demo script for Voucher AI Assistant RAG Pipeline
Showcases the complete Retrieval + Generation system
"""

import asyncio
import sys
import os
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent))

from advanced_vector_store import AdvancedVectorStore
import logging

# Configure logging
logging.basicConfig(level=logging.WARNING)  # Reduce noise for demo

def print_header(title):
    """Print formatted header"""
    print("\n" + "=" * 60)
    print(f"🎯 {title}")
    print("=" * 60)

def print_rag_response(response, query):
    """Print formatted RAG response"""
    print(f"❓ **Câu hỏi**: {query}")
    print(f"⏱️  **Thời gian xử lý**: {response.processing_time:.2f}s")
    print(f"🎯 **Độ tin cậy**: {response.confidence_score:.3f}")
    print(f"📊 **Số voucher tìm thấy**: {len(response.retrieved_vouchers)}")
    
    if response.query_intent:
        print("🧠 **Phân tích ý định**:")
        for intent, score in response.query_intent.items():
            if score and score != 'unknown':
                print(f"   • {intent}: {score}")
    
    print("\n🤖 **Câu trả lời AI**:")
    print("-" * 40)
    print(response.answer)
    print("-" * 40)
    
    if response.retrieved_vouchers:
        print(f"\n📋 **Top 3 voucher phù hợp**:")
        for i, voucher in enumerate(response.retrieved_vouchers[:3], 1):
            print(f"\n   {i}. **{voucher.get('voucher_name', 'N/A')}**")
            print(f"      📍 Địa điểm: {voucher.get('location', {}).get('name', 'N/A')}")
            print(f"      🏪 Dịch vụ: {voucher.get('service_info', {}).get('category', 'N/A')}")
            print(f"      ⭐ Độ phù hợp: {voucher.get('similarity_score', 0):.1f}%")

async def demo_rag_pipeline():
    """Interactive demo of the RAG pipeline"""
    
    print_header("VOUCHER AI ASSISTANT - RAG PIPELINE DEMO")
    print("🤖 Trợ lý AI thông minh cho voucher  ")
    print("🧠 Powered by Advanced Vector Search + LLM Integration")
    
    # Initialize vector store
    vector_store = AdvancedVectorStore(index_name="voucher_knowledge")
    
    # Wait for system to be ready
    await asyncio.sleep(1)
    
    # Demo scenarios showcasing different capabilities
    demo_scenarios = [
        {
            "title": "Tìm kiếm theo Location + Service + Target",
            "query": "Tôi muốn tìm voucher buffet ở Hà Nội cho gia đình 4 người",
            "description": "Demonstrates multi-intent processing with location, service type, and target audience"
        },
        {
            "title": "Tìm kiếm theo Service + Price Consideration", 
            "query": "Có voucher massage spa nào không quá đắt không?",
            "description": "Shows service-specific search with price sensitivity"
        },
        {
            "title": "Tìm kiếm theo Target Audience",
            "query": "Voucher nào phù hợp cho hẹn hò lãng mạn?",
            "description": "Focuses on target audience and romantic context"
        },
        {
            "title": "Tìm kiếm cụ thể hải sản",
            "query": "Tôi muốn ăn buffet hải sản ở TP.HCM",
            "description": "Specific food type with location targeting"
        },
        {
            "title": "Tìm kiếm trending vouchers",
            "query": "Voucher khuyến mãi gì hot nhất hiện tại?",
            "description": "General trending query for popular offers"
        }
    ]
    
    print(f"\n🎬 **DEMO: {len(demo_scenarios)} tình huống thực tế**\n")
    
    # Run demo scenarios
    for i, scenario in enumerate(demo_scenarios, 1):
        print_header(f"SCENARIO {i}: {scenario['title']}")
        print(f"📝 **Mô tả**: {scenario['description']}")
        
        try:
            # Get RAG response
            response = await vector_store.rag_search_with_llm(
                query=scenario['query'],
                top_k=5
            )
            
            # Display results
            print_rag_response(response, scenario['query'])
            
        except Exception as e:
            print(f"❌ **Lỗi**: {e}")
        
        # Pause between scenarios
        if i < len(demo_scenarios):
            print("\n" + "⏳ Processing next scenario..." + "\n")
            await asyncio.sleep(2)
    
    # Interactive section
    print_header("INTERACTIVE MODE")
    print("💬 **Thử nghiệm câu hỏi của riêng bạn**")
    print("🚪 **Gõ 'exit' để thoát**\n")
    
    while True:
        try:
            # Get user input
            user_query = input("❓ **Câu hỏi của bạn**: ").strip()
            
            if user_query.lower() in ['exit', 'quit', 'thoát']:
                print("👋 Cảm ơn bạn đã sử dụng Voucher AI Assistant!")
                break
            
            if not user_query:
                print("⚠️  Vui lòng nhập câu hỏi.")
                continue
            
            print("\n🔍 **Đang xử lý...**")
            
            # Get RAG response
            response = await vector_store.rag_search_with_llm(query=user_query)
            
            # Display results
            print_rag_response(response, user_query)
            print("\n" + "-" * 60 + "\n")
            
        except KeyboardInterrupt:
            print("\n👋 Demo đã được dừng bởi người dùng.")
            break
        except Exception as e:
            print(f"❌ **Lỗi**: {e}")
            print("🔄 Vui lòng thử lại.\n")

async def quick_demo():
    """Quick demo showing key capabilities"""
    
    print_header("QUICK DEMO - Key RAG Capabilities")
    
    vector_store = AdvancedVectorStore(index_name="voucher_knowledge")
    await asyncio.sleep(1)
    
    # Quick test query
    test_query = "Tìm voucher buffet hải sản cho gia đình ở Hồ Chí Minh"
    
    print(f"🎯 **Test Query**: {test_query}")
    print("🔍 **Processing...**\n")
    
    response = await vector_store.rag_search_with_llm(query=test_query)
    
    # Quick summary
    print("📊 **QUICK RESULTS SUMMARY**:")
    print(f"   ⏱️  Processing: {response.processing_time:.2f}s")
    print(f"   🎯 Confidence: {response.confidence_score:.3f}")
    print(f"   📈 Results: {len(response.retrieved_vouchers)} vouchers")
    print(f"   🔍 Method: {response.search_method}")
    
    print(f"\n🤖 **AI Response Preview**:")
    preview = response.answer[:150] + "..." if len(response.answer) > 150 else response.answer
    print(f"   {preview}")
    
    print(f"\n✅ **RAG Pipeline Status: OPERATIONAL**")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Voucher AI Assistant RAG Demo")
    parser.add_argument("--quick", action="store_true", help="Run quick demo")
    parser.add_argument("--full", action="store_true", help="Run full interactive demo")
    
    args = parser.parse_args()
    
    if args.quick:
        asyncio.run(quick_demo())
    elif args.full:
        asyncio.run(demo_rag_pipeline())
    else:
        # Default: run quick demo
        print("🚀 **Running Quick Demo** (use --full for interactive mode)")
        asyncio.run(quick_demo())
