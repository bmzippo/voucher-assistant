# 📡 API Documentation

> **  AI Voucher Assistant - RESTful API Reference**

## 📋 Table of Contents
- [Base URL & Authentication](#base-url--authentication)
- [Core Endpoints](#core-endpoints)
- [Request/Response Formats](#requestresponse-formats)
- [Error Handling](#error-handling)
- [Rate Limiting](#rate-limiting)
- [Examples](#examples)

## 🌐 Base URL & Authentication

### Base URL
```
Development: http://localhost:8001
Production: https://api.oneu.com/voucher-assistant
```

### Authentication
```http
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

## 🔧 Core Endpoints

### 1. Advanced Search
**The main search endpoint with hybrid search capabilities**

```http
POST /api/advanced-search
```

#### Request Body
```typescript
interface AdvancedSearchRequest {
  query: string;                    // Search query in Vietnamese/English
  top_k?: number;                   // Number of results (default: 10)
  location_filter?: string;         // Filter by location
  service_filter?: string;          // Filter by service type
  price_filter?: string;            // Filter by price range
}
```

#### Response
```typescript
interface AdvancedSearchResponse {
  query: string;
  parsed_components: {
    intent: string;                 // find_restaurant | find_hotel | etc.
    location: string | null;
    location_type: string | null;
    service_requirements: string[];
    target_audience: string | null;
    confidence: number;
  };
  search_strategy: {
    primary_field: string;
    boost_factors: Record<string, number>;
    filters: Record<string, any>;
    ranking_weights: {
      semantic_similarity: number;
      location_match: number;
      service_match: number;
      target_match: number;
    };
  };
  results: SearchResult[];
  explanations: {
    query_parsing: string;
    geographic_ranking: string;
  };
  metadata: {
    total_results: number;
    processing_time_ms: number;
    search_method: string;
    embedding_dimensions: number;
  };
}

interface SearchResult {
  voucher_id: string;
  voucher_name: string;
  content: string;
  similarity_score: number;
  location: {
    name: string;
    region: string;
    district: string;
  };
  service_info: {
    category: string;
    tags: string[];
    has_kids_area: boolean;
    restaurant_type: string;
  };
  price_info: {
    original_price: number;
    price_range: string;
    currency: string;
  };
  target_audience: string;
  search_method: string;
  ranking_factor?: string;
}
```

#### Example Request
```bash
curl -X POST "http://localhost:8001/api/advanced-search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "buffet tre em tai ha noi",
    "top_k": 5
  }'
```

#### Example Response
```json
{
  "query": "buffet tre em tai ha noi",
  "parsed_components": {
    "intent": "find_restaurant",
    "location": "Hà Nội",
    "location_type": "city",
    "service_requirements": [],
    "target_audience": null,
    "confidence": 0.33
  },
  "search_strategy": {
    "primary_field": "combined_embedding",
    "boost_factors": {
      "location_exact_match": 2.0
    },
    "filters": {
      "location": "Hà Nội"
    },
    "ranking_weights": {
      "semantic_similarity": 0.6,
      "location_match": 0.5,
      "service_match": 0.2,
      "target_match": 0.1
    }
  },
  "results": [
    {
      "voucher_id": "import_importvoucher_127",
      "voucher_name": "Set Saturday dinner buffet trẻ em tại Lộc Ally - Grand Mercure Hanoi",
      "content": "",
      "similarity_score": 0.40086,
      "location": {
        "name": "Hà Nội",
        "region": "Miền Bắc",
        "district": ""
      },
      "service_info": {
        "category": "Restaurant",
        "tags": ["buffet", "trẻ em"],
        "has_kids_area": true,
        "restaurant_type": "buffet"
      },
      "price_info": {
        "original_price": 0,
        "price_range": "Budget",
        "currency": "VND"
      },
      "target_audience": "Family",
      "search_method": "advanced_multi_field",
      "ranking_factor": "exact_location_match"
    }
  ],
  "explanations": {
    "query_parsing": "Phân tích query: 'buffet tre em tai ha noi'\\n- Ý định: find_restaurant\\n- Địa điểm: Hà Nội (city)\\n- Độ tin cậy: 0.33",
    "geographic_ranking": "Kết quả tìm kiếm cho địa điểm: Hà Nội..."
  },
  "metadata": {
    "total_results": 1,
    "processing_time_ms": 764.53,
    "search_method": "advanced_multi_field_with_intelligence",
    "embedding_dimensions": 768
  }
}
```

### 2. Health Check
**System health and status monitoring**

```http
GET /api/health
```

#### Response
```json
{
  "status": "healthy",
  "timestamp": "2025-07-22T10:30:00Z",
  "version": "1.0.0",
  "services": {
    "elasticsearch": "connected",
    "embedding_model": "loaded",
    "query_parser": "ready"
  },
  "performance": {
    "avg_response_time_ms": 156.7,
    "total_queries_today": 1247,
    "cache_hit_rate": 0.73
  }
}
```

### 3. Index Voucher (Admin)
**Add or update voucher in the search index**

```http
POST /api/index-voucher-advanced
```

#### Request Body
```typescript
interface IndexVoucherRequest {
  voucher_id: string;
  voucher_name: string;
  content?: string;
  metadata?: {
    price?: number;
    district?: string;
    category?: string;
  };
  created_at?: string;
  updated_at?: string;
}
```

#### Response
```json
{
  "success": true,
  "voucher_id": "new_voucher_123",
  "message": "Voucher indexed successfully",
  "processing_time_ms": 234.5
}
```

### 4. Bulk Index (Admin)
**Bulk index multiple vouchers**

```http
POST /api/bulk-index
```

#### Request Body
```typescript
interface BulkIndexRequest {
  vouchers: IndexVoucherRequest[];
  batch_size?: number;
}
```

### 5. Search Statistics
**Get search analytics and performance metrics**

```http
GET /api/statistics
```

#### Response
```json
{
  "total_vouchers": 10547,
  "total_searches_today": 1247,
  "avg_response_time_ms": 156.7,
  "popular_queries": [
    "buffet hà nội",
    "khách sạn hcm",
    "massage spa"
  ],
  "search_distribution": {
    "restaurant": 0.45,
    "hotel": 0.25,
    "entertainment": 0.15,
    "shopping": 0.10,
    "other": 0.05
  }
}
```

## 📝 Request/Response Formats

### Content Types
- **Request**: `application/json`
- **Response**: `application/json`
- **Encoding**: UTF-8

### Query Parameters
```typescript
// Common query parameters
interface QueryParams {
  page?: number;        // Pagination (default: 1)
  limit?: number;       // Results per page (default: 10, max: 100)
  sort?: string;        // Sort field
  order?: 'asc' | 'desc'; // Sort order
}
```

### Headers
```http
# Required headers
Content-Type: application/json
Accept: application/json

# Optional headers
Authorization: Bearer <token>
X-Request-ID: <uuid>
User-Agent: <client_info>
```

## ❌ Error Handling

### Standard Error Response
```typescript
interface ErrorResponse {
  error: {
    code: string;           // Error code
    message: string;        // Human-readable message
    details?: any;          // Additional error details
    timestamp: string;      // ISO 8601 timestamp
    request_id?: string;    // Request tracking ID
  };
}
```

### Error Codes
```typescript
// HTTP 400 - Bad Request
{
  "error": {
    "code": "INVALID_QUERY",
    "message": "Query must be at least 2 characters long",
    "details": {
      "field": "query",
      "provided_length": 1,
      "minimum_length": 2
    },
    "timestamp": "2025-07-22T10:30:00Z"
  }
}

// HTTP 429 - Too Many Requests
{
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Too many requests. Please try again later.",
    "details": {
      "limit": 100,
      "window": "1 hour",
      "retry_after": 3600
    },
    "timestamp": "2025-07-22T10:30:00Z"
  }
}

// HTTP 500 - Internal Server Error
{
  "error": {
    "code": "INTERNAL_ERROR",
    "message": "An internal error occurred. Please try again.",
    "details": {
      "error_id": "err_123456",
      "support_contact": "support@oneu.com"
    },
    "timestamp": "2025-07-22T10:30:00Z"
  }
}
```

### HTTP Status Codes
- **200**: Success
- **400**: Bad Request (invalid input)
- **401**: Unauthorized (missing/invalid token)
- **403**: Forbidden (insufficient permissions)
- **404**: Not Found
- **429**: Too Many Requests (rate limited)
- **500**: Internal Server Error
- **503**: Service Unavailable

## 🚦 Rate Limiting

### Limits
```yaml
Public API:
  - 100 requests per hour per IP
  - 1000 requests per day per IP

Authenticated API:
  - 1000 requests per hour per user
  - 10000 requests per day per user

Admin API:
  - 10000 requests per hour
  - No daily limit
```

### Rate Limit Headers
```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 87
X-RateLimit-Reset: 1642781400
X-RateLimit-Window: 3600
```

## 💡 Examples

### Simple Search
```javascript
// JavaScript/TypeScript example
const searchVouchers = async (query) => {
  try {
    const response = await fetch('/api/advanced-search', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        query: query,
        top_k: 10
      })
    });
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const data = await response.json();
    return data.results;
  } catch (error) {
    console.error('Search failed:', error);
    throw error;
  }
};

// Usage
const results = await searchVouchers("buffet hà nội");
```

### Advanced Search with Filters
```python
# Python example
import requests

def advanced_search(query, location=None, service_type=None):
    url = "http://localhost:8001/api/advanced-search"
    
    payload = {
        "query": query,
        "top_k": 10
    }
    
    if location:
        payload["location_filter"] = location
    if service_type:
        payload["service_filter"] = service_type
    
    response = requests.post(url, json=payload)
    response.raise_for_status()
    
    return response.json()

# Usage
results = advanced_search(
    query="spa massage", 
    location="Hà Nội",
    service_type="Beauty"
)
```

### Error Handling
```typescript
// TypeScript with proper error handling
interface ApiError {
  code: string;
  message: string;
  details?: any;
}

const handleApiError = (error: any): ApiError => {
  if (error.response?.data?.error) {
    return error.response.data.error;
  }
  
  return {
    code: 'UNKNOWN_ERROR',
    message: 'An unexpected error occurred'
  };
};

const searchWithErrorHandling = async (query: string) => {
  try {
    const response = await axios.post('/api/advanced-search', {
      query,
      top_k: 10
    });
    
    return response.data;
  } catch (error) {
    const apiError = handleApiError(error);
    
    switch (apiError.code) {
      case 'INVALID_QUERY':
        alert('Please enter a valid search query');
        break;
      case 'RATE_LIMIT_EXCEEDED':
        alert('Too many requests. Please wait before trying again.');
        break;
      default:
        alert('Search failed. Please try again.');
    }
    
    throw apiError;
  }
};
```

## 🧪 Testing

### API Testing with curl
```bash
# Health check
curl -X GET "http://localhost:8001/api/health"

# Basic search
curl -X POST "http://localhost:8001/api/advanced-search" \
  -H "Content-Type: application/json" \
  -d '{"query": "Bellissimo", "top_k": 3}'

# Search with filters
curl -X POST "http://localhost:8001/api/advanced-search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "buffet",
    "top_k": 5,
    "location_filter": "Hà Nội",
    "service_filter": "Restaurant"
  }'
```

### Load Testing
```bash
# Using Apache Bench
ab -n 1000 -c 10 -T "application/json" \
  -p search_payload.json \
  http://localhost:8001/api/advanced-search

# Using wrk
wrk -t12 -c400 -d30s \
  -s search_script.lua \
  http://localhost:8001/api/advanced-search
```

---

**Next**: [⚙️ Backend Guide](./BACKEND.md)
