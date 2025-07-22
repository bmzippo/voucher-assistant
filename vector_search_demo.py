#!/usr/bin/env python3
"""
Vector Search Demo - Tìm kiếm voucher bằng semantic search
Tìm kiếm với từ khóa: "quán cafe có không gian lãng mạn"
"""

import json
from elasticsearch import Elasticsearch
from sentence_transformers import SentenceTransformer
from typing import List, Dict
import time
import os

class VoucherVectorSearchDemo:
    def __init__(self):
        self.es_url = os.getenv("ELASTICSEARCH_URL", "http://localhost:9200")
        self.index_name = os.getenv("ELASTICSEARCH_INDEX", "voucher_knowledge")
        self.model_name = os.getenv("EMBEDDING_MODEL", "keepitreal/vietnamese-sbert")
        
        # Initialize components
        self.es = Elasticsearch([self.es_url], verify_certs=False, request_timeout=30)
        self.model = SentenceTransformer(self.model_name)
        
        print(f"🔧 Connected to Elasticsearch: {self.es_url}")
        print(f"🤖 Loaded embedding model: {self.model_name}")

    def create_query_embedding(self, query: str) -> List[float]:
        """Tạo vector embedding cho câu query"""
        print(f"\n📝 Creating embedding for query: '{query}'")
        start_time = time.time()
        
        embedding = self.model.encode(query)
        embedding_time = time.time() - start_time
        
        print(f"⏱️  Embedding creation time: {embedding_time:.3f}s")
        print(f"📊 Embedding vector dimensions: {len(embedding)}")
        print(f"🔢 Sample embedding values: {embedding[:5].tolist()}")
        
        return embedding.tolist()

    def semantic_search(self, query: str, size: int = 5, min_score: float = 0.7) -> Dict:
        """Thực hiện semantic search sử dụng vector similarity"""
        print(f"\n🔍 Starting semantic search...")
        print(f"📋 Search parameters:")
        print(f"   - Query: '{query}'")
        print(f"   - Results size: {size}")
        print(f"   - Minimum score: {min_score}")
        
        # Bước 1: Tạo embedding cho query
        query_embedding = self.create_query_embedding(query)
        
        # Bước 2: Xây dựng Elasticsearch query
        search_query = {
            "size": size,
            "min_score": min_score,
            "_source": [
                "voucher_id", 
                "voucher_name", 
                "content", 
                "merchant", 
                "metadata.price",
                "metadata.location",
                "metadata.source_file"
            ],
            "query": {
                "script_score": {
                    "query": {"match_all": {}},
                    "script": {
                        "source": "cosineSimilarity(params.query_vector, 'embedding') + 1.0",
                        "params": {"query_vector": query_embedding}
                    }
                }
            }
        }
        
        print(f"\n🔧 Elasticsearch query structure:")
        print(f"   - Using script_score with cosine similarity")
        print(f"   - Query vector size: {len(query_embedding)}")
        
        # Bước 3: Thực hiện search
        search_start = time.time()
        try:
            response = self.es.search(index=self.index_name, body=search_query)
            search_time = time.time() - search_start
            
            print(f"\n⚡ Search completed in {search_time:.3f}s")
            print(f"📊 Total hits: {response['hits']['total']['value']}")
            print(f"🎯 Results returned: {len(response['hits']['hits'])}")
            
            return response
            
        except Exception as e:
            print(f"❌ Search error: {e}")
            return {}

    def analyze_results(self, response: Dict, query: str):
        """Phân tích chi tiết kết quả tìm kiếm"""
        if not response or 'hits' not in response:
            print("❌ No results to analyze")
            return
            
        hits = response['hits']['hits']
        
        print(f"\n📊 DETAILED ANALYSIS OF SEARCH RESULTS")
        print(f"=" * 60)
        print(f"🔍 Query: '{query}'")
        print(f"📈 Total documents in index: {response['hits']['total']['value']}")
        print(f"🎯 Results matching criteria: {len(hits)}")
        
        if not hits:
            print("❌ No results found matching the minimum score threshold")
            return
            
        print(f"\n🏆 TOP RESULTS:")
        print("-" * 60)
        
        for i, hit in enumerate(hits, 1):
            source = hit['_source']
            score = hit['_score']
            
            print(f"\n#{i} - Score: {score:.4f}")
            print(f"📛 Voucher: {source.get('voucher_name', 'N/A')}")
            print(f"🏪 Merchant: {source.get('merchant', 'N/A')}")
            print(f"💰 Price: {source.get('metadata', {}).get('price', 'N/A'):,}đ")
            print(f"📍 Location: {source.get('metadata', {}).get('location', 'N/A')}")
            print(f"📁 Source: {source.get('metadata', {}).get('source_file', 'N/A')}")
            
            # Hiển thị nội dung (giới hạn 200 ký tự)
            content = source.get('content', '')
            if len(content) > 200:
                content = content[:200] + "..."
            print(f"📄 Content: {content}")
            
            # Phân tích độ liên quan
            self._analyze_relevance(source, query, score)
            print("-" * 40)

    def _analyze_relevance(self, source: Dict, query: str, score: float):
        """Phân tích tại sao kết quả này liên quan đến query"""
        content = source.get('content', '').lower()
        voucher_name = source.get('voucher_name', '').lower()
        
        # Keywords từ query
        query_keywords = ['cafe', 'quán', 'không gian', 'lãng mạn', 'coffee']
        
        matched_keywords = []
        for keyword in query_keywords:
            if keyword in content or keyword in voucher_name:
                matched_keywords.append(keyword)
        
        print(f"🎯 Relevance Analysis:")
        print(f"   - Similarity score: {score:.4f}")
        print(f"   - Matched keywords: {matched_keywords if matched_keywords else 'None (semantic similarity)'}")
        
        # Đánh giá mức độ phù hợp
        if score >= 1.8:
            relevance = "🟢 Highly Relevant"
        elif score >= 1.6:
            relevance = "🟡 Moderately Relevant" 
        elif score >= 1.4:
            relevance = "🟠 Somewhat Relevant"
        else:
            relevance = "🔴 Low Relevance"
            
        print(f"   - Assessment: {relevance}")

    def run_demo(self):
        """Chạy demo tìm kiếm"""
        print("🚀 VECTOR SEARCH DEMO - VOUCHER AI ASSISTANT")
        print("=" * 60)
        
        # Query test
        test_query = "quán cafe có không gian lãng mạn"
        
        print(f"🎯 Test case: Searching for '{test_query}'")
        print("📝 Expected results: Cafe/coffee vouchers with romantic ambiance")
        
        # Thực hiện tìm kiếm
        results = self.semantic_search(test_query, size=10, min_score=0.5)
        
        # Phân tích kết quả
        self.analyze_results(results, test_query)
        
        # Tóm tắt insights
        self._provide_insights(results, test_query)

    def _provide_insights(self, response: Dict, query: str):
        """Cung cấp insights về kết quả tìm kiếm"""
        if not response or 'hits' not in response:
            return
            
        hits = response['hits']['hits']
        
        print(f"\n💡 SEARCH INSIGHTS & RECOMMENDATIONS")
        print("=" * 60)
        
        if not hits:
            print("🔍 No results found. Suggestions:")
            print("   - Try broader keywords like 'cafe' or 'coffee'")
            print("   - Lower the minimum score threshold")
            print("   - Check if relevant vouchers exist in the database")
            return
        
        # Phân tích merchants
        merchants = {}
        locations = {}
        avg_price = 0
        total_price_count = 0
        
        for hit in hits:
            source = hit['_source']
            merchant = source.get('merchant', 'Unknown')
            location = source.get('metadata', {}).get('location', 'Unknown')
            price = source.get('metadata', {}).get('price', 0)
            
            merchants[merchant] = merchants.get(merchant, 0) + 1
            locations[location] = locations.get(location, 0) + 1
            
            if price > 0:
                avg_price += price
                total_price_count += 1
        
        print(f"📊 Results Statistics:")
        print(f"   - Total relevant vouchers: {len(hits)}")
        if total_price_count > 0:
            print(f"   - Average voucher value: {avg_price/total_price_count:,.0f}đ")
        
        print(f"\n🏪 Top Merchants:")
        for merchant, count in sorted(merchants.items(), key=lambda x: x[1], reverse=True)[:3]:
            print(f"   - {merchant}: {count} vouchers")
            
        print(f"\n📍 Locations:")
        for location, count in sorted(locations.items(), key=lambda x: x[1], reverse=True)[:3]:
            print(f"   - {location}: {count} vouchers")
        
        print(f"\n🎯 Search Quality Assessment:")
        high_quality = sum(1 for hit in hits if hit['_score'] >= 1.7)
        medium_quality = sum(1 for hit in hits if 1.5 <= hit['_score'] < 1.7)
        low_quality = len(hits) - high_quality - medium_quality
        
        print(f"   - High relevance (≥1.7): {high_quality} results")
        print(f"   - Medium relevance (1.5-1.7): {medium_quality} results")
        print(f"   - Lower relevance (<1.5): {low_quality} results")

if __name__ == "__main__":
    demo = VoucherVectorSearchDemo()
    demo.run_demo()
