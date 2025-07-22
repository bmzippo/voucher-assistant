#!/usr/bin/env python3

"""
Test vector search on content field to verify embedding indexing
"""

import asyncio
import logging
from pathlib import Path
import sys

# Add the backend directory to the Python path
sys.path.append(str(Path(__file__).parent))

from advanced_vector_store import AdvancedVectorStore

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_vector_search_content():
    """Test vector search on content field"""
    
    print("🔍 Testing Vector Search on Content Field")
    print("="*60)
    
    # Initialize vector store
    vector_store = AdvancedVectorStore()
    print("🤖 Initialized AdvancedVectorStore")
    
    # Test queries to search for content
    test_queries = [
        "cafe cà phê RuNam",  # Should find RuNam vouchers
        "giảm giá voucher",   # General voucher terms
        "DriverX tài xế",     # Should find DriverX voucher
        "thuê xe hộ",         # Related to DriverX service
        "thức ăn đồ uống"     # Food and beverage
    ]
    
    print(f"🎯 Testing {len(test_queries)} search queries...")
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n--- Query {i}: '{query}' ---")
        
        try:
            # Perform vector search
            results = await vector_store.advanced_vector_search(
                query=query,
                top_k=3
            )
            
            print(f"📊 Found {len(results)} results for '{query}'")
            
            if results:
                for j, result in enumerate(results, 1):
                    print(f"  {j}. {result['voucher_name']} (Score: {result['similarity_score']:.3f})")
                    print(f"     ID: {result['voucher_id']}")
                    
                    # Check if content was used in search
                    content_preview = result.get('content', '')[:100]
                    if content_preview:
                        print(f"     Content: {content_preview}...")
                    else:
                        print(f"     ⚠️  No content found in result")
                    print()
            else:
                print(f"  ❌ No results found for '{query}'")
                
        except Exception as e:
            print(f"  ❌ Error searching for '{query}': {e}")
    
    # Additional test: Check ES mapping and documents directly
    print("\n" + "="*60)
    print("🔧 Checking ES Index Structure")
    
    try:
        # Check index mapping
        mapping = vector_store.es.indices.get_mapping(index="voucher_knowledge")
        content_mapping = mapping['voucher_knowledge']['mappings']['properties'].get('content_embedding')
        
        if content_mapping:
            print(f"✅ content_embedding field exists in mapping")
            print(f"   Type: {content_mapping.get('type')}")
            print(f"   Dims: {content_mapping.get('dims')}")
        else:
            print("❌ content_embedding field not found in mapping")
        
        # Check a few documents
        search_result = vector_store.es.search(
            index="voucher_knowledge",
            body={
                "query": {"match_all": {}},
                "size": 2,
                "_source": ["voucher_id", "voucher_name", "content"]
            }
        )
        
        print(f"\n📄 Sample documents in ES:")
        for hit in search_result['hits']['hits']:
            source = hit['_source']
            content_length = len(source.get('content', ''))
            print(f"  - {source['voucher_id']}: {source['voucher_name']}")
            print(f"    Content length: {content_length} chars")
            if content_length > 0:
                print(f"    Content preview: {source['content'][:80]}...")
            else:
                print(f"    ⚠️  Content is empty!")
            print()
            
    except Exception as e:
        print(f"❌ Error checking ES structure: {e}")
    
    print("🎉 Vector search test completed!")

if __name__ == "__main__":
    asyncio.run(test_vector_search_content())
