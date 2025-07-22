#!/usr/bin/env python3
"""
Test script để kiểm tra content đã được tạo và index với VoucherContentGenerator
"""

import asyncio
import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent))
sys.path.append(str(Path(__file__).parent / "voucher_assistant" / "backend"))

from advanced_vector_store import AdvancedVectorStore
from elasticsearch import Elasticsearch

def test_indexed_content():
    """
    Kiểm tra content trong ES để xem VoucherContentGenerator có hoạt động không
    """
    print("Testing Indexed Content with VoucherContentGenerator")
    print("=" * 60)
    
    try:
        # Connect to ES
        es = Elasticsearch("http://localhost:9200")
        index_name = "voucher_knowledge"
        
        # Get some sample documents
        query = {
            "query": {
                "match_all": {}
            },
            "size": 5,
            "_source": ["voucher_id", "voucher_name", "content", "merchant", "price", "location"]
        }
        
        response = es.search(index=index_name, body=query)
        
        print(f"Found {response['hits']['total']['value']} total documents")
        print(f"Showing first {len(response['hits']['hits'])} documents:")
        print()
        
        for i, hit in enumerate(response['hits']['hits'], 1):
            source = hit['_source']
            print(f"DOCUMENT {i}:")
            print(f"Voucher ID: {source.get('voucher_id', 'N/A')}")
            print(f"Voucher Name: {source.get('voucher_name', 'N/A')}")
            print(f"Merchant: {source.get('merchant', 'N/A')}")
            print(f"Price: {source.get('price', 'N/A')}")
            print(f"Location: {source.get('location', 'N/A')}")
            
            content = source.get('content', '')
            print(f"Content Length: {len(content)} characters")
            print("Content Preview:")
            print("-" * 40)
            print(content[:300] + "..." if len(content) > 300 else content)
            print("-" * 40)
            print()
            
            # Check if content follows the new format
            has_merchant_line = "- Merchant:" in content
            has_price_line = "- Giá đổi voucher:" in content
            has_terms_line = "- Điều kiện sử dụng:" in content
            has_location_line = "- Địa chỉ nhà hàng cung cấp dịch vụ" in content
            
            print("Content Format Check:")
            print(f"  ✅ Has Merchant line: {has_merchant_line}")
            print(f"  ✅ Has Price line: {has_price_line}")
            print(f"  ✅ Has Terms line: {has_terms_line}")
            print(f"  ✅ Has Location line: {has_location_line}")
            
            if has_merchant_line and has_price_line and (has_terms_line or has_location_line):
                print("  🎉 Content follows NEW format (VoucherContentGenerator)")
            else:
                print("  ⚠️  Content might be using OLD format")
            
            print("=" * 60)
            print()
    
    except Exception as e:
        print(f"❌ Error checking indexed content: {e}")

def test_vector_search_with_new_content():
    """
    Test vector search để xem content mới có searchable không
    """
    print("Testing Vector Search with New Content Format")
    print("=" * 50)
    
    try:
        vector_store = AdvancedVectorStore()
        
        # Test queries that should work better with structured content
        test_queries = [
            "buffet lẩu nướng hàn quốc",
            "nhà hàng cao cấp ở hà nội",
            "voucher có giá 299000",
            "merchant pizza hut"
        ]
        
        for query in test_queries:
            print(f"Query: '{query}'")
            print("-" * 30)
            
            try:
                results = vector_store.advanced_vector_search(query, limit=3)
                
                print(f"Found {len(results)} results:")
                for i, result in enumerate(results, 1):
                    score = result.get('score', 0)
                    content = result.get('content', '')[:150] + "..."
                    voucher_name = result.get('voucher_name', 'N/A')
                    
                    print(f"  {i}. {voucher_name} (Score: {score:.3f})")
                    print(f"     Content: {content}")
                    print()
                
            except Exception as e:
                print(f"❌ Error with query '{query}': {e}")
            
            print("-" * 50)
    
    except Exception as e:
        print(f"❌ Error setting up vector search: {e}")

if __name__ == "__main__":
    test_indexed_content()
    print()
    test_vector_search_with_new_content()
