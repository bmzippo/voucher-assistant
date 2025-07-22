import asyncio
import sys
import os

# Add the backend directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'voucher_assistant', 'backend'))

from advanced_vector_store import AdvancedVectorStore

async def test_multi_field_search():
    """Test multi-field embedding search"""
    print("=== Testing Multi-Field Embedding Search ===")
    
    # Initialize advanced vector store
    advanced_store = AdvancedVectorStore()
    
    test_queries = [
        "buffet tại Hải Phòng",  # Location intent high
        "spa cho gia đình",      # Target intent high  
        "nhà hàng buffet",       # Service intent high
        "voucher pizza"          # General content
    ]
    
    for query in test_queries:
        print(f"\n🔍 Testing query: '{query}'")
        print("-" * 50)
        
        results = await advanced_store.advanced_vector_search(query, top_k=3)
        
        print(f"✅ Found {len(results)} results")
        for i, result in enumerate(results[:2], 1):
            print(f"  {i}. {result['voucher_name'][:50]}... (score: {result['similarity_score']})")
    
    print("\n✅ Multi-field search test completed")

if __name__ == "__main__":
    asyncio.run(test_multi_field_search())
