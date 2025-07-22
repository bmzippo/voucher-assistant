#!/bin/bash

# OneU AI Voucher Assistant - Demo Script
# Phát triển Vector Search API theo yêu cầu người dùng

echo "🚀 OneU AI Voucher Assistant - Vector Search Demo"
echo "================================================"
echo ""

# Test 1: Health Check
echo "1️⃣ Test Vector Search Health Check"
echo "-----------------------------------"
curl -s -X GET "http://localhost:8000/api/vector-search/health" | python3 -m json.tool
echo ""
echo ""

# Test 2: Vector Search - Spa Massage
echo "2️⃣ Test Vector Search - Query: 'voucher spa massage'"
echo "----------------------------------------------------"
curl -s -X POST "http://localhost:8000/api/vector-search" \
  -H "Content-Type: application/json" \
  -d '{"query": "voucher spa massage", "top_k": 2, "min_score": 0.05}' | \
  python3 -c "
import sys, json
data = json.load(sys.stdin)
print(f'Query: {data[\"query\"]}')
print(f'Results: {data[\"total_results\"]}')
print(f'Search Time: {data[\"search_time_ms\"]}ms')
print(f'Embedding Dimension: {data[\"embedding_dimension\"]}')
print('')
for i, result in enumerate(data['results'][:2]):
    print(f'Result {i+1}:')
    print(f'  - Voucher: {result[\"voucher_name\"]}')
    print(f'  - Similarity: {result[\"similarity_score\"]*100:.1f}%')
    print(f'  - Content: {result[\"content\"][:100]}...')
    print('')
"
echo ""

# Test 3: Vector Search - Food & Restaurant
echo "3️⃣ Test Vector Search - Query: 'voucher ăn uống nhà hàng'"
echo "-------------------------------------------------------"
curl -s -X POST "http://localhost:8000/api/vector-search" \
  -H "Content-Type: application/json" \
  -d '{"query": "voucher ăn uống nhà hàng", "top_k": 3, "min_score": 0.05}' | \
  python3 -c "
import sys, json
data = json.load(sys.stdin)
print(f'Query: {data[\"query\"]}')
print(f'Results: {data[\"total_results\"]}')
print(f'Search Time: {data[\"search_time_ms\"]}ms')
print('')
for i, result in enumerate(data['results'][:3]):
    print(f'Result {i+1}:')
    print(f'  - Voucher: {result[\"voucher_name\"]}')
    print(f'  - Similarity: {result[\"similarity_score\"]*100:.1f}%')
    print(f'  - Merchant: {result[\"metadata\"].get(\"source\", \"Unknown\")}')
    print('')
"
echo ""

# Test 4: Hybrid Search
echo "4️⃣ Test Hybrid Search - Query: 'giảm giá Brazil'"
echo "-----------------------------------------------"
curl -s -X POST "http://localhost:8000/api/hybrid-search" \
  -H "Content-Type: application/json" \
  -d '{"query": "giảm giá Brazil", "top_k": 2}' | \
  python3 -c "
import sys, json
data = json.load(sys.stdin)
print(f'Query: {data[\"query\"]}')
print(f'Vector Results: {data[\"total_vector_results\"]}')
print(f'Text Results: {data[\"total_text_results\"]}')
print(f'Search Time: {data[\"search_time_ms\"]}ms')
print('')
print('Vector Search Results:')
for i, result in enumerate(data['vector_results'][:2]):
    print(f'  {i+1}. {result[\"voucher_name\"]} (Score: {result[\"similarity_score\"]*100:.1f}%)')
print('')
print('Text Search Results:')
for i, result in enumerate(data['text_results'][:2]):
    print(f'  {i+1}. {result[\"voucher_name\"]} (Score: {result[\"text_score\"]:.2f})')
print('')
"

# Test 5: Performance Test
echo "5️⃣ Performance Test - Multiple Queries"
echo "--------------------------------------"
echo "Testing search performance with different queries..."

QUERIES=("voucher giảm giá" "nhà hàng ăn uống" "spa massage" "Brazil steak" "ưu đãi khuyến mãi")

for query in "${QUERIES[@]}"; do
    result=$(curl -s -X POST "http://localhost:8000/api/vector-search" \
      -H "Content-Type: application/json" \
      -d "{\"query\": \"$query\", \"top_k\": 1, \"min_score\": 0.01}")
    
    search_time=$(echo $result | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('search_time_ms', 0))")
    total_results=$(echo $result | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('total_results', 0))")
    
    printf "%-25s | %6.2fms | %2d results\n" "$query" "$search_time" "$total_results"
done

echo ""
echo "✅ Demo hoàn thành! Vector Search API đang hoạt động excellent!"
echo ""
echo "🌐 Frontend URL: http://localhost:3000"
echo "🔧 Backend API: http://localhost:8000"
echo "📊 API Health: http://localhost:8000/api/vector-search/health"
echo ""
echo "💡 Để test UI, vào http://localhost:3000 và scroll xuống phần 'Tìm kiếm Vector AI'"
