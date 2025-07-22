import asyncio
import sys
import os

# Add the backend directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'voucher_assistant', 'backend'))

from vector_store import VectorStore

async def test_query_logging():
    """Test ES query logging in vector search and hybrid search"""
    print("=== Testing ES Query Logging ===")
    
    # Initialize vector store
    vector_store = VectorStore()
    
    if not vector_store.is_ready:
        print("❌ Vector store not ready")
        return
    
    test_query = "voucher pizza"
    
    print(f"\n1. Testing Vector Search with query: '{test_query}'")
    print("-" * 50)
    vector_results = await vector_store.vector_search(test_query, top_k=3)
    print(f"Found {len(vector_results)} vector results")
    
    print(f"\n2. Testing Hybrid Search with query: '{test_query}'")
    print("-" * 50)
    hybrid_results = await vector_store.hybrid_search(test_query, top_k=3)
    print(f"Hybrid results - Vector: {hybrid_results['total_vector_results']}, Text: {hybrid_results['total_text_results']}")
    
    print("\n✅ ES Query logging test completed")

if __name__ == "__main__":
    asyncio.run(test_query_logging())
