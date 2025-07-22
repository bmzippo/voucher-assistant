#!/usr/bin/env python3
"""
Unified Search Demo - Showcasing all search modes
RAG vs Vector vs Hybrid comparison
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
logging.basicConfig(level=logging.WARNING)

def print_search_comparison(query, rag_result, vector_result, hybrid_result):
    """Compare results from different search modes"""
    
    print("=" * 80)
    print(f"🔍 SEARCH COMPARISON FOR: '{query}'")
    print("=" * 80)
    
    # RAG Results
    print("\n🤖 RAG SEARCH (Full AI Pipeline):")
    print("-" * 50)
    print(f"⏱️  Time: {rag_result.processing_time:.2f}s")
    print(f"🎯 Confidence: {rag_result.confidence_score:.3f}")
    print(f"📊 Results: {len(rag_result.retrieved_vouchers)}")
    print(f"🧠 Method: {rag_result.search_method}")
    print("\n📝 AI Generated Answer:")
    print(rag_result.answer[:300] + "..." if len(rag_result.answer) > 300 else rag_result.answer)
    
    # Vector Results  
    print("\n🎯 VECTOR SEARCH (Pure Semantic):")
    print("-" * 50)
    print(f"🎯 Confidence: {vector_result.confidence_score:.3f}")
    print(f"📊 Results: {len(vector_result.retrieved_vouchers)}")
    print(f"🧠 Method: {vector_result.search_method}")
    if vector_result.retrieved_vouchers:
        top_result = vector_result.retrieved_vouchers[0]
        print(f"🏆 Top match: {top_result.get('voucher_name', 'N/A')}")
        print(f"   Similarity: {top_result.get('similarity_score', 0):.2f}")
    
    # Hybrid Results
    print("\n⚡ HYBRID SEARCH (Vector + Basic Context):")
    print("-" * 50)
    print(f"🎯 Confidence: {hybrid_result.confidence_score:.3f}")
    print(f"📊 Results: {len(hybrid_result.retrieved_vouchers)}")
    print(f"🧠 Method: {hybrid_result.search_method}")
    print("\n📝 Hybrid Response:")
    print(hybrid_result.answer[:300] + "..." if len(hybrid_result.answer) > 300 else hybrid_result.answer)
    
    print("\n" + "=" * 80 + "\n")

async def demo_unified_search():
    """Demo unified search interface with all modes"""
    
    print("🚀 UNIFIED SEARCH INTERFACE DEMO")
    print("🎯 RAG vs Vector vs Hybrid Comparison")
    print("=" * 60)
    
    # Initialize vector store
    vector_store = AdvancedVectorStore(index_name="voucher_knowledge")
    await asyncio.sleep(1)
    
    # Test queries for comparison
    test_queries = [
        "Tôi muốn tìm voucher buffet hải sản ở Hồ Chí Minh cho gia đình",
        "Có voucher spa massage nào không quá đắt không?",
        "Voucher nào phù hợp cho hẹn hò lãng mạn?"
    ]
    
    for query in test_queries:
        print(f"\n🔍 Testing Query: '{query}'")
        print("🔄 Running all search modes...")
        
        # Run all search modes in parallel for fair comparison
        rag_task = vector_store.search(query, search_type="rag", top_k=3)
        vector_task = vector_store.search(query, search_type="vector", top_k=3)  
        hybrid_task = vector_store.search(query, search_type="hybrid", top_k=3)
        
        rag_result, vector_result, hybrid_result = await asyncio.gather(
            rag_task, vector_task, hybrid_task
        )
        
        # Display comparison
        print_search_comparison(query, rag_result, vector_result, hybrid_result)
        
        # Pause between queries
        await asyncio.sleep(1)

async def demo_search_modes():
    """Interactive demo of different search modes"""
    
    print("\n🎮 INTERACTIVE SEARCH MODE DEMO")
    print("=" * 50)
    print("Available modes:")
    print("1. 'rag' - Full RAG pipeline with AI generation")
    print("2. 'vector' - Pure vector similarity search")  
    print("3. 'hybrid' - Vector search + basic context")
    print("4. Type 'exit' to quit\n")
    
    vector_store = AdvancedVectorStore(index_name="voucher_knowledge")
    await asyncio.sleep(1)
    
    while True:
        try:
            # Get user input
            user_input = input("❓ Enter query and mode (e.g., 'buffet ở Hà Nội, rag'): ").strip()
            
            if user_input.lower() in ['exit', 'quit', 'thoát']:
                print("👋 Demo ended!")
                break
            
            if ',' in user_input:
                query, mode = [x.strip() for x in user_input.split(',', 1)]
            else:
                query = user_input
                mode = input("🔧 Search mode (rag/vector/hybrid): ").strip() or "rag"
            
            if not query:
                print("⚠️  Please enter a query.")
                continue
            
            if mode not in ['rag', 'vector', 'hybrid']:
                print("⚠️  Invalid mode. Use 'rag', 'vector', or 'hybrid'.")
                continue
            
            print(f"\n🔍 Searching with mode: '{mode}'...")
            
            # Perform search
            result = await vector_store.search(query, search_type=mode, top_k=5)
            
            # Display results
            print(f"\n🎯 RESULTS ({mode.upper()} MODE):")
            print("-" * 40)
            print(f"⏱️  Processing time: {getattr(result, 'processing_time', 0):.2f}s")
            print(f"🎯 Confidence: {result.confidence_score:.3f}")
            print(f"📊 Results found: {len(result.retrieved_vouchers)}")
            print(f"🧠 Search method: {result.search_method}")
            
            if mode == 'rag':
                print(f"\n🤖 AI Generated Answer:")
                print(result.answer)
            elif mode == 'hybrid':
                print(f"\n⚡ Hybrid Response:")
                print(result.answer)
            else:
                print(f"\n📋 Top Results:")
                for i, voucher in enumerate(result.retrieved_vouchers[:3], 1):
                    print(f"  {i}. {voucher.get('voucher_name', 'N/A')}")
                    print(f"     Similarity: {voucher.get('similarity_score', 0):.2f}")
            
            print("\n" + "-" * 60 + "\n")
            
        except KeyboardInterrupt:
            print("\n👋 Demo stopped by user.")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

async def quick_mode_comparison():
    """Quick demonstration of all modes"""
    
    print("⚡ QUICK MODE COMPARISON")
    print("=" * 40)
    
    vector_store = AdvancedVectorStore(index_name="voucher_knowledge")
    await asyncio.sleep(1)
    
    query = "buffet hải sản cho gia đình ở TP.HCM"
    print(f"🎯 Test query: '{query}'\n")
    
    # Test all modes
    modes = ['rag', 'vector', 'hybrid']
    results = {}
    
    for mode in modes:
        print(f"🔍 Testing {mode.upper()} mode...")
        result = await vector_store.search(query, search_type=mode, top_k=3)
        results[mode] = result
        
        print(f"   Confidence: {result.confidence_score:.3f}")
        print(f"   Results: {len(result.retrieved_vouchers)}")
        print(f"   Method: {result.search_method}")
        if hasattr(result, 'processing_time'):
            print(f"   Time: {result.processing_time:.2f}s")
        print()
    
    # Summary
    print("📊 COMPARISON SUMMARY:")
    print("-" * 30)
    for mode, result in results.items():
        print(f"{mode.upper():8}: {result.confidence_score:.3f} confidence, {len(result.retrieved_vouchers)} results")
    
    print(f"\n✅ All search modes operational!")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Unified Search Demo")
    parser.add_argument("--compare", action="store_true", help="Run comparison demo")
    parser.add_argument("--interactive", action="store_true", help="Run interactive demo")
    parser.add_argument("--quick", action="store_true", help="Run quick mode comparison")
    
    args = parser.parse_args()
    
    if args.compare:
        asyncio.run(demo_unified_search())
    elif args.interactive:
        asyncio.run(demo_search_modes())
    elif args.quick:
        asyncio.run(quick_mode_comparison())
    else:
        print("🚀 Running default quick comparison...")
        asyncio.run(quick_mode_comparison())
