# 🔍 Unified Search Interface Documentation

## Tổng Quan

Unified Search Interface cung cấp **3 chế độ tìm kiếm** khác nhau để phù hợp với các use case và requirements khác nhau trong hệ thống voucher AI Assistant.

## 🎯 3 Chế độ Tìm Kiếm

### 1. 🤖 RAG Mode (Recommended)
**Full RAG Pipeline**: Retrieval + AI Generation

```python
result = await vector_store.search(query, search_type="rag")
```

**Đặc điểm**:
- ✅ Complete AI-powered response với lời khuyên tự nhiên
- ✅ Context-aware và conversation-friendly
- ✅ Vietnamese language generation với cultural awareness
- ✅ Interactive với follow-up questions
- ⏱️ **Processing time**: 0.4-1.2s
- 🎯 **Best for**: Production chatbot, customer interaction

**Output example**:
```
🎯 Tôi tìm thấy **3 voucher** phù hợp với yêu cầu của bạn:

**1.** Buffet Hải Sản AC600 cho 01 người - Ambassador Club Nha Trang
**2.** Buffet Hải Sản Tôm Hùm AC900 cho 01 người

💡 **Lời khuyên:**
- Kiểm tra điều khoản sử dụng trước khi đặt
- Đặt bàn trước để đảm bảo có chỗ

❓ Bạn có muốn tôi giải thích chi tiết về voucher nào không?
```

### 2. 🎯 Vector Mode
**Pure Semantic Search**: Chỉ vector similarity

```python
result = await vector_store.search(query, search_type="vector")
```

**Đặc điểm**:
- ✅ Fastest response time (sub-100ms)
- ✅ Pure similarity scores
- ✅ Raw voucher data với metadata
- ⚡ **Processing time**: <0.1s
- 🎯 **Best for**: Backend APIs, bulk processing, similarity analysis

**Output**: Raw voucher list với similarity scores

### 3. ⚡ Hybrid Mode
**Vector + Basic Context**: Cân bằng speed và context

```python
result = await vector_store.search(query, search_type="hybrid")
```

**Đặc điểm**:
- ✅ Fast processing với basic formatting
- ✅ Structured voucher list với key details
- ✅ Minimal context without full AI generation
- ⏱️ **Processing time**: ~0.1s
- 🎯 **Best for**: Quick previews, mobile apps, search suggestions

**Output example**:
```
🎯 **Kết quả tìm kiếm cho**: "buffet hải sản gia đình"
📊 **Tìm thấy**: 3 voucher phù hợp

**1. Buffet Hải Sản AC600**
   📍 Hồ Chí Minh
   ⭐ Độ phù hợp: 79.5%

💡 **Để được tư vấn chi tiết hơn, hãy sử dụng chế độ RAG search!**
```

## 📊 Performance Comparison

| Mode | Processing Time | AI Generation | Use Case |
|------|----------------|---------------|----------|
| **RAG** | 0.4-1.2s | ✅ Full AI response | Production chatbot |
| **Vector** | <0.1s | ❌ Raw results only | Backend APIs |
| **Hybrid** | ~0.1s | ⚡ Basic formatting | Quick previews |

## 🔧 API Usage

### Basic Usage
```python
from advanced_vector_store import AdvancedVectorStore

# Initialize
vector_store = AdvancedVectorStore(index_name="voucher_knowledge")

# RAG Search (Recommended)
rag_result = await vector_store.search(
    query="buffet hải sản ở TP.HCM cho gia đình",
    search_type="rag",
    top_k=5
)

# Access results
print(f"AI Answer: {rag_result.answer}")
print(f"Confidence: {rag_result.confidence_score}")
print(f"Processing time: {rag_result.processing_time}s")
```

### Advanced Usage với Filters
```python
# Search với location và service filters
result = await vector_store.search(
    query="voucher spa massage",
    search_type="rag",
    top_k=3,
    location_filter="Hà Nội",
    service_filter="Beauty",
    price_filter="Budget"
)
```

### Batch Processing với Vector Mode
```python
queries = ["buffet hà nội", "spa massage", "cafe lãng mạn"]

# Fast batch processing
for query in queries:
    result = await vector_store.search(query, search_type="vector")
    print(f"Query: {query} -> {len(result.retrieved_vouchers)} results")
```

## 🎯 Recommendation Guidelines

### Sử dụng RAG Mode khi:
- ✅ Customer-facing chatbot
- ✅ Interactive conversation cần AI-generated responses
- ✅ Cần advice và recommendations chi tiết
- ✅ Vietnamese natural language responses

### Sử dụng Vector Mode khi:
- ✅ Backend API integration
- ✅ Bulk processing large volumes
- ✅ Similarity analysis và ranking
- ✅ Real-time suggestions với latency constraints

### Sử dụng Hybrid Mode khi:
- ✅ Mobile app với limited processing power
- ✅ Quick search previews
- ✅ Search suggestions dropdown
- ✅ Cần balance giữa speed và basic context

## 🚀 Production Deployment

### Environment Variables
```bash
# Required for RAG mode
export LLM_MODEL="gpt-4o-mini"
export OPENAI_API_KEY="your-api-key"
export LLM_TEMPERATURE="0.3"
export MAX_CONTEXT_TOKENS="4000"

# Elasticsearch configuration
export ELASTICSEARCH_INDEX="voucher_knowledge"
export EMBEDDING_MODEL="dangvantuan/vietnamese-embedding"
```

### Integration Examples

#### FastAPI Endpoint
```python
from fastapi import FastAPI
from advanced_vector_store import AdvancedVectorStore

app = FastAPI()
vector_store = AdvancedVectorStore()

@app.post("/search/rag")
async def rag_search(query: str):
    result = await vector_store.search(query, search_type="rag")
    return {
        "answer": result.answer,
        "confidence": result.confidence_score,
        "vouchers": result.retrieved_vouchers
    }

@app.post("/search/quick")  
async def quick_search(query: str):
    result = await vector_store.search(query, search_type="hybrid")
    return {
        "summary": result.answer,
        "vouchers": result.retrieved_vouchers
    }
```

#### React Frontend Integration
```javascript
// RAG search for detailed AI responses
const ragSearch = async (query) => {
  const response = await fetch('/api/search/rag', {
    method: 'POST',
    body: JSON.stringify({ query, search_type: 'rag' })
  });
  return response.json();
};

// Quick search for dropdowns/suggestions
const quickSearch = async (query) => {
  const response = await fetch('/api/search/quick', {
    method: 'POST', 
    body: JSON.stringify({ query, search_type: 'hybrid' })
  });
  return response.json();
};
```

## 📈 Monitoring & Analytics

### Key Metrics to Track
```python
# Track search performance by mode
search_metrics = {
    'rag': {
        'avg_processing_time': 0.8,
        'avg_confidence': 0.95,
        'user_satisfaction': 0.92
    },
    'vector': {
        'avg_processing_time': 0.05,
        'avg_confidence': 0.88,
        'click_through_rate': 0.15
    },
    'hybrid': {
        'avg_processing_time': 0.12,
        'avg_confidence': 0.90,
        'conversion_rate': 0.25
    }
}
```

### A/B Testing Framework
```python
# A/B test different modes for same queries
async def ab_test_search_modes(query: str, user_segment: str):
    if user_segment == 'premium':
        return await vector_store.search(query, search_type="rag")
    elif user_segment == 'mobile':
        return await vector_store.search(query, search_type="hybrid")
    else:
        return await vector_store.search(query, search_type="vector")
```

---

## 🎉 Conclusion

Unified Search Interface cung cấp **flexibility cho mọi use case**:

- **RAG Mode**: Production-ready AI chatbot với full Vietnamese conversation
- **Vector Mode**: High-performance backend processing
- **Hybrid Mode**: Balanced approach cho mobile và quick interactions

**Recommendation**: Bắt đầu với **RAG mode** cho customer-facing features, và sử dụng Vector/Hybrid modes cho backend optimization và mobile performance.

---

*Documentation version: 1.0*  
*Last updated: January 22, 2025*
