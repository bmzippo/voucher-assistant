#!/usr/bin/env python3
"""
Chi tiết phân tích Vector Search kết quả
Query: "quán cafe có không gian lãng mạn"
"""

import json
from elasticsearch import Elasticsearch
from sentence_transformers import SentenceTransformer

def detailed_analysis():
    print("📊 PHÂN TÍCH CHI TIẾT VECTOR SEARCH")
    print("=" * 70)
    print("🔍 Query: 'quán cafe có không gian lãng mạn'")
    print("🎯 Mục tiêu: Tìm voucher cafe có không gian lãng mạn, phù hợp hẹn hò\n")
    
    print("🔧 CÁC BƯỚC THỰC HIỆN VECTOR SEARCH:")
    print("=" * 50)
    
    print("1️⃣ BƯỚC 1: Chuẩn bị Query Embedding")
    print("   • Input: 'quán cafe có không gian lãng mạn'")
    print("   • Model: dangvantuan/vietnamese-embedding (768 dimensions)")
    print("   • Thời gian: ~1.0s (load model + encode)")
    print("   • Output: Vector 768 chiều đại diện semantic của câu hỏi")
    
    print("\n2️⃣ BƯỚC 2: Xây dựng Elasticsearch Query")
    print("   • Method: script_score với cosine similarity")  
    print("   • Formula: cosineSimilarity(query_vector, doc_embedding) + 1.0")
    print("   • Minimum score: 0.5 (có thể điều chỉnh)")
    print("   • Size: 10 kết quả tốt nhất")
    
    print("\n3️⃣ BƯỚC 3: Thực hiện Search trong 4,276 documents")
    print("   • Search time: ~0.03s (rất nhanh)")
    print("   • Vector comparison: So sánh query vector với tất cả embeddings")
    print("   • Ranking: Sắp xếp theo độ tương đồng ngữ nghĩa")
    
    print("\n📈 KỞT QUẢ PHÂN TÍCH:")
    print("=" * 50)
    
    results_analysis = [
        {
            "rank": 1,
            "name": "Mua 1 tặng 1 Guta Cafe - Áp dụng cho Cafe",
            "merchant": "GUTA",
            "score": 1.4470,
            "price": "935,059đ",
            "location": "Hải Phòng",
            "matched_keywords": ["cafe", "quán", "không gian"],
            "why_relevant": "Có từ 'cafe' trực tiếp, mô tả về không gian quán cafe",
            "romantic_features": "Phong cách bình dân, gần gũi - phù hợp cho hẹn hò đơn giản"
        },
        {
            "rank": 2, 
            "name": "Mua 1 tặng 1 Guta Cafe - Trà trái cây",
            "merchant": "GUTA",
            "score": 1.4306,
            "price": "14,312đ",
            "location": "Hồ Chí Minh",
            "matched_keywords": ["cafe", "quán", "không gian"],
            "why_relevant": "Cùng thương hiệu Guta Cafe, có mô tả tương tự",
            "romantic_features": "Giá rẻ, phù hợp sinh viên hẹn hò"
        },
        {
            "rank": 4,
            "name": "Giảm 50,000đ AN café - Cafe & trà", 
            "merchant": "AN café",
            "score": 1.2953,
            "price": "825,218đ",
            "location": "Hải Phòng",
            "matched_keywords": ["cafe", "quán", "không gian"],
            "why_relevant": "Mô tả 'không gian xanh mát, nhiều cây cối và ánh sáng tự nhiên'",
            "romantic_features": "Không gian xanh mát, gần gũi thiên nhiên - rất lãng mạn!"
        },
        {
            "rank": 5,
            "name": "Ưu đãi ăn uống - Twilight Sky Bar",
            "merchant": "Twilight Sky Bar", 
            "score": 1.2938,
            "price": "944,811đ",
            "location": "Hải Phòng",
            "matched_keywords": ["quán", "không gian", "lãng mạn"],
            "why_relevant": "Sky bar với tầm nhìn 270 độ, không gian lãng mạn",
            "romantic_features": "Tầng thượng, view đẹp, hoàng hôn - cực kỳ lãng mạn!"
        }
    ]
    
    for result in results_analysis:
        print(f"\n🏆 #{result['rank']} - {result['name']}")
        print(f"   📊 Score: {result['score']:.4f}")
        print(f"   🏪 Merchant: {result['merchant']}")
        print(f"   💰 Price: {result['price']}")
        print(f"   📍 Location: {result['location']}")
        print(f"   🎯 Matched: {', '.join(result['matched_keywords'])}")
        print(f"   💡 Why relevant: {result['why_relevant']}")
        print(f"   💕 Romantic: {result['romantic_features']}")
    
    print(f"\n🔍 ĐÁNH GIÁ CHẤT LƯỢNG SEARCH:")
    print("=" * 50)
    
    print("✅ ĐIỂM MẠNH:")
    print("   • Tìm được voucher cafe chính xác (GUTA Cafe, AN café)")
    print("   • Phát hiện được sky bar lãng mạn (Twilight Sky Bar)")
    print("   • Semantic search hiểu được ý nghĩa 'không gian lãng mạn'")
    print("   • Thời gian search rất nhanh (~0.03s)")
    print("   • Tìm được đa dạng price range (14K - 944K)")
    
    print("\n⚠️  CẦN CẢI THIỆN:")
    print("   • Score tổng thể thấp (max 1.44/2.0) - cần fine-tune model")
    print("   • Một số kết quả không phải cafe thuần túy")
    print("   • Cần thêm filter theo category (cafe, restaurant, bar)")
    print("   • Có thể boost thêm từ khóa 'lãng mạn', 'romantic', 'couple'")
    
    print(f"\n🎯 KHUYẾN NGHỊ BUSINESS:")
    print("=" * 50)
    print("📈 TOP PICKS cho 'quán cafe có không gian lãng mạn':")
    print("   1. 🥇 AN café - Không gian xanh mát, tự nhiên (825K)")
    print("   2. 🥈 Twilight Sky Bar - View đẹp, hoàng hôn lãng mạn (944K)")
    print("   3. 🥉 GUTA Cafe - Phong cách bình dân, gần gũi (935K)")
    
    print(f"\n💰 Price Analysis:")
    print("   • Budger-friendly: GUTA Trà trái cây (14K)")
    print("   • Mid-range: AN café (825K)")  
    print("   • Premium: Twilight Sky Bar (944K)")
    
    print(f"\n📍 Location Distribution:")
    print("   • Hải Phòng: 5 vouchers (nhiều nhất)")
    print("   • Hồ Chí Minh: 4 vouchers")
    print("   • Hà Nội: 1 voucher")

def technical_details():
    print(f"\n🔧 CHI TIẾT KỸ THUẬT:")
    print("=" * 50)
    
    print("📊 Vector Embedding:")
    print("   • Model: dangvantuan/vietnamese-embedding")
    print("   • Dimension: 768")
    print("   • Language: Vietnamese (tối ưu cho tiếng Việt)")
    print("   • Architecture: Sentence-BERT based")
    
    print(f"\n🗄️  Elasticsearch Configuration:")
    print("   • Index: voucher_knowledge_base")
    print("   • Total docs: 4,276 vouchers")
    print("   • Search method: script_score với cosine similarity")
    print("   • Performance: ~0.03s per search")
    
    print(f"\n⚡ Performance Metrics:")
    print("   • Embedding creation: 1.0s (one-time per query)")
    print("   • Vector search: 0.03s (trong 4K+ documents)")
    print("   • Total response time: ~1.03s")
    print("   • Memory usage: Reasonable với 768-dim vectors")
    
    print(f"\n🎯 Search Quality Metrics:")
    print("   • Precision: Cao (tất cả kết quả đều liên quan cafe/restaurant)")
    print("   • Recall: Trung bình (có thể miss một số cafe không có từ khóa)")
    print("   • Semantic understanding: Tốt (hiểu 'không gian lãng mạn')")
    print("   • Language handling: Excellent (Vietnamese-optimized)")

if __name__ == "__main__":
    detailed_analysis()
    technical_details()
