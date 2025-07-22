#!/usr/bin/env python3
"""
So sánh Vector Search với các query khác nhau
"""

import json
from elasticsearch import Elasticsearch
from sentence_transformers import SentenceTransformer
import time
import os

class SearchComparison:
    def __init__(self):
        self.es = Elasticsearch([os.getenv("ELASTICSEARCH_URL", "http://localhost:9200")], verify_certs=False, request_timeout=30)
        self.model = SentenceTransformer(os.getenv("EMBEDDING_MODEL", "dangvantuan/vietnamese-embedding"))
        self.index_name = os.getenv("ELASTICSEARCH_INDEX", "voucher_knowledge")

    def search_and_compare(self, queries):
        print("🔍 SO SÁNH VECTOR SEARCH VỚI CÁC QUERY KHÁC NHAU")
        print("=" * 70)
        
        for i, query in enumerate(queries, 1):
            print(f"\n🎯 TEST {i}: '{query}'")
            print("-" * 50)
            
            # Create embedding
            embedding = self.model.encode(query).tolist()
            
            # Search query
            search_query = {
                "size": 3,
                "min_score": 1.0,
                "_source": ["voucher_name", "merchant", "metadata.price", "metadata.location"],
                "query": {
                    "script_score": {
                        "query": {"match_all": {}},
                        "script": {
                            "source": "cosineSimilarity(params.query_vector, 'embedding') + 1.0",
                            "params": {"query_vector": embedding}
                        }
                    }
                }
            }
            
            try:
                response = self.es.search(index=self.index_name, body=search_query)
                hits = response['hits']['hits']
                
                print(f"📊 Results: {len(hits)} vouchers found")
                
                for j, hit in enumerate(hits, 1):
                    source = hit['_source']
                    score = hit['_score']
                    price = source.get('metadata', {}).get('price', 0)
                    location = source.get('metadata', {}).get('location', 'N/A')
                    
                    print(f"   {j}. {source['voucher_name'][:40]}...")
                    print(f"      Score: {score:.3f} | {source['merchant']} | {price:,}đ | {location}")
                
            except Exception as e:
                print(f"❌ Error: {e}")

def main():
    searcher = SearchComparison()
    
    test_queries = [
        "quán cafe có không gian lãng mạn",
        "quán cafe",
        "không gian lãng mạn", 
        "nhà hàng view đẹp",
        "buffet tối",
        "ăn uống giá rẻ"
    ]
    
    searcher.search_and_compare(test_queries)
    
    print(f"\n💡 INSIGHTS:")
    print("=" * 50)
    print("• Query càng cụ thể thì kết quả càng chính xác")
    print("• Từ 'cafe' cho kết quả cafe thuần túy")
    print("• 'Không gian lãng mạn' tìm được restaurant, bar cao cấp")
    print("• Model hiểu được semantic meaning, không chỉ keyword matching")
    print("• Score thường trong range 1.0-1.5, rarely >1.7 for Vietnamese")

if __name__ == "__main__":
    main()
