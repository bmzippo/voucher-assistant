import asyncio
import sys
import os
import logging

# Add the backend directory to Python path
sys.path.append(os.path.join(os.getcwd(), 'voucher_assistant', 'backend'))

from advanced_vector_store import AdvancedVectorStore

logging.basicConfig(level=logging.INFO)

async def test_detailed():
    """Test with detailed logging"""
    print("=== Testing Multi-Field Search with Detailed Logs ===")
    
    store = AdvancedVectorStore()
    results = await store.advanced_vector_search('buffet tại Hải Phòng', top_k=2)
    
    print(f"\n✅ Results: {len(results)}")
    for result in results:
        print(f"- {result['voucher_name'][:60]}... (score: {result['similarity_score']})")

if __name__ == "__main__":
    asyncio.run(test_detailed())
