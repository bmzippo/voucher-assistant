#!/usr/bin/env python3
"""
Test script for complete RAG pipeline
Tests the integration of retrieval and generation components
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
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_rag_pipeline():
    """Test complete RAG pipeline with various queries"""
    
    print("🚀 Starting RAG Pipeline Test")
    print("=" * 60)
    
    # Initialize vector store
    vector_store = AdvancedVectorStore(
        index_name="voucher_knowledge"
    )
    
    # Wait for ES to be ready
    await asyncio.sleep(2)
    
    # Test queries covering different scenarios
    test_queries = [
        {
            "query": "Tôi muốn tìm voucher buffet ở Hà Nội cho gia đình 4 người",
            "description": "Family buffet query with location and group size",
            "expected_intent": ["location", "service", "target"]
        },
        {
            "query": "Có voucher massage spa nào không quá đắt không?",
            "description": "Service-specific query with price consideration",
            "expected_intent": ["service", "price"]
        },
        {
            "query": "Voucher nào phù hợp cho hẹn hò lãng mạn?",
            "description": "Target audience specific query",
            "expected_intent": ["target", "service"]
        },
        {
            "query": "Tôi muốn đặt bàn ăn tối ở quận 1",
            "description": "Location and service specific query",
            "expected_intent": ["location", "service"]
        },
        {
            "query": "Voucher khuyến mãi gì hot nhất hiện tại?",
            "description": "General trending query",
            "expected_intent": ["content"]
        }
    ]
    
    print(f"🧪 Testing {len(test_queries)} different query scenarios\n")
    
    results = []
    
    for i, test_case in enumerate(test_queries, 1):
        print(f"📋 TEST {i}: {test_case['description']}")
        print(f"❓ Query: '{test_case['query']}'")
        print("-" * 40)
        
        try:
            # Call RAG pipeline using unified search interface
            rag_response = await vector_store.search(
                query=test_case['query'],
                search_type="rag",  # Use full RAG pipeline
                top_k=3
            )
            
            # Display results
            print(f"⏱️  Processing time: {rag_response.processing_time:.2f}s")
            print(f"🎯 Confidence score: {rag_response.confidence_score:.3f}")
            print(f"📊 Retrieved vouchers: {len(rag_response.retrieved_vouchers)}")
            print(f"🔍 Search method: {rag_response.search_method}")
            
            # Show query intent analysis
            if rag_response.query_intent:
                print("🧠 Query intent analysis:")
                for intent, score in rag_response.query_intent.items():
                    if score > 0:
                        print(f"   {intent}: {score}")
            
            # Show top retrieved voucher
            if rag_response.retrieved_vouchers:
                top_voucher = rag_response.retrieved_vouchers[0]
                print(f"🏆 Top match: {top_voucher.get('voucher_name', 'N/A')}")
                print(f"   Similarity: {top_voucher.get('similarity_score', 0):.2f}")
            
            # Show generated answer (truncated)
            answer_preview = rag_response.answer[:200] + "..." if len(rag_response.answer) > 200 else rag_response.answer
            print(f"🤖 Generated answer preview:\n{answer_preview}")
            
            # Store results for summary
            results.append({
                'query': test_case['query'],
                'success': True,
                'confidence': rag_response.confidence_score,
                'retrieval_count': len(rag_response.retrieved_vouchers),
                'processing_time': rag_response.processing_time
            })
            
        except Exception as e:
            print(f"❌ Error in RAG pipeline: {e}")
            results.append({
                'query': test_case['query'],
                'success': False,
                'error': str(e)
            })
        
        print("\n" + "=" * 60 + "\n")
    
    # Print summary
    print("📊 RAG PIPELINE TEST SUMMARY")
    print("=" * 60)
    
    successful_tests = [r for r in results if r['success']]
    failed_tests = [r for r in results if not r['success']]
    
    print(f"✅ Successful tests: {len(successful_tests)}/{len(results)}")
    print(f"❌ Failed tests: {len(failed_tests)}")
    
    if successful_tests:
        avg_confidence = sum(r['confidence'] for r in successful_tests) / len(successful_tests)
        avg_processing_time = sum(r['processing_time'] for r in successful_tests) / len(successful_tests)
        avg_retrieval_count = sum(r['retrieval_count'] for r in successful_tests) / len(successful_tests)
        
        print(f"📈 Average confidence: {avg_confidence:.3f}")
        print(f"⏱️  Average processing time: {avg_processing_time:.2f}s")
        print(f"📊 Average retrieval count: {avg_retrieval_count:.1f}")
    
    if failed_tests:
        print("\n❌ Failed test details:")
        for test in failed_tests:
            print(f"   Query: {test['query']}")
            print(f"   Error: {test['error']}")
    
    print("\n🎉 RAG Pipeline test completed!")

async def test_specific_rag_query():
    """Test a specific query with detailed output"""
    
    print("\n🔬 DETAILED RAG ANALYSIS")
    print("=" * 60)
    
    vector_store = AdvancedVectorStore(
        index_name="voucher_knowledge"
    )
    
    query = "Tôi muốn tìm voucher buffet hải sản ở Hồ Chí Minh cho gia đình"
    
    print(f"🎯 Query: '{query}'")
    print("-" * 40)
    
    # Get RAG response using unified interface
    rag_response = await vector_store.search(query, search_type="rag")
    
    # Detailed analysis
    print("📋 DETAILED RAG RESPONSE ANALYSIS:")
    print(f"Processing time: {rag_response.processing_time:.3f}s")
    print(f"Confidence score: {rag_response.confidence_score:.3f}")
    print(f"Search method: {rag_response.search_method}")
    
    print("\n🧠 Query Intent Analysis:")
    for intent, score in rag_response.query_intent.items():
        print(f"  {intent}: {score}")
    
    print(f"\n📊 Retrieved Vouchers ({len(rag_response.retrieved_vouchers)}):")
    for i, voucher in enumerate(rag_response.retrieved_vouchers, 1):
        print(f"\n  {i}. {voucher.get('voucher_name', 'N/A')}")
        print(f"     Content: {voucher.get('content', 'N/A')[:100]}...")
        print(f"     Location: {voucher.get('location', {}).get('name', 'N/A')}")
        print(f"     Service: {voucher.get('service_info', {}).get('category', 'N/A')}")
        print(f"     Similarity: {voucher.get('similarity_score', 0):.2f}")
    
    print(f"\n🤖 Generated Answer:")
    print(rag_response.answer)
    
    print("\n✅ Detailed analysis completed!")

if __name__ == "__main__":
    # Run tests
    asyncio.run(test_rag_pipeline())
    
    # Run detailed analysis
    asyncio.run(test_specific_rag_query())
